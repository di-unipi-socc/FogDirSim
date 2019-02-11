import os
db_username = "alessandro"
db_password = "FogDirector"
db_host = "localhost" 
#db_host = "server.apagiaro.it"
db_port = int(os.environ.get('DB_PORT', 27017))
