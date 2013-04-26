import matplotlib
matplotlib.use('TkAgg')
import matplotlib.dates
import matplotlib.pyplot as plt
import re
import sys

from collections import defaultdict
from datetime import datetime

from commit import Commit

class Repo:
    def __init__(self, logfile=None):
        if logfile:
            self.commits = Repo.parse(logfile)


    def getfilecommits(self, filename, before=datetime.now(),
                       after=datetime(1, 1, 1)):
        """
        Get a list of commits a given file was changed in.  If the file does not
        exist in the repo, an empty list is returned.
        
        :param filename: The file to return change summary on.
        :param before: A datetime object, all commits after this will be
            excluded
        :param after: A datetime object all commits before this will be excluded
        :returns: A list sorted from earliest to latest changes.  Each list
            element is a tuple of the format
            `(datetime, additions, subtractions)`
            where datetime is a datetime object of the change, and additions and
            subtractions contain the number of changes to the file.  If the file
            never existed in the repository, an empty list is returned.
        """
        regex = re.compile(re.escape(filename))
        changes = []
        
        # extract commits fitting inside the date bounds first
        # we know they are already sorted earliest to latest
        commits = [commit for commit in self.commits if commit.date < before and commit.date > after]
        for commit in commits:
            for change in commit.changes:
                if re.search(regex, change[0]):
                    changes.append(commit)

        return changes


    def getfileloc(self, filename, date=datetime.now()):
        """
        Get the number of lines in a file at a given date.
        
        :param filename: Name of file to use.
        :param date: Date to count up to
        :returns: The number of lines in the file specified as of date supplied
        """
        regex = re.compile(re.escape(filename))
        commits = self.getfilecommits(filename, before=date)
        total = 0
        for commit in commits:
            for change in commit.changes:
                if re.search(regex, change[0]):
                    total += change[1] - change[2]
        
        return total


    def getfilechanges(self, filename, before=datetime.now(),
                           after=datetime(1, 1, 1)):
        """
        Get a list of size changes to a file.  Each list element is a tuple of
            the form `(date, added, deleted)`, where date is a datetime object.
        
        :param filename: The file to search for.
        :param before: A datetime object, all commits after this will be
            excluded
        :param after: A datetime object all commits before this will be
            excluded
        :returns: A list containing the dates and size changes of the specified
            file.
        """
        regex = re.compile(re.escape(filename))
        filechanges = []
        
        filecommits = self.getfilecommits(filename)
        for commit in filecommits:
            if commit.date < before and commit.date > after:
                for change in commit.changes:
                    if re.search(regex, change[0]) or change[0] == filename:
                        filechanges.append((commit.date, change[1], change[2]))
        return filechanges


    def getallfilesizes(self, date=datetime.now()):
        """
        Get a dict of filenames and sizes.  dict elements are of the
        format `{'filename': filesize}`.  Date may optionally be specified.
        Much faster than getting individual sizes for each file if you are
        getting many at a time.
        
        :param date: Point in time at which to get file sizes.
        :returns: A dict of filenames and sizes
        """
        files = defaultdict(int)
        commits = (commit for commit in self.commits if commit.date < date)
        for commit in commits:
            for change in commit.changes:
                files[change[0]] += change[1] - change[2]
        return files
    
    
    def getcommitsperfile(self, date=datetime.now()):
        """
        Get a dict of filenames and number of commits.  dict elements are of the
        format `{'filename': commits}`.  Date may optionally be specified.
        Much faster than getting individual commits for each file if you are
        getting many at a time.
        
        :param date: Point in time at which to get file sizes.
        :returns: A dict of filenames and number of times it was committed
        """
        files = defaultdict(int)
        commits = (commit for commit in self.commits if commit.date < date)
        for commit in commits:
            for change in commit.changes:
                files[change[0]] += 1
        return files


    def plotrepoloc(self, before=datetime.now(), after=datetime(1, 1, 1),
                     title=None, scalefactor=1, savefile=None):
        """
        Plot total LOC in the repository.  Arguments `before` and `after`
        may be specified to include/exclude a range from plotting.  They should
        be datetime objects.  A scale factor may optionally be specified to make
        the y-axis easier to read.
        
        :param before: A datetime object, all commits after this will be
            excluded from the plot
        :param after: A datetime object all commits before this will be excluded
            from the plot
        :param title: Optional title to give the plot
        :param scalefactor: An optional scale factor.  Total LOC will be divided
            by this, to make the plot easier to read
        :param savefile: Filename to save plot as.
        """
        excludedcommits = [commit for commit in self.commits if commit.date < before and commit.date > after]
        dates = matplotlib.dates.date2num(c.date for c in excludedcommits)
        vals = [0] * len(dates)
        for i, change in enumerate(excludedcommits):
            vals[i] = vals[i - 1] + excludedcommits[i].getnetchange() / float(scalefactor)

        plt.plot_date(dates, vals, 'b-')
        if scalefactor == 1000:
            label = 'k' # kilo-lines of code
        elif scalefactor == 1000000:
            label = 'M' # Mega-lines of code
        else:
            label = '' # just lines of code
        plt.ylabel('Total {}LOC'.format(label))
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()


    def plotcumulativecommits(self, before=datetime.now(),
                              after=datetime(1, 1, 1), savefile=None):
        """
        Plot cumulative commits.  Arguments `before` and `after`
        may be specified to include/exclude a range from plotting.  They should
        be datetime objects.  A scale factor may optionally be specified to make
        the y-axis easier to read.
        
        :param before: A datetime object, all commits after this will be
            excluded from the plot
        :param after: A datetime object all commits before this will be excluded
            from the plot
        :param savefile: Filename to save plot as.
        """
        commits = [commit for commit in self.commits if commit.date < before and commit.date > after]
        dates = matplotlib.dates.date2num(c.date for c in commits)

        plt.plot_date(dates, range(len(dates)), 'b-')
        plt.title('Cumulative commits')
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()


    def plotfileloc(self, filename, before=datetime.now(),
                    after=datetime(1, 1, 1), scalefactor=1, savefile=None):
        """
        Plot LOC for a file.  Filename may be specified or regular expression.
        Usage is the same as `plottotalloc()`, except for the filename.
        """
        filecommits = self.getfilecommits(filename)
        sizechanges = self.getfilechanges(filename)
        dates = matplotlib.dates.date2num(change[0] for change in sizechanges)
        vals = [0] * len(sizechanges)
        for i, change in enumerate(sizechanges):
            vals[i] = vals[i - 1] + (change[1] - change[2]) / float(scalefactor)
        
        plt.plot_date(dates, vals, 'b-')
        if scalefactor == 1000:
            label = 'k' # kilo-lines of code
        elif scalefactor == 1000000:
            label = 'M' # Mega-lines of code
        else:
            label = '' # just lines of code
        plt.ylabel('Total {}LOC'.format(label))
        plt.title(filename)
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()
    
    
    def plotcommitsizehist(self, scalefactor=1, log=False, numexcluded=None,
                           savefile=None):
        """
        Plot a histogram of commit sizes.
        
        :param scalefactor: Scale the results to make chart easier to read.
        :param log: If true, histogram will be plotted with a logarithmic
            y-axis.  This makes it easier to read if you have a very tall
            plot.
        :param numexcluded: Number of commits to clip off each end of the
            distribution.  Again, can make it easier to read if you have a few
            very far outliers.
        :param savefile: Filename to save plot as.
        """
        sizes = [float(commit.getnetchange()) / scalefactor for commit in self.commits]
        if numexcluded and numexcluded > 0:
            sizes.sort()
            sizes = sizes[numexcluded:-numexcluded]
        
        plt.hist(sizes, log=log)
        if scalefactor == 1000:
            label = 'k' # kilo-lines of code
        elif scalefactor == 1000000:
            label = 'M' # Mega-lines of code
        else:
            label = '' # just lines of code
        plt.xlabel('Net {}LOC change'.format(label))
        plt.ylabel('Number of commits')
        plt.title('Commit size')
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()

        
    def plotfilesizehist(self, date=datetime.now(), scalefactor=1, log=False,
                         numexcluded=None, savefile=None):
        """
        Plot a histogram of file sizes.
        
        :param date: Date to show file sizes at.
        :param scalefactor: Scale the results to make chart easier to read.
        :param log: If true, histogram will be plotted with a logarithmic
            y-axis.  This makes it easier to read if you have a very tall
            plot.
        :param numexcluded: Number of commits to clip off each end of the
            distribution.  Again, can make it easier to read if you have a few
            very far outliers.
        :param savefile: Filename to save plot as.
        """
        files = self.getallfilesizes(date=date)
        sizes = files.values()

        if numexcluded and numexcluded > 0:
            sizes.sort()
            sizes = sizes[:-numexcluded]

        plt.hist(sizes, log=log)
        if scalefactor == 1000:
            label = 'k' # kilo-lines of code
        elif scalefactor == 1000000:
            label = 'M' # Mega-lines of code
        else:
            label = '' # just lines of code
        plt.xlabel('File size - {}LOC'.format(label))
        plt.ylabel('Number of files')
        plt.title('File size - {}'.format(date.ctime()))
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()
    
    
    def plotauthorcommits(self, date=datetime.now(), savefile=None):
        """
        Plot a bar chart of the number of commits each author has.
        
        :param date: Date at which to plot commit totals.
        :param savefile: Filename to save chart to.
        """
        commits = [commit for commit in self.commits if commit.date < date]
        commitsperauthor = defaultdict(int)
        for commit in commits:
            commitsperauthor[commit.author] += 1
        commits = [(author, commitnum) for author, commitnum in commitsperauthor.items()]
        commits.sort(key=lambda commit:commit[0])
        authors, commits = zip(*commits)

        fig, ax = plt.subplots()
        ax.bar(range(len(commits)), commits)
        ax.set_xlabel('Authors')
        ax.set_xticks([x + .5 for x in range(len(commits))])
        ax.set_xticklabels(authors, fontsize=8, rotation='vertical')
        ax.set_ylabel('Commits')
        ax.set_title('Commits by Author')
        plt.tight_layout()
        
        if savefile:
            plt.savefig(savefile)
        else:
            plt.show()
        
    

    @staticmethod
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

    
    @staticmethod
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
                changes = Repo.extractchanges(sections[2].strip().split('\n'))
                parsedcommits.append(Commit(commithash, author, date, message, changes))
            parsedcommits.sort(key=lambda commit: commit.date)
            return parsedcommits





if __name__ == '__main__':
    filename = sys.argv[1]
    repo = Repo(filename)
    repo.plotfilesizehist()
    





