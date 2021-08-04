'''
Created on 2021-07-26

@author: wf
'''
from typing import Callable

from lodstorage.csv import CSV
from lodstorage.entity import EntityManager
from lodstorage.jsonable import JSONAble
from lodstorage.lod import LOD
from lodstorage.sql import SQLDB
from lodstorage.storageconfig import StorageConfig

class EventStorage:
    '''
    common storage aspects of the EventManager and EventSeriesManager
    '''
    @staticmethod
    def getStorageConfig(debug:bool=False,mode='sql')->StorageConfig:
        '''
        get the storageConfiguration
        
        Args:
            debug(bool): if True show debug information
            mode(str): sql or json
        
        Return:
            StorageConfig: the storage configuration to be used
        '''
        if mode=='sql':
            config=StorageConfig.getSQL(debug=debug)
        elif mode=='json':
            config=StorageConfig.getJSON()
        elif mode=='jsonpickle':
            config=StorageConfig.getJsonPickle(debug=debug)
        else:
            raise Exception(f"invalid mode {mode}")
        config.cacheDirName="conferencecorpus"
        cachedir=config.getCachePath() 
        if mode=='sql':
            config.cacheFile=f"{cachedir}/EventCorpus.db"
        return config
    
    @classmethod
    def getSqlDB(cls):
        '''
        get the SQL Database
        '''
        config=EventStorage.getStorageConfig()
        sqlDB=SQLDB(config.cacheFile)
        return sqlDB
    
    @classmethod
    def getTableList(cls,withInstanceCount:bool=True)->list:
        '''
        get the list of SQL Tables involved
        
        Return:
            list: the map of SQL tables used for caching
            withInstanceCount(bool): if TRUE add the count of instances to the table Map 
        '''
        sqlDB=EventStorage.getSqlDB()
        tableList=sqlDB.getTableList()
        for table in tableList:
            tableName=table["name"]
            if withInstanceCount:
                countQuery="SELECT count(*) as count from %s" % tableName
                countResult=sqlDB.query(countQuery)
                table['instances']=countResult[0]['count']
        return tableList
    
    @classmethod
    def getCommonViewDDL(cls):
        '''
        get the SQL DDL for a common view 
        
        Return:
            str: the SQL DDL CREATE VIEW command
        '''
        common="eventId,title,url,acronym,source,year"
        viewDDL="""CREATE VIEW IF NOT EXISTS event AS\n"""
        delim=""
        sqlDB=EventStorage.getSqlDB()
        tableList=sqlDB.getTableList()
        for table in tableList:
            tableName=table["name"]
            if tableName.startswith("event_"):
                viewDDL=f"{viewDDL}{delim}  SELECT {common} FROM {tableName}"
                delim="\nUNION\n" 
        return viewDDL
    
    @classmethod
    def createView(cls):
        ''' 
          create the general Event view
          
        Args:
            cacheFileName(string): the path to the database
        '''
        sqlDB=EventStorage.getSqlDB()
        viewDDL=EventStorage.getCommonViewDDL()
        sqlDB.c.execute(viewDDL)
    

class Event(JSONAble):
    '''
    base class for Event entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

    def __str__(self):
        '''
        return my
        '''
        text=self.__class__.__name__
        attrs=["pageTitle","acronym","eventId","title","year","source","url"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
    
class EventSeries(JSONAble):
    '''
    base class for Event Series entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()


class EventBaseManager(EntityManager):
    '''
    common entity Manager for ConferenceCorpus
    '''
    
    def __init__(self,name,entityName,entityPluralName:str,listName:str=None,clazz=None,tableName:str=None,primaryKey:str=None,config=None,handleInvalidListTypes=False,filterInvalidListTypes=False,debug=False,profile=True):
        '''
        Constructor
        
        Args:
            name(string): name of this eventManager
            entityName(string): entityType to be managed e.g. Country
            entityPluralName(string): plural of the the entityType e.g. Countries
            config(StorageConfig): the configuration to be used if None a default configuration will be used
            handleInvalidListTypes(bool): True if invalidListTypes should be converted or filtered
            filterInvalidListTypes(bool): True if invalidListTypes should be deleted
            debug(boolean): override debug setting when default of config is used via config=None
            profile(boolean): True if profiling/timing information should be shown for long-running operations
        '''
        self.profile=profile
        if config is None:
            config=EventStorage.getStorageConfig(debug=debug)
        super().__init__(name, entityName, entityPluralName, listName, clazz, tableName, primaryKey, config, handleInvalidListTypes, filterInvalidListTypes, debug)
        
    def configure(self):
        '''
        configure me - abstract method that needs to be overridden
        '''    
        raise Exception(f"specialized configure for {self.name} needs to be implemented")
 
    def setAllAttr(self,listOfDicts,attr,value):
        '''
        set all attribute values of the given attr in the given list of Dict to the given value 
        '''
        for record in listOfDicts:
            record[attr]=value

    def asCsv(self, separator:str=',', selectorCallback:Callable=None):
        """
        Converts the events to csv format
        Args:
            separator(str): character separating the row values
            selectorCallback: callback functions returning events to be converted to csv. If None all events are converted.

        Returns:
            csv string of events
        """
        events=self.getList()
        if selectorCallback is not None and callable(selectorCallback):
            events=selectorCallback()
        fields=None
        # limit csv fields to the fields defined in the samples
        if hasattr(self, 'getSamples') and callable(getattr(self, 'getSamples')):
            fields=LOD.getFields(self.getSamples())
        csvString=CSV.toCSV(events, includeFields=fields)
        return csvString
    
class EventSeriesManager(EventBaseManager):
    '''
    Event series list
    '''
    def __init__(self,name:str,clazz=None,tableName:str=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super().__init__(name=name,entityName="EventSeries",entityPluralName="EventSeries",primaryKey=primaryKey,listName="series",clazz=clazz,tableName=tableName,handleInvalidListTypes=True,config=config,debug=debug)
        
            
class EventManager(EventBaseManager):
    '''
    Event entity list
    '''
    
    def __init__(self,name:str,clazz=None,tableName:str=None,primaryKey:str=None,config:StorageConfig=None,debug=False):
        '''
        constructor 
        '''
        super(EventManager, self).__init__(name=name,entityName="Event",entityPluralName="Events",primaryKey=primaryKey,listName="events",clazz=clazz,tableName=tableName,config=config,handleInvalidListTypes=True,debug=debug)
        
 
    def linkSeriesAndEvent(self, eventSeriesManager:EventSeriesManager, seriesKey:str="series"):
        '''
        link Series and Event using the given foreignKey

        Args:
            seriesKey(str): the key to be use for lookup
            eventSeriesManager(EventSeriesManager):
        '''
        # get foreign key hashtable
        self.seriesLookup = LOD.getLookup(self.getList(), seriesKey, withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup = LOD.getLookup(eventSeriesManager.getList(), "acronym", withDuplicates=True)

        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents = self.seriesLookup[seriesAcronym]
                if hasattr(self, 'verbose') and self.verbose:
                    print(f"{seriesAcronym}:{len(seriesEvents):4d}")
            else:
                if self.debug:
                    print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print("%d events/%d eventSeries -> %d linked" % (
            len(self.getList()), len(eventSeriesManager.getList()), len(self.seriesLookup)))
            
    def getEventsInSeries(self,seriesAcronym):
        """
        Return all the events in a given series.
        """
        if seriesAcronym in self.seriesAcronymLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
            return None
        return seriesEvents

