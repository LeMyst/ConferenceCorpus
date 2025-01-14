'''
Created on 2021-04-16

@author: wf
'''
from corpus.event import EventManager, EventSeriesManager, EventStorage
from corpus.config import EventDataSourceConfig            
from corpus.quality.rating import RatingManager
from corpus.datasources.download import Download

class EventDataSource(object):
    '''
    a data source for events
    '''
    
    def __init__(self,eventManager:EventManager,eventSeriesManager:EventSeriesManager,sourceConfig=EventDataSourceConfig):
        '''
        constructor
        
        Args:
            sourceConfig(EventDataSourceConfig): the configuration for the EventDataSource
            eventManager(EventManager): manager for the events
            eventSeriesManager(EventSeriesManager): manager for the eventSeries
        '''
        self.sourceConfig=sourceConfig
        self.name=self.sourceConfig.name
        
        self.eventManager=eventManager
        self.eventManager.dataSource=self
        
        self.eventSeriesManager=eventSeriesManager
        self.eventSeriesManager.dataSource=self
        pass
        
    def load(self,forceUpdate=False):
        '''
        load this data source
        '''
        self.eventSeriesManager.configure()
        self.eventManager.configure()
        # first events
        self.eventManager.fromCache(force=forceUpdate)
        # then series
        self.eventSeriesManager.fromCache(force=forceUpdate)
        # TODO use same foreign key in all dataSources
        self.eventManager.linkSeriesAndEvent(self.eventSeriesManager,"inEventSeries")
        
    def rateAll(self,ratingManager:RatingManager):
        '''
        rate all events and series based on the given rating Manager
        '''
        self.eventManager.rateAll(ratingManager)
        self.eventSeriesManager.rateAll(ratingManager)
        

class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False,verbose=False):
        '''
        Constructor
        
        Args:
            debug(bool): set debugging if True
            verbose(bool): set verbose output if True
        '''
        self.debug=debug
        self.verbose=verbose
        self.eventDataSources={}

    def addDataSource(self, eventDataSource:EventDataSource):
        '''
        adds the given eventDataSource
        
        Args:
            eventDataSource: EventDataSource
        '''
        self.eventDataSources[eventDataSource.sourceConfig.lookupId]=eventDataSource
        pass
    
    def loadAll(self,forceUpdate:bool=False):
        '''
        load all eventDataSources
        
        Args:
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
        '''
        for eventDataSource in self.eventDataSources.values():
            eventDataSource.load(forceUpdate=forceUpdate)
           
    @staticmethod        
    def download():
        '''
        download the EventCorpus.db if needed
        '''
        fileName="EventCorpus.db"
        url = f"https://github.com/WolfgangFahl/ConferenceCorpus/wiki/data/{fileName}.gz"
        targetDirectory=EventStorage.getStorageConfig().getCachePath()
        Download.downloadBackupFile(url, fileName, targetDirectory)
     
