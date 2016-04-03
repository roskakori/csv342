# -*- coding: utf-8 -*-
"""
Tests for loxun.
"""
# Copyright (C) 2010-2011 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Allow "with" statement to be used in tests even for Python 2.5

from __future__ import unicode_literals
from __future__ import with_statement

import io
import os
import unittest

import csv342 as csv


class Csv342Test(unittest.TestCase):
    _TEST_FOLDER = os.path.dirname(__file__)

    def _test_path(self, name, must_exist=True):
        assert name is not None
        result = os.path.join(Csv342Test._TEST_FOLDER, name + '.csv')
        if must_exist:
            self.assertTrue(os.path.exists(result), 'test file must exist: {0}'.format(result))
        return result

    def _open(self, name, encoding='utf-8'):
        assert name is not None
        return io.open(self._test_path(name), encoding=encoding, newline='')

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
        self._assert_data_match('quoted', [['a', 'a', '"a"', u'\na']])

    def test_can_read_cp1252(self):
        self._assert_data_match('cp1252', [['\u20ac']], encoding='cp1252')

    def test_can_read_utf8(self):
        self._assert_data_match('utf-8', [['\u20ac']], encoding='utf-8')

    def test_fails_on_non_ascii_characters_with_ascii_encoding(self):
        self.assertRaises(UnicodeDecodeError, self._data, 'cp1252', encoding='ascii')
        self.assertRaises(UnicodeDecodeError, self._data, 'utf-8', encoding='ascii')


if __name__ == "__main__": # pragma: no cover
    unittest.main()
