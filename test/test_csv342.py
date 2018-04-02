# -*- coding: utf-8 -*-
"""
Tests for csv342.
"""
# Copyright (c) 2016-2018, Thomas Aglassinger
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of csv342 nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Allow "with" statement to be used in tests even for Python 2.5

from __future__ import unicode_literals
from __future__ import with_statement

import doctest
import io
import os
import unittest
from contextlib import closing

import csv342 as csv


class _CsvTest(unittest.TestCase):
    _TEST_FOLDER = os.path.dirname(__file__)

    def _test_path(self, name, must_exist=True):
        assert name is not None
        result = os.path.join(_CsvTest._TEST_FOLDER, name + '.csv')
        if must_exist:
            self.assertTrue(os.path.exists(result), 'test file must exist: {0}'.format(result))
        return result

    def _open(self, name, encoding='utf-8'):
        assert name is not None
        return io.open(self._test_path(name), encoding=encoding, newline='')


class ReaderTest(_CsvTest):
    def _data(self, name, delimiter=',', encoding='utf-8'):
        with self._open(name, encoding=encoding) as csv_file:
            result = list(csv.reader(csv_file, delimiter=delimiter))
        return result

    def _assert_data_match(self, name, expected_data, delimiter=',', encoding='utf-8'):
        data_path = self._test_path(name)
        actual_data = self._data(name, delimiter=delimiter, encoding=encoding)
        self.assertEqual(
            actual_data, expected_data,
            'data read from "{0}" must match: {1} != {2}'.format(
                data_path, actual_data, expected_data))

    def test_can_read_quoted_csv(self):
        self._assert_data_match('quoted', [['a', 'a', '"a"', '\na']])

    def test_can_read_cp1252(self):
        self._assert_data_match('cp1252', [['\u20ac']], encoding='cp1252')

    def test_can_read_utf8(self):
        self._assert_data_match('utf-8', [['\u20ac']], encoding='utf-8')

    def test_fails_on_non_ascii_characters_with_ascii_encoding(self):
        self.assertRaises(UnicodeDecodeError, self._data, 'cp1252', encoding='ascii')
        self.assertRaises(UnicodeDecodeError, self._data, 'utf-8', encoding='ascii')

    def test_can_read_from_StringIO(self):
        with io.StringIO('ä,b\nc') as csv_stream:
            csv_reader = csv.reader(csv_stream, delimiter=',')
            actual_rows = list(csv_reader)
        self.assertEqual([['ä', 'b'], ['c']], actual_rows)

    def test_fails_on_obsolete_StringIO(self):
        if csv.IS_PYTHON2:
            import StringIO
            with closing(StringIO.StringIO('a')) as csv_stream:
                self.assertRaises(csv.Error, csv.reader, csv_stream)


class ExamplesText(_CsvTest):
    # FIXME: For some reason, the test code causes EOF errors when indented.
    def _test_can_doctest_readme(self):
        project_folder = os.path.dirname(_CsvTest._TEST_FOLDER)
        readme_path = os.path.join(project_folder, 'README.rst')
        doctest.testfile(readme_path, module_relative=False)


class WriterTest(_CsvTest):
    def test_can_write_to_StringIO(self):
        with io.StringIO(newline='') as csv_stream:
            csv_writer = csv.writer(csv_stream, delimiter=',')
            csv_writer.writerows([
                ['ä', 'b', 'c'],
                [],
                [1, None, 3]
            ])
            self.assertEqual(
                '\xe4,b,c\r\n\r\n1,,3\r\n',
                csv_stream.getvalue())


class DictReaderTest(unittest.TestCase):
    def test_can_read_using_specific_fieldnames(self):
        lines_to_read = 'a,b,c\nx,yy,zzz\n,y\n'
        expected_data = [
            {'a': 'x', 'b': 'yy', 'c': 'zzz'},
            {'a': '', 'b': 'y', 'c': None},
        ]
        with io.StringIO(lines_to_read) as csv_file:
            names_to_values = list(csv.DictReader(csv_file, delimiter=','))
        self.assertEqual(expected_data, names_to_values)

    def test_can_skip_empty_rows(self):
        lines_to_read = 'a\n1\n\n2\n'
        expected_data = [
            {'a': '1'},
            {'a': '2'},
        ]
        with io.StringIO(lines_to_read) as csv_file:
            names_to_values = list(csv.DictReader(csv_file, delimiter=','))
        self.assertEqual(expected_data, names_to_values)

    def test_can_use_specified_fieldnames(self):
        lines_to_read = '1,2\n3,4'
        expected_data = [
            {'a': '1', 'b': '2'},
            {'a': '3', 'b': '4'},
        ]
        with io.StringIO(lines_to_read) as csv_file:
            names_to_values = list(csv.DictReader(csv_file, delimiter=',', fieldnames=['a', 'b']))
        self.assertEqual(expected_data, names_to_values)

    def test_can_read_from_list(self):
        lines_to_read = 'a,b\n1,2'.splitlines()
        expected_data = [
            {'a': '1', 'b': '2'}
        ]
        names_to_values = list(csv.DictReader(lines_to_read, delimiter=','))
        self.assertEqual(expected_data, names_to_values)

    def test_can_read_from_empty_list(self):
        names_to_values = list(csv.DictReader([]))
        self.assertEqual([], names_to_values)


class DictWriterTest(_CsvTest):
    def test_can_write(self):
        with io.StringIO() as csv_stream:
            csv_writer = csv.DictWriter(csv_stream, ['name', 'size', 'nothing', 'date_of_birth'])
            data = {
                'name': 'Alice',
                'size': 167.5,
                'nothing': None,
                'date_of_birth': '1983-11-27',
            }
            csv_writer.writeheader()
            csv_writer.writerow(data)
            content = csv_stream.getvalue().replace('\r\n', '\n').replace('\r', '\n')
        self.assertEqual(
            'name,size,nothing,date_of_birth\nAlice,167.5,,1983-11-27\n',
            content)


if __name__ == "__main__": # pragma: no cover
    unittest.main()
