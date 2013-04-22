Look at your git repo in hindsight.

Usage
=====

    (on the command line)
    
    $ git log --numstat > gitlog.txt

    (in python)
    
    >>> from hindsight import Repo
    
    >>> repo = Repo('gitlog.txt')
    >>> repo.plotfileloc('foo.py')
    
    >>> from datetime import datetime
    >>> repo.plotrepoloc(after=datetime(2013, 1, 10))


Planned functionality
=====================

    -View graphs of your codebase over time:
        
        1.Change in file count
        
        2.Biggest files
        
        3.Biggest/smallest commits
        
        4.Mean/median/mode commit size
        
        5.Commit frequency
    
    -Most frequent committers
    
    -Who added/deleted the most lines
    
    -Histogram of file sizes
    
    -Histogram of commits (both number of files touched and LOC changed)
