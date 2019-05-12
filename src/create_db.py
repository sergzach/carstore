"""
A file to create schema of database with help of SQLAlchemy.
"""

from carstore_model import get_engine, Base


def main():
	"""
	The entry point.
	"""
	engine = get_engine()
	Base.metadata.create_all(engine)


if __name__ == '__main__':
	main()