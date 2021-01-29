# changelog

Every noteable change is logged here.

## v2.19.0

### Feature

* add optional cli plus hook (b54541b212fe)
* add option to skip writing result (982b61fdf8df)
* update value in tuple (7940726b8c26)
* add method to determine width and height of rectangle (70d24aac35db)
* add method to parse numbers (67e8803d3243)
* add wait option to wait till resources are ready (dc5bc4ab676a)
* add method to group content lists together (fd9a51ecfb47)

### Fix

* group zero or '' correctly (ad79c95307b3)

### Documentation

* extend interface documentation (aed53f97b034)

## v2.18.1

### Feature

* add live flag to directly log to stdout/err (f81df6225b2f)

## v2.18.0

### Feature

* add method to decorate and verify decoration (4dc2892efb30)
* add method to manipulate rectangle (bb2152360c5f)
* add GeorgFork context manager to run methods in parallel (caa73286da41)

## v2.17.0

### Feature

* add function to evaluate exp between two points (6b3e7f95a0bd)
* add default value to log newlines (4545b6370dc1)
* add set support for similar check (fe487a4723cc)
* add method to split string into set of string (3c60aa2835fb)
* add method to lowercase list of strings (52b3744449ed)
* add method to determine max value index in collection (3edf628a1d16)
* add method to convert str to float (07d9a23d5321)
* add method to verify data type (ba2110be4538)
* add method to verify float type (643563db665f)
* add default value to str2int (31cecdfc83bf)
* add flag to always return returncode (cf3c60e31064)
* extend reserved workplan steps (c251e8ac4dad)
* add default step size (88f86ada7cec)

### Fix

* do not change datatype for single item (a9b580619df8)
* replace with python range syntax (7b14a1f8f9b2)
* make file_count thread safe (1438100ec3d2)
* make file list thread safe (b470d2f86825)

### Documentation

* Happy New Year! (ce7522704e15)
* add fork documentation (673ba60dc5a2)
* fix return type (1c77ce0ccce5)

## v2.16.1

### Fix

* avoid side effects to other work plans (643d4c0dbe46)

## v2.16.0

### Feature

* add method to select none empty items (e4b5fa36c2bc)
* add option to not raise error if item in flatten is already flat (194e7269f3e1)
* add German umlaut to sorting (5b0ac1f97645)
* enable pages and multi flag (d36942ba0636)

## v2.15.0

### Feature

* do not allow reserved work step names (1d4e1ef5a64a)
* enable using result of fork (e8c57c612c2d)

### Fix

* handle None description correctly (e53663065a17)
* change default feature step message (93e60c3f990a)
* ensure that prefix work schedule is executed correctly (169fc57531b6)
* ease data type check (91856cb43b6c)
* pass missing sortable parameter (37fdc0d65aaa)

## v2.14.0

### Feature

* add parameter to generate sortable dates (83fd562b4764)
* add now to determine current unix time (6d9df643aa5c)
* add method to list directories (a50146b9f512)
* add method to simplify data structure (34e85c3a61a6)
* introduce method interface to determine secure hash's (ae1cefc867e0)
* add ranged_list method (cd7cde195a0a)
* add flag how handle file copy conflict (01692a5ea448)
* add method to check equal length (5b79c2444a92)
* add classifier to merge rectangle (bd0da1b643cd)
* add method to check if two rectangle intersect each other (101b46978f3b)
* add option to add --cache flag (12d9f197248e)
* add first draft to use cache in feature pack (fcf43997250a)
* add feature result cache (faed13311e70)
* add method to determine hash of file/directory (607a86920027)
* add digits parameter to round line (b189834a4919)

### Fix

* improve assert check (5123b9eaa92f)
* improve cache selector (a05d0c3d6743)

### Documentation

* extend interface documentation (5885f3b0f7f6)
* sort doc by importance (2b1044518d71)

## v2.13.0

### Feature

* add files without extension to file_list (011aace27d3b)
* extend ascending test to support floats (76e0d5675007)
* improve three side equal cluster (2c6f0923ced2)
* add method to merge lines to single line(s) (d72957b3b588)
* add global before and after hooks (dae70f371a31)
* add before, after and error hook to feature processor (518160051455)
* add ProcessStep data type to represent created runtime (74167dc76adb)
* add zip optimizer (2e32f1909d18)
* add wrapper for os.path.exists to reduce amount of code (a7558070acb6)
* add ANY strategy (1fda6f628b98)
* add method to check intersecting ending of two lines (b76acb0bdd7c)

### Fix

* sort shortcut before longcut (d7c317e22bfb)

### Documentation

* extend interface documentation (f5cf03e93d43)

## v2.12.0

### Feature

* make sorting before grouping optional (5c5dff22f70f)
* extend public API (02a0170707fa)
* decrease required log level (a6cfdd82534c)
* add profile step to profile complete step (5827bb887e1f)

### Documentation

* extend interface documentation (1d86040a4cf8)

## v2.11.0

### Feature

* add key field to sort content of cluster before returning (883aa9320f88)
* add methods to sort rectangles/boundings (f22dd9774f42)
* add matcher field to cluster more complex data types (637879d1ff43)
* add None to simplify_pages (c3dca78e5963)
* extend public API (dddf76731281)
* add ParameterAppended (c6eca5b6e73a)
* add FlagCounted to express -DD-Flags easier (55708318523a)

### Documentation

* extend interface documentation (8b581a84720b)

## v2.10.0

### Feature

* add method to compare two vectors (6db33674f4f4)
* add method to simplify pages representation (f986e12f7526)

## v2.9.0

### Feature

* add method to create maximum bounding (2aa202f964cd)
* add checker to check if a rectangle is inside (61b27db33130)
* add method to use default value if value is None (30f48f977343)

### Fix

* fix group empty data (626e70c585d6)

## v2.8.0

### Feature

* add contextmanager to temporary disable environment variables (0031c862f9ae)

## v2.7.0

### Feature

* add method to compute length of vector (ce5d97fb192a)
* add method to remove none elements (14c83a9062c1)
* add option to change max diff of zero checker (7e5235ba8e72)

### Fix

* reduce verbosity of logging (a689274031e9)

### Documentation

* add hint how to use common cluster (259a99fd29d9)
* extend interface documentation (c92ea6048474)

## v2.6.0

### Feature

* add strategy argument to select matching strategy (9b7a8e718c7c)
* add method to parallelize methods calls (b6820ba1cacd)
* add pnear to compute percentage diff between two numbers (4e9d7aed8a35)
* add support for non decimal page numbers (aac3f722c984)
* add flag to always accept item in near_dims (7eb6c9a431c8)
* add method to detect if two elements are similar (f8f82a4eb7ce)

## v2.5.0

### Feature

* add algorithm to determine near for multiple dimension (02c8de13696c)
* add method to determine border between 2 neighbors (4c205e6af8d9)
* add strict parameter to ascending checker (cc01c914de45)
* add method chunks to separate container into smaller parts (ed931c0f52af)
* raises AssertionError when using duplicate pages (d1f14aa4a545)

### Fix

* fix number type checker (b2e6413b10d9)
* add workaround to solve FILEHASHS and ??? ext bug (bc47a5662f4d)

## v2.4.0

### Feature

* add {FILEHASHS} to express multiple result value like *-pattern (4022c20eb93e)
* increase verbose cli log readability (46441034e50d)
* let cli fail when step produces invalid data type result (cfeb53bdffb4)

### Fix

* handle variable return type correctly (03d2f0a5fe64)
* ensure correct max length for container with string content (dc755c0f40d3)

## v2.3.0

### Feature

* add support for multiple directory groups (b6b892be5918)
* shrink output error of failing cli processes (2c7dd8612253)
* add method to shrink string to maximum length (ec82c7d4e5c8)

### Fix

* fix logging of wrong pattern (3f378090d4ae)
* hash non bytes, non str data correctly (3df10219f130)

## v2.2.0

### Feature

* add {FILEHASH} to make file name dependent on file content (772e838fe003)
* add freehash to simplify hashing non secure data (bae9d80f267e)
* add method to choose random items (2a56320e917c)
* add partition method to divide iterator (1b2d8bbf22cf)
* add ranges method with float steps (a960ca6e617a)
* add method to select page content directly (1b97938b4fd4)

### Fix

* fix directory pattern (9ed0721a6fd6)

## v2.1.1

### Fix

* fix todo decorator (ee6899fc6ced)
* move required todo to a later release (2027faf605b9)

## v2.1.0

### Feature

* add same line cluster (929c4d85be53)
* replace with hey cluster code (ef3c4c9445d4)
* add bucket collector (331c59164739)

### Documentation

* exclude test module from central documentation (3ce6e09cfe9c)

## v2.0.0

### Feature

* remove test code (213cd7540164)

## v1.26.0

### Feature

* add longest, shortest and group by diff selector (a6342c47258a)

### Documentation

* improve text style (78694fff05af)

## v1.25.1

### Fix

* fix optional flag check (b1707f1fb994)

## v1.25.0

### Feature

* add optional flag to introduce optional resources (89a5b96a9c9d)
* add method to separate groups of ascending items (2aa5a36a5bbe)
* add method to group list by none hole (3cf3dbb51e7f)
* add optional separator to join tuple to string (8cb30bc75218)
* print skipping feature step in verbose mode only (b4e3f7ee866b)
* add default --verbose option to command line interface (7d91b5f001d0)
* add method to write captured pytest log/error data (aad695cbb28c)

### Fix

* fix used processed evaluation (dd51657a5b52)

## v1.24.0

### Feature

* enable creating test file names against root folder (d33f8f6e8278)
* use safe loader as default yaml loader (fb7d21ef14e1)
* extend public API (2c876c1cd15e)
* add method to create ranged tuple (ff2dbe2f7ff6)
* move code from texmex package (9ae2907a568c)

## v1.23.1

### Feature

* add method to check if item is a number (e81fabf425b9)
* add method to update `OUTFILE` (ccf1ba2c1ec5)
* add method to determine current time in file useable format (01e9211139d2)

### Fix

* fix multiprocessing message (be916f86da32)
* dump correct line ending (349d0163cf46)

## v1.23.0

### Feature

* add flag `OUTFILE` to write all logging in single file (f479d3ae0b42)
* add parsed description to command line interface --help (c2e78963c7f2)
* introduce datatype to improve code style (10bf63bb00a8)
* add option to use @profile as decorator (56c7006eb7c8)

## v1.22.2

### Feature

* add method to create a tuple (30aa9686de26)
* remove tmp prefix cause name indicates random file (be2e43cf0f03)
* add auto flag to choose number of jobs automatically (30b0ce33a7e5)

## v1.22.1

### Feature

* add method to convert tuple to str (2c39b7df074f)
* add optional fallback if accessing out of range (2bd60734b23e)
* support negative indexing to access page numbers from behind (6049887ffadf)
* add method to convert points/pixel to millimeter et vice versa (ac9a2c02a30c)
* log step name if using verbose flag (d99c540d8576)
* add flag to log executed command (30076860df97)

## v1.22.0

### Feature

* add option `!` to disable single processing steps (663ed3607ae0)
* use cwd if no path is given (41e969e95f86)
* add method to parse page number from client input (e0e52b89e9c5)
* add option to disable yielding pagenumber (07b93dbc3431)
* add option to return None for missing in or output path (d7dc4c820111)
* add method to select multiple pages at once (2766e77b7cd3)

### Fix

* ensure to handle return value correctly (8ad865a6b79f)

### Documentation

* fix wrong typing information (42f1639abdf8)

## v1.21.1

### Feature

* if no cwd is given run `assert_run` in current (c2bc31cc0eed)
* include chars into tmp name (78a7bd10ef38)

### Fix

* do not convert list to tuple (24489ea96a5e)

### Documentation

* extend interface documentation (a99074bcc545)

## v1.21.0

### Feature

* change `modes` behavior (9b49f36fa7a8)
* add method to load and verify yaml data (f6d3cabb6867)
* add multiple --pages inputs (12223aeefd73)
* add flag to make listed files absolute (01fadc418f3b)
* add methods least and limit to define borders (112208f5ac46)
* add method to determine max and min of iterable or single item (a1bf4421de34)
* add Single to check if item was already used (7a9272aef7fb)
* add method to create temporary directory with context manager (e36242803669)
* add program name to --version command (3f19fc22edac)
* ensure to get correct input data (43e3cd8da6b1)
* add convert flag to roundme to avoid changing datatype (b43605c53386)

### Fix

* dump None as not valid dumping (be26165de5a7)
* fix tmpdir creation (9e58ed256a2e)

## v1.20.1

### Fix

* ensure to work correctly with paths which contain \n (f2b328efaac4)

## v1.20.0

### Feature

* add methods to determine file name and ext and sort files (50339a237800)
* add option to disable file sorting (9d841919ae45)
* add further data types to store ints and floats (c7d37b08b9df)
* add assert method to ensure types in list (9a409d9507cf)

### Fix

* add missing imports (d35750aafd9c)

## v1.19.0

### Feature

* add method to check if two lines intersects with each other (2735e240412b)
* add const package to determine if a value is near inf or zero (ef4590fb73e9)
* move config dumper and loader (7f0793e088c4)
* add method to check if string contains any template pattern (9070b70d0c5f)
* add package to handle lines and distances (b9b3bda0cea4)

### Fix

* enable single execution pattern in deeper methods (2fc3ab9aa1de)

## v1.18.1

### Fix

* group multiple input directories to a single one (942490148fc2)

## v1.18.0

### Feature

* add `File` write output to defined file (becdcae827ab)
* add method to scan directory recursively (42b0a66d5771)
* add `Directory` pattern to support directories as input (e572485fa976)
* support different package version to check for (063220811dfe)
* add method to normalize white spaces (138956af8ce5)

### Fix

* do not check existence of folder input (5d094e657238)
* ensure to restore old working directory (0588e4affaf5)

## v1.17.4

### Feature

* create subdirectory only if there are files to write (4e6f92eaef65)

## v1.17.3

### Fix

* fix support different datatypes (1fc11c95ef39)

## v1.17.2

### Feature

* add default type to reduce required amount of code (c629c3c5015f)
* introduce datatype pattern to describe variable file types (08288af8f3cf)
* add type Strings to handle list of str (d264e421f7f1)

## v1.17.1

### Feature

* ensure to have forward slash only (5b8260861a7f)

### Fix

* enable checking zero files created (9fbfeb9ad13c)

## v1.17.0

### Feature

* add list of tuples as generated output (a7bfe2bd42be)
* add option to write binary output data (6c24a4c5dad3)
* add method to overwrite and create binary files (a6a00e10dd96)
* add decorator/contextmanager to signal required todo/refactoring (8c9d57a85717)
* add method to create temporary directories (9f3871ca3262)
* add method to count files in folder (455c17e28247)
* extend insure file count with maxdiff flag (7a01bd16bc94)

### Fix

* catch splitting error (1d5c879fb644)
* clarify call parameter check (67b8ab642f49)
* do not skip step if no input data is required (5ec19703610b)
* do not check existence of path connector root (eac43e8a6754)
* avoid converting LocalPath to str, do it inside method (42664b1bf790)

## v1.16.4

### Fix

* handle very long string correctly (abb943234792)

## v1.16.3

### Feature

* add optional validation step (b060181b0f61)
* add validation step (8b5eaae19d3f)

### Fix

* ensure that creating output folder does not break application (d6c36363cc22)

## v1.16.2

### Feature

* enable Number as type for float and int (de6c2c3c0867)

### Documentation

* remove outdated information (9a6cec0cb44b)
* increase interface documentation (e57544157e61)

## v1.16.1

### Feature

* introduce `Bool` to pass bool to working steps (3be74d27343b)
* empty workplan: quit early (b51d5b7e4f0c)

## v1.16.0

### Feature

* add option to pass configuration file (f7fcdab221ff)
* add method to parse configuration file (90540465f1f2)
* format in- and outputs (abe8df241d43)

### Fix

* fix reference (90b997a6e2b5)

### Documentation

* clarify docs (57ccbd04ecfe)

## v1.15.3

### Feature

* add loading from default file name (5988fa029627)

## v1.15.2

### Feature

* move code from `hey` (74250980d742)
* move iterator to sync iterator of content pages (e7d525d8b934)
* add information of wrong page to assertion (891f8511f8b7)
* support chaining page pattern (0786ae4f12a0)

### Fix

* use equal exit point (0656d04926b1)
* ensure that tuple of bool is handled correctly (3b0467fffd0d)
* ensure to handle unsorted `page` correctly (69c0cdb146b4)

### Documentation

* add doctest to convert list of items to list of numbers (ba25f1f1923f)
* clarify some comments (3058d64c6fcd)

## v1.15.1

### Fix

* fix logging output (1943e6c4cf8b)
* support converting bool as input (1c39083adc9b)

## v1.15.0

### Feature

* move rectangle merger from `hey` (28c37aaa6743)
* add method to determine that 2 numbers are near together (d3d74d3eae98)
* copy_content supports multiple pattern right now (403892d70d3c)
* support int variables correctly (0a0aceac3cc2)
* support type conversion for parse tuple (ce9cf2b130e3)
* add methods to convert str to bool or int (a01559f2bd40)
* add path connector to public API (19dbe8b456dc)
* introduce config to reduce complexity (3f822b17f527)

### Fix

* convert bool args correctly (e885175c54f3)
* ensure to convert \n to /n and don't preserve as newline (a429349a7cf8)
* save vertical space (b1f3691085d7)

### Documentation

* remove noisy todo hint (0a408ebcc853)
* use docstring to improve roundme documentation (b163d1b2bc54)

## v1.14.0

### Feature

* support multiple input files (39c4741196e5)
* reduce logging level of FINDING (31e2a85e3ad2)
* add verbose flag to log copy operation (fea445b9f703)
* add context manager to open website on single test execution (3d006faabbcb)
* add expected file fount to increased_filecount (1f139a2a6dbb)
* print log to console immediately (de76bbd11d18)
* support different iterable's (9273a9aeb014)
* add method to convert string to tuple of float (a2f2fd4c185d)

### Fix

* handle .tmp folder correctly as folder not as a file (ffea551ef776)

### Documentation

* extend interface documentation (4b78be11beb0)

## v1.13.1

### Fix

* ensure that SkipCollector handles pages=None correctly (b02fefeec2f1)

## v1.13.0

### Feature

* add method to run commands in parallel (7734d98ffa73)
* add context manager to ensure that files were created (fb239e84238b)
* add method to test that pytest test is executed as single test (f18ed33c5caf)
* add method to support ambiguous modes (4568df9bf92f)
* extend roundme method to round list of floats (10e5dab77fc8)
* add method to check that iterable contains only ascending numbers (6c1470f66343)
* add typing Numbers to public API (c87249760029)
* introduce regex package to add some recipes (24c7078cbde1)
* add context manager to temporary set logging level (baeebdeb626b)
* ensure to handle single values correctly (75579801c1cc)

### Fix

* rename classificator to correct work classifier (64a6affc033c)
* add newline after logging process to run (1ca6e06d0119)
* correct text of --help message (7c3a9526b293)

### Documentation

* add link to backlog on index page (14412d7c4bed)
* use general doc approach on bugs and todo (2245775625ad)
* extend interface documentation (8fd91647d0a9)

## v1.12.1

### Fix

* use Flag instead of Parameter (9799a6e0ff03)
* move logging to better place to display step name (18ec3ac7ed71)
* support every function input to `nothing` context manager (a31f9ce92d05)

## v1.12.0

### Feature

* support automate creation of subfolder (8fb9d0731ec7)
* add --profile step to print runtime for every process step (feffe588f7bc)
* add context manager `nothing` to ease code (980360ff363b)

### Documentation

* extend interface documentation (84b1f37c9a05)
* extend interface documentation (e9917b2ddb30)

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
