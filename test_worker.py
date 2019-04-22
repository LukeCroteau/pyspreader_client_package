'''
Development Test Module for SpreadWorker
'''
import argparse
import datetime
from dotenv import load_dotenv
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

def scan_thing(wrkr, params):
    print(str.format('{} - Scanned! - Params: {}', datetime.datetime.now(), params))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prefix_chars='/')
    parser.add_argument('/id', required=True)
    xargs = parser.parse_args()

    print('*******************************')
    worker = SpreadWorker(debug=True, id=xargs.id)
    print('SpreadWorker: ', worker)

    worker.register_simple_scanner(scan_thing, 2)

    print('Starting...')
    worker.start()

    print('Waiting for Client to close process...')
    worker.wait_for_worker_close()

    print('Finished')
