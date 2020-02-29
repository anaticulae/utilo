.. _backlog:

backlog
=======

* validate selection of cli --commands. Print error if some selection can
  not result in valid process cause of some missing resource which is
  produced by own application but not selected via --cmd.

* file:copy_content: add flag to log but not execute copy operation

* utila.copy_content(source, root, pattern='rawmaker__*.yaml')
  utila.copy_content(source, root, pattern='groupme__*.yaml')
  unit to one pattern.
