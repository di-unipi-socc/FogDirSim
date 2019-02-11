import os
db_username = os.environ.get('DB_USER', 'alessandro')
db_password = os.environ.get('DB_PSW', 'FogDirector')
db_host = os.environ.get('DB_HOST', 'localhost') 
#db_host = "server.apagiaro.it"
db_port = int(os.environ.get('DB_PORT', 27017))

