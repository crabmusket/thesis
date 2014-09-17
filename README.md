# Thesis [![PDF Status](https://www.sharelatex.com/github/repos/eightyeight/thesis/builds/latest/badge.svg)](https://www.sharelatex.com/github/repos/eightyeight/thesis/builds/latest/output.pdf)

Model predictive control for solar hot water systems.

## Setup

Download [Vagrant][] and [VirtualBox][], then run `vagrant up` in this directory.
It will take some time (over an hour on my desktop).
I recommend using [vagrant-cachier][] to speed up any subsequent provisions.

[Vagrant]: http://vagrantup.com
[VirtualBox]: https://www.virtualbox.org/
[vagrant-cachier]: https://github.com/fgrehm/vagrant-cachier

## Software

I make use of [cvxpy][] and [python-control][] for the core of the control work.
These two libraries in turn rely upon [Slycot][] and [SciPy][], which is also used for simulation.
And, of course, [matplotlib][] handles the output.
[ShareLaTeX][] provides TeX [CI builds][].

[cvxpy]: https://github.com/cvxgrp/cvxpy
[python-control]: http://www.cds.caltech.edu/~murray/wiki/Control_Systems_Library_for_Python
[Slycot]: https://github.com/avventi/Slycot
[SciPy]: http://www.scipy.org/
[matplotlib]: http://matplotlib.org/
[ShareLaTeX]: https://www.sharelatex.com
[CI builds]: https://www.sharelatex.com/github/repos/eightyeight/thesis
