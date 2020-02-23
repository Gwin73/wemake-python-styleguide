# -*- coding: utf-8 -*-

import ast
from typing import List, Optional, Tuple

from wemake_python_styleguide import types
from wemake_python_styleguide.compat.aliases import AssignNodes
from wemake_python_styleguide.constants import ALLOWED_BUILTIN_CLASSES
from wemake_python_styleguide.logic import nodes
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
    """Returns all class and instance attributes of a class."""
    class_attributes = []
    instance_attributes = []

    for nd in ast.walk(node):
        if isinstance(nd, ast.Attribute) and isinstance(nd.ctx, ast.Store):
            instance_attributes.append(nd)
            continue

        has_assign = (
            nodes.get_context(nd) == node and
            getattr(nd, 'value', None)
        )
        if isinstance(nd, AssignNodes) and has_assign:
            class_attributes.append(nd)

    return class_attributes, instance_attributes
