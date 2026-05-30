# -*- coding: utf-8 -*-

"""Convert JLCEDA Pro ENET JSON netlists into equivalent SKiDL programs."""

from __future__ import annotations

import json
import keyword
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .logger import active_logger


@dataclass(frozen=True)
class EnetNode:
    """A component pin connected to an ENET net."""

    ref: str
    pin_key: str


@dataclass
class EnetNet:
    """An ENET electrical net and its connected pins."""

    name: str
    nodes: list[EnetNode] = field(default_factory=list)


@dataclass
class EnetComponent:
    """A component extracted from a JLCEDA Pro ENET document."""

    ref: str
    value: str
    footprint: str
    lib: str
    symbol: str
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class EnetDocument:
    """The subset of an ENET document required to generate SKiDL source."""

    version: str
    components: list[EnetComponent]
    nets: list[EnetNet]


class EnetFormatError(ValueError):
    """Raised when an ENET document cannot be converted safely."""


def legalize_name(name: str) -> str:
    """Return a stable Python identifier for an ENET object name."""

    name = str(name or "").lstrip("/ ")
    if name.endswith("+"):
        name = name[:-1] + "_p"
    elif name.endswith("-"):
        name = name[:-1] + "_n"
    if name.startswith("+"):
        name = "_p_" + name[1:]
    elif name.startswith("-"):
        name = "_n_" + name[1:]
    legalized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if not legalized:
        legalized = "_"
    if legalized[0].isdigit():
        legalized = "_" + legalized
    if keyword.iskeyword(legalized):
        legalized += "_"
    return legalized


def _load_enet_json(enet_src: Any) -> tuple[dict[str, Any], str]:
    """Load ENET JSON from a path, file-like object, bytes, or text."""

    source_name = "<ENET text>"
    try:
        text = enet_src.read()
        source_name = getattr(enet_src, "name", source_name)
    except AttributeError:
        if isinstance(enet_src, Path):
            source_name = str(enet_src)
            text = enet_src.read_text(encoding="utf-8")
        elif isinstance(enet_src, bytes):
            text = enet_src.decode("utf-8")
        elif isinstance(enet_src, str):
            stripped = enet_src.lstrip()
            if stripped.startswith("{"):
                text = enet_src
            else:
                source_name = enet_src
                text = Path(enet_src).read_text(encoding="utf-8")
        else:
            raise TypeError("ENET source must be a path, text, bytes, or readable object.")
    except OSError as exc:
        raise EnetFormatError(f"Unable to read ENET file {source_name!r}: {exc}") from exc

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise EnetFormatError(f"Invalid ENET JSON in {source_name!r}: {exc}") from exc
    if not isinstance(data, dict):
        raise EnetFormatError(f"ENET root in {source_name!r} must be a JSON object.")
    return data, source_name


def _as_text(value: Any) -> str:
    """Convert an ENET scalar property into source-safe text."""

    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _pick(props: dict[str, Any], *names: str) -> str:
    """Return the first non-empty property value from names."""

    for name in names:
        value = _as_text(props.get(name)).strip()
        if value:
            return value
    return ""


def parse_enet(enet_src: Any) -> EnetDocument:
    """Parse a JLCEDA Pro ENET JSON document and validate its connectivity."""

    data, source_name = _load_enet_json(enet_src)
    raw_components = data.get("components")
    if not isinstance(raw_components, dict) or not raw_components:
        raise EnetFormatError(f"ENET file {source_name!r} has no components object.")

    components: list[EnetComponent] = []
    refs: set[str] = set()
    nets: dict[str, EnetNet] = {}
    unnamed_net_index = 0

    for component_id, raw_component in raw_components.items():
        if not isinstance(raw_component, dict):
            raise EnetFormatError(
                f"Component {component_id!r} in {source_name!r} must be an object."
            )
        props = raw_component.get("props")
        if not isinstance(props, dict):
            raise EnetFormatError(
                f"Component {component_id!r} in {source_name!r} has no props object."
            )

        ref = _pick(props, "Designator")
        if not ref:
            raise EnetFormatError(
                f"Component {component_id!r} in {source_name!r} has no Designator."
            )
        if ref in refs:
            raise EnetFormatError(f"Duplicate component Designator {ref!r} in {source_name!r}.")
        refs.add(ref)

        value = _pick(
            props,
            "Manufacturer Part",
            "LCSC Part Name",
            "DeviceName",
            "Name",
        )
        symbol = _pick(props, "DeviceName", "Manufacturer Part", "LCSC Part Name", "Name")
        footprint = _pick(props, "FootprintName", "Supplier Footprint")
        if not value:
            active_logger.warning("ENET component %s has no value metadata.", ref)
        if not symbol:
            symbol = ref
            active_logger.warning("ENET component %s has no symbol metadata; using ref.", ref)
        if not footprint:
            active_logger.warning("ENET component %s has no footprint metadata.", ref)

        fields = {str(key): _as_text(val) for key, val in props.items()}
        components.append(
            EnetComponent(
                ref=ref,
                value=value,
                footprint=footprint,
                # JLCEDA uses hash IDs rather than KiCad library names. Keep a
                # wildcard so downstream project-symbol matching can resolve it.
                lib="*",
                symbol=symbol,
                fields=fields,
            )
        )

        pin_map = raw_component.get("pinInfoMap")
        if not isinstance(pin_map, dict):
            raise EnetFormatError(
                f"Component {ref!r} in {source_name!r} has no pinInfoMap object."
            )
        for pin_id, raw_pin in pin_map.items():
            if not isinstance(raw_pin, dict):
                raise EnetFormatError(
                    f"Pin {ref}.{pin_id} in {source_name!r} must be an object."
                )
            pin_key = _pick(raw_pin, "number", "name") or str(pin_id).strip()
            if not pin_key:
                raise EnetFormatError(f"Pin on component {ref!r} in {source_name!r} has no key.")

            net_name = _pick(raw_pin, "net")
            if not net_name:
                unnamed_net_index += 1
                net_name = f"unconnected-{ref}-{pin_key}-{unnamed_net_index}"
                active_logger.warning("ENET pin %s.%s has no net; using %s.", ref, pin_key, net_name)
            nets.setdefault(net_name, EnetNet(name=net_name)).nodes.append(
                EnetNode(ref=ref, pin_key=pin_key)
            )

    return EnetDocument(
        version=_as_text(data.get("version")),
        components=components,
        nets=sorted(nets.values(), key=lambda net: net.name),
    )


def _stable_identifiers(names: list[str], kind: str) -> dict[str, str]:
    """Build unique identifiers while keeping collisions deterministic."""

    by_base: dict[str, int] = defaultdict(int)
    identifiers: dict[str, str] = {}
    for name in names:
        base = legalize_name(name)
        by_base[base] += 1
        identifier = base if by_base[base] == 1 else f"{base}_{by_base[base]}"
        if identifier != base:
            active_logger.warning(
                "ENET %s name %r collides after legalization; using %s.",
                kind,
                name,
                identifier,
            )
        identifiers[name] = identifier
    return identifiers


def enet_document_to_skidl(document: EnetDocument) -> str:
    """Generate a single-sheet SKiDL Python program from an ENET document."""

    components = sorted(document.components, key=lambda component: component.ref)
    nets = sorted(document.nets, key=lambda net: net.name)
    component_vars = _stable_identifiers([component.ref for component in components], "component")
    net_vars = _stable_identifiers([net.name for net in nets], "net")

    lines = ["# -*- coding: utf-8 -*-", "from skidl import *", "", "@subcircuit", "def top():"]
    if nets:
        lines.append("    # Local nets")
        for net in nets:
            lines.append(f"    {net_vars[net.name]} = Net({net.name!r})")
        lines.append("")

    if components:
        lines.append("    # Components")
        for component in components:
            args = [repr(component.lib), repr(component.symbol)]
            if component.value:
                args.append(f"value={component.value!r}")
            if component.footprint:
                args.append(f"footprint={component.footprint!r}")
            args.append(f"ref={component.ref!r}")
            if component.fields:
                args.append(f"fields={component.fields!r}")
            lines.append(f"    {component_vars[component.ref]} = Part({', '.join(args)})")
        lines.append("")

    if nets:
        lines.append("    # Connections")
        for net in nets:
            pins = ", ".join(
                f"{component_vars[node.ref]}[{node.pin_key!r}]" for node in net.nodes
            )
            lines.append(f"    {net_vars[net.name]} += {pins}")
        lines.append("")

    lines.append("    return")
    lines.append("")
    return "\n".join(lines)


def enet_to_skidl(enet_src: Any, output_dir: str | None = None) -> str:
    """Convert a JLCEDA Pro ENET file or JSON string into a SKiDL program."""

    source = enet_document_to_skidl(parse_enet(enet_src))
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "top.py").write_text(source, encoding="utf-8")
        return ""
    return source

