bugs
====

open
----

* adding feature with name `pages` conflicting with --pages flag and
  produces an error:

  .. code-block:: none

    ---------------------------- Captured stderr call -----------------------------
    [ERROR] 'bool' object has no attribute 'strip'
    [ERROR] Traceback (most recent call last):
      File "C:/usr/python/372/lib/site-packages/utila/error.py", line 57, in wrapper
        ret = user_function(*args, **kwds)
      File "C:/usr/python/372/lib/site-packages/utila/feature.py", line 128, in featurepack
        processes, failfast, pages, profiling = evaluate_flags(args, multiprocessed)
      File "C:/usr/python/372/lib/site-packages/utila/cli.py", line 426, in evaluate_flags
        pages = parse_pages(args.get(PAGES_FLAG, ALL_PAGES))
      File "C:/usr/python/372/lib/site-packages/utila/pages.py", line 60, in parse_pages
        pattern = pattern.strip()
    AttributeError: 'bool' object has no attribute 'strip'

closed
------
