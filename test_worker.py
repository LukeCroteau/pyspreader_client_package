'''
Development Test Module for SpreadWorker
'''
import argparse
import datetime
from dotenv import load_dotenv
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

class WorkerSaysYes(SpreadWorker):
    ''' A simple subclass that always returns True for our tasks '''
    def do_task(self, task_params: str) -> bool:
        return True

def scan_thing(wrkr, params):
    ''' A simple Scan method '''
    print(str.format('{} - Scanned! - Params: {}', datetime.datetime.now(), params))

if __name__ in ('__main__', 'test_worker'):
    parser = argparse.ArgumentParser(prefix_chars='/')
    parser.add_argument('/id', required=True)
    xargs = parser.parse_args()

    print('*******************************')
    worker = WorkerSaysYes(debug=True, id=xargs.id)
    print('SpreadWorker: ', worker)

    worker.register_simple_scanner(scan_thing, 2)

    print('Starting...')
    worker.start()

    print('Waiting for Client to close process...')
    worker.wait_for_worker_close()

    print('Finished')
