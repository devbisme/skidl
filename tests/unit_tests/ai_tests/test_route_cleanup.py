from skidl.geometry import BBox, Point, Segment, Tx
from skidl.schematics import route as route_module


def setup_function():
    del route_module.pin_pts[:]


class DummyPart:
    def __init__(self, bbox):
        self.bbox = bbox
        self.tx = Tx()


class DummyPin:
    def __init__(self, part, pt):
        self.part = part
        self.pt = pt


class DummyNode:
    def __init__(self, parts, wires, net_pins):
        self.parts = parts
        self.wires = wires
        self._net_pins = net_pins

    def get_internal_pins(self, net):
        return list(self._net_pins[net])

    _segment_obstructed = route_module.Router._segment_obstructed
    route_straight_nets = route_module.Router.route_straight_nets


def _seg_coords(seg):
    pts = sorted(((seg.p1.x, seg.p1.y), (seg.p2.x, seg.p2.y)))
    return tuple(pts)


def test_cleanup_wires_straightens_aligned_two_pin_detour():
    net = object()
    left = DummyPart(BBox(Point(-1, -1), Point(1, 1)))
    right = DummyPart(BBox(Point(19, -1), Point(21, 1)))
    pin_a = DummyPin(left, Point(0, 0))
    pin_b = DummyPin(right, Point(20, 0))

    node = DummyNode(
        [left, right],
        {
            net: [
                Segment(Point(0, 0), Point(0, 10)),
                Segment(Point(0, 10), Point(20, 10)),
                Segment(Point(20, 10), Point(20, 0)),
            ]
        },
        {net: [pin_a, pin_b]},
    )

    route_module.cleanup_wires(node)

    assert len(node.wires[net]) == 1
    assert _seg_coords(node.wires[net][0]) == ((0, 0), (20, 0))


def test_cleanup_wires_keeps_detour_when_direct_path_hits_obstacle():
    net = object()
    left = DummyPart(BBox(Point(-1, -1), Point(1, 1)))
    right = DummyPart(BBox(Point(19, -1), Point(21, 1)))
    blocker = DummyPart(BBox(Point(8, -2), Point(12, 2)))
    pin_a = DummyPin(left, Point(0, 0))
    pin_b = DummyPin(right, Point(20, 0))

    node = DummyNode(
        [left, right, blocker],
        {
            net: [
                Segment(Point(0, 0), Point(0, 10)),
                Segment(Point(0, 10), Point(20, 10)),
                Segment(Point(20, 10), Point(20, 0)),
            ]
        },
        {net: [pin_a, pin_b]},
    )

    route_module.cleanup_wires(node)

    assert len(node.wires[net]) > 1


def test_route_straight_nets_prioritizes_aligned_direct_segment():
    net = object()
    left = DummyPart(BBox(Point(-1, -1), Point(1, 1)))
    right = DummyPart(BBox(Point(19, -1), Point(21, 1)))
    pin_a = DummyPin(left, Point(0, 0))
    pin_b = DummyPin(right, Point(20, 0))
    node = DummyNode([left, right], {net: []}, {net: [pin_a, pin_b]})

    routed = node.route_straight_nets([net])

    assert routed == [net]
    assert len(node.wires[net]) == 1
    assert _seg_coords(node.wires[net][0]) == ((0, 0), (20, 0))


def test_route_straight_nets_skips_blocked_direct_segment():
    net = object()
    left = DummyPart(BBox(Point(-1, -1), Point(1, 1)))
    right = DummyPart(BBox(Point(19, -1), Point(21, 1)))
    blocker = DummyPart(BBox(Point(8, -2), Point(12, 2)))
    pin_a = DummyPin(left, Point(0, 0))
    pin_b = DummyPin(right, Point(20, 0))
    node = DummyNode([left, right, blocker], {net: []}, {net: [pin_a, pin_b]})

    routed = node.route_straight_nets([net])

    assert routed == []
    assert node.wires[net] == []
