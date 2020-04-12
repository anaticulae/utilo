.. _backlog:

backlog
=======

* validate selection of cli --commands. Print error if some selection can
  not result in valid process cause of some missing resource which is
  produced by own application but not selected via --cmd.

* file:copy_content: add flag to log but not execute copy operation

* support multiple pages flag: upme --pages=5 --pages=3 --pages=6 --pages=5

* add contextmanager and decorator:

  .. code-block:: python

    with utila.refactor(major=1, minor=17, patch=5):
        pass

    @utila.refactor(major=1, minor=17, patch=5)
    def method():
        pass

  fail when code was not replaced.

* add file_ext to determine file extention
