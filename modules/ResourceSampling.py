import pymongo as pm
import time, json
import SECRETS as config

client = pm.MongoClient("mongodb://%s:%s@%s:%d" % (config.db_username, 
                                                   config.db_password, 
                                                   config.db_host, 
                                                   config.db_port))
db = client.realDatabase

def RandomSample(time, devid):
    return 