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
    
    def getchangedates(filename):
        """
        Get a list of dates a given file was changed on, along with the number
        of lines added or subtracted.  If the file does not exist in the repo,
        an empty list is returned.
        
        :param filename: The file to return change summary on.
        :returns: A list sorted from earliest to latest changes.  Each list
            element is a tuple of the format (datetime, lines), where datetime
            is a datetime object of the change, and lines is an int containing
            the number of additions or subtractions to the file.  If the file
            never existed in the repository, an empty list is returned.
        """
        pass
