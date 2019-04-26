# Changelog

Every noteable change is logged here.

## v0.5.10

### Feature

* support commands which contains only a longcut (6cd496a8c5a6)

### Fix

* correct position of output-parameter if no input-parameter is given (3f4102c02a56)

## v0.5.9

### Feature

* add date and time in ~German~ format (5db940568ec4)

## v0.5.8

### Feature

* make length of tempname changeable (5e80c17ee991)
* allow mocking sys.stdout/stderr via pytest (a3acd755ac2a)

### Fix

* fix invocation when file exists and fix style (eba50a3d4057)

## v0.5.7

### Fix

* add missing import (09f6b4bffa6c)

## v0.5.6

### Feature

* provide content from interface or use direct raw content (01e0bfa19b60)

## v0.5.5

### Feature

* add constant INF (063aa907d004)

## v0.5.4

### Feature

* add parser for -i and -o to extract input and output (a1bcc4d1f7fe)

## v0.5.3

### Feature

* flag `create` to create folder when appending to not existing file (f3c4d2f2b591)

## v0.5.2

### Fix

* input is not mandatory, if not given, stdin is used (e999c42a43bc)

## v0.5.1

### Feature

* add default input-, output-, version-flag (49e9149050c1)

## v0.5.0

### Feature

* provide logging_stacktrace (e041c6a17431)

## v0.4.4

### Fix

* add NEWLINE to public API (580cefb39875)

## v0.4.3

### Feature

* add RequiredCommand as new commandline-type (a5660155c231)

### Fix

* check cwd of existence and correctness before running cmd (87f9cf977ef2)

## v0.4.2

### Fix

* make skip_not_virtual depends on environment var VIRTUAL (ef5555528272)

## v0.4.1

### Feature

* add methods to simplify testing (a3a202863dd7)

## v0.4.0

### Feature

* add simple command line parser (5e673e2e8577)

## v0.3.0

### Feature

* expose posix-errorcodes for success and failure (faac47f04464)

## v0.2.0

### Feature

* add url to package and sort attributes (380f1b1dc8bc)
* saveme-wrapper to ensure correct SystemReturnValue on startup (139c2bbe6b09)

## v0.1.0

### Feature

* generalize code from baw-package (0bd4b34556f2)

## v0.0.0 Initial release

