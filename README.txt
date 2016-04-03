csv342
======

csv342 is a Python module similar to the the csv module in the standard
library. Under Python 3, it just calls the standard csv module. Under
Python 2, it provides a Python 3 like interface to reading and writing CSV
files, in particular concerning non ASCII characters.

It is distributed under the BSD license with the source code available from
https://github.com/roskakori/csv342.

Example
-------

Once you import csv342 as

>>> import csv342 as csv

your code can call CSV functions the same independent whether it runs under
Python 2 or 3. In particular, you can no process UTF-8 encoded CSV files
with non ASCII characters using:

>>> import io
>>> import os.path
>>> csv_path = os.path.join('test', 'utf-8.csv')
>>> with io.open(csv_path, encoding='utf-8', newline='') as csv_file:
>>>     csv_reader = csv.reader(csv_file, delimiter=',')
>>>     for row in csv_reader:
>>>         print('row {0:d}: data={1}'.format(csv_reader.line_num, row))

Limitations
-----------
* All limitations of the standard csv module apply.
* Requires Python 2.5+.

License
-------

Copyright (c) 2016, Thomas Aglassinger
All rights reserved.

Distributed under the BSD License. For more information, see LICENSE.txt.


Version history
===============

Version 0.1, 2016-04-xx

* Initial release.
