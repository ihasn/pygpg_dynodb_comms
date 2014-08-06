This is just me testing a message transfer app via python.

Additional python modules needed are aws and gnupg.  pip install gnupg, pip install aws to set it up. 

Added option to search for keys from MIT's PGP server.

A valid AWS account with DynamoDB access is required.  Currently DynamoDB table is hardcoded to 'comms'

To operate use the follow:

$ python dynodb.py

Follow the prompts
