"""
An intermideate file to test SQLAlchemy. The file can be deleted now.
"""


from carstore_model import get_car, save_car
import random


def _new_car_data():
	car_data = {	
		'serial_number': 18446744073709551615,
		'location_center_id': 4294967295,
		'owner_name': 'sergzach',
		'model_year': 18446744073709551615,
		'code': '123' * 20,
		'vehicle_code': '123' * 20,
		'engine__capacity': 65535,
		'engine__num_cylinders': 255,
		'fuel_figures__speed': 65535,
		'fuel_figures__mpg': 123.123,
		'fuel_figures__usage_description': '123' * 20,
		'performance_figures__octane_rating': 65535,
		'performance_figures__acceleration__mph': 65535,
		'performance_figures__acceleration__seconds': 123.123,
		'manufacturer': '123' * 20
	}
	return car_data


def test_add():
	car_data = _new_car_data()
	save_car(car_data)




def main():
	"The entry point for 2 tests."
	test_add()


if __name__ == '__main__':
	main()