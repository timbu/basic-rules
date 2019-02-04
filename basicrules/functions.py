
function_classes = {}


class RegisteringMetaclass(type):
    def __new__(*args):  # pylint: disable=no-method-argument
        cls = type.__new__(*args)
        if cls.name:
            function_classes[cls.name] = cls
        return cls


class Function(metaclass=RegisteringMetaclass):
    name = None
    min_args = None
    max_args = None

    def __init__(self, *args):
        if self.min_args is not None and len(args) < self.min_args:
            raise ValueError(
                'Expected min {} args but was {}'.format(self.min_args, len(args))
            )
        if self.max_args is not None and len(args) > self.max_args:
            raise ValueError(
                'Expected max {} args but was {}'.format(self.max_args, len(args))
            )
        self.args = args

    def evaluate(self, context):
        raise NotImplementedError()

    def debug(self, context):
        try:
            result = self.evaluate(context)
        except Exception as e:
            result = type(e).__name__

        return '<{}({})={}>'.format(
            self.name,
            ', '.join(
                f.debug(context) if isinstance(f, Function) else str(f)
                for f in self.args
            ),
            result,
        )

    def to_dict(self):
        return {
            self.name: [
                f.to_dict()
                if isinstance(f, Function) else f for f in self.args
            ]
        }

    @classmethod
    def from_dict(cls, dct):
        if (
            isinstance(dct, dict) and
            len(dct) == 1 and
            list(dct.keys())[0] in function_classes
        ):
            func_name, arg_dicts = list(dct.items())[0]
            func_class = function_classes[func_name]
            return func_class(*[
                cls.from_dict(arg_dict) for arg_dict in arg_dicts
            ])

        return dct


class Equals(Function):
    name = 'equals'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        result1 = self.args[0].evaluate(context)
        result2 = self.args[1].evaluate(context)
        return result1 == result2


class Lte(Function):
    name = 'lte'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        result1 = self.args[0].evaluate(context)
        result2 = self.args[1].evaluate(context)
        return result1 <= result2


class Gte(Function):
    name = 'gte'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        result1 = self.args[0].evaluate(context)
        result2 = self.args[1].evaluate(context)
        return result1 >= result2


class In(Function):
    name = 'in'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) in self.args[1].evaluate(context)


class NotIn(Function):
    name = 'notin'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) not in self.args[1].evaluate(context)


class Or(Function):
    name = 'or'
    min_args = 2
    max_args = None

    def evaluate(self, context):
        return any(f.evaluate(context) for f in self.args)


class And(Function):
    name = 'and'
    min_args = 2
    max_args = None

    def evaluate(self, context):
        return all(f.evaluate(context) for f in self.args)


class Not(Function):
    name = 'not'
    min_args = 1
    max_args = 1

    def evaluate(self, context):
        return not self.args[0].evaluate(context)


class If(Function):
    name = 'if'
    min_args = 3
    max_args = 3

    def evaluate(self, context):
        if self.args[0].evaluate(context):
            return self.args[1].evaluate(context)
        return self.args[2].evaluate(context)


class Constant(Function):
    name = 'constant'
    min_args = 1
    max_args = 1

    def evaluate(self, context):
        return self.args[0]

    def debug(self, context):
        return '<constant({})>'.format(str(self.args[0]))


class ParamMixin:

    def _evaluate(self, context):
        result = context
        for item in self.path_items:
            if hasattr(result, item):
                result = getattr(result, item)
            elif isinstance(result, dict):
                result = result.get(item)
            else:
                return None
        return result


class Param(Function, ParamMixin):
    name = 'param'
    min_args = 1
    max_args = 1

    def __init__(self, path):
        super().__init__(path)
        self.path_items = path.split('.')

    def evaluate(self, context):
        return self._evaluate(context)


class ParamWithDefault(Function, ParamMixin):
    name = 'dparam'
    min_args = 2
    max_args = 2

    def __init__(self, path, default):
        super().__init__(path, default)
        self.path_items = path.split('.')
        self.default = default

    def evaluate(self, context):
        result = self._evaluate(context)
        if result is None:
            return self.default
        return result


class Add(Function):
    name = 'add'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) + self.args[1].evaluate(context)


class Subtract(Function):
    name = 'subtract'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) - self.args[1].evaluate(context)


class Multiply(Function):
    name = 'multiply'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) * self.args[1].evaluate(context)


class Divide(Function):
    name = 'divide'
    min_args = 2
    max_args = 2

    def evaluate(self, context):
        return self.args[0].evaluate(context) / self.args[1].evaluate(context)
