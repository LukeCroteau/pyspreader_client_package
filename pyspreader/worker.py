'''
Worker module for Spreader
New Workers would create a subclass from here, and implement the required methods.
'''
import argparse
import threading

class SpreadWorker:
    '''
    Main Worker Class
    '''

    __transfer_lock = threading.Lock()
    __socket = None
    __last_keep_alive = None
    __job_id = None
    __port = None

    def __init__(self, **kwargs):
        parser = argparse.ArgumentParser(prefix_chars='/')
        parser.add_argument('/id', required=True)
        xargs = parser.parse_args()
        self.__job_id = xargs.id

        if 'port' in kwargs:
            self.__port = int(kwargs['port'])
        else:
            self.__port = 21200

        print('Job ID = ', self.__job_id)

    def __repr__(self):
        return str.format('<SpreadWorker, Job {}, Port {}>', self.__job_id, self.__port)

    def __read_response(self):
        with self.__transfer_lock:
            #response =
            pass
