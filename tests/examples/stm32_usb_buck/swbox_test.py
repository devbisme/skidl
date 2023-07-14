from random import randint

from skidl import *
from skidl.route import *

width = 20
height = 10

swbx_width = width * GRID
swbx_height = height * GRID

bottom_track = GlobalTrack(orientation=HORZ, coord=0, idx=1)
top_track = GlobalTrack(orientation=HORZ, coord=swbx_height, idx=2)
left_track = GlobalTrack(orientation=VERT, coord=0, idx=3)
right_track = GlobalTrack(orientation=VERT, coord=swbx_width, idx=4)

bottom_face = Face(None, bottom_track, left_track, right_track)
top_face = Face(None, top_track, left_track, right_track)
left_face = Face(None, left_track, bottom_track, top_track)
right_face = Face(None, right_track, bottom_track, top_track)

bottom_face.create_nonpin_terminals()
top_face.create_nonpin_terminals()
left_face.create_nonpin_terminals()
right_face.create_nonpin_terminals()


def clear_terminals():
    for terminal in top_face.terminals:
        terminal.net = None
    for terminal in bottom_face.terminals:
        terminal.net = None
    for terminal in left_face.terminals:
        terminal.net = None
    for terminal in right_face.terminals:
        terminal.net = None


def set_net_terminals(net, top=[], bottom=[], left=[], right=[]):
    for terminal in top:
        top_face.terminals[terminal].net = net
    for terminal in bottom:
        bottom_face.terminals[terminal].net = net
    for terminal in left:
        left_face.terminals[terminal].net = net
    for terminal in right:
        right_face.terminals[terminal].net = net
    print(
        f"set_net_terminals(Net('{net.name}'), top={list(top)}, bottom={list(bottom)}, left={list(left)}, right={list(right)})"
    )


def randints(num, rng):
    return list(set([randint(1, rng - 2) for _ in range(num)]))


for i in range(5):
    set_net_terminals(
        Net(f"N{i}"),
        top=randints(1, width),
        bottom=randints(1, width),
        left=randints(1, height),
        right=randints(1, height),
    )

# set_net_terminals(Net("N1"), top=[1], bottom=[6])
# set_net_terminals(Net("N2"), bottom=[8,10], left=[5])
# set_net_terminals(Net("N2"), top=[6], bottom=[2], right=[4])
# set_net_terminals(Net("N3"), top=[2,4,7], left=[3,7])

# set_net_terminals(Net('N0'), top=[5], bottom=[16], left=[7], right=[4])
# set_net_terminals(Net('N1'), top=[10], bottom=[17], left=[2], right=[2])
# set_net_terminals(Net('N2'), top=[13], bottom=[18], left=[1], right=[1])
# set_net_terminals(Net('N3'), top=[5], bottom=[8], left=[3], right=[3])
# set_net_terminals(Net('N4'), top=[5], bottom=[2], left=[7], right=[2])

# set_net_terminals(Net('N0'), top=[1], bottom=[13], left=[1], right=[7])
# set_net_terminals(Net('N2'), top=[1], bottom=[2], left=[3], right=[2])
# set_net_terminals(Net('N3'), top=[18], bottom=[9], left=[8], right=[4])
# set_net_terminals(Net('N4'), top=[9], bottom=[16], left=[5], right=[5])

# Has an unroutable terminal on the right side.
# set_net_terminals(Net('N0'), top=[10], bottom=[18], left=[8], right=[3])
# set_net_terminals(Net('N1'), top=[1], bottom=[2], left=[6], right=[4])
# set_net_terminals(Net('N2'), top=[4], bottom=[17], left=[8], right=[1])
# set_net_terminals(Net('N3'), top=[5], bottom=[15], left=[7], right=[5])
# set_net_terminals(Net('N4'), top=[7], bottom=[9], left=[8], right=[4])

# Unroutable.
# set_net_terminals(Net('N0'), top=[12], bottom=[9], left=[6], right=[4])
# set_net_terminals(Net('N1'), top=[13], bottom=[15], left=[2], right=[5])
# set_net_terminals(Net('N2'), top=[16], bottom=[15], left=[7], right=[2])
# set_net_terminals(Net('N3'), top=[10], bottom=[4], left=[4], right=[6])
# set_net_terminals(Net('N4'), top=[10], bottom=[2], left=[1], right=[3])

# set_net_terminals(Net('N0'), top=[12, 15], bottom=[], left=[], right=[7])

# set_net_terminals(Net('N0'), top=[0, 1, 15], bottom=[20], left=[4], right=[7])

single_run = True

if single_run:
    swbx = SwitchBox(top_face)
    try:
        swbx.route(flags=[])
    except RoutingFailure:
        print("Routing failure! Flipping routing direction.")
        swbx.flip_xy()
        try:
            swbx.route(flags=[])
        except RoutingFailure:
            print("Total routing failure!")
        swbx.flip_xy()
    swbx.draw()

else:
    attempts = 0
    failures = 0

    for _ in range(20):
        attempts += 1
        clear_terminals()
        for i in range(8):
            set_net_terminals(
                Net(f"N{i}"),
                top=randints(1, width),
                bottom=randints(1, width),
                left=randints(1, height),
                right=randints(1, height),
            )
        swbx = SwitchBox(top_face)
        try:
            swbx.route(flags=[])
        except RoutingFailure:
            print("Routing failure! Flipping routing direction.")
            swbx.flip_xy()
            try:
                swbx.route(flags=[])
            except RoutingFailure:
                failures += 1
            swbx.flip_xy()
        # swbx.draw()
    print(f"Routing attempts = {attempts}; failures = {failures}")
