# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Structural round-trip tests for the generic schematic netlist emitter
(``skidl.schematic_netlist.build_generic_netlist``).

These tests assert that the emitted JSON document faithfully carries the
circuit's electrical structure (components, connectivity, hierarchy),
embedded symbol geometry, and layout hints (mirror/rotate + net stubbing).
They are deliberately *structural*: they reconstruct the connectivity graph
from the JSON and compare it to the original circuit, rather than generating
a schematic and diffing files. Schematic placement is nondeterministic
(randomized force-directed placer), so byte-level comparison is not
meaningful; the structure, however, must round-trip exactly.
"""

import json

from skidl import Circuit, Net, Part, subcircuit
from skidl.schematic_netlist import (
    SCHEMA_NAME,
    SCHEMA_VERSION,
    build_generic_netlist,
)


# ---------------------------------------------------------------------------
# Circuit builders
# ---------------------------------------------------------------------------


def _flat_circuit():
    """A flat RC circuit exercising a user mirror hint and a stubbed net."""
    ckt = Circuit()
    with ckt:
        vcc, gnd, sig = Net("VCC"), Net("GND"), Net("SIG")
        r1 = Part(
            "Device", "R", value="10k",
            footprint="Resistor_SMD:R_0805_2012Metric",
        )
        c1 = Part(
            "Device", "C", value="100nF",
            footprint="Capacitor_SMD:C_0805_2012Metric",
        )
        r1[1] += vcc
        r1[2] += sig
        c1[1] += sig
        c1[2] += gnd
        gnd.stub = True          # user net-stub hint
        gnd.netio = "i"          # user io-direction hint
        r1.symtx = "H"           # user mirror hint
    ckt.merge_net_names()
    ckt.merge_nets()
    return ckt


@subcircuit
def _rc_stage(vin, vout, gnd):
    r = Part(
        "Device", "R", value="1k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )
    c = Part(
        "Device", "C", value="10nF",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )
    r[1] += vin
    r[2] += vout
    c[1] += vout
    c[2] += gnd


def _hier_circuit():
    """A two-stage RC filter built from nested subcircuits."""
    ckt = Circuit()
    with ckt:
        vin, mid, out, gnd = Net("VIN"), Net("MID"), Net("OUT"), Net("GND")
        _rc_stage(vin, mid, gnd)
        _rc_stage(mid, out, gnd)
    ckt.merge_net_names()
    ckt.merge_nets()
    return ckt


# ---------------------------------------------------------------------------
# Helpers: extract the connectivity graph from a Circuit and from a document
# ---------------------------------------------------------------------------


def _connectivity_from_circuit(ckt):
    """Return {net_name: sorted[(ref, pin_num)]} for real parts in a circuit."""
    graph = {}
    for net in ckt.get_nets():
        nodes = []
        for pin in net.pins:
            nodes.append((pin.part.ref, str(pin.num)))
        graph[net.name] = sorted(nodes)
    return graph


def _connectivity_from_doc(doc):
    """Return {net_name: sorted[(ref, pin_num)]} from a netlist document."""
    graph = {}
    for net in doc["nets"]:
        nodes = [(n["ref"], str(n["pin"])) for n in net["nodes"]]
        graph[net["name"]] = sorted(nodes)
    return graph


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_document_shape_and_serializable():
    """The document has the expected top-level shape and is JSON-serializable."""
    doc = build_generic_netlist(_flat_circuit(), title="T", top_name="flat")

    # Must be losslessly JSON-serializable (no Sexp/defaultdict leakage).
    reloaded = json.loads(json.dumps(doc))
    assert reloaded == doc

    assert doc["format"] == SCHEMA_NAME
    assert doc["version"] == SCHEMA_VERSION
    assert doc["title"] == "T"
    assert doc["top_name"] == "flat"
    for key in ("symbols", "components", "nets", "sheets"):
        assert key in doc


def test_component_and_symbol_coverage():
    """Every real part yields a component; every lib_id yields one symbol."""
    ckt = _flat_circuit()
    doc = build_generic_netlist(ckt)

    real_parts = [p for p in ckt.parts if p.name != "NT"]
    assert len(doc["components"]) == len(real_parts)

    refs = {c["ref"] for c in doc["components"]}
    assert refs == {p.ref for p in real_parts}

    # Symbols are deduplicated by lib_id and cover every component.
    comp_lib_ids = {c["lib_id"] for c in doc["components"]}
    assert set(doc["symbols"]) == comp_lib_ids
    assert len(doc["symbols"]) == 2  # Device:R and Device:C


def test_connectivity_round_trips():
    """The JSON reproduces the circuit's net connectivity exactly."""
    for builder in (_flat_circuit, _hier_circuit):
        ckt = builder()
        doc = build_generic_netlist(ckt)
        assert _connectivity_from_doc(doc) == _connectivity_from_circuit(ckt)


def test_component_contract_fields_present():
    """Each component carries the full contract, incl. layout-hint fields.

    Fails loudly if a required field is dropped from the emitter.
    """
    required = {
        "ref",
        "lib_id",
        "value",
        "footprint",
        "hiertuple",
        "symtx",
        "orientation_locked",
        "pins",
    }
    doc = build_generic_netlist(_flat_circuit())
    for comp in doc["components"]:
        assert required <= set(comp), (
            f"{comp.get('ref')} missing {required - set(comp)}"
        )
        for pin in comp["pins"]:
            assert {"num", "unit", "net"} <= set(pin)


def test_net_contract_fields_present():
    """Each net carries the full contract, incl. stub/io hint fields."""
    required = {
        "name",
        "code",
        "stub",
        "stub_explicit",
        "netio",
        "implicit",
        "nodes",
    }
    doc = build_generic_netlist(_flat_circuit())
    for net in doc["nets"]:
        assert required <= set(net), (
            f"{net.get('name')} missing {required - set(net)}"
        )


def test_mirror_hint_round_trips():
    """A user-set part.symtx is captured on exactly that component."""
    doc = build_generic_netlist(_flat_circuit())
    by_ref = {c["ref"]: c for c in doc["components"]}
    assert by_ref["R1"]["symtx"] == "H"
    assert by_ref["C1"]["symtx"] == ""


def test_net_stub_hint_round_trips():
    """A user-set net.stub/netio is captured and marked explicit."""
    doc = build_generic_netlist(_flat_circuit())
    by_name = {n["name"]: n for n in doc["nets"]}
    assert by_name["GND"]["stub"] is True
    assert by_name["GND"]["stub_explicit"] is True
    assert by_name["GND"]["netio"] == "i"
    # A net the user never stubbed is not marked explicit.
    assert by_name["SIG"]["stub"] is False
    assert by_name["SIG"]["stub_explicit"] is False


def test_embedded_symbol_pin_geometry_complete():
    """Embedded symbols carry pin geometry covering every pin of every part."""
    ckt = _flat_circuit()
    doc = build_generic_netlist(ckt)

    for comp in doc["components"]:
        sym = doc["symbols"][comp["lib_id"]]
        # Collect every pin number described by the embedded symbol units.
        sym_pin_nums = set()
        for unit in sym["units"].values():
            for pin in unit["pins"]:
                sym_pin_nums.add(str(pin["num"]))
                # Geometry fields the placement/routing engine needs.
                assert {"num", "x", "y", "orient"} <= set(pin)
        comp_pin_nums = {str(p["num"]) for p in comp["pins"]}
        assert comp_pin_nums <= sym_pin_nums


def test_hierarchy_round_trips():
    """Hierarchy (hiertuple) and sheet levels are captured for subcircuits."""
    ckt = _hier_circuit()
    doc = build_generic_netlist(ckt)

    hiertuples = {tuple(c["hiertuple"]) for c in doc["components"]}
    # Two distinct subcircuit instances, each a depth-2 level under root "".
    assert len(hiertuples) == 2
    assert all(len(h) == 2 and h[0] == "" for h in hiertuples)
    sub_names = {h[1] for h in hiertuples}
    assert len(sub_names) == 2  # the two stages are distinct nodes

    # Each stage contains exactly one R and one C.
    by_level = {}
    for comp in doc["components"]:
        by_level.setdefault(tuple(comp["hiertuple"]), []).append(comp["lib_id"])
    for lib_ids in by_level.values():
        assert sorted(lib_ids) == ["Device:C", "Device:R"]

    # The subcircuit levels appear among the emitted sheet paths.
    sheet_tuples = {tuple(s) for s in doc["sheets"]}
    assert hiertuples <= sheet_tuples


def test_emitter_is_deterministic():
    """Emitting twice from equivalent circuits yields identical documents.

    The emitter must be deterministic even though schematic *placement* is not.
    """
    a = build_generic_netlist(_flat_circuit(), title="t", top_name="x")
    b = build_generic_netlist(_flat_circuit(), title="t", top_name="x")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_part_fields_emitted():
    """User part fields (MPN, DNP, ...) are carried in components[].fields."""
    ckt = Circuit()
    with ckt:
        r1 = Part("Device", "R", value="10k")
        r1.fields["MPN"] = "RC0805FR-0710KL"
        r1.fields["DNP"] = True
        r1[1] += Net("A")
        r1[2] += Net("B")
    ckt.merge_net_names()
    ckt.merge_nets()
    doc = build_generic_netlist(ckt)
    (comp,) = doc["components"]
    assert comp["fields"] == {"MPN": "RC0805FR-0710KL", "DNP": True}
    json.dumps(doc)


def test_netclass_attrs_emitted():
    """Net classes appear in nets[].attrs and their definitions at top level."""
    from skidl import NetClass

    ckt = Circuit()
    with ckt:
        power = NetClass("Power", trace_width=0.5, clearance=0.2, circuit=ckt)
        vcc, gnd = Net("VCC"), Net("GND")
        r1 = Part("Device", "R", value="10k")
        r1[1] += vcc
        r1[2] += gnd
        vcc.netclasses = power
    ckt.merge_net_names()
    ckt.merge_nets()
    doc = build_generic_netlist(ckt)
    nets = {n["name"]: n for n in doc["nets"]}
    assert nets["VCC"]["attrs"] == {"netclasses": ["Power"]}
    assert nets["GND"]["attrs"] == {}
    assert doc["netclasses"]["Power"]["trace_width"] == 0.5
    assert doc["netclasses"]["Power"]["clearance"] == 0.2
    json.dumps(doc)


def test_no_connect_net_emitted():
    """Pins on NC are emitted as a net flagged "nc" so readers can draw NC flags."""
    ckt = Circuit()
    with ckt:
        q = Part("Device", "R", value="1k")
        q[1] += Net("A")
        q[2] += ckt.NC
    ckt.merge_net_names()
    ckt.merge_nets()
    doc = build_generic_netlist(ckt)
    nc_nets = [n for n in doc["nets"] if n.get("nc")]
    assert len(nc_nets) == 1
    assert [(nd["ref"], nd["pin"]) for nd in nc_nets[0]["nodes"]] == [(q.ref, "2")]
    (comp,) = doc["components"]
    pin_nets = {p["num"]: p["net"] for p in comp["pins"]}
    assert pin_nets["2"] == nc_nets[0]["name"]


def test_generate_generic_netlist_writes_json(tmp_path):
    """Circuit.generate_generic_netlist() writes the same document it returns."""
    ckt = _flat_circuit()
    out = tmp_path / "flat.json"
    doc = ckt.generate_generic_netlist(file_=str(out), title="Flat", top_name="flat")
    assert out.exists()
    assert json.loads(out.read_text()) == json.loads(json.dumps(doc))
    assert doc["format"] == SCHEMA_NAME
    assert doc["top_name"] == "flat"
