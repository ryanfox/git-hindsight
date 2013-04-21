import matplotlib
matplotlib.use('TkAgg')
import matplotlib.dates
import matplotlib.pyplot
import re
import sys

from datetime import datetime

from commit import Commit


def getfilecommits(commits, filename):
    """
    Get a list of commits a given file was changed in.  If the file does not
    exist in the repo, an empty list is returned.
    
    :param filename: The file to return change summary on.  A regular expression
        may be used as well.
    :returns: A list sorted from earliest to latest changes.  Each list
        element is a tuple of the format (datetime, additions, subtractions),
        where datetime is a datetime object of the change, and additions and
        subtractions contain the number of changes to the file.  If the file
        never existed in the repository, an empty list is returned.
    """
    changes = []
    for commit in commits:
        for change in commit.changes:
            if re.match(filename, change[0]) or change[0] == filename:
                changes.append(commit)

    return changes


def getfilesizechanges(commits, filename):
    """
    Get a list of size changes to a file.  Each list element is a tuple of the
    form `(date, added, deleted)`, where date is a datetime object.
    
    :param commits: The list of commits to get changes from
    :param filename: The file to search for.  The path relative to git root
        or regular expressions are accepted.
    :returns: A list containing the dates and size changes of the specified
        file.
    """
    sizechanges = []
    
    filecommits = getfilecommits(commits, filename)
    for commit in filecommits:
        for change in commit.changes:
            if re.match(filename, change[0]) or change[0] == filename:
                sizechanges.append((commit.date, change[1], change[2]))
    return sizechanges
    

def getnetsizechange(commit):
    """
    Get the net line count change resulting from a commit or list of commits.
    
    :param commit: A commit of list of commits to add up.
    :returns: The sum of line changes (additions - subtractions) from all the
        provided commits
    """
    if isinstance(commit, list):
        return sum(getnetsizechange(c) for c in commit) # recursive call
    total = 0
    for change in commit.changes:
        total += change[1] - change[2]
    return total


def extractchanges(lines):
    """
    Extract per-file changes from a list of lines formatted by
    `git log --numstat`.  Return a list of tuples of the format
        (filename, netchanges)
    Don't call this method directly, use parse(filename) instead.
    
    :param lines: The lines from `git log` to parse
    :returns: A list of tuples containing the filenames and net line changes
    """
    changes = []
    
    striplines = [line.strip() for line in lines]
    for line in striplines:
        line = re.split('\s+', line)
        try:
            added = int(line[0])
        except ValueError:
            added = 0
        try:
            subtracted = int(line[1])
        except ValueError:
            subtracted = 0
        changes.append((line[2], added, subtracted))

    return changes

def parse(filename):
    """
    Parse a file formatted by `git log --numstat`
    
    :param filename: Name of the file to parse
    :returns: A list of Commit objects.
    """
    with open(filename) as f:
        parsedcommits = []
        # have to add a newline to the start so regular expression lines up
        logfile = '\n' + f.read()
        commits = re.split('\n(commit [0-9a-f]{40})', logfile)
        for i in range(1, len(commits), 2):
            commithash = commits[i].split(' ')[1]

            sections = commits[i + 1].split('\n\n')
            authorsection = sections[0].split('\n')
            if any(line.startswith('Merge:') for line in authorsection):
                continue # Skip merge commits

            author = authorsection[1].split('Author: ')[1]
            
            # remove time zone from date
            dateline = authorsection[2]
            datestring = ' '.join(dateline.split(' ')[1:-1])
            date = datetime.strptime(datestring.strip(), '%a %b %d %H:%M:%S %Y')
            
            message = sections[1].strip()
            changes = extractchanges(sections[2].strip().split('\n'))
            parsedcommits.append(Commit(commithash, author, date, message, changes))
        parsedcommits.sort(key=lambda commit: commit.date)
        return parsedcommits





if __name__ == '__main__':
    filename = sys.argv[1]
    commits = parse(filename)
    dates = matplotlib.dates.date2num(c.date for c in commits)
    vals = [0] * len(dates)
    for i, change in enumerate(commits):
        vals[i] = vals[i - 1] + getnetsizechange(commits[i]) / 1000000.0
        if abs(getnetsizechange(commits[i])) > 50000:
            print commits[i]
            print getnetsizechange(commits[i])
            print
    matplotlib.pyplot.plot_date(dates, vals, 'b-')
    matplotlib.pyplot.ylabel('Total MLOC')
    matplotlib.pyplot.show()
    





