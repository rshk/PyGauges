PyGauges
########

Utilities for displaying real-time data with Python.

This is a SDL-based library (via `PyGame`_) providing various components
useful for building dashboards to display live data.

.. _PyGame: http://www.pygame.org/


Components
==========

Right now, the included components are:

* An "application" class that attempts to hide away all the low-level stuff,
  such as event loop and screen redrawing

* Some "displays", that can be added on the application dashboard to display
  some data. Right now we have:

  * A clock, displaying time in analog format

  * A (partially-written) "virtual horizon", for displaying roll/pitch.
    Partially implemented because the roll and pitch indicators should affect
    the same graph line, not be two separate needles, but right now I'm too
    tired to make the necessary calculations :)

  * A "lines" visualizer, for displaying line charts.

For the moment, the charts are tied to displaying some random data, but
of course they can be extended to read from other sources.

Some nicer way to associate displays with sensors / probes / sources is WIP,
as I don't want to risk adding too much complexity or being limited by some
wrong choice; probably the best solution would be to allow pluggable
"data sourcing" methods that use different mixins to leverage the capabilities
of each source. (For example, in certain cases we want PUSH vs PULL retrieval
method, keep historical data, get a bunch of data at once, ...)


Todo List
=========

* Add support for plugging actual "probes" to the displays, find most
  use cases and make sure we can satisfy all

* More base objects, for example the "with background" displays can be
  made into a "multilayer" display.

* Better mixins functionality. We risk to have conflicts by using
  mixins too much: we need a better way to provide "pluggable"
  functionality.

* Allow a better way to "theme" displays: user should be able
  to select a "base theme" per application / dashboard / display.

  Displays should be able to choose the right color to use
  from the specified palette.



License (BSD 3-Clause)
======================

Copyright (c) 2013, Samuele Santi
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the Author nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


.. image:: https://d2weczhvl823v0.cloudfront.net/rshk/pygauges/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

