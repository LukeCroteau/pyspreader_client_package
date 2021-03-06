'''
Development Test Module
'''
# import os
import argparse
from dotenv import load_dotenv
#from pyspreader.client import SpreadClient, MSSQLSpreadClient
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

if __name__ == '__main__':
    # cli = MSSQLSpreadClient(connection_string=os.environ.get('SPREADER_LIVE_DSN'), debug=True)
    # cli.agent_name = 'Test Agent'
    # agentid = cli.connect()

    # print('Current Agent ID is', agentid)

    parser = argparse.ArgumentParser(prefix_chars='/')
    parser.add_argument('/id', required=True)
    xargs = parser.parse_args()

    print('*******************************')
    worker = SpreadWorker(debug=True, id=xargs.id)
    print('SpreadWorker: ', worker)

    print('Starting...')
    worker.start()

    print('Waiting for Client to close process...')
    worker.wait_for_worker_close()

    print('Finished')
