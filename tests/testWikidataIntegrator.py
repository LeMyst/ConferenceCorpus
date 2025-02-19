'''
Created on 2021-10-24

@author: wf
'''
import unittest
from wikibaseintegrator import wbi_core, wbi_login, wbi_datatype,wbi_functions
import json

class TestWikiBaseIntegrator(unittest.TestCase):
    '''
    test access to Wikidata
    '''
    def prettyJson(self,jsonStr):
        parsed = json.loads(jsonStr)
        print(json.dumps(parsed, indent=2, sort_keys=True))

    def testQ5(self):
        '''
        test Q5 access
        '''
        query = {
    'action': 'query',
    'prop': 'revisions',
    'titles': 'Q5',
    'rvlimit': 10
}
        result=wbi_functions.mediawiki_api_call_helper(query, allow_anonymous=True)
        self.prettyJson(json.dumps(result))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()