'''
Development Test Module
'''
import os
from dotenv import load_dotenv
from pyspreader.client import SpreadClient
load_dotenv(verbose=True)

cli = SpreadClient(connection_string=os.environ.get('SPREADER_LIVE_DSN'), debug=True)
cli.agent_name = 'Test Agent'
cli.connect()

print('Finished')
