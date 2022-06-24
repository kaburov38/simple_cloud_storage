from MySQLdb import DatabaseError
from nameko.rpc import rpc

import account_database

class AccountService:
    
    name="account_service"

    database = account_database.AccountDatabase()

    @rpc
    def register(self, username, password):
        if(self.database.check_username_exist(username)):
            return False
        else:
            self.database.insert_user(username, password)
            return True
    
    @rpc
    def login(self, username, password):
        return self.database.check_login(username, password)
    
    @rpc 
    def is_username_exist(self, username):
        return self.database.check_username_exist(username)
