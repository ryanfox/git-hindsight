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
