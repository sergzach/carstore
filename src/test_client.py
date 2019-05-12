"""
A simple client sending requests to working server and output server answers.
It's not a classical test but very simple one.
"""

import os
from functools import partial
from random import choice, randint, random
from string import ascii_letters
import json
import asyncio
import argparse
import pytest


# total number of test loops
_NUM_SUBTESTS = 100
# end byte
_END_REQUEST = b'\0'
# reading timeout in milliseconds
_READ_TIMEOUT = 1000
# testing server host
_HOST = os.environ['CARSTORE_HOST']
# testing server port
_PORT = os.environ['CARSTORE_PORT']


@asyncio.coroutine
def _test_client(*, host, port, loop):
	"""
	Send car data, retrieve car data and publish answers of a server.
	"""
	send = asyncio.coroutine(partial(_send, host=host, port=port, loop=loop))

	for i in range(_NUM_SUBTESTS):
		# insert random car
		car_data = _create_car_data()
		request_data = _pack_request_data(action=_PackActions.SAVE, car_data=car_data)
		msg = _dict_as_bytes(request_data)
		answer = yield from send(msg=msg)
		assert answer['answer'] == 'ok'
		yield answer
		# request inserted car by serial_number
		serial_number = request_data['serial_number']
		request_data = _pack_request_data(action=_PackActions.GET, serial_number=serial_number)
		msg = _dict_as_bytes(request_data)
		answer = yield from send(msg=msg)
		assert len(answer) > 0 and 'answer' not in answer
		yield answer
		# delete inserted car to roll DB back
		request_data = _pack_request_data(action=_PackActions.DELETE, serial_number=serial_number)
		msg = _dict_as_bytes(request_data)
		answer = yield from send(msg=msg)
		assert answer['answer'] == 'ok'
		yield answer
		# check if inserted car has been deleted
		request_data = _pack_request_data(action=_PackActions.GET, serial_number=serial_number)
		msg = _dict_as_bytes(request_data)
		answer = yield from send(msg=msg)
		assert answer['answer'] == 'not_found'
		yield answer



def _parse_answer(answer):
	"""
	Get answer as dict.
	"""
	return json.loads(answer[:-1].decode())


@asyncio.coroutine
def _send(*, host, port, loop, msg):
	"""
	Send msg to host port via TCP and return the server answer.
	"""
	reader, writer = yield from asyncio.open_connection(host, port, loop=loop)
	writer.write(msg + _END_REQUEST)
	try:
		answer = yield from asyncio.wait_for(reader.readuntil(_END_REQUEST), timeout=_READ_TIMEOUT)
	except asyncio.TimeoutError:
		return None
	else:
		return _parse_answer(answer)
	finally:
		writer.close()		


def _create_car_data():
	"""
	Create fields for data but 'action' and 'serial_number' fields.
	"""
	car_data = {}	
	car_data['location_center_id'] = randint(0, 65535)
	car_data['owner_name'] = choice(['John', 'Mikhail', 'Anna', 'Claire', 'Sergey'])	
	car_data['model_year'] = randint(0, 65536)
	car_data['code'] = ''.join([choice(ascii_letters) for _ in range(32)])
	car_data['vehicle_code'] = ''.join([choice(ascii_letters) for _ in range(64)])
	car_data['engine__capacity'] = randint(1, 64)
	car_data['engine__num_cylinders'] = choice(range(4, 33, 2))
	car_data['fuel_figures__speed'] = randint(1, 64)
	car_data['fuel_figures__mpg'] = randint(1, 64)
	car_data['fuel_figures__usage_description'] = 'Empty description.'
	car_data['performance_figures__octane_rating'] = choice([60, 62, 88, 90])
	car_data['performance_figures__acceleration__mph'] = randint(100, 250)
	car_data['performance_figures__acceleration__seconds'] = randint(5, 30) + random()
	car_data['manufacturer'] = 'Empty manufacturer.'	

	return car_data	


class _PackActions:
	"""
	A class to pass as action instance into _pack_request_data.
	"""
	GET = 0
	DELETE = 1
	SAVE = 2


def _pack_request_data(*, action, car_data=None, serial_number=None):
	"""
	Pack to full request data with 'action' and 'serial_number' fields.
	"""
	request_data = {}
	
	if action == _PackActions.GET:		
		request_data['action'] = 'get'
	elif action == _PackActions.DELETE:
		request_data['action'] = 'delete'
	elif action == _PackActions.SAVE:
		request_data['action'] = 'save'
		request_data['car_data'] = car_data
	request_data['serial_number'] = randint(10000, 1000000) if serial_number is None else serial_number

	return request_data


def _dict_as_bytes(data):
	return json.dumps(data).encode()


@asyncio.coroutine
def _main(loop):
	for msg in _test_client(host=_HOST, port=_PORT, loop=loop):
		if isinstance(msg, asyncio.Future):
			yield from msg
		else:
			# when msg is None there is reading timeout
			assert msg is not None
			print(msg)


def test_main():
	"""
	The entry point.
	"""
	loop = asyncio.get_event_loop()
	loop.run_until_complete(_main(loop))
	loop.close()

