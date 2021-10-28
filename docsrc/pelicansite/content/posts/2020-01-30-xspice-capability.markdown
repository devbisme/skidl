title: xspice capability
date: 2020-01-30
author: Dave Vandenbout
slug: xspice-capability

[Somebody asked about using XSPICE components](https://github.com/devbisme/skidl/issues/76) in SPICE simulations with SKiDL.
That wasn't possible since [PySpice](https://pyspice.fabrice-salvaire.fr/) didn't really support these when I [built the interface](https://devbisme.github.io/skidl/docs/_site/blog/spice-simulation).
So I added XSPICE parts to the [SKiDL SPICE interface](https://github.com/devbisme/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb) and released it as [SKiDL 0.0.29](https://pypi.org/project/skidl/).
