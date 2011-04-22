#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
from pymongo.objectid import ObjectId

class MongoQuery(object):
    """
    Query handles all the querying done by the Database Library. 
    """

    def get_mongodb_databases(self):
        """
        Returns a list of all of the databases currently on the MongoDB 
        server you are connected to.

        Usage is:
        | @{allDBs} | Get Mongodb Databases |
        | Log Many | @{allDBs} |
        | Should Contain | ${allDBs} | DBName |
        """
        cur = None
        try:
            allDBs = self._dbconnection.database_names()
            return allDBs
        finally :
            if cur :
                self._dbconnection.end_request() 

    def get_mongodb_collections(self, dbName):
        """
        Returns a list of all of the collections for the database you
        passed in on the connected MongoDB server.

        Usage is:
        | @{allCollections} | Get MongoDB Collections | DBName |
        | Log Many | @{allCollections} |
        | Should Contain | ${allCollections} | CollName |
        """
        db = None
        try:
            dbName = str(dbName)
            db = self._dbconnection['%s' % (dbName,)]
            allCollections = db.collection_names()
            return allCollections
        finally :
            if db :
                self._dbconnection.end_request() 

    def drop_mongodb_database(self, dbDelName):
        """
        Deletes the database passed in from the MongoDB server if it exists.
        If the database does not exist, no errors are thrown.

        Usage is:
        | Drop MongoDB Database | myDB |
        | @{allDBs} | Get MongoDB Collections | myDB |
        | Should Not Contain | ${allDBs} | myDB |
        """
        cur = None
        try:
            dbDelName = str(dbDelName)
            self._dbconnection.drop_database('%s' % (dbDelName))
        finally :
            if cur :
                self._dbconnection.end_request() 

    def drop_mongodb_collection(self, dbName, dbCollName):
        """
        Deletes the named collection passed in from the database named.
        If the collection does not exist, no errors are thrown.

        Usage is:
        | Drop MongoDB Collection | myDB | CollectionName |
        | @{allCollections} | Get MongoDB Collections | myDB |
        | Should Not Contain | ${allCollections} | CollectionName |
        """
        db = None
        try:
            dbName = str(dbName)
            db = self._dbconnection['%s' % (dbName,)]
            db.drop_collection('%s' % (dbCollName))
        finally :
            if db :
                self._dbconnection.end_request() 

    def validate_mongodb_collection(self, dbName, dbCollName):
        """
        Returns a string of validation info. Raises CollectionInvalid if 
        validation fails.

        Usage is:
        | ${allResults} | Validate MongoDB Collection | DBName | CollectionName |
        | Log | ${allResults} |
        """
        db = None
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            db = self._dbconnection['%s' % (dbName,)]
            allResults = db.validate_collection('%s' % dbCollName)
            return allResults
        finally :
            if db :
                self._dbconnection.end_request() 

    def get_mongodb_collection_count(self, dbName, dbCollName):
        """
        Returns the number records for the collection specified.

        Usage is:
        | ${allResults} | Get MongoDB Collection Count | DBName | CollectionName |
        | Log | ${allResults} |
        """
        db = None
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            db = self._dbconnection['%s' % (dbName,)]
            coll = db['%s' % (dbCollName)]
            count = coll.count()
            return count
        finally :
            if db :
                self._dbconnection.end_request() 

    def save_mongodb_records(self, dbName, dbCollName, recordJSON):
        """
        If to_save already has an "_id" then an update() (upsert) operation is 
        performed and any existing document with that "_id" is overwritten. 
        Otherwise an insert() operation is performed. In this case if manipulate 
        is True an "_id" will be added to to_save and this method returns the 
        "_id" of the saved document.

        | ${allResults} | Save MongoDB Records | DBName | CollectionName | JSON |

        Enter a new record usage is:
        | ${allResults} | Save MongoDB Records | foo | bar | {"timestamp":1, "msg":"Hello 1"} |
        | Log | ${allResults} |

        Update an existing record usage is:
        | ${allResults} | Save MongoDB Records | foo | bar | {"timestamp":1, "msg":"Hello 1"} |
        | Log | ${allResults} |
        """
        db = None
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            recordJSON = dict(json.loads(recordJSON))
            if recordJSON.has_key('_id'):
                recordJSON['_id']=ObjectId(recordJSON['_id'])
            db = self._dbconnection['%s' % (dbName,)]
            coll = db['%s' % (dbCollName)]
            allResults = coll.save(recordJSON)
            return allResults
        finally :
            if db :
                self._dbconnection.end_request() 

    def retrieve_all_mongodb_records(self, dbName, dbCollName):
        """
        Retrieve ALL of the records in a give MongoDB database collection.
        Returned value must be single quoted for comparison, otherwise you will
        get a TypeError error.

        Usage is:
        | ${allResults} | Retrieve All MongoDB Records | DBName | CollectionName |
        | Log | ${allResults} |
        | Should Contain X Times | ${allResults} | '${recordNo1}' | 1 |
        """
        db = None
        results = ''
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            db = self._dbconnection['%s' % (dbName,)]
            coll = db['%s' % (dbCollName)]
            for d in coll.find():
                results = '%s%s' % (results, d.items())
            return results
        finally :
            if db :
                self._dbconnection.end_request() 

    def retrieve_some_mongodb_records(self, dbName, dbCollName, recordJSON):
        """
        Retrieve some of the records from a given MongoDB database collection
        based on the JSON entered.
        Returned value must be single quoted for comparison, otherwise you will
        get a TypeError error.

        Usage is:
        | ${allResults} | Retrieve Some MongoDB Records | DBName | CollectionName | JSON |
        | Log | ${allResults} |
        | Should Contain X Times | ${allResults} | '${recordNo1}' | 1 |
        """
        db = None
        results = ''
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            recordJSON = dict(json.loads(recordJSON))
            db = self._dbconnection['%s' % (dbName,)]
            coll = db['%s' % (dbCollName)]
            for d in coll.find(recordJSON):
                results = '%s%s' % (results, d.items())
            return results
        finally :
            if db :
                self._dbconnection.end_request() 

    def remove_mongodb_records(self, dbName, dbCollName, recordJSON):
        """
        Remove some of the records from a given MongoDB database collection
        based on the JSON entered.
        
        The JSON fed in must be double quoted but when doing a comparison, it
        has to be single quoted.  See Usage below
        
        Usage is:
        | ${allResults} | Remove MongoDB Records | ${MDBDB} | ${MDBColl} | {"_id": "4dacab2d52dfbd26f1000000"} |
        | Log | ${allResults} |
        | ${output} | Retrieve All MongoDB Records | ${MDBDB} | ${MDBColl} |
        | Should Not Contain | ${output} | '4dacab2d52dfbd26f1000000' |
        or
        | ${allResults} | Remove MongoDB Records | ${MDBDB} | ${MDBColl} | {"timestamp": {"$lt": 2}} |
        | Log | ${allResults} |
        | ${output} | Retrieve All MongoDB Records | ${MDBDB} | ${MDBColl} |
        | Should Not Contain | ${output} | 'timestamp', 1 |
        """
        db = None
        try:
            dbName = str(dbName)
            dbCollName = str(dbCollName)
            recordJSON = json.loads(recordJSON)
            if recordJSON.has_key('_id'):
                recordJSON['_id']=ObjectId(recordJSON['_id'])
            db = self._dbconnection['%s' % (dbName,)]
            coll = db['%s' % (dbCollName)]
            allResults = coll.remove(recordJSON)
            return allResults
        finally :
            if db :
                self._dbconnection.end_request() 

