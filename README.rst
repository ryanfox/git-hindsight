Look at your git repo in hindsight.

Usage
=====

    (on the command line)
    
    $ git log --numstat > gitlog.txt

    (in python)
    
    >>> from hindsight import *
    
    >>> repo = Repo('gitlog.txt')
    >>> repo.plotfileloc('foo.py')
    
    >>> from datetime import datetime
    >>> repo.plotrepoloc(after=datetime(2013, 1, 10))


Planned functionality
=====================

    -View graphs of your codebase over time:
        
        Change in file count
        Biggest files
        Biggest/smallest commits
        Mean/median/mode commit size
        Commit frequency
    
    -Most prolific committers
    
    -Who added/deleted the most lines
    
    -Histogram of commits (both number of files touched and LOC changed)

    -Refactor to use object-oriented matplotlib plotting pattern
