'''
Development Test Module
'''
import os
from dotenv import load_dotenv
from pyspreader.client import SpreadClient, MSSQLSpreadClient
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

cli = MSSQLSpreadClient(connection_string=os.environ.get('SPREADER_LIVE_DSN'), debug=True)
cli.agent_name = 'Test Agent'
agentid = cli.connect()

print('Current Agent ID is', agentid)

tmp = SpreadWorker()
print('SpreadWorker: ', tmp)

print('Finished')
