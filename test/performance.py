"""
Performance test for csv342.
"""
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import timeit
import tempfile

import csv342 as csv

_TEST_ROW_COUNT = 3000
_TEST_CSV_PATH = os.path.join(tempfile.gettempdir(), 'csv342_performance.csv')
_TEST_ROW = [
    'test',
    '"' * 10,
    1,
    None,
    'a' * 200
] * 20


def _read_and_write_csv():
    has_temp_file = False
    try:
        with io.open(_TEST_CSV_PATH, 'w', encoding='utf-8', newline='') as csv_file:
            has_temp_file = True
            csv_writer = csv.writer(csv_file)
            for _ in range(_TEST_ROW_COUNT):
                csv_writer.writerow(_TEST_ROW)
        with io.open(_TEST_CSV_PATH, 'r', encoding='utf-8', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for _ in csv_reader:
                pass
    finally:
        if has_temp_file:
            os.remove(_TEST_CSV_PATH)


if __name__ == '__main__':
    duration = timeit.timeit('performance._read_and_write_csv()', 'import performance', number=10)
    print('%.2f' % duration)
