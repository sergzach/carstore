"""
A server application which can pick up any response module (an application).
"""

import sys
import os
from functools import partial
from contextlib import contextmanager
from importlib import import_module
import json
from time import time
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import select
import signal
import argparse


_LOG_DT_FORMAT = '%m/%d/%Y %H:%M:%S'
_DEFAULT_POLL_TIMEOUT = 1
_MSG_STARTED = 'Started at {host}:{port}.'
_MSG_HANDLING_EXCEPTION = 'Exception when handling client {client}: {exception}.'
_MSG_RESPONSE_EXCEPTION = 'Exception in on_response: {exception}'

_HOST = os.environ['CARSTORE_HOST']
_PORT = int(os.environ['CARSTORE_PORT'])


def _log(s):
	dt = datetime.now().strftime(_LOG_DT_FORMAT)
	print('{}: {}'.format(dt, s))


def _warn(s):
	_log('WARNING {}'.format(s))


class ReadTimeout(Exception):
	"""
	It occurs when a server waits more then timeout on a read operation.
	"""


class TCPServer:
	"""
	A class of a tcp-socket server.
	"""
	_END_REQUEST = b'\0'
	_RESPONSE_FUNCTION_NAME = 'on_response'
	_ANSWER_OK = {'answer': 'ok'}
	_ANSWER_FAIL = {'answer': 'fail'}
	_ANSWER_NOT_FOUND = {'answer': 'not_found'}

	def __init__(	self,
					host, 
					port, 
					max_connections, 
					buf_size, 
					response_module_name, 
					max_read_time, 
					poll_timeout):
		"""
		The class constructor.
		Parameters
		----------
		host: str
			Server host.
		port: int
			Server port.
		max_connections: int
			Number of maximum clients which can wait in a queue.
		buf_size: int
			Maximum length of client packet.
		response_module_name: type str
			A module to process_data which must be importable (in a current container).
		max_read_time: int
			Maximum time to read client response (milliseconds)
		poll_timeout: int
			Number of milliseconds to check socket for incomming connections for a client.
		"""
		self._host = host
		self._port = port
		self._max_connections = max_connections
		self._buf_size = buf_size
		self._response_module_name = response_module_name
		self._max_read_time_secs = max_read_time / 1000.0
		self._poll_timeout = poll_timeout	


	def serve(self):
		"""
		Start server sharing it's port.
		Several instances can work together on the same port.
		"""
		self._register_exit()
		self._append_workdir()
		self._import_process_module()
		for msg in self._loop():
			yield msg


	def _register_exit(self):
		"""
		Register exit to try to release resources on SIGTERM or SIGKILL.
		"""
		signal.signal(signal.SIGINT, self._exit)
		signal.signal(signal.SIGTERM, self._exit)


	def _exit(self, signum, frame):
		self._is_working = False


	@staticmethod
	def _append_workdir():
		sys.path.append(os.getcwd())



	def _import_process_module(self):
		"""
		Import a process module.
		"""		
		module = import_module(self._response_module_name)
		self._response_callback = getattr(module, self._RESPONSE_FUNCTION_NAME)


	def _send(self, client, msg):
		msg = json.dumps(msg)
		msg = msg.encode()
		client.send(msg + self._END_REQUEST)


	def _loop(self):
		"""
		The main serving loop.
		"""
		# TCP socket without waiting 'natural' timeout to wait OS socket releasing 
		# before starting the next server session
		server = socket(AF_INET, SOCK_STREAM)
		server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		# 'not blocking' to reject reading from client if the operation is too long
		server.setblocking(False)
		server.bind((self._host, self._port))
		server.listen(self._max_connections)		
		
		with self._poll_obj(server) as poller:
			self._is_working = True

			while self._is_working:				
				events = poller.poll(self._poll_timeout)

				for desc, event in events:
					client, addr = server.accept()
					data = b''
					self._reset_read_time()
					try:											
						while data == b'' or data[-1] != ord(self._END_REQUEST):
							self._check_read_time()
							data += client.recv(self._buf_size)
					except Exception as e:
						yield _warn(_MSG_HANDLING_EXCEPTION.format(client=client, exception=e))
					else:
						# truncate 'end' byte
						data = data[:-1]
						data = data.decode()
						send = partial(self._send, client)
						try:
							answer = self._response_callback(data)												
						except Exception as e:
							yield _warn(_MSG_RESPONSE_EXCEPTION.format(exception=e))
							send(self._ANSWER_FAIL)
						else:
							if answer is True:
								send(self._ANSWER_OK)
							elif answer is None:
								send(self._ANSWER_NOT_FOUND)
							else:
								send(answer)
					finally:
						client.close()


	@contextmanager
	def _poll_obj(self, server):
		"""
		A contextlib method to unregister poller in case of exception.
		Parameters
		----------
		server: Socket object
			A server socket object.
		"""
		poller = select.poll()
		poller.register(server, select.POLLIN)
		try:
			yield poller
		finally:
			poller.unregister(server)


	def _reset_read_time(self):
		"""
		Reset read time (call in beginning waiting the whole packet from a client).
		"""
		self._read_start = time()


	def _check_read_time(self):
		"""
		Check read time and raise a ReadTimeout if read time is more then read timeout.
		"""
		if time() > self._read_start + self._max_read_time_secs:
			raise ReadTimeout()



def _create_arg_parser():
	"""
	Call to parse user command-line options.
	"""
	parser = argparse.ArgumentParser()
	# run-build options
	parser.add_argument('--max-connections', type=int, 
		help='max client connections waiting in a queue', required=True)
	parser.add_argument('--buff-size', type=int, 
		help='maximum buffer size for a client packet', required=True)
	parser.add_argument('--response-module', type=str, 
		help='a module name in which on_response placed (application)', required=True)
	parser.add_argument('--max-read-time', type=int, 
		help='maximum time to read client response (milliseconds)', required=True)
	parser.add_argument('--poll_timeout', type=int, 
		help='maximum polling time to check new clients (to response on SIGTERM or SIGINT)', 
		default=_DEFAULT_POLL_TIMEOUT)

	return parser.parse_args()


def main():
	"""
	The entry point.
	"""
	args = _create_arg_parser()
	tcp_server = TCPServer(	_HOST,
							_PORT, 
							args.max_connections, 
							args.buff_size, 
							args.response_module, 
							args.max_read_time, 
							args.poll_timeout)
	_log(_MSG_STARTED.format(host=_HOST, port=_PORT))
	for msg in tcp_server.serve():
		_log(msg)


if __name__ == '__main__':
	main()
