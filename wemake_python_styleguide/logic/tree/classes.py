# -*- coding: utf-8 -*-

import ast
from typing import List, Optional, Set, Tuple, Union

from wemake_python_styleguide import types
from wemake_python_styleguide.compat.aliases import AssignNodes, FunctionNodes
from wemake_python_styleguide.constants import ALLOWED_BUILTIN_CLASSES
from wemake_python_styleguide.logic import nodes, source
from wemake_python_styleguide.logic.naming.builtins import is_builtin_name


def is_forbidden_super_class(class_name: Optional[str]) -> bool:
    """
    Tells whether or not the base class is forbidden to be subclassed.

    >>> is_forbidden_super_class('str')
    True

    >>> is_forbidden_super_class('Exception')
    False

    >>> is_forbidden_super_class('object')
    False

    >>> is_forbidden_super_class('type')
    False

    >>> is_forbidden_super_class('CustomName')
    False

    >>> is_forbidden_super_class(None)
    False

    """
    if not class_name or not class_name.islower():
        return False
    if class_name in ALLOWED_BUILTIN_CLASSES:
        return False
    return is_builtin_name(class_name)


def get_attributes(
    node: ast.ClassDef,
) -> Tuple[List[types.AnyAssign], List[ast.Attribute]]:
    """Returns all non annotated class and instance attributes of a class."""
    return get_class_attributes(node), get_instance_attributes(node)


def get_all_attributes(
    node: ast.ClassDef,
) -> Tuple[List[types.AnyAssign], List[ast.Attribute]]:
    """Returns all class and instance attributes of a class."""
    return get_all_class_attributes(node), get_instance_attributes(node)


def get_class_attributes(
    node: ast.ClassDef,
) -> List[Union[ast.Assign, ast.AnnAssign]]:
    """Returns all non annotated class attributes of a class."""
    class_attributes = []
    for sub in ast.walk(node):
        correct_context = nodes.get_context(sub) == node
        has_value = getattr(sub, 'value', None)
        if isinstance(sub, AssignNodes) and has_value and correct_context:
            class_attributes.append(sub)

    return class_attributes


def get_all_class_attributes(
    node: ast.ClassDef,
) -> List[Union[ast.Assign, ast.AnnAssign]]:
    """Returns all class attributes of a class."""
    class_attributes = []
    for sub in ast.walk(node):
        correct_context = nodes.get_context(sub) == node
        has_value = getattr(sub, 'value', None)
        if isinstance(sub, AssignNodes) and has_value and correct_context:
            class_attributes.append(sub)
            continue
        if isinstance(sub, ast.AnnAssign) and correct_context:
            class_attributes.append(sub)

    return class_attributes


def get_instance_attributes(node: ast.ClassDef) -> List[ast.Attribute]:
    """Returns all instance attributes of a class."""
    instance_attributes = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and isinstance(sub.ctx, ast.Store):
            instance_attributes.append(sub)
    return instance_attributes

def get_set_postfixes(node: ast.ClassDef) -> Tuple[Set[str], Set[str]]:
    """
    Return postfixes of class getter or setter methods.

    get_class_attribute becomes class_attribute

    set_instance_attribute becomes instance_attribute

    """
    class_method_postfixes = set()
    instance_method_postfixes = set()
    for sub in ast.walk(node):
        correct_context = nodes.get_context(sub) == node
        if isinstance(sub, FunctionNodes) and correct_context and is_getter_setter(sub):
            if check_decorator(sub, 'classmethod'):
                class_method_postfixes.add(sub.name.partition('get_')[2])
                class_method_postfixes.add(sub.name.partition('set_')[2])
                continue
            instance_method_postfixes.add(sub.name.partition('get_')[2])
            instance_method_postfixes.add(sub.name.partition('set_')[2])

    return class_method_postfixes, instance_method_postfixes


def is_getter_setter(node: types.AnyFunctionDef) -> bool:
    """Check if name of node startswith `get_` or `set_`."""
    return any(node.name.startswith(prefix) for prefix in ('get_', 'set_'))


def check_decorator(node: types.AnyFunctionDef, name: str) -> bool:
    """Check if name is in decorator name."""
    return any(
        name == source.node_to_string(decorator)
        for decorator in node.decorator_list
    )
