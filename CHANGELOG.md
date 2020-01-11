# changelog

Every noteable change is logged here.

## v1.11.4

### Feature

* support dir-path as file-input (6c50c9bd160f)
* improve variable presentation (526714c82d5c)
* add quite flag to suppress logging (cd82339945e0)
* extend public API (58c35e1ac7e9)

### Fix

* correct input/output resource definition (c36f84594f35)

### Documentation

* extend interface documentation (d513b5953d7d)
* extend interface documentation (fa416be74f80)
* extend interface documentation (4cd76f92ea77)

## v1.11.3

### Documentation

* Happy New Year! (76dbc29a1173)

## v1.11.2

## v1.11.1

### Feature

* support multiple output parameter (b4aba2476ffd)

### Documentation

* fix interface documentation (bed5a55ffeb8)

## v1.11.0

### Feature

* disable prefix flag as default (18d5937e67f1)
* disable verbose flag as default (22fc646ca992)
* disable --ff as default (10295e6d93ae)
* sort parameter alphabetically (bd17c54230dc)
* extend public API (a631bcb7cda6)
* add parameter to make parser creation more configuration able (a2fefc90f537)
* add return code to `run_command` (ed2566c1e65f)
* extend interface documentation (878c40743938)
* extend should_skip to support check of multiple pages in one (604ef943e940)
* add check to avoid changing with chdir to path location (be9bdb28e272)

### Fix

* remove malformed long cut (5e65bdc1da15)
* fix spelling error (67523fbe8b67)

### Documentation

* extend interface documentation (800c61cb8e52)
* extend interface documentation (3b1a215391c1)
* improve interface documentation (463c2e4de682)
* extend interface documentation (eee4e5f6e2ec)
* fix interface documentation (ad6f001edc7e)

## v1.10.0

### Feature

* print path which is not able to change to (3d813b94f4e3)
* add `pattern` to filter copy content (bfa67620cc78)
* add method to check if path is file to public API (1e383c91f600)
* extend roundme to define amount of numbers after dot (69b669ffae9d)
* add method to filter collection by data type (70344f8a1850)
* give likelihood computation a new order (6fe393065709)

### Fix

* enable multi processing tests (4c7eec0faefc)

### Documentation

* extend documentation of likelihood test (1fba1f0cdd6b)
* improve docs for using in Sphinx documentation (07d996a48b40)
* add anchor point for planning upcoming releases (fbb266806f2c)

## v1.9.2

### Fix

* fix determining correct step dependencies (c77b41d09f11)

## v1.9.1

### Fix

* fix passing correct process name (c473e6565b67)

## v1.9.0

### Feature

* add make_package to convert file path to python package path (5f9848afbdff)
* add option to avoid converting \n in forward_slash (af6e2dbe8257)
* add method log_raw to print assertion error (9a2dee821fed)
* add context manager to change current working directory (ce27a0638256)
* return default value if page does not exists (c08b89fbff2b)

### Fix

* support multi-core environment (cc45221cc9f4)
* fail if given data is not path (acdc9921ed3f)
* log correct process step name (501c08686354)

### Documentation

* extend release plan 1.9.0 (36999a3e6445)
* add release plan 1.9.0 (9f65a09fec71)

## v1.8.1

### Feature

* add method to read binary files (b84f34a9fd26)

### Fix

* support comparing non utf8 files (4d1e46167999)

## v1.8.0

### Feature

* add method to log input of function calls (8e6505ba3511)
* add method to lock, unlock and check lock protection. (51d8e9fe6bdd)
* add parameter skip_overwrite (4621a907c8c5)
* add method to compare content of two files (9e1d266d6d41)

### Documentation

* add first draft of RP 1.8.0 (4a03469e3595)

## v1.7.0

### Feature

* add method to extract str out of re.Match (e0d3a6c05588)
* add method to check that process completed correctly/with failure (823a37125dc2)
* add method to format result of `CompletedProcess` (13e1724c1e7c)
* add option to shorten name of make_single (117a3d7ccef3)
* include replacing dot of filename in make_single (1eac24567cd0)
* add method to ensure that filename ends with yaml extension (dd41fc515a08)

### Documentation

* add todo for later breaking interface change (81c58ec4d6c1)

## v1.6.0

### Feature

* add method to print environment variables (d535d16494f7)
* add method to select special page out of pages collection (51a6dba0eae6)
* add method to stable remove duplicated items from collection (990abdc188ac)
* add method to create absolute path to public API (7374f26491e8)
* add method to cut common leading sequence of two paths (5395cbd7f935)
* add method to convert path into single fileable peace of str (b7040b70ab7a)

## v1.5.3

### Fix

* fix tuple flag parameter definition (1b9fba339626)

### Documentation

* extend interface documentation (0a888a691efa)

## v1.5.2

### Feature

* add method to check if user flag is set (d1fabd9259c4)

### Fix

* fix todo collector approach (119f563e7a97)

## v1.5.1

### Feature

* replace linter with general flag approach (4f2d77eebc87)

## v1.5.0

### Feature

* add parameter to write linter result (551bba646901)

## v1.4.0

### Feature

* add check to create_step correctly (ecf7bbe84a32)
* add error hook to catch failures while processing (08b52639059c)

### Fix

* extend pages pattern to support `50:` (5427f6d52676)

## v1.3.0

### Feature

* add optional `msg` to differentiate runtime logs (9f38e94b3eda)

## v1.2.8

### Feature

* add NIGHTLY and @skip_nightly to control test execution (4fdfdcc72d6a)

## v1.2.7

## v1.2.6

### Feature

* add @skip_virtual flag to skip test running in virtual env (f85f81f092b9)
* add FASTRUN and LONGRUN to public API (3c6c9e05b92f)
* add positional accessible ctor to ResultFile (7a5c5ea05bf0)

## v1.2.5

### Feature

* support single value page selection to should skip function (ad004b0681e5)

## v1.2.4

### Fix

* fix forward slash to not replace '\n' newlines (5a71ebd215c3)
* change pages return type to tuple (a075bb757e92)

## v1.2.3

### Feature

* add method to test if page should be processed (9d0ffec74caa)
* add context manager SkipCollector to skip page calculation (f513b7429d74)

## v1.2.2

### Fix

* add comma ',' to increase readability (9f5cfb5ee898)

## v1.2.1

### Feature

* add option to change end-line when logging (2dcc0c76232f)

## v1.2.0

### Feature

* add --pages flag to specify processed pages (4aa00ee404b0)
* add method to parse user defined page ranges `5:10`; 1,2,3 (b2169db1ebdc)

## v1.1.5

### Fix

* rename multiple job flag according to GNU reference (75f68fe412c8)

## v1.1.4

### Feature

* add parameter to `run` to manipulate the environment variable (296a6c76fbdf)
* return SystemExit when running wrong featurepack configuration (fee9ee46508f)
* add --ff to stop execution after the first error (27f441c12594)
* catch error on failed file access while copy items (4ab936eb16b0)

### Fix

* fix pickle problem in multithreading (71d95fa1026e)

## v1.1.3

## v1.1.2

### Fix

* fix avoid double data input (cb91baef8ee4)
* write all level step results before processing next level (a1314c338dfc)

## v1.1.1

### Fix

* fix multiprocessing problem (e3f02c847b93)
* print step name when work starts (8188da525fc4)
* fix passing process count (6c142069291f)
* support single file as requirement (ac214bd511fc)

## v1.1.0

### Feature

* add multiprocessing support (02761224b0d6)

## v1.0.0

### Feature

* add method to determine order of processes (577cdef0637c)
* remove old logging/error interface (11c325255298)
* add parallelized process interface (cea91b42a829)
* add multiple input sources (7673f17d1b65)
* add method to make path absolute (7a5a216330e3)

### Documentation

* extend public interface documentation of read_workplan (2314382d8fae)

## v0.9.1

### Feature

* extend `copy_content` to support copy files and folder (f03814865111)

### Fix

* add __init__ to access directories as packages (b67664979cc4)

## v0.9.0

### Feature

* add @skip_longrun to support baw --test=longrun (b6457070edf1)
* declare --prefix parameter optional (cc623f211ff5)
* print name of executable before log actions (466490e396b6)

### Fix

* swap printing error message (4f281f9bf828)

### Documentation

* extend interface documentation of `run` (daa884e6baf2)

## v0.8.0

### Feature

* support external variables in description preview (ceb4514bc56a)
* add --all flag to run every feature step (eb9f5b17683c)
* continue on error and terminate with error at the end (169792d1d029)
* use current working directory as default in/output path (5dbcc62a4244)
* add format ability to parser description (fc644b8ffb52)
* print inputs/outputs of working plan via --help (f1805d8af1c1)

### Documentation

* extend interface documentation and fix some spelling errors (d0549124cad5)

## v0.7.8

### Feature

* add method to round and to chain a list of lists (0d2cfedc1d29)
* add print broken parameter name to ease debugging (f6b73f144515)

## v0.7.7

### Feature

* support @checkdatatype with feature worker (9aed44b45154)
* add type checker to verify that input match with defined datatype (91453883c1a7)
* add method to compute common likelihood on base 1 (b093d7e51239)
* print given args on values error to ease verifying error (1fb8b01a2b80)

### Fix

* fix logging output (e67d3235e82a)

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
