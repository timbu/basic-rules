from basicrules.functions import (
    Function, Equals, Add, Param, Constant, Lte, Gte, In, NotIn, Or, And, Not, If,
    ParamWithDefault, Subtract, Multiply, Divide
)
import pytest


class TestFunction:

    @pytest.fixture
    def sub_func(self):
        class SubFunc(Function):
            min_args = 1
            max_args = 2
        return SubFunc

    def test_min_args_validation(self, sub_func):
        with pytest.raises(ValueError) as exc:
            sub_func()

        assert 'Expected min 1 args but was 0' in str(exc)

    def test_max_args_validation(self, sub_func):
        with pytest.raises(ValueError) as exc:
            sub_func(1, 2, 3)

        assert 'Expected max 2 args but was 3' in str(exc)

    def test_args_setting(self, sub_func):
        func = sub_func(1, 2)
        assert func.args == (1, 2)

        func = sub_func(1)
        assert func.args == (1,)

    def test_evaluate_not_implemented(self, sub_func):
        func = sub_func(1, 2)
        with pytest.raises(NotImplementedError):
            func.evaluate({})

    def test_debug(self):
        func = Equals(Param('foo'), Add(Param('bar'), Constant(5)))
        assert func.debug({'foo': 1, 'bar': 2}) == (
            '<equals('
            '<param(foo)=1>, <add(<param(bar)=2>, <constant(5)>)=7>'
            ')=False>'
        )
        assert func.debug({'bar': None}) == (
            '<equals('
            '<param(foo)=None>, <add(<param(bar)=None>, <constant(5)>'
            ')=TypeError>)=TypeError>'
        )

    def test_evaluate(self):
        func = Equals(Param('foo'), Add(Param('bar'), Constant(5)))
        assert func.debug({'foo': 1, 'bar': 2}) == (
            '<equals('
            '<param(foo)=1>, <add(<param(bar)=2>, <constant(5)>)=7>'
            ')=False>'
        )


class TestSerialize:

    @pytest.fixture
    def sub_func(self):
        class SubFunc(Function):
            min_args = 0
            max_args = 3
            name = 'sub_func'

        return SubFunc

    def test_from_dict_with_no_args(self, sub_func):
        dct = {'sub_func': []}
        func = Function.from_dict(dct)
        assert func.args == ()
        assert func.to_dict() == {'sub_func': []}

    def test_from_dict_with_one_arg(self, sub_func):
        dct = {'sub_func': ['foo']}
        func = Function.from_dict(dct)
        assert func.args == ('foo', )
        assert func.to_dict() == {'sub_func': ['foo']}

    def test_from_dict_with_two_args(self, sub_func):
        dct = {'sub_func': ['foo', [1, 2, 3]]}
        func = Function.from_dict(dct)
        assert func.args == ('foo', [1, 2, 3])

        assert func.to_dict() == {'sub_func': ['foo', [1, 2, 3]]}

    def test_serialize_and_deserialize(self):
        dct = {'if': [
            {'or': [
                {'equals': [
                    {'param': ['foo.bar']},
                    {'param': ['blah']},
                ]},
                {'in': [
                    {'param': ['letter']},
                    {'constant': [['a', 'b']]},
                ]},
            ]},
            {'add': [
                {'multiply': [
                    {'constant': [5]},
                    {'constant': [2]},
                ]},
                {'subtract': [
                    {'divide': [
                        {'constant': [44]},
                        {'constant': [2]},
                    ]},
                    {'constant': [21]},
                ]},
            ]},
            {'constant': ['blue']},
        ]}

        func = Function.from_dict(dct)
        back_dict = func.to_dict()
        func2 = Function.from_dict(back_dict)
        back_dict2 = func2.to_dict()

        # test round trip
        assert dct == back_dict2

        # test evaluate function
        assert func2.evaluate({'blah': 3, 'foo': {'bar': 2}, 'letter': 'a'}) == 11
        assert func2.evaluate({'blah': 3, 'foo': {'bar': 2}, 'letter': 'b'}) == 11
        assert func2.evaluate({'blah': 2, 'foo': {'bar': 2}, 'letter': 'c'}) == 11
        assert func2.evaluate({'blah': 3, 'foo': {'bar': 2}, 'letter': 'c'}) == 'blue'


class TestComparisonFunctions:

    @pytest.mark.parametrize(
        ('cls', 'arg1', 'arg2', 'expected'), [
            (Equals, 1, 1, True),
            (Equals, 1, 0, False),
            (Equals, 'aaa', 'aaa', True),
            (Equals, 'aaa', None, False),
            (Lte, 1, 2, True),
            (Lte, 1, 1, True),
            (Lte, 2, 1, False),
            (Gte, 1, 2, False),
            (Gte, 1, 1, True),
            (Gte, 2, 1, True),
            (In, 'a', ['a', 'b'], True),
            (In, 'a', ['c', 'b'], False),
            (In, 'a', [], False),
            (NotIn, 'a', ['a', 'b'], False),
            (NotIn, 'a', ['c', 'b'], True),
            (NotIn, 'a', [], True),

        ]
    )
    def test_func(self, cls, arg1, arg2, expected):
        arg1 = Constant(arg1)
        arg2 = Constant(arg2)
        func = cls(arg1, arg2)
        assert func.evaluate({}) == expected


class TestBooleanFunctions:

    @pytest.mark.parametrize(
        ('func', 'expected'), [
            (Or(Constant(True), Constant(False)), True),
            (Or(Constant(False), Constant(False)), False),
            (Or(Constant(True), Constant(True)), True),
            (Or(Constant(False), Constant(False), Constant(True)), True),
            (And(Constant(True), Constant(False)), False),
            (And(Constant(False), Constant(False)), False),
            (And(Constant(True), Constant(True)), True),
            (And(Constant(True), Constant(True), Constant(False)), False),
            (Not(Constant(True)), False),
            (Not(Constant(False)), True),
            (If(Constant(True), Constant('A'), Constant('B')), 'A'),
            (If(Constant(False), Constant('A'), Constant('B')), 'B'),
        ]
    )
    def test_func(self, func, expected):
        assert func.evaluate({}) == expected


class TestParamFunctions:

    class Obj:
        def __init__(self, foo):
            self.foo = foo

    @pytest.mark.parametrize(
        ('func', 'context', 'expected'), [
            (Param('foo'), {'foo': 5}, 5),
            (Param('foo'), {'foo': None}, None),
            (Param('foo'), {'bar': 5}, None),
            (Param('foo.bar'), {}, None),
            (Param('foo.bar'), {'foo': {}}, None),
            (Param('foo.bar'), {'foo': {'bar': 5}}, 5),
            (Param('foo.bar'), Obj({'bar': 5}), 5),
            (ParamWithDefault('foo', 1), {'foo': 5}, 5),
            (ParamWithDefault('foo', 1), {'foo': None}, 1),
            (ParamWithDefault('foo', 1), {'bar': 5}, 1),
            (ParamWithDefault('foo.bar', 1), {}, 1),
            (ParamWithDefault('foo.bar', 1), {'foo': {}}, 1),
            (ParamWithDefault('foo.bar', 1), {'foo': {'bar': 5}}, 5),

        ]
    )
    def test_func(self, func, context, expected):
        assert func.evaluate(context) == expected


class TestMathsFunctions:

    @pytest.mark.parametrize(
        ('cls', 'arg1', 'arg2', 'expected'), [
            (Add, 2, 3, 5),
            (Subtract, 5, 3, 2),
            (Multiply, 5, 3, 15),
            (Divide, 15, 3, 5),
        ]
    )
    def test_func(self, cls, arg1, arg2, expected):
        arg1 = Constant(arg1)
        arg2 = Constant(arg2)
        func = cls(arg1, arg2)
        assert func.evaluate({}) == expected
