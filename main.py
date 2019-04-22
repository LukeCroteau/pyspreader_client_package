'''
Development Test Module
'''
# import os
import time
from dotenv import load_dotenv
#from pyspreader.client import SpreadClient, MSSQLSpreadClient
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

if __name__ == '__main__':
    # cli = MSSQLSpreadClient(connection_string=os.environ.get('SPREADER_LIVE_DSN'), debug=True)
    # cli.agent_name = 'Test Agent'
    # agentid = cli.connect()

    # print('Current Agent ID is', agentid)

    print('*******************************')
    tmp = SpreadWorker(debug=True)
    print('SpreadWorker: ', tmp)

    print('Starting...')
    tmp.start()

    print('Waiting 5 seconds...')
    time.sleep(5)

    input('Press Enter to Stop\n')

    print('Stopping...')
    tmp.log_debug('Stopping Worker')
    tmp.stop()

    print('Finished')
