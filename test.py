#!/usr/bin/env python

import unittest
from seqdiff import *

class TestSeq(unittest.TestCase):
    def test_ref_parsing(self):
        l = "Ref XYZ 3"
        ref, tlen = grab_ref_and_tag_len(l)
        self.assertEqual(ref, "XYZ")
        self.assertEqual(tlen, 4)

        l = "Ref  XYZ 3"
        ref, tlen = grab_ref_and_tag_len(l)
        self.assertEqual(ref, "XYZ")
        self.assertEqual(tlen, 5)

if __name__ == "__main__":
    unittest.main()
