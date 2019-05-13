'''
Development Test Module for SpreadClient
'''
import os
from dotenv import load_dotenv
from pyspreader.client import SpreadClient, MSSQLSpreadClient
load_dotenv(verbose=True)

if __name__ in ('__main__', 'test_client'):
    '''
    cli = SpreadClient(connection_string=os.environ.get('SPREADER_TEST_PG_DSN'), debug=True)
    cli.agent_name = 'Test Agent'
    agentid = cli.connect()

    print('Current PG Agent ID is', agentid)
    '''

    cliMS = MSSQLSpreadClient(connection_string=os.environ.get('SPREADER_TEST_MS_DSN'), debug=True)
    cliMS.agent_name = 'Test Agent'
    agentid = cliMS.connect()

    print('Current MS Agent ID is', agentid)

    print('Finished')
