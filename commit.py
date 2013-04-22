class Commit:
    """
    A class representing a commit in git.  Changes should be a list representing
    files that were changed in the commit.  Each list element should be a dict
    of the form:
        {'name': file_name,
         'additions': additions, 
         'deletions': deletions}
    """
    def __init__(self, commithash=None, author=None,
                 date=None, message=None, changes=[]):
        self.commithash = commithash
        self.author = author
        self.date = date
        self.message = message
        self.changes = changes
    
    def __str__(self):
        return '{}\n{}\n{}'.format(self.author, self.date, self.message)
    
    def getnetchange(commit):
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
