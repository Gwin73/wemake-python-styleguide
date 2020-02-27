# -*- coding: utf-8 -*-

import pytest

from wemake_python_styleguide.violations.complexity import (
    TooManyRaisesViolation,
)
from wemake_python_styleguide.visitors.ast.complexity.function import (
    FunctionComplexityVisitor,
)

module_many_raises = """
if some:
    raise SomeException
raise SomeOtherException
"""

lambda_many_raises = """
lambda: SomeException if some else SomeOtherException
"""

function_template = """
def function(parameter):
    {0}
"""

instance_method_template = """
class Test(object):
    def method(self, parameter):
        {0}
"""

class_method_template = """
class Test(object):
    @classmethod
    def method(cls, parameter):
        {0}
"""

static_method_template = """
class Test(object):
    @staticmethod
    def method(parameter):
        {0}
"""

no_raises_block = """
...
"""

raises_block = """
if some:
    raise SomeException
raise SomeOtherException
"""

nested_raises_block = """
def helper():
    raise SomeException
raise SomeOtherException
"""


# I don't think this should fail
@pytest.mark.parametrize('code', [
    module_many_raises,
    lambda_many_raises,
])
def test_asserts_correct_count1(
    assert_errors,
    parse_ast_tree,
    code,
    default_options,
):
    """Testing that raises counted correctly."""
    tree = parse_ast_tree(code)

    visitor = FunctionComplexityVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('context', [
    function_template,
    instance_method_template,
    class_method_template,
    static_method_template,
])
@pytest.mark.parametrize('code', [
    no_raises_block,
    raises_block,
    nested_raises_block,
])
def test_raises_correct_count2(
    assert_errors,
    parse_ast_tree,
    context,
    code,
    default_options,
):
    """Testing that raises are counted correctly."""
    tree = parse_ast_tree(context.format(code))

    visitor = FunctionComplexityVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('context', [
    function_template,
    instance_method_template,
    class_method_template,
    static_method_template,
])
@pytest.mark.parametrize('code', [
    raises_block,
    nested_raises_block,
])
def test_raises_wrong_count(
    assert_errors,
    assert_error_text,
    parse_ast_tree,
    options,
    context,
    code,
):
    """Testing that many raises raises a warning."""
    tree = parse_ast_tree(code)

    option_values = options(max_raises=1)
    visitor = FunctionComplexityVisitor(option_values, tree=tree)
    visitor.run()

    assert_errors(visitor, [TooManyRaisesViolation])
    assert_error_text(visitor, '2', option_values.max_raises)
