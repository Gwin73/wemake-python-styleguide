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
    asd: int

    @property
    def get_asd(self):
        ...

    @property
    def set_asd(self):
        ...
"""

dataclass_getter_setter = """
@dataclass
class DataClass(object):
    asd: int

    def get_asd(self):
        ...

    def set_asd(self):
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

instance_attribute_template = """
class Template(object):
    def __init__(self):
        self.{0}{1}{2}

    {3}
    def {4}(self):
        ...
"""

class_attribute_template = """
class Template(object):
    {0}{1}

    {2}
    def {3}:
        ...
"""

class_mixed = """
class Test(object):
    first: int
    second = 2
    third: int = 3

    def __init__(self):
        self.{0}{1} = 5

    def get_{2}(self):
        ...

    def set_{3}(self):
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


@pytest.mark.parametrize('access', ['', '_', '__'])
@pytest.mark.parametrize('assignment', [
    ' = 1',
    ': int = 1',
    ' = self.other = 1',
    ', self.other = 1, 2',
])
@pytest.mark.parametrize(('attribute_name', 'annotation', 'method_name'), [
    ('attribute', '', 'get_attribute_some'),
    ('attribute', '', 'some_get_attribute'),
    ('attribute', '', 'get_some_attribute'),
    ('attribute', '', 'attribute_get'),
    ('some_attribute', '', 'get_attribute'),
    ('attribute_some', '', 'get_attribute'),
])
def test_nonmatching_attribute_getter_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    access,
    assignment,
    attribute_name,
    annotation,
    method_name,
    mode,
):
    """Testing that non matching attribute and getter/setter is allowed."""
    test_instance = instance_attribute_template.format(
        access, attribute_name, assignment, annotation, method_name,
    )
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('access', ['', '_', '__'])
@pytest.mark.parametrize('assignment', [
    ' = 1',
    ': int = 1',
    ' = self.other = 1',
    ', self.other = 1, 2',
])
@pytest.mark.parametrize(('attribute_name', 'annotation', 'method_name'), [
    ('attribute', '', 'get_attribute'),
    ('attribute', '@classmethod', 'set_attribute'),
    ('_attribute', '@classmethod', 'set_attribute'),
    ('__attribute', '@classmethod', 'set_attribute'),
    ('attribute', '@property', 'get_attribute'),
    ('_attribute', '@property', 'get_attribute'),
    ('__attribute', '@property', 'get_attribute'),
    ('attribute', '@attribute.setter', 'set_attribute'),
    ('_attribute', '@attribute.setter', 'set_attribute'),
    ('__attribute', '@attribute.setter', 'set_attribute'),
])
def test_instance_and_class_getter_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    access,
    assignment,
    attribute_name,
    annotation,
    method_name,
    mode,
):
    """Testing that class attribute and getter/setter is prohibited."""
    test_instance = instance_attribute_template.format(
        access, attribute_name, assignment, annotation, method_name,
    )
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [UnpythonicGetterSetterViolation])


@pytest.mark.parametrize('access', ['', '_', '__'])
@pytest.mark.parametrize(('first', 'second', 'third'), [
    ('attribute', 'some', 'other'),
    ('attribute', 'some', 'some'),
])
def test_class_mixed(
    assert_errors,
    parse_ast_tree,
    default_options,
    access,
    first,
    second,
    third,
    mode,
):
    """Testing correct use of methods with get/set in name."""
    test_instance = class_mixed.format(access, first, second, third)
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])


@pytest.mark.parametrize('code', [
    class_attribute_instance_getter_setter,
    dataclass_getter_setter,
    property_getter_and_setter,
    dataclass_property_getter_setter,
])
def test_invalid_getter_and_setter(
    assert_errors,
    parse_ast_tree,
    default_options,
    code,
    mode,
):
    """Testing that wrong use of getter/setter is prohibited."""
    tree = parse_ast_tree(mode(code))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [UnpythonicGetterSetterViolation])


@pytest.mark.parametrize(('attribute_name', 'annotation', 'method_name'), [
    ('attribute', '', 'get_attribute()'),
    ('attribute', '', 'get_attribute(self)'),
    ('attribute', '@classmethod', 'get_attribute(self)'),

    ('attribute', '', 'set_attribute()'),
    ('attribute', '', 'set_attribute(self)'),
    ('attribute', '@classmethod', 'set_attribute(self)'),
])
@pytest.mark.parametrize('assignment', [
    ' = 1',
    ': int = 1',
    ' = other = 1',
    ', other = 1, 2',
])
def test_class_attributes_getter_setters(
    assert_errors,
    parse_ast_tree,
    default_options,
    attribute_name,
    annotation,
    method_name,
    assignment,
    mode,
):
    """Testing that using getter/setters with class attributes is prohibited."""
    test_instance = class_attribute_template.format(
        attribute_name, assignment, annotation, method_name,
    )
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [UnpythonicGetterSetterViolation])


@pytest.mark.parametrize(('attribute_name', 'annotation', 'method_name'), [
    ('attribute', '', 'get_attribute_some()'),
    ('attribute', '', 'some_get_attribute()'),
    ('attribute', '', 'get_some_attribute()'),
    ('attribute', '', 'attribute_get()'),
    ('some_attribute', '', 'get_attribute()'),
    ('attribute_some', '', 'get_attribute()'),

    ('attribute', '', 'get_attribute_some(self)'),
    ('attribute', '', 'some_get_attribute(self)'),
    ('attribute', '', 'get_some_attribute(self)'),
    ('attribute', '', 'attribute_get(self)'),
    ('some_attribute', '', 'get_attribute(self)'),
    ('attribute_some', '', 'get_attribute(self)'),

    ('attribute', '@classmethod', 'get_attribute_some(self)'),
    ('attribute', '@classmethod', 'some_get_attribute(self)'),
    ('attribute', '@classmethod', 'get_some_attribute(self)'),
    ('attribute', '@classmethod', 'attribute_get(self)'),
    ('some_attribute', '@classmethod', 'get_attribute(self)'),
    ('attribute_some', '@classmethod', 'get_attribute(self)'),
])
@pytest.mark.parametrize('assignment', [
    ' = 1',
    ': int = 1',
    ' = other = 1',
    ', other = 1, 2',
])
def test_nonmatching_class_attributes(
    assert_errors,
    parse_ast_tree,
    default_options,
    attribute_name,
    annotation,
    method_name,
    assignment,
    mode,
):
    """Testing that nonmatching class attribute and getter/setter is allowed."""
    test_instance = class_attribute_template.format(
        attribute_name, assignment, annotation, method_name,
    )
    tree = parse_ast_tree(mode(test_instance))

    visitor = WrongClassVisitor(default_options, tree=tree)
    visitor.run()

    assert_errors(visitor, [])
