import matplotlib
import re
import sys

from datetime import datetime

from commit import Commit

def extractchanges(lines):
    """
    Extract per-file changes from a list of lines formatted by
    `git log --numstat`.  Return a list of tuples of the format
        (filename, netchanges)
    
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
        commits = re.split('\n(commit [0-9a-f]{40})', f.read())
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
        return parsedcommits





if __name__ == '__main__':
    filename = sys.argv[1]
    alist = parse(filename)
    





