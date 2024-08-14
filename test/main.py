import json

from datasets import load_dataset

from agents.search import SearchAgent
from agents.search_choose import SearchResultChoose
from agents.search_decision import SearchDecision
from fleet.context import Context

ds = load_dataset("princeton-nlp/SWE-bench_Lite")


def load_context(id: str) -> Context:
    context = Context()

    tests = ds.get("test")
    issue = None
    for test in tests:
        if test['instance_id'] == id:
            issue = test
            break
    context.issue = f"<description>:{issue['problem_statement']}</description>"
    if "hints_text" in issue and issue['hints_text']:
        context.issue += f"\n<hints>:{issue['hints_text']}</hints>"
    return context


ctx = load_context("pytest-dev__pytest-5221")

print("START")
print("============ PROBLEM ====================")
print(ctx.issue)
print("=========================================")

# search_agent = SearchAgent(ctx)
# search_agent.run()


results = {
  "results": [
    [
      {
        "name": "src/_pytest/python.py",
        "lines": [
          [
            75,
            "\"--fixtures\","
          ],
          [
            84,
            "\"--fixtures-per-test\","
          ]
        ]
      },
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            751,
            "msg += \"\\n use 'pytest --fixtures [testpath]' for help on them.\""
          ]
        ]
      },
      {
        "name": "src/_pytest/helpconfig.py",
        "lines": [
          [
            199,
            "tw.line(\"to see available fixtures type: pytest --fixtures\")"
          ]
        ]
      }
    ],
    [
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            839,
            "class FixtureDef:"
          ],
          [
            46,
            "class PseudoFixtureDef:"
          ],
          [
            119,
            "# an existing FixtureDef structure for all arguments."
          ],
          [
            139,
            "# register artificial FixtureDef's so that later at test execution"
          ],
          [
            140,
            "# time we can rely on a proper FixtureDef to exist for fixture setup."
          ],
          [
            158,
            "fixturedef = FixtureDef("
          ],
          [
            316,
            "name2fixturedefs = attr.ib()  # List[str, List[FixtureDef]]"
          ],
          [
            360,
            "self._fixture_defs = {}  # type: Dict[str, FixtureDef]"
          ],
          [
            505,
            "return PseudoFixtureDef(cached_result, scope)"
          ],
          [
            524,
            "def _compute_fixture_value(self, fixturedef: \"FixtureDef\") -> None:"
          ],
          [
            527,
            "force the FixtureDef object to throw away any previous results and compute a new fixture value, which"
          ],
          [
            528,
            "will be stored into the FixtureDef object itself."
          ],
          [
            931,
            "return \"<FixtureDef argname={!r} scope={!r} baseid={!r}>\".format("
          ],
          [
            1227,
            "fixture function definitions into FixtureDef objects and internal"
          ],
          [
            1440,
            "fixture_def = FixtureDef("
          ],
          [
            1473,
            ":return: list[FixtureDef]"
          ],
          [
            335,
            "# FixtureDefs which wrap 'get_direct_param_fixture_func(request)'."
          ],
          [
            1235,
            "The FuncFixtureInfo object holds information about fixtures and FixtureDefs"
          ]
        ]
      },
      {
        "name": "src/_pytest/nodes.py",
        "lines": [
          [
            24,
            "from _pytest.fixtures import FixtureDef"
          ],
          [
            151,
            "self._name2pseudofixturedef = {}  # type: Dict[str, FixtureDef]"
          ]
        ]
      }
    ],
    [
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            1221,
            "class FixtureManager:"
          ],
          [
            64,
            "session._fixturemanager = FixtureManager(session)"
          ]
        ]
      },
      {
        "name": "src/_pytest/main.py",
        "lines": [
          [
            27,
            "from _pytest.fixtures import FixtureManager"
          ],
          [
            374,
            "_fixturemanager = None  # type: FixtureManager"
          ]
        ]
      }
    ],
    [
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            1283,
            "def getfixtureinfo(self, node, func, cls, funcargs=True):"
          ],
          [
            290,
            "fi = fm.getfixtureinfo(function.parent, function.obj, None)"
          ]
        ]
      },
      {
        "name": "src/_pytest/python.py",
        "lines": [
          [
            1465,
            "fixtureinfo = self.session._fixturemanager.getfixtureinfo("
          ]
        ]
      },
      {
        "name": "src/_pytest/doctest.py",
        "lines": [
          [
            516,
            "doctest_item._fixtureinfo = fm.getfixtureinfo("
          ]
        ]
      },
      {
        "name": "src/_pytest/unittest.py",
        "lines": [
          [
            33,
            "# marker for fixturemanger.getfixtureinfo()"
          ]
        ]
      }
    ],
    [
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            48,
            "scope = attr.ib()"
          ],
          [
            1015,
            "scope = attr.ib()"
          ],
          [
            687,
            "def scope2index(scope, descr, where=None):"
          ],
          [
            1366,
            "def sort_by_scope(arg_name):"
          ],
          [
            600,
            "def _check_scope(self, argname, invoking_scope, requested_scope):"
          ],
          [
            77,
            "def scopeproperty(name=None, doc=None):"
          ],
          [
            78,
            "def decoratescope(func):"
          ],
          [
            240,
            "def reorder_items_atscope(items, argkeys_cache, items_by_argkey, scopenum):"
          ],
          [
            683,
            "def scopemismatch(currentscope, newscope):"
          ],
          [
            69,
            "scope2props = dict(session=())  # type: Dict[str, Tuple[str, ...]]"
          ],
          [
            67,
            "scopename2class = {}  # type: Dict[str, Type[nodes.Node]]"
          ],
          [
            679,
            "scopes = \"session package module class function\".split()"
          ],
          [
            680,
            "scopenum_function = scopes.index(\"function\")"
          ],
          [
            93,
            "def get_scope_package(node, fixturedef):"
          ],
          [
            108,
            "def get_scope_node(node, scope):"
          ],
          [
            820,
            "def _eval_scope_callable(scope_callable, fixture_name, config):"
          ],
          [
            624,
            "def _getscopeitem(self, scope):"
          ],
          [
            70,
            "scope2props[\"package\"] = (\"fspath\",)"
          ],
          [
            71,
            "scope2props[\"module\"] = (\"fspath\", \"module\")"
          ],
          [
            72,
            "scope2props[\"class\"] = scope2props[\"module\"] + (\"cls\",)"
          ],
          [
            73,
            "scope2props[\"instance\"] = scope2props[\"class\"] + (\"instance\",)"
          ],
          [
            74,
            "scope2props[\"function\"] = scope2props[\"instance\"] + (\"function\", \"keywords\")"
          ],
          [
            82,
            "if func.__name__ in scope2props[self.scope]:"
          ],
          [
            85,
            "\"{} not available in {}-scoped context\".format(scopename, self.scope)"
          ],
          [
            109,
            "cls = scopename2class.get(scope)"
          ],
          [
            111,
            "raise ValueError(\"unknown scope\")"
          ],
          [
            126,
            "arg2scope = {}"
          ],
          [
            134,
            "if argname not in arg2scope:"
          ],
          [
            136,
            "arg2scope[argname] = scopes[scopenum]"
          ],
          [
            143,
            "# if we have a scope that is higher than function we need"
          ],
          [
            145,
            "# a per-scope basis. We thus store and cache the fixturedef on the"
          ],
          [
            146,
            "# node related to the scope."
          ],
          [
            147,
            "scope = arg2scope[argname]"
          ],
          [
            149,
            "if scope != \"function\":"
          ],
          [
            150,
            "node = get_scope_node(collector, scope)"
          ],
          [
            152,
            "assert scope == \"class\" and isinstance(collector, _pytest.python.Module)"
          ],
          [
            153,
            "# use module-level collector for class-scope (for now)"
          ],
          [
            163,
            "arg2scope[argname],"
          ],
          [
            186,
            "the specified scope. \"\"\""
          ],
          [
            212,
            "# down to the lower scopes such as to minimize number of \"high scope\""
          ],
          [
            358,
            "#: Scope string, one of \"function\", \"class\", \"module\", \"session\""
          ],
          [
            359,
            "self.scope = \"function\""
          ],
          [
            381,
            "\"\"\" underlying collection node (depends on current request scope)\"\"\""
          ],
          [
            382,
            "return self._getscopeitem(self.scope)"
          ],
          [
            407,
            "\"\"\" test function object if the request has a per-function scope. \"\"\""
          ],
          [
            453,
            "self._addfinalizer(finalizer, scope=self.scope)"
          ],
          [
            455,
            "def _addfinalizer(self, finalizer, scope):"
          ],
          [
            456,
            "colitem = self._getscopeitem(scope)"
          ],
          [
            504,
            "scope = \"function\""
          ],
          [
            505,
            "return PseudoFixtureDef(cached_result, scope)"
          ],
          [
            534,
            "scope = fixturedef.scope"
          ],
          [
            578,
            "# if a parametrize invocation set a scope it will override"
          ],
          [
            579,
            "# the static scope defined with the fixture function"
          ],
          [
            582,
            "scope = scopes[paramscopenum]"
          ],
          [
            584,
            "subrequest = SubRequest(self, scope, param, param_index, fixturedef)"
          ],
          [
            587,
            "subrequest._check_scope(argname, self.scope, scope)"
          ],
          [
            603,
            "if scopemismatch(invoking_scope, requested_scope):"
          ],
          [
            607,
            "\"ScopeMismatch: You tried to access the %r scoped \""
          ],
          [
            610,
            "% ((requested_scope, argname, invoking_scope, \"\\n\".join(lines))),"
          ],
          [
            625,
            "if scope == \"function\":"
          ],
          [
            628,
            "if scope == \"package\":"
          ],
          [
            629,
            "node = get_scope_package(self._pyfuncitem, self._fixturedef)"
          ],
          [
            631,
            "node = get_scope_node(self._pyfuncitem, scope)"
          ],
          [
            632,
            "if node is None and scope == \"class\":"
          ],
          [
            635,
            "assert node, 'Could not obtain a node for scope \"{}\" for function {!r}'.format("
          ],
          [
            636,
            "scope, self._pyfuncitem"
          ],
          [
            648,
            "def __init__(self, request, scope, param, param_index, fixturedef):"
          ],
          [
            654,
            "self.scope = scope"
          ],
          [
            688,
            "\"\"\"Look up the index of ``scope`` and raise a descriptive value error"
          ],
          [
            692,
            "return scopes.index(scope)"
          ],
          [
            695,
            "\"{} {}got an unexpected scope value '{}'\".format("
          ],
          [
            696,
            "descr, \"from {} \".format(where) if where else \"\", scope"
          ],
          [
            822,
            "result = scope_callable(fixture_name=fixture_name, config=config)"
          ],
          [
            827,
            "scope_callable, fixture_name"
          ],
          [
            833,
            "\"{!r}\".format(scope_callable, fixture_name, result),"
          ],
          [
            848,
            "scope,"
          ],
          [
            858,
            "if callable(scope):"
          ],
          [
            859,
            "scope = _eval_scope_callable(scope, argname, fixturemanager.config)"
          ],
          [
            860,
            "self.scope = scope"
          ],
          [
            861,
            "self.scopenum = scope2index("
          ],
          [
            862,
            "scope or \"function\","
          ],
          [
            931,
            "return \"<FixtureDef argname={!r} scope={!r} baseid={!r}>\".format("
          ],
          [
            932,
            "self.argname, self.scope, self.baseid"
          ],
          [
            969,
            "request._check_scope(argname, request.scope, fixdef.scope)"
          ],
          [
            1046,
            "FIXTURE_ARGS_ORDER = (\"scope\", \"params\", \"autouse\", \"ids\", \"name\")"
          ],
          [
            1049,
            "def _parse_fixture_args(callable_or_scope, *args, **kwargs):"
          ],
          [
            1051,
            "\"scope\": \"function\","
          ],
          [
            1062,
            "if isinstance(callable_or_scope, str):"
          ],
          [
            1064,
            "args.insert(0, callable_or_scope)"
          ],
          [
            1066,
            "fixture_function = callable_or_scope"
          ],
          [
            1089,
            "callable_or_scope=None,"
          ],
          [
            1091,
            "scope=\"function\","
          ],
          [
            1115,
            ":arg scope: the scope for which this fixture is shared, one of"
          ],
          [
            1123,
            "See :ref:`dynamic scope` in the docs for more information."
          ],
          [
            1150,
            "callable_or_scope,"
          ],
          [
            1152,
            "scope=scope,"
          ],
          [
            1158,
            "scope = arguments.get(\"scope\")"
          ],
          [
            1166,
            "return FixtureFunctionMarker(scope, params, autouse, name=name)("
          ],
          [
            1170,
            "return FixtureFunctionMarker(scope, params, autouse, ids=ids, name=name)"
          ],
          [
            1174,
            "callable_or_scope=None,"
          ],
          [
            1176,
            "scope=\"function\","
          ],
          [
            1188,
            "callable_or_scope,"
          ],
          [
            1190,
            "scope=scope,"
          ],
          [
            1198,
            "@fixture(scope=\"session\")"
          ],
          [
            1374,
            "fixturenames_closure.sort(key=sort_by_scope)"
          ],
          [
            1401,
            "scope=fixturedef.scope,"
          ],
          [
            1445,
            "marker.scope,"
          ],
          [
            55,
            "scopename2class.update("
          ],
          [
            79,
            "scopename = name or func.__name__"
          ],
          [
            90,
            "return decoratescope"
          ],
          [
            135,
            "scopenum = callspec._arg2scopenum.get(argname, scopenum_function)"
          ],
          [
            184,
            "def get_parametrized_fixture_keys(item, scopenum):"
          ],
          [
            187,
            "assert scopenum < scopenum_function  # function"
          ],
          [
            197,
            "if cs._arg2scopenum[argname] != scopenum:"
          ],
          [
            199,
            "if scopenum == 0:  # session"
          ],
          [
            201,
            "elif scopenum == 1:  # package"
          ],
          [
            203,
            "elif scopenum == 2:  # module"
          ],
          [
            205,
            "elif scopenum == 3:  # class"
          ],
          [
            211,
            "# it is called for scopenum==0 (session) first and performs sorting"
          ],
          [
            219,
            "for scopenum in range(0, scopenum_function):"
          ],
          [
            220,
            "argkeys_cache[scopenum] = d = {}"
          ],
          [
            221,
            "items_by_argkey[scopenum] = item_d = defaultdict(deque)"
          ],
          [
            224,
            "get_parametrized_fixture_keys(item, scopenum)"
          ],
          [
            231,
            "return list(reorder_items_atscope(items, argkeys_cache, items_by_argkey, 0))"
          ],
          [
            235,
            "for scopenum in range(0, scopenum_function):"
          ],
          [
            236,
            "for key in argkeys_cache[scopenum].get(item, []):"
          ],
          [
            237,
            "items_by_argkey[scopenum][key].appendleft(item)"
          ],
          [
            241,
            "if scopenum >= scopenum_function or len(items) < 3:"
          ],
          [
            246,
            "scoped_items_by_argkey = items_by_argkey[scopenum]"
          ],
          [
            247,
            "scoped_argkeys_cache = argkeys_cache[scopenum]"
          ],
          [
            256,
            "k for k in scoped_argkeys_cache.get(item, []) if k not in ignore"
          ],
          [
            264,
            "i for i in scoped_items_by_argkey[slicing_argkey] if i in items"
          ],
          [
            271,
            "no_argkey_group = reorder_items_atscope("
          ],
          [
            272,
            "no_argkey_group, argkeys_cache, items_by_argkey, scopenum + 1"
          ],
          [
            405,
            "@scopeproperty()"
          ],
          [
            410,
            "@scopeproperty(\"class\")"
          ],
          [
            427,
            "@scopeproperty()"
          ],
          [
            432,
            "@scopeproperty()"
          ],
          [
            580,
            "paramscopenum = funcitem.callspec._arg2scopenum.get(argname)"
          ],
          [
            586,
            "# check if a higher-level scoped fixture accesses a lower level one"
          ],
          [
            608,
            "\"fixture %r with a %r scoped request object, \""
          ],
          [
            684,
            "return scopes.index(newscope) > scopes.index(currentscope)"
          ],
          [
            1200,
            "\"\"\"Session-scoped fixture that returns the :class:`_pytest.config.Config` object."
          ],
          [
            1370,
            "return scopes.index(\"function\")"
          ],
          [
            1372,
            "return fixturedefs[-1].scopenum"
          ],
          [
            581,
            "if paramscopenum is not None:"
          ]
        ]
      },
      {
        "name": "src/_pytest/python.py",
        "lines": [
          [
            1147,
            "def _find_parametrized_scope(argnames, arg2fixturedefs, indirect):"
          ],
          [
            470,
            "@fixtures.fixture(autouse=True, scope=\"module\")"
          ],
          [
            494,
            "@fixtures.fixture(autouse=True, scope=\"function\")"
          ],
          [
            699,
            "@fixtures.fixture(autouse=True, scope=\"class\")"
          ],
          [
            723,
            "@fixtures.fixture(autouse=True, scope=\"function\")"
          ],
          [
            865,
            "scope: \"Optional[str]\" = None,"
          ],
          [
            910,
            ":arg scope: if specified it denotes the scope of the parameters."
          ],
          [
            911,
            "The scope is used for grouping tests by parameter instances."
          ],
          [
            912,
            "It will also override any fixture-function defined scope, allowing"
          ],
          [
            913,
            "to set a dynamic scope using test context or configuration."
          ],
          [
            915,
            "from _pytest.fixtures import scope2index"
          ],
          [
            932,
            "if scope is None:"
          ],
          [
            933,
            "scope = _find_parametrized_scope(argnames, self._arg2fixturedefs, indirect)"
          ],
          [
            953,
            "scopenum = scope2index("
          ],
          [
            954,
            "scope, descr=\"parametrize() call in {}\".format(self.function.__name__)"
          ],
          [
            1148,
            "\"\"\"Find the most appropriate scope for a parametrized call based on its arguments."
          ],
          [
            1150,
            "When there's at least one direct argument, always use \"function\" scope."
          ],
          [
            1153,
            "(e.g. fixtures), return the most narrow scope based on the fixtures used."
          ],
          [
            1167,
            "fixturedef[0].scope"
          ],
          [
            1172,
            "# Takes the most narrow scope from used fixtures"
          ],
          [
            1173,
            "for scope in reversed(scopes):"
          ],
          [
            1174,
            "if scope in used_scopes:"
          ],
          [
            1175,
            "return scope"
          ],
          [
            1393,
            "if fixturedef.scope != \"function\":"
          ],
          [
            1394,
            "tw.write(\" [%s scope]\" % fixturedef.scope, cyan=True)"
          ],
          [
            454,
            "\"\"\"Injects a hidden autouse, module scoped fixture into the collected module object"
          ],
          [
            481,
            "\"\"\"Injects a hidden autouse, function scoped fixture into the collected module object"
          ],
          [
            688,
            "\"\"\"Injects a hidden autouse, class scoped fixture into the collected class object"
          ],
          [
            712,
            "\"\"\"Injects a hidden autouse, function scoped fixture into the collected class object"
          ],
          [
            773,
            "self._arg2scopenum = {}  # used for sorting parametrized resources"
          ],
          [
            783,
            "cs._arg2scopenum.update(self._arg2scopenum)"
          ],
          [
            801,
            "def setmulti2(self, valtypes, argnames, valset, id, marks, scopenum, param_index):"
          ],
          [
            807,
            "self._arg2scopenum[arg] = scopenum"
          ],
          [
            970,
            "scopenum,"
          ],
          [
            1157,
            "from _pytest.fixtures import scopes"
          ],
          [
            1166,
            "used_scopes = ["
          ],
          [
            1171,
            "if used_scopes:"
          ]
        ]
      },
      {
        "name": "src/_pytest/nodes.py",
        "lines": [
          [
            116,
            "#: a unique name within the scope of the parent node"
          ],
          [
            141,
            "#: keywords/markers collected from all scopes"
          ]
        ]
      },
      {
        "name": "src/_pytest/tmpdir.py",
        "lines": [
          [
            153,
            "@pytest.fixture(scope=\"session\")"
          ],
          [
            161,
            "@pytest.fixture(scope=\"session\")"
          ]
        ]
      },
      {
        "name": "src/_pytest/doctest.py",
        "lines": [
          [
            681,
            "@pytest.fixture(scope=\"session\")"
          ]
        ]
      },
      {
        "name": "src/_pytest/terminal.py",
        "lines": [
          [
            1170,
            "# this is workaround, because for now we cannot identify the scope of a skip marker"
          ],
          [
            1171,
            "# TODO: revisit after marks scope would be fixed"
          ]
        ]
      },
      {
        "name": "src/_pytest/junitxml.py",
        "lines": [
          [
            336,
            "@pytest.fixture(scope=\"session\")"
          ],
          [
            342,
            "This is a ``session``-scoped fixture which is called with ``(name, value)``. Example:"
          ]
        ]
      },
      {
        "name": "src/_pytest/unittest.py",
        "lines": [
          [
            72,
            "cls, \"setUpClass\", \"tearDownClass\", scope=\"class\", pass_self=False"
          ],
          [
            78,
            "cls, \"setup_method\", \"teardown_method\", scope=\"function\", pass_self=True"
          ],
          [
            84,
            "def _make_xunit_fixture(obj, setup_name, teardown_name, scope, pass_self):"
          ],
          [
            90,
            "@pytest.fixture(scope=scope, autouse=True)"
          ]
        ]
      },
      {
        "name": "src/_pytest/setuponly.py",
        "lines": [
          [
            56,
            "\"{step} {scope} {fixture}\".format("
          ],
          [
            58,
            "scope=fixturedef.scope[0].upper(),"
          ],
          [
            54,
            "tw.write(\" \" * 2 * fixturedef.scopenum)"
          ]
        ]
      },
      {
        "name": "src/_pytest/python_api.py",
        "lines": [
          [
            619,
            "raised *must* be the final line in the scope of the context manager."
          ],
          [
            620,
            "Lines of code after that, within the scope of the context manager will"
          ],
          [
            630,
            "scope)::"
          ]
        ]
      }
    ],
    [],
    [
      {
        "name": "src/_pytest/python.py",
        "lines": [
          [
            812,
            "class Metafunc:"
          ],
          [
            136,
            "def pytest_generate_tests(metafunc: \"Metafunc\") -> None:"
          ],
          [
            137,
            "for marker in metafunc.definition.iter_markers(name=\"parametrize\"):"
          ],
          [
            139,
            "metafunc.parametrize(*marker.args, **marker.kwargs, _param_mark=marker)  # type: ignore[misc] # noqa: F821"
          ],
          [
            406,
            "metafunc = Metafunc("
          ],
          [
            415,
            "self.ihook.pytest_generate_tests.call_extra(methods, dict(metafunc=metafunc))"
          ],
          [
            417,
            "if not metafunc._calls:"
          ],
          [
            421,
            "fixtures.add_funcarg_pseudo_fixture_def(self, metafunc, fm)"
          ],
          [
            428,
            "for callspec in metafunc._calls:"
          ],
          [
            768,
            "def __init__(self, metafunc):"
          ],
          [
            769,
            "self.metafunc = metafunc"
          ],
          [
            778,
            "cs = CallSpec2(self.metafunc)"
          ],
          [
            814,
            "Metafunc objects are passed to the :func:`pytest_generate_tests <_pytest.hookspec.pytest_generate_tests>` hook."
          ],
          [
            1554,
            "crappy metafunc hack"
          ]
        ]
      },
      {
        "name": "src/_pytest/fixtures.py",
        "lines": [
          [
            115,
            "def add_funcarg_pseudo_fixture_def(collector, metafunc, fixturemanager):"
          ],
          [
            122,
            "if not metafunc._calls[0].funcargs:"
          ],
          [
            127,
            "for callspec in metafunc._calls:"
          ],
          [
            141,
            "arg2fixturedefs = metafunc._arg2fixturedefs"
          ],
          [
            1230,
            "During collection of test functions, metafunc-mechanics instantiate"
          ],
          [
            1377,
            "def pytest_generate_tests(self, metafunc):"
          ],
          [
            1378,
            "for argname in metafunc.fixturenames:"
          ],
          [
            1379,
            "faclist = metafunc._arg2fixturedefs.get(argname)"
          ],
          [
            1383,
            "markers = list(metafunc.definition.iter_markers(\"parametrize\"))"
          ],
          [
            1397,
            "metafunc.parametrize("
          ]
        ]
      },
      {
        "name": "src/_pytest/hookspec.py",
        "lines": [
          [
            305,
            "def pytest_generate_tests(metafunc):"
          ]
        ]
      }
    ],
    [],
    [
      {
        "name": "src/_pytest/python.py",
        "lines": [
          [
            1286,
            "def show_fixtures_per_test(config):"
          ],
          [
            1292,
            "def _show_fixtures_per_test(config, session):"
          ],
          [
            86,
            "dest=\"show_fixtures_per_test\","
          ],
          [
            131,
            "if config.option.show_fixtures_per_test:"
          ],
          [
            132,
            "show_fixtures_per_test(config)"
          ],
          [
            1289,
            "return wrap_session(config, _show_fixtures_per_test)"
          ]
        ]
      }
    ],
    [
      {
        "name": "src/_pytest/runner.py",
        "lines": [
          [
            47,
            "def pytest_terminal_summary(terminalreporter):"
          ]
        ]
      },
      {
        "name": "src/_pytest/hookspec.py",
        "lines": [
          [
            611,
            "def pytest_terminal_summary(terminalreporter, exitstatus, config):"
          ]
        ]
      },
      {
        "name": "src/_pytest/warnings.py",
        "lines": [
          [
            131,
            "def pytest_terminal_summary(terminalreporter):"
          ]
        ]
      },
      {
        "name": "src/_pytest/pastebin.py",
        "lines": [
          [
            89,
            "def pytest_terminal_summary(terminalreporter):"
          ]
        ]
      },
      {
        "name": "src/_pytest/terminal.py",
        "lines": [
          [
            746,
            "def pytest_terminal_summary(self):"
          ],
          [
            733,
            "self.config.hook.pytest_terminal_summary("
          ]
        ]
      },
      {
        "name": "src/_pytest/junitxml.py",
        "lines": [
          [
            664,
            "def pytest_terminal_summary(self, terminalreporter):"
          ]
        ]
      }
    ]
  ]
}

# search_decide = SearchResultChoose(ctx, json.dumps(results))
# search_decide.run()

with open("./build/5221/_source_python.py") as f:
    source = f.read()
search_decision = SearchDecision(ctx, source)
search_decision.run()
print("Done")