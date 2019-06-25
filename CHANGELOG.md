# Changelog

Every noteable change is logged here.

## v0.7.6

### Fix

* ignore existing files, overwrite them (56ab5f521f4c)

## v0.7.5

### Feature

* add recursive inputs to use resource which are generated later (4b9401c8848a)
* add different logging level by -vvv (36accbc2bb83)
* extend logging API with different logging level (c72ed1f66d82)

### Fix

* remove dependencies to BoundingBox (bcf09f8b4a3a)

## v0.7.4

### Fix

* fix single file input as source (176fcb18c7c9)

## v0.7.3

### Feature

* add default value for running without all parameter (af5559936abf)

## v0.7.2

### Fix

* do not allow defining conflicting cmdline interface (f454f69d49a2)

## v0.7.1

### Feature

* add new feature creator (36947b30d85d)

## v0.7.0

### Feature

* replace old feature collector with new one (656111c01737)
* support single/multiple file input (4bb2a19beef2)
* parse passed --flags as todo (649fc652bf83)

### Fix

* fix feature definition to pass the tests (54bae89f8791)

## v0.6.5

### Feature

* add singleinput flag to allow files as direct input (6c8134747e6c)
* add method to uniform the result of a likelihood computation (841077cc845a)
* add clean_install method to test setup.py of project (bd9c05646776)

## v0.6.4

### Feature

* add recursive flag to copy_content (60b2d932e6c5)
* replace existing files instead of throwing an error (616c49f4eddc)
* add prefix to feature output (21e6eb9e61c9)
* extend public API with UTF8 (d2a36111a38f)
* add error output for missing workplan (418d18cead40)

### Fix

* remove create_parser from public API, use featurepack (46494046f45c)
* rename cmdline test to easier invoke cmdline tests (1082b399e955)

### Documentation

* add hint that `create_parser` should not be part of public API (d41233052d83)

## v0.6.3

### Feature

* support multiple parameter of feature cmdline tool (8da62bc9aa35)
* support features without name or commandline method (edb45cc417b9)
* add assert_file, assert_html to public API (4da5a4dacd8b)
* extend public API with classificatory (2bb00196c3bd)
* add `returncode()` to public API (64258eba882e)

### Fix

* replace feature_path with root - interface change (41110f4cf563)

## v0.6.2

### Feature

* support single file input as input for cmdline interface (e87cf5616d33)
* add hint to asserted type when loading from wrong datatype (4c366d24f325)
* add hint which file already exists (786a04be40ad)
* add featurepack to public API (44741219646c)

## v0.6.1

### Feature

* support @saveme decorator without braces (84fd67f6c181)
* extend public API with error code CANCELLED_BY_USER (b3a47c6074db)
* add option to use return value of saveme - or exit instantly (9d24731fce7a)
* add test pattern to un/install and run package to verify setup process (eb5affdfcbcb)

### Fix

* add missing invocation of decorator() (0a501ca18574)
* add separate test for testing without SHARED_TEMP environment var (02303cab6002)
* use direct import instead of public API (d947abf49933)
* avoid conversion problem when logging to windows console (44d54407594b)

## v0.6.0

### Feature

* add method to copy the content of a folder (35523e200ea1)
* add verbose flag to default parser - supports verbose level (375355821592)
* redirect creating temp file to separated folder. (9c822581a709)

### Fix

* exit codes higher than one fail too (a17fa580f69c)

## v0.5.15

### Feature

* support run without passing cwd, use current cwd instead (d60bcc41fb4f)

### Fix

* add skip_nonvirtual to public api (59b63ec8d2a8)

## v0.5.14

### Feature

* add method to run tests with pytester (ccb63ff5009b)
* use skip_nonvirtual instead of skip_not_virtual (ffc6cc185537)

### Fix

* use callable to test if variable is callable (26937211d5ec)

### Documentation

* extend sphinx global documentation (0da5b2442f64)

## v0.5.13

### Feature

* use only directory's as in and output - support simpler --flags (61783fb976de)
* add new tests and refactor old one (0010987a11c9)

### Fix

* remove unused code (4aee57aced0b)
* use new Parameter instead of Command (0ea45f9d0158)

## v0.5.12

### Fix

* flush immediately when printing error to avoid confusion (921e80410dd9)

## v0.5.11

### Feature

* add option to add short- and long-description to cmdline (768604d499d8)
* add Flag and Parameter to differentiate between different cmdline types (cf0389c84b6e)

### Fix

* initialize object correctly due adding dataclass decorator (92e8e3b73ae5)
* do not throw exception, when output or input is not defined (99a41d083fea)

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
