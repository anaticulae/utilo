.. _backlog:

backlog
=======

* validate selection of cli --commands. Print error if some selection can
  not result in valid process cause of some missing resource which is
  produced by own application but not selected via --cmd.

* extend utila.roundme to round multiple value at once

  .. code-block:: python

      a, b, c = utila.roundme(a,b,c)
