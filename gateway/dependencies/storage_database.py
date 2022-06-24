from nameko.extensions import DependencyProvider

import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
import hashlib
import uuid

def hash_password(password, salt):
    pepper = "informatika_ya_petra:)"
    return hashlib.sha256(password.encode() + pepper.encode() + salt.encode()).hexdigest()

class StorageDatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection
    
    def upload(self, username, hash_name, real_name):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute("SELECT * FROM file WHERE owner = %s AND name = %s ORDER BY version DESC", (username, real_name))
        res = cursor.fetchone()
        if res:
            cursor.execute("INSERT INTO file (owner, path, name, version) VALUES (%s, %s, %s, %s)", (username, hash_name, real_name, res[4] + 1))
        else:   
            cursor.execute("INSERT INTO file (owner, path, name, version) VALUES (%s, %s, %s, %s)", (username, hash_name, real_name, 1))
        self.connection.commit()
    
    def download(self, username, filename):
        cursor = self.connection.cursor(buffered=True)
        cursor.execute("SELECT * FROM file WHERE owner = %s AND name = %s ORDER BY version DESC", (username, filename))
        result = cursor.fetchone()
        if result:
            return result[2]
        else:
            return False

    
class StorageDatabase(DependencyProvider):

    connection_pool = None

    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="database_pool",
                pool_size=5,
                pool_reset_session=True,
                host='localhost',
                database='cloud_storage_db',
                user='root',
                password=''
            )
        except Error as e :
            print ("Error while connecting to MySQL using Connection pool ", e)
    
    def get_dependency(self, worker_ctx):
        return StorageDatabaseWrapper(self.connection_pool.get_connection())
    
    



