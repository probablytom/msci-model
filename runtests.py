import unittest
import theatre_ag
import resp_base

if __name__ == "__main__":
    unittest.main.loader.TestLoader.discover(".",
                                             pattern='test*.py',
                                             top_level_dir=None)
