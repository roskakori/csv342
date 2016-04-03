"""
csv342 is a Python module similar to the the csv module in the standard
library. Under Python 3, it just calls the standard csv module. Under
Python 2, it provides a Python 3 like interface to reading and writing CSV
files, in particular concerning non ASCII characters.

It is distributed under the BSD license with the source code available from
https://github.com/roskakori/csv342.
"""
# Copyright (c) 2016, Thomas Aglassinger
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
from __future__ import unicode_literals

import sys

__version__ = "0.1"


# Compatibility helpers for Python 2 and 3.
if sys.version_info[0] != 2:
    IS_PYTHON2 = False
    from csv import *
else:
    IS_PYTHON2 = False
    _binary_type = str
    _text_type = unicode

    # Read and write CSV using Python 2.6+.
    import csv
    import io

    def _key_to_str_value_map(key_to_value_map):
        """
        Similar to ``key_to_value_map`` but with values of type `unicode`
        converted to `str` because in Python 2 `csv.reader` can only process
        byte strings for formatting parameters, e.g. delimiter=b';' instead of
        delimiter=u';'. This quickly becomes an annoyance to the caller, in
        particular with `from __future__ import unicode_literals` enabled.
        """
        return dict((key, value if not isinstance(value, _text_type) else _binary_type(value))
                    for key, value in key_to_value_map.items())

    class _UnicodeCsvWriter(object):
        r"""
        A CSV writer for Python 2 which will write rows to `target_stream`
        which must be able to write unicode strings.

        To obtain a target stream for a file use for example (note the
        ``newline=''``):

        >>> import io
        >>> import os
        >>> import tempfile
        >>> target_path = os.path.join(tempfile.tempdir, 'test_csv342.UnicodeCsvWriter.csv')
        >>> target_stream = io.open(target_path, 'w', newline='', encoding='utf-8')

        This is based on ``UnicodeWriter`` from <https://docs.python.org/2/library/csv.html> but expects the
        target to accept unicode strings.
        """

        def __init__(self, target_stream, dialect=csv.excel, **keywords):
            self._target_stream = target_stream
            self._queue = io.BytesIO()
            str_keywords = _key_to_str_value_map(keywords)
            self._csv_writer = csv.writer(self._queue, dialect=dialect, **str_keywords)

        def writerow(self, row):
            assert row is not None

            row_as_list = list(row)
            # Convert ``row`` to a list of unicode strings.
            row_to_write = []
            for item in row_as_list:
                if item is None:
                    item = ''
                elif not isinstance(item, _text_type):
                    item = _text_type(item)
                row_to_write.append(item.encode('utf-8'))
            try:
                self._csv_writer.writerow(row_to_write)
            except TypeError as error:
                raise TypeError('%s: %s' % (error, row_as_list))
            data = self._queue.getvalue()
            data = data.decode('utf-8')
            self._target_stream.write(data)
            # Clear the BytesIO before writing the next row.
            self._queue.seek(0)
            self._queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)

    class _Utf8Recoder(object):
        """
        Iterator that reads a text stream and reencodes the input to UTF-8.
        """
        def __init__(self, text_stream):
            self._text_stream = text_stream

        def __iter__(self):
            return self

        def __next__(self):
            return self._text_stream.next().encode('utf-8')

        def next(self):
            return self.__next__()

    class _UnicodeCsvReader(object):
        """
        A CSV reader which will iterate over lines in the CSV file 'csv_file',
        which is encoded in the given encoding.
        """

        def __init__(self, csv_file, dialect=csv.excel, **keywords):
            csv_file = _Utf8Recoder(csv_file)
            str_keywords = _key_to_str_value_map(keywords)
            self.reader = csv.reader(csv_file, dialect=dialect, **str_keywords)
            self.line_num = -1

        def __next__(self):
            self.line_num += 1
            row = self.reader.next()
            result = [item.decode('utf-8') for item in row]
            return result

        def next(self):
            return self.__next__()

        def __iter__(self):
            return self


    def reader(source_text_stream, dialect=csv.excel, **keywords):
        """
        Same as Python 3's `csv.reader` but works with Python 2.
        """
        assert source_text_stream is not None

        return _UnicodeCsvReader(source_text_stream, dialect=dialect, **keywords)


    def writer(target_text_stream, dialect=csv.excel, **keywords):
        """
        Same as Python 3's `csv.writer` but works with Python 2.
        """
        assert target_text_stream is not None

        return _UnicodeCsvWriter(target_text_stream, dialect=dialect, **keywords)


if __name__ == '__main__':
    if IS_PYTHON2:  # Doctests only work with Python 2 due u'...' prefix mess.
        import doctest
        print('csv342 {0}: running doctest'.format(__version__))
        doctest.testmod()
