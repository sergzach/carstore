from setuptools import setup

setup(
    name='carserver',
    python_requires=">=3.0",
    version='0.0.1',
    description='Carserver '
                'A server application which can pick up any response module (an application) '
                'in a current directory.',
    author='Sergey Zakharov',
    author_email='sergzach@gmail.com',
    scripts=['carserver.py'],
    setup_requires=['psycopg2'],
    tests_require=['pytest']
)
