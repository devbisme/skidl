---
layout: post
title: xspice capability
date: 2020-01-30T09:01:10-05:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/xspice-capability
---

[Somebody asked about using XSPICE components](https://github.com/xesscorp/skidl/issues/76) in SPICE simulations with SKiDL.
That wasn't possible since [PySpice](https://pyspice.fabrice-salvaire.fr/) didn't really support these when I [built the interface](https://xesscorp.github.io/skidl/docs/_site/blog/spice-simulation).
So I added XSPICE parts to the [SKiDL SPICE interface](https://github.com/xesscorp/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb) and released it as [SKiDL 0.0.29](https://pypi.org/project/skidl/).
