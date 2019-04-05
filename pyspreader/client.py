'''
Primary Client module for Spreader
'''
import datetime
import platform
import psutil
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

class SpreadClient:
    '''
    Main Client
    '''
    _engine = None
    _session = None
    debug_mode = False
    __current_agent_id = None

    _client_version_string = '0.0.1a1'
    agent_name = ''

    def __init__(self, **kwargs):
        if 'debug' in kwargs:
            self.debug_mode = kwargs['debug']
            self.debug_log('Debug Mode')

        self._engine = create_engine(kwargs['connection_string'],
            connect_args={'application_name': str.format('Python Ref Client {}', self._client_version_string)},
            convert_unicode=True)
        self._session = scoped_session(sessionmaker(autocommit=False,
            autoflush=False,
            bind=self._engine))

    def debug_log(self, log_string):
        '''
        Default Logging to Console
        '''
        if self.debug_mode:
            print(str.format('{} - {}', datetime.datetime.now(), log_string))

    def _call_stored_procedure_with_output(self, procedure_name, *args):
        connection = self._engine.raw_connection()
        result = None
        try:
            cursor = connection.cursor()
            result = cursor.callproc(procedure_name, args)
            cursor.fetchall()
            cursor.close()
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        return result

    def _call_stored_procedure(self, procedure_name, *args):
        self._call_stored_procedure_with_output(procedure_name, *args)

    def connect(self):
        '''
        Calls initial agent_init Stored Procedure
        '''
        self.debug_log('Initializing')
        if self.agent_name == '':
            self.agent_name = 'Python Ref Client'
        __current_agent_id = self._call_stored_procedure_with_output('agent_init', platform.node(), self.agent_name,
                psutil.cpu_count(), psutil.virtual_memory().total // 1048576)
