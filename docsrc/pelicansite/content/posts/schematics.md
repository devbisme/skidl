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


# SKiDL Now Supports Schematic Generation (from ChatGPT)

Status: Draft
Author: Dave Vandenbout
Tags: Schematics
Summary: You can now generate schematics from your SKiDL code, allowing you to visualize the circuitry.

When I presented SKiDL at KiCon in 2019, I frequently received a question afterward: "Can it output schematics?" Initially, this question disappointed me because SKiDL was designed to eliminate the need for schematics. However, I realized that providing schematics could aid in the adoption of SKiDL by allowing users to visualize their code-generated circuits.

At first, I hesitated to tackle this task as I knew it would be challenging. It required intelligent placement of part symbols and proper routing of wires, all while ensuring the resulting schematics were aesthetically pleasing. The amount of work involved with no guarantee of positive results made me postpone the implementation in 2019, 2020, and 2021. However, someone else came to the rescue! Shane Mattner, before starting a new job, developed an initial version of schematic generation between August and October. His code was capable of creating hierarchical schematics, as demonstrated by the examples below:

- STM32 top-level schematic by Shane Mattner
- STM32 microcontroller schematic by Shane Mattner
- STM32 power circuit schematic by Shane Mattner

Although Shane's code had some limitations, such as arbitrary part selection and limited routing capabilities, it was able to generate KiCad-compatible schematics. Given this gift and Shane's departure to pursue other endeavors, I decided to take the project forward. I estimated a couple of months of refactoring would be sufficient to prepare it for a general release. However, I soon discovered that I had underestimated the complexity of the task.

Initially, I focused on implementing basic geometric primitives like transformation matrices, points, vectors, and bounding boxes. This allowed me to rewrite sections of the code using these new constructs. I also began separating the KiCad-specific code from the generic schematic-generation code. To manage the hierarchy of the schematics, I introduced a `Node` object that stored schematic parts at different levels and their corresponding child nodes. Additionally, I added a `flatten` parameter to control how the hierarchy was expressed in the schematic, either as linked subsheets or as blocks of circuitry within the parent sheet.

By the end of 2021, I had reached a significant milestone. Shane's examples served as valuable test cases, enabling me to verify that my code produced the same results. However, as 2022 began, I realized that a more robust routing solution was necessary. I divided the routing process into several phases, each executed on every node of the circuit hierarchy:

1. Generation of coarse routing cells between schematic parts within each node.
2. Global routing of nets between part symbol pins through the coarse cells.
3. Assignment of global nets to fixed terminals on the periphery of each routing cell.
4. Detailed switchbox routing of nets between the terminals of each routing cell.
5. Concatenation of detailed switchbox routes for each net to create a complete end-to-end wire.

In late May, I shifted my focus to developing the code for placing schematic parts. This effort was also divided into several phases, progressing from the leaf nodes to the top node of the hierarchy:

1. Expanding the bounding box of each part in a node to accommodate wire routing after placement.
2. Grouping parts within each node into sets of explicitly-connected parts, floating parts without explicit connections (e.g., bypass capacitors), and part blocks consisting of subsheets or flattened blocks from lower-level nodes.
3. Force-directed placement of connected parts, considering attractive forces from interconnecting nets and repulsive forces due to part overlaps.
4. Force-directed placement of floating parts, considering attractive forces based on part similarity and repulsive forces due to part overlaps.
5. Force-directed placement of blocks of connected and floating parts, along with subsheets of flattened blocks from lower-level nodes.

By early October, I integrated the placement and routing phases and began addressing issues, refactoring code, and documenting various aspects. Finally, multi-unit parts were supported. Although I had hoped to release a new version of SKiDL with schematic generation by the end of 2022, that deadline passed without any fanfare.

Throughout January 2023, in addition to bug fixing and refactoring, I introduced a few new features to enhance the resulting schematics:

1. An initial compression step was implemented during placement, leveraging attractive net forces to bring connected parts closer together as a starting point for the main placement routine.
2. Kernighan-Lin optimization was added after placement to improve part orientations (rotation, horizontal/vertical flipping), followed by another round of force-directed placement for further refinement.
3. If the router failed to complete the wiring of parts, the part bounding boxes were expanded toincrease the routing area, and another round of placement and routing would be performed.

From February to mid-March, I focused on local optimizations to eliminate stubs, jogs, and cycles from the generated schematic wiring. I also introduced a "part jumper" feature to the placement code, which attempted to improve the layout by jumping parts over each other, reducing wire crossings and lengths. Of course, I continued to address bugs, refactor the code, and improve documentation during this period.

In mid-March, I came to the realization that further efforts to beautify the wire routes were leading to diminishing returns. Instead, I decided to concentrate on improving the part placement, as a well-placed circuit is crucial for optimal routing. I explored various changes to the placement algorithm, but most of them were ultimately rejected. I retained the most promising approaches that yielded the best results and simplified the code by removing unnecessary complexity. Finally, at the end of June, I decided to call it a day and deemed this the best version I could deliver for now. I fixed a few remaining bugs (which, unsurprisingly, uncovered a few more), merged the changes into the `master` branch, and released it as version 1.2.0 of SKiDL.

Although the generated schematics are not perfect and fall short of my initial expectations in terms of quality, they are still a significant improvement over the previous state. I wish I had released it sooner, as user feedback could have helped guide the development process. However, I am confident that even the small SKiDL community will provide valuable feedback, which will drive further improvements—depending, of course, on the energy and dedication of myself and other volunteers.

The journey of adding schematic generation to SKiDL has been challenging, but it has also been a rewarding experience. I am grateful for Shane Mattner's initial contribution, as well as the support and encouragement from the SKiDL community. With each iteration, SKiDL continues to evolve and become a more powerful tool for circuit design and simulation. I look forward to the future and the possibilities it holds for SKiDL's growth and development.

