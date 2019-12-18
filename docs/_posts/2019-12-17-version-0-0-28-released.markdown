---
layout: post
title: Version 0.0.28 Released!
date: 2019-12-17T07:57:17-05:00
author:
    name: Dave Vandenbout
    photo: devb-pic.jpg
    email: devb@xess.com
    description: Relax, I do this stuff for a living.
category: blog
permalink: blog/Release_0_0_28
---

Well, that didn't last long.

I released version 0.0.27 of SKiDL yesterday, but I didn't like
having the `zyc` utility bundled in there because that pulls in `wxpython`
as a requirement.
That's likely to cause problems for some people when they try to install
it with `pip`.

So I made `zyc` a [separate utility you can install](https://pypi.org/project/zyc/), and removed it from
the newly-released 0.0.28 version of SKiDL.

This is the last SKiDL release for this year.
I mean it this time.
Really.
