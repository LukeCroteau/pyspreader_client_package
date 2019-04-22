'''
Worker module for Spreader
New Workers would create a subclass from here, and implement the required methods.
'''
from multiprocessing import Process, Queue, Lock
import datetime
import queue
import socket
from socket import timeout
import time

SPREADER_LOG_DEBUG = 0
SPREADER_LOG_MESSAGE = 1
SPREADER_LOG_WARNING = 2
SPREADER_LOG_ERROR = 3
SPREADER_LOG_FATAL = 4

SPREADER_WORKER_PING_LIMIT_IN_SECONDS = 180
SPREADER_WORKER_TIMEOUT_LIMIT_IN_SECONDS = 600

def encode_params(decoded_data: str) -> str:
    ''' Prepare data for Spreader Interop '''
    return decoded_data.replace('|', '&#124;').replace('\r\n', '&#13;&#10;')

def decode_params(encoded_data: str) -> str:
    ''' Decode Parameter data from Spreader Interop '''
    return encoded_data.replace('&#124;', '|').replace('&#13;&#10;', '\r\n')

def output_to_console(log_message):
    ''' Write a message to Console '''
    print(str.format('{} - {}', datetime.datetime.now(), log_message))

class SpreadWorker:
    '''
    Main Worker Class
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, **kwargs):
        self.__transfer_lock = None
        self.__last_keep_alive = None
        self.__command_queue = Queue()
        self.__running = False
        self.__last_keep_alive = None
        self.debug_mode = False
        self.__registered_simple_scanners = []
        self.__job_parameters = ''
        self.__accesscodes = []

        if 'debug' in kwargs:
            self.debug_mode = kwargs['debug']
        if self.debug_mode:
            self.__log_debug('Debug Mode', False)

        if 'id' in kwargs:
            self.__worker_id = kwargs['id']
        else:
            raise Exception('You must specify a Worker ID.')

        self.__process = None

        if 'port' in kwargs:
            self.__port = int(kwargs['port'])
        else:
            self.__port = 21200

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(0.25)

        self.__log_debug(str.format('Worker ID = {}, Port = {}', self.__worker_id, self.__port), False)

    def __log_debug(self, log_string, log_to_client=True):
        ''' Log a Debug string to Console and Client '''
        if self.debug_mode:
            output_to_console(log_string)
            if log_to_client:
                self.__send_log_debug(log_string)

    def __log_message(self, log_string):
        ''' Log a Message to Console and Client '''
        output_to_console(log_string)
        self.__send_log_message(log_string)

    def __log_warning(self, log_string):
        ''' Log a Warning to Console and Client '''
        output_to_console(log_string)
        self.__send_log_warning(log_string)

    def __log_error(self, log_string):
        ''' Log an Error to Console and Client '''
        output_to_console(log_string)
        self.__send_log_error(log_string)

    def __log_fatal(self, log_string):
        ''' Log a Fatal message to Console and Client '''
        output_to_console(log_string)
        self.__send_log_fatal(log_string)

    def __repr__(self):
        return str.format('<SpreadWorker, WorkerID {}, Port {}>', self.__worker_id, self.__port)

    def __read_response(self):
        with self.__transfer_lock:
            #response =
            pass

    def __send_to_socket(self, command, data=''):
        self.__log_debug(str.format('Sending to socket, Command {}, Data {}', command, data), False)
        with self.__transfer_lock:
            output = command + '|' + self.__worker_id + '|' + data + '\r\n'
            self.__socket.send(output.encode())

    def __send_log(self, level, log_string):
        self.__send_to_socket('WKRLOG', str.format('{}|{}', level, encode_params(log_string)))

    def __send_log_debug(self, log_string):
        self.__send_log(SPREADER_LOG_DEBUG, log_string)

    def __send_log_message(self, log_string):
        self.__send_log(SPREADER_LOG_MESSAGE, log_string)

    def __send_log_warning(self, log_string):
        self.__send_log(SPREADER_LOG_WARNING, log_string)

    def __send_log_error(self, log_string):
        self.__send_log(SPREADER_LOG_ERROR, log_string)

    def __send_log_fatal(self, log_string):
        self.__send_log(SPREADER_LOG_FATAL, log_string)

    def __send_worker_start(self):
        self.__send_to_socket('WKRSTARTED')

    def __handle_client_ping(self):
        self.__send_to_socket('WKRPONG')

    def __handle_client_pong(self):
        self.__last_keep_alive = datetime.datetime.now()

    def __handle_client_init(self, params):
        self.__accesscodes = params.split('|')[0].split(';')
        self.__job_parameters = decode_params(params.split('|')[2])
        self.__send_to_socket('WKRINITIALIZED')

    def __handle_client_task(self, task_data):
        datasplit = task_data.split('|')
        taskid = datasplit[0]
        params = datasplit[1]
        success = False

        self.__send_to_socket('WKRTASKDONE', str.format('{}|{}', taskid, 1 if success else 0))

    def __parse_queue_command(self, data):
        ''' Internal Queue Parser. '''
        try:
            tmpidx = data.index('|')
        except ValueError:
            tmpidx = 0

        if tmpidx > 0:
            command = data[:tmpidx]
            params = data[tmpidx + 1:]
        else:
            command = data
            params = ''

        if command == 'QUIT':
            self.__running = False
        elif command == 'DEBUG':
            self.__log_debug(params)
        elif command == 'MESSAGE':
            self.__log_message(params)
        elif command == 'WARNING':
            self.__log_warning(params)
        elif command == 'ERROR':
            self.__log_error(params)
        elif command == 'FATAL':
            self.__log_fatal(params)
        else:
            self.__log_debug(str.format('** Unknown Command: {}', command), False)

    def __parse_client_data(self, data):
        ''' Main Client Data Parser '''
        self.__log_debug(str.format('Received Client Data: {}', data), False)
        try:
            tmpidx = data.index('|')
        except ValueError:
            tmpidx = 0

        if tmpidx > 0:
            command = data[:tmpidx]
            params = data[tmpidx + 1:]
        else:
            command = data
            params = ''

        if command == 'WKRPING':
            self.__handle_client_ping()
        elif command == 'WKRTASK':
            self.__log_debug(str.format('Received a Task! Params: {}', params), False)
            self.__handle_client_task(params)
        elif command == 'WKRPONG':
            self.__handle_client_pong()
        elif command == 'WKRINIT':
            self.__handle_client_init(params)
        elif command == 'WKRSTOP':
            self.__log_debug('Received Stop. Quitting.', False)
            self.__running = False
        else:
            self.__log_debug(str.format('Unknown Command {}, Quitting.', command), False)
            self.__running = False

    def __check_keep_alive(self):
        ''' Check to see if we've lost connection '''
        current = datetime.datetime.now()
        diff = current - self.__last_keep_alive
        diffinseconds = diff.total_seconds()
        if diffinseconds > SPREADER_WORKER_TIMEOUT_LIMIT_IN_SECONDS:
            self.__log_debug('Lost connection to Client', False)
        elif diffinseconds > SPREADER_WORKER_PING_LIMIT_IN_SECONDS:
            self.__send_to_socket('WKRPING')

    def __has_access(self, access_code):
        return access_code in self.__accesscodes

    def __do_scan(self):
        for idx in range(len(self.__registered_simple_scanners)):
            params = self.__registered_simple_scanners[idx]
            if (datetime.datetime.now() - params['last_run']).total_seconds() > params['loop_every']:
                params['method'](self, self.__job_parameters)
                params['last_run'] = datetime.datetime.now()

    def _command_loop(self, work_queue: Queue):
        ''' Method called by __process start/stop '''

        self.__log_debug('Connecting to Spreader Client via Localhost', False)
        self.__socket.connect(('localhost', self.__port))
        self.__transfer_lock = Lock()

        self.__last_keep_alive = datetime.datetime.now()
        self.__send_to_socket('WKRSTARTED')

        self.__log_debug('Starting Command Loop.', False)
        while self.__running:
            if not work_queue.empty():
                try:
                    n = work_queue.get(timeout=0.01)
                    self.__log_debug(str.format('Found Queue Item: {}', n), False)
                    self.__parse_queue_command(n)
                except queue.Empty:
                    self.__log_debug('Queue not empty, but no Queue item found. Waiting', False)

            try:
                with self.__transfer_lock:
                    data = self.__socket.recv(4096)
                self.__last_keep_alive = datetime.datetime.now()
                data = data.decode().strip()
                self.__parse_client_data(data)
            except (timeout, BlockingIOError):
                pass

            self.__check_keep_alive()

            if self.__has_access('SCAN'):
                self.__do_scan()

            time.sleep(0.25)
        self.__log_debug('** Command Loop Stopped.', False)

    def start(self):
        '''
        Start monitoring the Client for work
        '''
        if not self.__process:
            self.__running = True
            self.__process = Process(target=self._command_loop, args=(self.__command_queue,))
            self.__process.start()

    def wait_for_worker_close(self):
        '''
        Use this method in a Client implementation where you want to let the Worker dictate when to exit.
        WARNING: You will NOT be able to reclaim control until the main client disconnects the worker.
        '''
        if self.__process:
            self.__process.join()

    def stop(self):
        '''
        Adds a QUIT message to the __process queue, and waits for the process to stop
        '''
        if self.__process:
            self.__command_queue.put('QUIT')
            self.__process.join()

    def log_debug(self, log_message):
        ''' Adds a Debug message to the Local Queue '''
        self.__command_queue.put(str.format('DEBUG|{}', log_message))

    def log_message(self, log_message):
        ''' Adds a Message to the Local Queue '''
        self.__command_queue.put(str.format('MESSAGE|{}', log_message))

    def log_warning(self, log_message):
        ''' Adds a Warning to the Local Queue '''
        self.__command_queue.put(str.format('WARNING|{}', log_message))

    def log_error(self, log_message):
        ''' Adds an Error message to the Local Queue '''
        self.__command_queue.put(str.format('ERROR|{}', log_message))

    def log_fatal(self, log_message):
        ''' Adds a Fatal message to the Local Queue '''
        self.__command_queue.put(str.format('FATAL|{}', log_message))

    def register_simple_scanner(self, scan_method, loop_frequency=5):
        '''
        Registers a Simple Scanner method.
        The worker will execute your method every [loop_frequency] seconds.
        scan_method should be a method with two parameters:
            An object representing a SpreadWorker
            A string, which will contain the parameters for the Job
        '''
        self.__registered_simple_scanners.append({'loop_every': loop_frequency,
            'method': scan_method,
            'last_run': datetime.datetime.now()})
