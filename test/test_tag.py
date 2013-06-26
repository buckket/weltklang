import unittest

import rfk.database
from rfk.database.show import Tag

class Test(unittest.TestCase):

    def setUp(self):
        rfk.database.init_db('sqlite://', False)

    def tearDown(self):
        pass

    def test_tag_dupplicate(self):
        tag_ref = Tag.get_tag('tag')
        tag_ref2 = Tag.get_tag('tag')
        self.assertIs(tag_ref, tag_ref2)

    def test_tag_entry(self):
        tag_ref = Tag.get_tag('tag2')
        tag_ref2 = Tag.get_tag('tag3')
        self.assertIsNot(tag_ref, tag_ref2)
    
    def test_parse_tags(self):
        taglist = ['tag1', 'tag2', 'tag3', 'tag4']
        tags = Tag.parse_tags(' '.join(taglist))
        self.assertIs(len(tags),4)
        for tagname in taglist:
            self.assertIn(Tag.get_tag(tagname),tags)
    
    def test_parse_tags_with_dupplicate(self):
        taglist = ['tag1', 'tag2', 'tag3', 'tag1']
        tags = Tag.parse_tags(' '.join(taglist))
        self.assertIs(len(tags),3)
        for tagname in taglist:
            self.assertIn(Tag.get_tag(tagname),tags)
    
    def test_parse_tags_with_empty_tags(self):
        taglist = ['tag1', '', '', 'tag2']
        tags = Tag.parse_tags(' '.join(taglist))
        self.assertIs(len(tags),2)
        for tagname in taglist:
            if tagname == '':
                continue
            self.assertIn(Tag.get_tag(tagname),tags)
            
    def test_parse_tags_with_empty_string(self):
        tags = Tag.parse_tags('')
        self.assertIs(len(tags),0)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()