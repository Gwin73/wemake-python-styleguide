# -*- coding: utf-8 -*-

import pytest

from wemake_python_styleguide.visitors.ast.complexity.function import (
    FunctionComplexityVisitor,
    TooManyRaisesViolation,
)

function_without_raises = 'def function(): ...'

function_with_raises = """
def function():
    if 1 > 2:
        raise error1
    raise error2
"""

function_with_nested_function_and_raises = """
def function():  # has two raises
    def factory():  # has one raise
        raise error3
    raise error4
"""


@pytest.mark.parametrize('code', [
    function_without_raises,
    function_with_raises,
    function_with_nested_function_and_raises,
])
def test_raises_correct_count(
    assert_errors,
    parse_ast_tree,
    code,
    default_options,
    mode,
):
    """Testing that raises counted correctly."""
    tree = parse_ast_tree(mode(code))

    visitor = FunctionComplexityVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('code', [
    function_with_raises,
    function_with_nested_function_and_raises,
])
def test_raises_wrong_count(
    assert_errors,
    assert_error_text,
    parse_ast_tree,
    options,
    code,
    mode,
):
    """Testing that many raises raises a warning."""
    tree = parse_ast_tree(mode(code))

    option_values = options(max_raises=1)
    visitor = FunctionComplexityVisitor(option_values, tree=tree)
    visitor.run()

    assert_errors(visitor, [TooManyRaisesViolation])
    assert_error_text(visitor, '2', option_values.max_raises)
