Title: SKiDL Has Schematics!
Status: draft
Author: Dave Vandenbout
Tags: schematics
Summary: You can finally generate schematics from your SKiDL code.


When I talked about [SKiDL at KiCon in 2019](), the most frequently-asked question I got  
afterwards was "Can it output schematics?" This was somewhat disappointing since the whole
point of SKiDL is to avoid schematics. But outputting schematics
might help with the adoption of SKiDL if people could see what their code is generating.

But I didn't want to write the code for this because I knew it was *hard!*
Hard not just in the sense that it would have to intelligently place part symbols and route
wires between them, but the result had to be aesthetically pleasing because people
are exceedingly picky about their schematics. So the entire effort might be a ton of work
with no positive results.

So I didn't even attempt this in 2019. Or 2020. Or 2021. Until somebody else did it for me!
[Shane Mattner](https://github.com/shanemmattner) wrote an initial version during the August-October time frame
before he started a new job. By then, his code was able to create hierarchical schematics like this:
![STM32 top-level schematic by Shane Mattner](../images/schematic-generation/mattner-stm32-top.png)
![STM32 microcontroller schematic by Shane Mattner](../images/schematic-generation/mattner-stm32-uc.png)
![STM32 power circuit schematic by Shane Mattner](../images/schematic-generation/mattner-stm32-pwr.png)

There were a number of limitations with Shane's code: 1) the first part was arbitrarily selected in each page, and then the rest of the parts were arranged around that, 2) only simple connections between parts could be routed, 3) multi-unit parts weren't handled, 4) etc... But these were incidental matters: his code could actually create KiCad-compatible schematics!

Having been given this gift, and since Shane was on to bigger things, I decided to push forward with it.
I figured a couple of months of refactoring and it would be ready for a general release.

I was very wrong.

My initial efforts went pretty smoothly:
1. I implemented some basic geometric primitives like transformation matrices, points, vectors, bounding boxes, etc. and began to rewrite pieces of the code with these.
2. I started to separate the KiCad-specific pieces of the code from the generic schematic-generation code.
3. I create a `Node` object that stores the schematic parts at a particular level of the hierarchy as well as child nodes for lower levels.
4. I added a `flatten` parameter to control how the hierarchy was expressed in the schematic, either as linked subsheets or as blocks of circuitry within the parent sheet.

This took me up to the end of 2021. It was a big help to have Shane's examples to test on so I could verify my code was producing the same results as his.

At the beginning of 2022, it became clear to me that a more robust routing solution was needed.
I divided this into several phases that were run on each node of the circuit hierarchy:
1. Generation of coarse routing cells between the schematic parts in each node.
2. Global routing of nets between part symbol pins through the coarse cells.
3. Assignment of global nets to fixed terminals on the periphery of each routing cell.
4. Detailed switchbox routing of nets between the terminals of each routing cell.
5. Concatenation of detailed switchbox routes for each net to create a complete end-to-end wire.

Near the end of May, I began to develop the code for placing schematic parts.
Once again, I divided the effort into several phases that proceeded from the bottom-most leaf node up to the node
at the top of the hierarchy:
1. Expansion of the bounding box of every part in a node to allow room for routing of wires after placement.
1. Grouping of the parts in each node into one or more sets of *explicitly-connected parts*,
   a single set of *floating parts* without explicit connections (e.g., bypass capacitors), and *part blocks*
   of either subsheets or flattened blocks of circuitry from lower-level nodes in the hierarchy.
2. Force-directed placement of connected parts under the influence of attractive forces from their interconnecting nets and
   repulsive forces due to part overlaps.
3. Force-directed placement of floating parts with attractive forces based on part similarity and repulsive forces due
   to part overlaps.
4. Force-directed placement of the blocks of connected and floating parts along with the subsheets of flattened blocks
   of lower-level nodes.

At the beginning of October, I integrated the placement and routing phases together and began fixing problems,
refactoring, and documenting various parts of the code. Also, finally, multi-unit parts were supported.
While I had hoped to finally release a new versiof SKiDL with schematic generation at the end of 2022, that deadline
passed without fanfare.

During January of 2023, in addition to the usual bug fixing and refactoring, I added a few new features to try to
improve the resulting schematics:
1. An initial *compression* was done at the start of placement that used only the attractive net forces to pull
   connected parts together as a starting point for the main placement routine when repulsive forces would kick in.
2. After placement was done, Kernighan-Lin optimization was added to make improvements in the part orientations
   (rotation, flipping horizontally/vertically) and then the force-directed placement would be re-run, hopefully giving
   an even better result.
3. If the router failed to completely wire the parts together, then the part bounding boxes would be expanded
   to increase the area for routing and another round of placement and routing would occur.

From February to mid-March, I worked on local optimizations to remove stubs, jogs and cycles from the generated schematic wiring.
I also added a "part jumper" to the placement code that would attempt to make local improvements be jumping parts over
one another to reduce wire crossings and lengths.
And, of course, more bug fixes, refactorings, and documentation were done.

In mid-March, I decided that more work on beautifying the wire routes was a dead end and that improving the part
placement would produce better schematics: you can't really route your way out of a bad placement.
Many changes to the placement algorithm were tried, modified, and most were rejected.
I kept the most promising avenues that were generating the best results and stripped out the rest to simplify the code.
Finally, at the end of June, I called "time" and decided this was the best I could do right now.
I fixed a few more bugs (which, of course, revealed some more bugs), merged it into the `master` branch, and
released it as version 1.2.0 of SKiDL.

It's more than what we had, but less than what I wanted in terms of the quality of the schematics that are generated.
I wish I'd released it sooner; perhaps having others use it would have helped focused the development.
But I'm sure the community (even as small as it is) will provide enough feedback to drive further improvements
(depending upon how much energy I and other volunteers have).



