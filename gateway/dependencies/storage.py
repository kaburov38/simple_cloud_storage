from MySQLdb import DatabaseError
from nameko.rpc import rpc
import pickle
import werkzeug
import uuid
import sys

import storage_database

class StorageService:
    
    name="storage_service"

    database = storage_database.StorageDatabase()

    @rpc
    def upload(self, username, hash_name, real_name):
        return self.database.upload(username, hash_name, real_name)
    
    @rpc
    def download(self, username, filename):
        return self.database.download(username, filename)
