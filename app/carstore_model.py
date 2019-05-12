"""
A model for car store.
"""
import os
import decimal
from sqlalchemy import Column, CheckConstraint
from sqlalchemy.types import *
from sqlalchemy.dialects.postgresql.ranges import NUMRANGE
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


_DBPG_HOST = os.environ['CARSTORE__DBPG_HOST']
_DBPG_PORT = os.environ['CARSTORE__DBPG_PORT']
_DBPG_NAME = os.environ['CARSTORE__DBPG_NAME']
_DBPG_USER = os.environ['CARSTORE__DBPG_USER']
_DBPG_PASSWORD = os.environ['CARSTORE__DBPG_PASSWORD']


class UINTConstraintError(Exception):
	pass


def _constraint_uint(name, num_bits):
	"""
	To add constraint for uint64/32/16/8.
	"""
	if num_bits not in [8, 16, 32, 64]:
		raise UINTConstraintError('Wrong number of bits.')
	return CheckConstraint(	'{name} >= 0 AND {name} < {max_num}'.format(name=name, max_num = 2 ** num_bits), 
							name='{}_positive'.format(name))


Base = declarative_base()


class Car(Base):
	"""
	A car model.
	"""

	__tablename__ = 'car'
	# center where car is located
	serial_number = Column(NUMERIC, nullable=False, primary_key=True)
	location_center_id = Column(NUMERIC, index=True)
	owner_name = Column(String)
	model_year = Column(NUMERIC)
	code = Column(String)
	vehicle_code = Column(String)
	engine__capacity = Column(Integer)
	engine__num_cylinders = Column(SmallInteger)
	fuel_figures__speed = Column(Integer)
	fuel_figures__mpg = Column(Float)
	fuel_figures__usage_description = Column(String)
	performance_figures__octane_rating = Column(Integer)
	performance_figures__acceleration__mph = Column(Integer)
	performance_figures__acceleration__seconds = Column(Float)
	manufacturer = Column(String)
	__table_args__ = (
		_constraint_uint('location_center_id', 32),
		_constraint_uint('serial_number', 64),
		_constraint_uint('model_year', 64),
		_constraint_uint('engine__capacity', 16),
		_constraint_uint('engine__num_cylinders', 8),
		_constraint_uint('fuel_figures__speed', 16),
		_constraint_uint('performance_figures__octane_rating', 16),
		_constraint_uint('performance_figures__acceleration__mph', 16)
	)


def get_engine():
	"""
	Get SQLAlchemy engine for car DB.
	"""
	connect_arg = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(	\
		user=_DBPG_USER,
		password=_DBPG_PASSWORD,
		host=_DBPG_HOST,
		port=_DBPG_PORT,
		name=_DBPG_NAME)

	engine = create_engine(connect_arg)
	return engine


def _get_session(*, autocommit=False):
	"""
	Get SQLAlchemy session for car DB.
	"""
	engine = get_engine()
	Session = sessionmaker(bind=engine, autocommit=autocommit)
	session = Session()
	return session


def _change_json_types(d, supported_json_types, replace_types):
	"""
	Core function (without predifined arguments) for fixing model fields to make 
	it serializable.
	"""	
	out_d = {}
	for key, val in d.items():
		type_of = type(val)
		if type_of in supported_json_types:
			replace_val = d[key]
			if type_of in replace_types:
				replace_val = replace_types[type_of](replace_val)
			out_d[key] = replace_val

	return out_d


def _as_json_types(d):
	"""
	Fixing (changling/removing) model fields to make it serializable.
	"""	
	return _change_json_types(d, (decimal.Decimal, float, int, str), {decimal.Decimal: int})


def get_car(*, serial_number):
	"""
	Getting a car data by it's serial number.
	"""	
	session = _get_session()
	car_data = session.query(Car).filter_by(serial_number=serial_number).scalar()
	result = _as_json_types(car_data.__dict__) if car_data is not None else None
	return result


def save_car(car_data):
	"""
	Saving the information about a car. All fields are required.
	"""
	session = _get_session(autocommit=True)
	car = Car(**car_data)
	session.merge(car)
	session.flush()


def delete_car(*, serial_number):
	"""
	Delete a car by a serial number (it is used by test).
	"""
	session = _get_session(autocommit=True)
	session.query(Car).filter_by(serial_number=serial_number).delete()
	session.flush()