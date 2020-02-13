.. _backlog:

backlog
=======

* validate selection of cli --commands. Print error if some selection can
  not result in valid process cause of some missing resource which is
  produced by own application but not selected via --cmd.

* add method to automate open html file with webbrowser avoid writing code.

 .. code-block:: python

     def open_webbrowser()
        if utila.single_execution():
            webbrowser.open(outpath)
