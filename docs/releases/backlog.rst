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

* file:copy_content add flag to log copy operation

* file:copy_content add flag to log but not execute copy operation

* test:increased_filecount: change ending to ext

* test:increased_filecount: introduce optional file_number_diff_count
