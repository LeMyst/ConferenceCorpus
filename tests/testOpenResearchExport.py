'''
Created on 2021-08-07

@author: wf
'''

import unittest
from tests.testDblpXml import TestDblp
from tests.datasourcetoolbox import DataSourceTest
from corpus.lookup import CorpusLookup
import getpass

class TestOpenResearchExport(DataSourceTest):
    '''
    test the dblp data source
    '''
 
    def setUp(self):
        '''
        '''
        DataSourceTest.setUp(self)
        pass

    def testDblpSeriesExport(self):
        '''
        test exporting a single series
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        acronym='qurator'
        lookup=CorpusLookup(lookupIds=["dblp"])
        lookup.load(forceUpdate=False)
        dblpDataSource=lookup.getDataSource("dblp")
        seriesByAcronym,_dup=dblpDataSource.eventSeriesManager.getLookup("acronym")
        series=seriesByAcronym[acronym]
        print(series.asWikiMarkup())
        eventBySeries=dblpDataSource.eventManager.getLookup("series",withDuplicates=True)
        events=eventBySeries[acronym]
        for event in events:
            print(event.asWikiMarkup())
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()