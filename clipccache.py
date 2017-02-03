
import psycopg2 as _psycopg2

import hashlib
from datetime import datetime
from inspect import currentframe
import requests
import logging
import os

logger = logging.getLogger('server_logger')


def get_linenumber():
    cf = currentframe()
    return __file__, cf.f_back.f_lineno

def logerror(file=None, line=None, mess=None):
    logger.error("[%s] [%s]: %s", file, line, mess)

def logwarning(file=None, line=None, mess=None):
    logger.warning("[%s] [%s]: %s", file, line, mess)

def loginfo(file=None, line=None, mess=None):
    logger.info("[%s] [%s]: %s", file, line, mess)

def logdebug(file=None, line=None, mess=None):
    logger.debug("[%s] [%s]: %s", file, line, mess)

class clipccache():

    max_tuple = 5

    def __init__(self, username, password, server='127.0.0.1', port=5432, db='clipcache', homedir=None):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.db=db
        self.homedir=homedir;
        self.result_id = None
        self.conn=None
        self.request = None;
        if self.username is None or self.password is None or self.server is None or self.port is None or self.homedir is None or self.db is None:
            logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), 'One or more Cache DB connection parameters are None')
            raise RuntimeError('One or more connection parameters are None')
        try:
            self.conn =_psycopg2.connect(database=db,user=username,host=server,port=port,password=password)
        except (Exception, _psycopg2.Error), e:
            logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), str(e))

    def __del__(self):
        del self.username
        del self.password
        del self.server
        del self.port
        del self.db
        del self.homedir
        del self.result_id
        if self.conn is not None:
            self.conn.close()
        logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), "DESTRUCTOR")

    def cache_request(query, dbuser='root', dbpasswd="abcd", dbhost="127.0.0.1"):
        #result = cache_search(dbuser, dbpasswd, dbhost, query)
        #return result
        pass


    def cache_search(self, curprocess=None, query=None):
        logger.debug("cache_search");
        try:
            if curprocess is None:
                logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Cache process request in empty')
                raise RuntimeError(' %s %s Request in empty' % (get_linenumber()[0],get_linenumber[1]))
            c = self.conn.cursor()

            CacheRequest = "Homedir=" + self.homedir + ";ProcessID=" + str(curprocess.identifier) + ";"
            for inputs in curprocess.inputs:
                #logger.debug("Found INPUT")
                #logger.debug("IDENTIFIER: " + inputs + " value " + str(curprocess.getInputValue(inputs)))
                CacheRequest += inputs + "=" + str(curprocess.getInputValue(inputs)) + ";"

            CacheRequest = hashlib.sha512(str(CacheRequest).encode()).hexdigest()
            myquery = "SELECT id, result, status from cache_table where query='" + CacheRequest + "'"
            logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
            c.execute(myquery)
            result = c.fetchone()
            #logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), str(result[0]) + " " + str(result[1]))
            if result is not None and result[2] == 0:
                #check
                logger.debug(result[1]);
                
                useLocalFile = False
                theCacheFileIsFound = False
                
                """ Check whether this file can be identified locally, based on C4I's POF_OUTPUT_URL environment vars """
                try:
                  POF_OUTPUT_URL  = os.environ['POF_OUTPUT_URL']
                  POF_OUTPUT_PATH = os.environ['POF_OUTPUT_PATH']
                  useLocalFile = True
                except (Exception):
                  pass

                
                """ This is a local file, check whether it is available """
                if useLocalFile == True:
                  """ Check whether the file resides on disc """
                  logger.debug(POF_OUTPUT_URL);
                  logger.debug(POF_OUTPUT_PATH);
                  filecheck = result[1].replace(POF_OUTPUT_URL,POF_OUTPUT_PATH)
                  logger.debug("File to check: "+filecheck);
                  if os.path.isfile(filecheck) == False:
                    theCacheFileIsFound = False
                  else:
                    theCacheFileIsFound = True
                    logger.debug("The file is there.")

                """ Check the opendap URL for existance by using the das object """
                if useLocalFile == False:
                  filecheck = requests.head(result[1] + ".das")
                  #filecheck = requests.head("http://127.0.0.1/ophidia")
                  logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Checking remote file: '+ str(filecheck.status_code) +';'+ str(filecheck.text) + ';' +  str(filecheck.headers))
                  if filecheck.status_code == 404:
                    theCacheFileIsFound = False
                  else:
                    theCacheFileIsFound = True
                    
                if theCacheFileIsFound == False:
                        #File was deleted
                        myquery="DELETE from cache_table where id = " + str(result[0])
                        logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
                        c.execute(myquery)
                        logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Output file not found. Number of rows deleted: '+ str(c.rowcount))
                        self.conn.commit()
                        self.request = CacheRequest 
                        return (None)
                
                #Update the last_request timestamp column
                self.result_id=result[0]
                myquery = "UPDATE cache_table SET last_request = '" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "', hit_count = hit_count + 1 WHERE id = " + str(result[0])
                logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
                c.execute(myquery)
                self.conn.commit()
                return (result[1])
            else:
                self.request = CacheRequest 
                logger.debug("cache_search file not there");
                return (None)
        except (Exception, _psycopg2.Error), e:
            logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), e)
            logger.debug("cache_search something is wrong");
            return (None)


    def insert_new(self, curprocess=None, query=None):
        try:
            if curprocess is None:
                logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Query request in empty')
                raise RuntimeError(' %s %s Process istance is empty' % (get_linenumber()[0],get_linenumber()[1]))

            c = self.conn.cursor()
            myquery = "INSERT INTO cache_table (query, result, last_request) VALUES ('" + self.request + "','" + curprocess.opendapURL.value + "','" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "')"
            logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
            c.execute(myquery)
            logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Number of rows inserted: '+ str(c.rowcount))
            #logger.debug("Number of rows updated: %s",(c.rowcount))
            self.conn.commit()
            #LRU management
            myquery="SELECT count(*) from cache_table"
            logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
            c.execute(myquery)
            result = c.fetchone()
            if result is None:
                logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Internal PostgreSQL query error')
                raise RuntimeError(' %s %s Internal PostgreSQL query error' % (get_linenumber()[0],get_linenumber()[1]))
            if result[0] > clipccache.max_tuple:
                logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), 'RESULT ' + str(result[0]) + ' MAX_TUPLE ' + str(clipccache.max_tuple))
                myquery="SELECT id from cache_table where last_request = (SELECT min(last_request) from cache_table)"
                logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
                c.execute(myquery)
                result = c.fetchone()
                if result is None:
                    logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Internal PostgreSQL query error')
                    raise RuntimeError(' %s %s Internal PostgreSQL query error' % (get_linenumber()[0],get_linenumber()[1]))
                myquery="DELETE from cache_table where id = " + str(result[0])
                logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), myquery)
                c.execute(myquery)
                logdebug(str(get_linenumber()[0]), str(get_linenumber()[1]), 'Number of rows deleted: '+ str(c.rowcount))
                self.conn.commit()
            #db.close()
            return 1
        except (Exception, _psycopg2.Error), e:
            logerror(str(get_linenumber()[0]), str(get_linenumber()[1]), str(e))
            #print(get_linenumber(),"Something went wrong in cache updating:", e)
            return (None)
