File Deuper
===========
Copyright (c) 2014, Christopher Speck 
See LICENSE for license information and copyright.

Installing & Running
--------------------
Setup:
 mkvirtualenv deduper
 pip install -e .

To scan:
 deduper -s

To remove files:
 deduper -d graphical (will display images)
 deduper -d cli (will give you a cursors dialog)
 deduper -d auto (will choose for you)

This will by default hardlink duplicates to the selected keeper file.

Run without arguements to see all options.

Running the tests
-----------------
pip install -r requirements-dev.txt
py.test