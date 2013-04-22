import hindsight
import unittest

from datetime import datetime

class RepoTest(unittest.TestCase):
    def setUp(self):
        self.repo = hindsight.Repo('git_numstat.txt')
    
    def test_getfilecommits(self):
        commits = self.repo.getfilecommits('hindsight.py')
        self.assertEqual(len(commits), 3)
        
        commits = self.repo.getfilecommits('commit.py')
        self.assertEqual(len(commits), 3)
        
        commits = self.repo.getfilecommits('README.rst')
        self.assertEqual(len(commits), 2)
    
    def test_getfileloc(self):
        lines = self.repo.getfileloc('hindsight.py')
        self.assertEqual(lines, 232)
        
        lines = self.repo.getfileloc('hindsight.py', datetime(2013, 4, 21, 12, 0))
        self.assertEqual(lines, 77)
    
    def test_getfilechanges(self):
        changes = self.repo.getfilechanges('hindsight.py')
        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[0][0], datetime(2013, 4, 21, 4, 19, 37))
        self.assertEqual(changes[0][1], 77)
        self.assertEqual(changes[0][2], 0)
    
    def test_plotrepoloc(self):
        pass
    
    def test_plotfileloc(self):
        pass
    
    def test_extractchanges(self):
        lines = ['14      0       README.rst',
                 '31      0       commit.py',
                 '77      0       hindsight.py']
        extracted = hindsight.Repo.extractchanges(lines)
        self.assertEqual(extracted[0], ('README.rst', 14, 0))
        self.assertEqual(extracted[1], ('commit.py', 31, 0))
        self.assertEqual(extracted[2], ('hindsight.py', 77, 0))
    
    def test_parse(self):
        commits = hindsight.Repo.parse('git_numstat.txt')
        self.assertEqual(len(commits), 3)
        self.assertEqual(commits[0].commithash, 'a137816c79714740d7964fe96878febaac014d8a')
        self.assertEqual(commits[0].author, 'Ryan Fox <ryan@foxrow.com>')
        self.assertEqual(commits[0].date, datetime(2013, 4, 21, 4, 19, 37))
        self.assertEqual(commits[0].message, 'Initial commit.  parses log file.')

if __name__ == '__main__':
    unittest.main()
