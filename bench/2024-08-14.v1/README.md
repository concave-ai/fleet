logs: 2024-08-15.v2

```
root_casue_found: 12
might: 4
can't fix: 3 
```


note
``` 
- pytest-5262 ✅
    - src/_pytest/capture.py 
    - class EncodedFile
    
- pytest-5631 ✅
    - src/_pytest/compat.py
    - def num_mock_patch_args
    
- pytest-5785 ✅? 
    - src/_pytest/reports.py
    - class BaseReport
    - def BaseReport.to_json
RCA found, btw relavant_symbols give a lot(11)
    
- pytest-5809  ✅
    - src/_pytest/pastebin.py
    - def create_new_paste
    
- pytest-5840 ⚠️ 
    - src/_pytest/config/__init__.py
    - class PytestPluginManager
        - def _set_initial_conftests
        - def _importconftest
        
found _importconftest, not found _set_initial_conftests
not sure _set_initial_conftests need or not. 

- pytest-6197 🙅🙅🙅
    - src/_pytest/python.py
    - class Module
        - def Module.collect
    - class PyobjMixin
        - obj
        
this hard, change a lot 


- pytest-6202 ✅
    - src/_pytest/python.py
    - class PyobjMixin
        - def getmodpath
        
        
- pytest-7205 ✅
    - src/_pytest/setuponly.py
    - _show_fixture_action

- pytest-7236 🙅 
    - src/_pytest/unittest.py
    - class UnitTestCase
        - def collect
    - def _make_xunit_fixture
        - def fixture
    - class TestCaseFunction
        - def runtest
        
this hard，create a new skip check def,  change three files。
almost give me all info, btw some in relavant_symbols, not root_cause

    
- pytest-7324 ⚠️
    - src/_pytest/mark/expression.py
    - def not_expr
    - class MatcherAdapter
        - def __getitesm__
in relavant_symbols, not root_cause


- pytest-7432 ✅
    - src/_pytest/skipping.py
    - def pytest_runtest_makereport

    
- pytest-7490 🙅🙅🙅
    - src/_pytest/logging.py
    - def pytest_runtest_setup
    - def pytest_runtest_call

gard
wrong file choosed. 

- pytest-7521   ⚠️
    - src/_pytest/capture.py
    - class FDCaptureBinary
        - def __init__
 found FDCapture, not found FDCaptureBinary(is FDCaptureBinary a subclass of FDCapture)   
    
- pytest-7571  ✅
    - src/_pytest/logging.py
    - class LogCaptureFixture
        - def __init__
        - def _finalize
        - def set_level
        
- pytest-7982  ✅
    - src/_pytest/pathlib.py
    - visit
可能产生了幻觉，在两个文件中都认为是根源问题。

    
- pytest-8399 ⚠️
    - src/_pytest/python.py
    - class Module
        - def xunit_setup_module_fixture
        - def xunit_setup_function_fixture
        - def xunit_setup_class_fixture_
        - def xunit_setup_method_fixture_
    - src/_pytest/unittest.py
    - def _make_xunit_fixture
        - def fixture
几乎做出来了

- pytest-10051  ✅
    - src/_pytest/logging.py
    - class LogCaptureHandler
        - clear
    - class LogCaptureFixture !
        - clear
        
- pytest-10081  ✅
    - src/_pytest/unittest.py
    - class TestCaseFunction
        - def runtest

- pytest-10356  ✅
    - src/_pytest/mark/structures.py
    - def get_unpacked_marks
    - def store_mark

need change get_unpacked_marks args.
so will change store_mark too (store_mark is called by get_unpacked_marks)


```