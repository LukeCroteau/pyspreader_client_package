'''
Development Test Module for SpreadWorker
'''
import argparse
import datetime
import random
from dotenv import load_dotenv
from pyspreader.worker import SpreadWorker
load_dotenv(verbose=True)

class WorkerSaysYes(SpreadWorker):
    ''' A simple subclass that always returns True for our tasks '''
    def do_task(self, task_params: str) -> bool:
        return True

def scan_thing(wrkr, params):
    '''
    A simple Scan method
    Occasionally it should add a new task to the database.
    This call will fail unless you've added USELESS_ACCESS_CODE to your job access code list.
    '''
    print(str.format('{} - Scanned! - Worker: {}, Job Params: {}', datetime.datetime.now(), wrkr, params))
    randx = random.randrange(100)
    print('Random number was ', randx)
    if randx < 25:
        newid = wrkr.task_add_new('TEST_TASK', '', 'USELESS_ACCESS_CODE')
        if newid != 0:
            wrkr.task_log_debug(str.format('Added new task with ID {}', newid))
        else:
            wrkr.task_log_error('Task Add Failed!')


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
