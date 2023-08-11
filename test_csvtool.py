#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test suite for csvtool."""

import logging

from csvtool import (
    RangeIterator,
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


def test_version_major():
    """Test the application version:major."""
    assert version.major == 0


def test_version_minor():
    """Test the application version:minor."""
    assert version.minor == 1


def test_version_patch():
    """Test the application version:patch."""
    assert version.patch == 0
