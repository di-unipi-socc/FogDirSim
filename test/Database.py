import pymongo as pm 

class Database():
    def __init__(self, username, password, host, port):
        self.client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (username, password, host, port))
    
    