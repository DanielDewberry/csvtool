#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CsvTool a tool to make working with CSV files a doddle."""

import argparse
import csv
import logging
import operator
import sys
from itertools import chain
from typing import List


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, **kwargs, file=sys.stdout)  # NoQA: T201


def range_normalizer(ranges: str, ulim: int = 2**128):
    """Harmonise csv string of ranges and produce list of tuples.

    Permissible inputs (where N is an integral value):
        -   all values
        N   N where N is an integer value
        -N  closed range from zero to N
        N-  closed range from N to pseudo-infinity

    Examples:
        '-'         everything
        '-12'       zero to 12
        '1,4,10-20' 1, 4, 10, 11, 12, ..., 20
    """
    ranges = ranges.split(',')
    normalized_sequences = []
    for sequence in ranges:
        atoms = sequence.split('-')
        if len(atoms) == 0:
            continue
        elif len(atoms) == 1:
            if atoms == ['']:
                continue
            else:
                lbound = int(atoms[0])
                ubound = int(atoms[0])
        elif len(atoms) == 2:
            if atoms[0] == '':
                lbound = 0
            else:
                lbound = int(atoms[0])

            if atoms[1] == '':
                ubound = ulim
            else:
                ubound = int(atoms[1])
        else:
            raise ValueError(f'expected 0, 1 or 2. got {len(atoms)}')
        normalized_sequences.append((lbound, ubound))
    normalized_sequences = sorted(normalized_sequences, key=operator.itemgetter(0, 1))

    l1 = len(normalized_sequences) - 1
    l2 = len(normalized_sequences)
    n1 = 0
    while n1 < l1:
        n2 = n1 + 1
        while n2 < l2:
            seq1_0 = normalized_sequences[n1][0]
            seq1_1 = normalized_sequences[n1][1]
            seq2_0 = normalized_sequences[n2][0]
            seq2_1 = normalized_sequences[n2][1]

            modified = False
            if seq1_0 <= seq2_0 and seq1_1 >= seq2_0 - 1:
                normalized_sequences[n1] = (seq1_0, max(seq1_1, seq2_1))
                modified = True

            if modified is True:
                l2 -= 1
                normalized_sequences.pop(n2)
                continue

            n2 += 1
        n1 += 1
    return normalized_sequences


class RangeIterator:
    """Custom Iterator.

    Parameters:
        iterable    something to which to apply the RangeIterator
        sequences   csv string of sequences (seerange_normalize)
        filter_out  False to keep, True to discard

    Example:
        with open('/proc/self/status', 'r') as fp:
            for line in RangeIterator(fp, '1, 3, 5-', False):
                print(line)
    """

    _enumeration = None
    _iter = None
    _iterable = None
    _sequence_item = None
    _sequences = None
    _filter_out = None

    def __init__(self, iterable, sequences, filter_out=False):
        """Construct object."""
        self._filter_out = filter_out
        self._iterable = iterable
        if isinstance(sequences, str):
            self._sequences = range_normalizer(sequences)
        else:
            self._sequences = sequences

    def __iter__(self):
        """Construct iterator."""
        # Iterable
        self._iter = enumerate(self._iterable)

        # Sequencing
        self._generator = chain(*[range(l, u + 1) for (l, u) in self._sequences])
        self._sequence_item = next(self._generator)

        self._end_iter_encountered = False
        self._end_sequence_encountered = False

        return self

    def __next__(self):
        """Increment iterator."""
        self._enumeration = next(self._iter)
        while self._end_iter_encountered is False:
            val = self._enumeration[1]
            if self._enumeration[0] == self._sequence_item:
                try:
                    self._sequence_item = next(self._generator)
                except StopIteration:
                    self._end_sequence_encountered = True

                if self._filter_out is False:
                    return val
            else:
                if self._filter_out is True:
                    return val

            try:
                self._enumeration = next(self._iter)
            except StopIteration:
                self._end_iter_encountered = True

        raise StopIteration


def argparser_factory() -> argparse.ArgumentParser():
    """Create a default argument parser for the application."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        default='/proc/self/fd/0',
                        help='input file (default stdin)')
    parser.add_argument('--output', '-o',
                        default='/proc/self/fd/1',
                        help='Destination to write (default stdout)')
    parser.add_argument('columns',
                        nargs='+',
                        help='The columns to extract')
    parser.add_argument('--named',
                        help='Operate in named column mode. Columns must be a set of integers',
                        action='store_true',
                        default=False)
    parser.add_argument('--new',
                        nargs='+',
                        help='The new column names',
                        default=None)
    parser.add_argument('--filter',
                        help='comma separated filter (filter in) of the form "-a,b,c-d,e-" (default None)',
                        default='-')
    parser.add_argument('--invert-filter',
                        help='invert the filter (default True)',
                        default=False,
                        action='store_true')
    parser.add_argument('--no-print-header',
                        help='do not print the data header (default False)',
                        default=False,
                        action='store_true')
    parser.add_argument('--log-level', '-L',
                        help='Logging level',
                        choices=['debug', 'info', 'warning', 'error', 'critical', 'exception'],
                        default='warning')
    parser.add_argument('--log-root',
                        help='Attach the logging handler to the root logger instead of the application logger (default False)',  # NoQA: E501
                        default=False,
                        action='store_true')
    return parser


def main(*,
         logger: logging.Logger,
         filename_input: str,
         filename_output: str,
         column_names: List[str],
         new_columns: List[str],
         named_mode: bool,
         row_filter: str,
         filter_inversion: bool,
         print_header: bool):
    """Entrypoint."""
    with open(filename_input, 'r') as fp_input, open(filename_output, 'w') as fp_output:
        reader = csv.reader(RangeIterator(fp_input, row_filter, filter_inversion))

        writer = csv.writer(fp_output, quoting=csv.QUOTE_NONNUMERIC)

        headers = next(reader)
        header_length = len(headers)
        logger.info('Header has %s columns', header_length)
        histogram = {}
        histogram[header_length] = header_length

        if named_mode is True:
            missing = []
            for column in column_names:
                if column not in headers:
                    missing.append(column)
            if len(missing) > 0:
                logger.error('CSV file header does not contain %s of %s keys: %s',
                             len(column_names),
                             len(missing),
                             ', '.join([f'"{m}"' for m in missing]),
                             )
                sys.exit(1)
            columns = [(k, headers.index(k)) for k in column_names]
        else:
            columns = column_names
            column_names = [headers[column] for column in columns]
            columns = [(headers[column], column) for column in columns]
        logger.warning('Working on columns: %s', str(columns))

        max_header_element = max([x[1] for x in columns])

        if print_header is True:
            if new_columns is not None:
                writer.writerow(new_columns)
            else:
                writer.writerow(column_names)

        for n, line in enumerate(reader, 1):
            length = len(line)
            if max_header_element > length - 1:
                logger.error(f'Bounds error on line {n}')
            histogram[length] = histogram.get(length, 0) + 1
            if length != header_length:
                logger.warn(f'Warning: line[{n}] width ({length}) different to header width ({header_length})')
            st = [line[column_index] for column_name, column_index in columns]
            writer.writerow(st)

    # Summary diagnostics
    if len(histogram) != 1:
        logger.warn('Line size histogram shows there were %s line lengths', len(histogram))


def log_level_from_string(level_string: str, ignore_case: bool = False) -> int:
    """Convert a logging level from a string to the corresponding int."""
    level_string = level_string.lower()
    if level_string == 'debug':
        return logging.DEBUG
    elif level_string == 'info':
        return logging.INFO
    elif level_string == 'warning':
        return logging.WARNING
    elif level_string == 'error':
        return logging.ERROR
    elif level_string == 'critical':
        return logging.CRITICAL
    raise ValueError('Unknown logging level')


if __name__ == '__main__':
    logger = logging.getLogger('csv-tool')
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    parser = argparser_factory()
    args = parser.parse_args()

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logging_level = log_level_from_string(args.log_level)
    logger.setLevel(logging_level)
    ch.setLevel(logging_level)

    if args.log_root is True:
        logging.getLogger('').addHandler(ch)
    else:
        logger.addHandler(ch)

    if args.input == '-':
        args.input = '/proc/self/fd/0'
    if args.named is False:
        args.columns = [int(i) for i in args.columns]

    if args.new is not None and len(args.new) != len(args.columns):
        logger.error(f'there are {len(args.new)} new names but {len(args.columns)}')
        sys.exit(1)

    try:
        main(logger=logger,
             filename_input=args.input,
             filename_output=args.output,
             column_names=args.columns,
             new_columns=args.new,
             named_mode=args.named,
             row_filter=args.filter,
             filter_inversion=args.invert_filter,
             print_header=not args.no_print_header)
    except BrokenPipeError:
        sys.exit(0)

    sys.exit(0)
