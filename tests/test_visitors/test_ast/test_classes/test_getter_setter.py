# -*- coding: utf-8 -*-

import pytest

from wemake_python_styleguide.violations.oop import (
    UnpythonicGetterSetterViolation,
)
from wemake_python_styleguide.visitors.ast.classes import WrongClassVisitor

module_getter_and_setter = """
attribute = 1

def get_attribute():
    ...

def set_attribute():
    ...
"""

static_getter_and_setter = """
attribute = 1

class Test(object):
    @staticmethod
    def get_attribute():
        ...

    @staticmethod
    def set_attribute():
        ...
"""

property_getter_and_setter = """
class Test(object):
    def __init__(self):
        self.attribute = 1

    @property
    def get_attribute(self):
        ...

    @property.setter
    def set_attribute(self):
        ...
"""

dataclass_property_getter_setter = """
@dataclass
class DataClass(object):
    attribute: int

    @property
    def get_attribute(self):
        ...

    @property
    def set_attribute(self):
        ...
"""

child_getter_and_setter = """
class TestParent(object):
    def __init__(self):
        self.attribute = 1

class TestChild(TestParent):
    def get_attribute(self):
        ...

    def set_attribute(self):
        ...
"""

nested_getter_and_setter = """
class Template(object):
    def __init__(self):
        self.attribute = 1

    def some_function(self):
        def get_attribute(self):
            ...
        def set_attribute(self):
            ...
        get_attribute(self)
"""

class_attribute_template = """
class Template(object):
    def __init__(self):
        self.{0}

    {1}
    def {2}(self):
        ...
"""

class_mixed = """
class Test(object):
    first: int
    second = 2
    third: int = 3

    def __init__(self):
        self.{0} = 5

    def get_{1}(self):
        ...

    def set_{2}(self):
        ...
"""

class_attribute_instance_getter_setter = """
class Test(object):
    attribute = 1

    def get_attribute(self):
        ...

    def set_attribute(self):
        ...
"""


@pytest.mark.parametrize('code', [
    module_getter_and_setter,
    static_getter_and_setter,
    property_getter_and_setter,
    dataclass_property_getter_setter,
    child_getter_and_setter,
    nested_getter_and_setter,
])
def test_property_getter_and_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    code,
    mode,
):
    """Testing that attribute, getter and setter is allowed outside of class."""
    tree = parse_ast_tree(mode(code))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize(('first', 'second', 'third'), [
    ('attribute = 1', '', 'get_attribute_some'),
    ('attribute = 1', '', 'some_get_attribute'),
    ('attribute = 1', '', 'get_some_attribute'),
    ('attribute = 1', '', 'attribute_get'),
    ('some_attribute = 1', '', 'get_attribute'),
    ('attribute_some = 1', '', 'get_attribute'),
    ('attribute: int = 1', '', 'get_attribute_some'),
    ('attribute: int = 1', '', 'some_get_attribute'),
    ('attribute: int = 1', '', 'get_some_attribute'),
    ('attribute: int = 1', '', 'attribute_get'),
    ('some_attribute: int = 1', '', 'get_attribute'),
    ('attribute_some: int = 1', '', 'get_attribute'),
    ('attribute = self.other = 1', '', 'get_attribute_some'),
    ('attribute = self.other = 1', '', 'some_get_attribute'),
    ('attribute = self.other = 1', '', 'get_some_attribute'),
    ('attribute = self.other = 1', '', 'attribute_get'),
    ('some_attribute = self.other = 1', '', 'get_attribute'),
    ('attribute_some = self.other = 1', '', 'get_attribute'),
    ('attribute, self.other = 1, 2', '', 'get_attribute_some'),
    ('attribute, self.other = 1, 2', '', 'some_get_attribute'),
    ('attribute, self.other = 1, 2', '', 'get_some_attribute'),
    ('attribute, self.other = 1, 2', '', 'attribute_get'),
    ('some_attribute, self.other = 1, 2', '', 'get_attribute'),
    ('attribute_some, self.other = 1, 2', '', 'get_attribute'),
])
def test_nonmatching_attribute_getter_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    first,
    second,
    third,
    mode,
):
    """Testing that non matching attribute and getter/setter is allowed."""
    test_instance = class_attribute_template.format(first, second, third)
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize(('first', 'second', 'third'), [
    ('attribute = 1', '', 'get_attribute'),
    ('_attribute = 1', '', 'get_attribute'),
    ('__attribute = 1', '', 'get_attribute'),
    ('attribute = 1', '@classmethod', 'set_attribute'),
    ('_attribute = 1', '@classmethod', 'set_attribute'),
    ('__attribute= 1', '@classmethod', 'set_attribute'),
])
def test_instance_and_class_getter_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    first,
    second,
    third,
    mode,
):
    """Testing that instance/class attribute and getter/setter is prohibited."""
    test_instance = class_attribute_template.format(first, second, third)
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [UnpythonicGetterSetterViolation])


@pytest.mark.parametrize(('first', 'second', 'third'), [
    ('attribute', 'some', 'other'),
    ('_attribute', 'some', 'other'),
    ('__attribute', 'some', 'other'),
    ('attribute', 'some', 'some'),
    ('_attribute', 'some', 'some'),
    ('__attribute', 'some', 'some'),
])
def test_class_mixed(
    assert_errors,
    parse_ast_tree,
    default_options,
    first,
    second,
    third,
    mode,
):
    """Testing correct use of methods with get/set in name."""
    test_instance = class_mixed.format(first, second, third)
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('code', [
    class_attribute_instance_getter_setter,
])
def test_invalid_getter_and_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    code,
    mode,
):
    """Testing that wrong use of getter/setter is."""
    tree = parse_ast_tree(mode(code))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [UnpythonicGetterSetterViolation])
