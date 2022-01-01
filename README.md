# dirsToHtml

A python program that creates a html documents that allows navigating local directory structure and the containing files.

# Description
This program attempts to do the following:
Traverses a directory structure on the disk and creates a html document (default file name index.html) linking to the files found inside these folders. The overall aim is to make a directory structure traversable via Web-links and make browsing easier.

The general idea is to offer an convenient way to browse the directory/files

Some command line arguments (not yet exahaustive):

-d [directory] : directory to start traversing

-o [output file]: file to write html into

-c : color cycling (random) of directory names at each level

-s [css file]: Style sheet to use (default is style.css)

...and others. Sorry, no time to fully complete the list.

-v0.65b@20022021
For comments/improvements please contact: tzagara@upatras.gr

This has been developed in about 2 days. I apologize for any error, bad design decision or omission. Such problems are exclusively mine.
