"""
A response module for car store.
"""
import json
from carstore_model import get_car, save_car, delete_car

_FIELD_ACTION = 'action'
_FIELD_CAR_DATA = 'car_data'
_FIELD_SERIAL_NUMBER = 'serial_number'
_ACTION_GET = 'get'
_ACTION_SAVE = 'save'
_ACTION_DELETE = 'delete'


class ResponseFormatError(Exception):
	"""
	It raises when format of client request is wrong.
	"""
	pass


def on_response(data):
	"""
	A response function for carstore application.
	"""
	data = json.loads(data)
	action = data[_FIELD_ACTION]	
	if action == _ACTION_GET:
		serial_number = int(data[_FIELD_SERIAL_NUMBER])
		car_data = get_car(serial_number=serial_number)
		return car_data
	elif action == _ACTION_SAVE:
		car_data = data[_FIELD_CAR_DATA]
		car_data[_FIELD_SERIAL_NUMBER] = data[_FIELD_SERIAL_NUMBER]
		save_car(car_data)
		return True
	elif action == _ACTION_DELETE:
		serial_number = int(data[_FIELD_SERIAL_NUMBER])
		delete_car(serial_number=serial_number)
		return True
	else:
		raise ResponseFormatError('Wrong data format from client.')