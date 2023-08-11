#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test suite for csvtool."""

import logging
import operator

from csvtool import (
    RangeIterator,
    Version,
    log_level_from_string,
    range_normalizer,
    version,
)

import pytest


@pytest.mark.parametrize('test_input,expected',
                         [('0', [(0, 0)]),
                          ('-', [(0, 2**128)]),
                          ('-,-', [(0, 2**128)]),
                          ('0,1', [(0, 1)]),
                          ('-4', [(0, 4)]),
                          ('4-', [(4, 2**128)]),
                          ('-4,6,8,10-', [(0, 4), (6, 6), (8, 8), (10, 2**128)]),
                          ('-4,6-8,7-11,10-', [(0, 4), (6, 2**128)]),
                          ])
def test_range_skipper(test_input, expected):
    """Test a variety of inputs to validate range_skipper."""
    assert range_normalizer(test_input) == expected


@pytest.mark.parametrize('test_input,expected',
                         [((range(0, 1), '0', False), [0]),
                          ((range(0, 1), '0', True), []),
                          ((range(0, 2), '0', False), [0]),
                          ((range(0, 2), '0', True), [1]),
                          ((range(0, 2), '1', False), [1]),
                          ((range(0, 2), '1', True), [0]),
                          ((range(0, 3), '0', False), [0]),
                          ((range(0, 3), '1', False), [1]),
                          ((range(0, 3), '2', False), [2]),
                          ((range(0, 3), '0', True), [1, 2]),
                          ((range(0, 3), '1', True), [0, 2]),
                          ((range(0, 3), '2', True), [0, 1]),
                          ((range(0, 3), '-', False), [0, 1, 2]),
                          ((range(0, 3), '-', True), []),
                          ((range(0, 3), '-1', False), [0, 1]),
                          ((range(0, 3), '-1', True), [2]),
                          ((range(0, 3), '1-', False), [1, 2]),
                          ((range(0, 3), '1-', True), [0]),
                          ((range(0, 10), '0,2-4,8-', False), [0, 2, 3, 4, 8, 9]),
                          ((range(0, 10), '0,2-4,8-', True), [1, 5, 6, 7]),
                          ((range(0, 9), '0,2-4,8', False), [0, 2, 3, 4, 8]),
                          ((range(0, 9), '0,2-4,8', True), [1, 5, 6, 7]),
                          ])
def test_range_filter(test_input, expected):
    """Test a variety of inputs to validate RangeIterator."""
    assert [*RangeIterator(*test_input)] == expected


# +---+-----+
# | I | R   |
# +---+-----+
# | 0 | 0   |
# | 1 | -   |
# | 2 | 2   |
# | 3 | 3   |
# | 4 | 4   |
# | 5 | -   |
# | 6 | -   |
# | 7 | -   |
# | 8 | 8   |
# | 9 | 9   |
# | - | 10  |
# | - | ... |
# | - | ... |


@pytest.mark.parametrize('test_input,expected',
                         [('debug', logging.DEBUG),
                          ('info', logging.INFO),
                          ('warning', logging.WARNING),
                          ('error', logging.ERROR),
                          ('critical', logging.CRITICAL),
                          ])
def test_log_level_from_string_case_sensitive__valid(test_input, expected):
    """Test a variety of valid inputs to log_level_from_string."""
    assert log_level_from_string(test_input) == expected


@pytest.mark.parametrize('test_input,expected',
                         [('Debug', logging.DEBUG),
                          ('iNfo', logging.INFO),
                          ('waRning', logging.WARNING),
                          ('errOr', logging.ERROR),
                          ('critIcal', logging.CRITICAL),
                          ])
def test_log_level_from_string_case_insensitive__valid(test_input, expected):
    """Test a variety of valid inputs to log_level_from_string."""
    assert log_level_from_string(test_input) == expected


@pytest.mark.parametrize('test_input',
                         [('nonsense'),
                          ])
def test_log_level_from_string_case_sensitive__invalid(test_input):
    """Test a variety of valid inputs to log_level_from_string."""
    with pytest.raises(ValueError):
        assert log_level_from_string(test_input)


@pytest.mark.parametrize('test_input',
                         [('Nonsense'),
                          ])
def test_log_level_from_string_case_insensitive__invalid(test_input):
    """Test a variety of valid inputs to log_level_from_string."""
    with pytest.raises(ValueError):
        assert log_level_from_string(test_input)


@pytest.mark.parametrize('test_input',
                         [(0, 0, 0),
                          (1, 0, 0),
                          (0, 1, 0),
                          (0, 0, 1),
                          ])
def test_version_class_inputs(test_input):
    """Test the Version object constructs and the members are accessible."""
    version = Version(*test_input)
    assert version.major == test_input[0]
    assert version.minor == test_input[1]
    assert version.patch == test_input[2]


def generate_paramtrized_data(op):
    """Generate a tuple of two integer-tripplets and an operator comparison result."""
    tests = []
    base = 10000
    r = 2
    for i1 in range(r):
        for i2 in range(r):
            for i3 in range(r):
                for i4 in range(r):
                    for i5 in range(r):
                        for i6 in range(r):
                            a = i1 * base**2 + i2 * base + i3
                            b = i4 * base**2 + i5 * base + i6
                            tests.append(((i1, i2, i3), (i4, i5, i6), op(a, b)))
    return tests


@pytest.mark.parametrize('test_input1,test_input2,expected',
                         generate_paramtrized_data(operator.eq))
def test_version_class_eq(test_input1, test_input2, expected):
    """Test Version equality operator."""
    version_lhs = Version(*test_input1)
    version_rhs = Version(*test_input2)
    assert (version_lhs == version_rhs) is expected


@pytest.mark.parametrize('test_input1,test_input2,expected',
                         generate_paramtrized_data(operator.lt))
def test_version_class_lt(test_input1, test_input2, expected):
    """Test Version less than operator."""
    version_lhs = Version(*test_input1)
    version_rhs = Version(*test_input2)
    assert (version_lhs < version_rhs) is expected


@pytest.mark.parametrize('test_input1,test_input2,expected',
                         generate_paramtrized_data(operator.gt))
def test_version_class_gt(test_input1, test_input2, expected):
    """Test Version greater than operator."""
    version_lhs = Version(*test_input1)
    version_rhs = Version(*test_input2)
    assert (version_lhs > version_rhs) is expected


@pytest.mark.parametrize('test_input1,test_input2,expected',
                         generate_paramtrized_data(operator.le))
def test_version_class_le(test_input1, test_input2, expected):
    """Test Version less than or equal operator."""
    version_lhs = Version(*test_input1)
    version_rhs = Version(*test_input2)
    assert (version_lhs <= version_rhs) is expected


@pytest.mark.parametrize('test_input1,test_input2,expected',
                         generate_paramtrized_data(operator.ge))
def test_version_class_ge(test_input1, test_input2, expected):
    """Test Version greater than or equal operator."""
    version_lhs = Version(*test_input1)
    version_rhs = Version(*test_input2)
    assert (version_lhs >= version_rhs) is expected


@pytest.mark.parametrize('test_input,expected',
                         [((0, 0, 0), '0.0.0'),
                          ])
def test_version_class_str(test_input, expected):
    """Test str(Version) yields correct result."""
    assert str(Version(*test_input)) == expected


def test_version_major():
    """Test the application version:major."""
    assert version.major == 0


def test_version_minor():
    """Test the application version:minor."""
    assert version.minor == 6


def test_version_patch():
    """Test the application version:patch."""
    assert version.patch == 0
