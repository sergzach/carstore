## How to start carstore_app test
* Setup requirements from `src`: `pip3 install -r requirements.txt`.
* Setup carserver.py from `src`: `python3 setup.py install`.
* Add environment variables from `run/env.txt`. Fix ports to carserver.py/PostgreSQL for other settings.
* Setup PostgreSQL and adjust `pg_hba.conf` settings as in `run/env.txt` (env. variables start with `CARSTORE__DBPG`).
* Run `cd src && python3 create_db.py` to create a database.
* Run `run/server.sh`. Fix the options if mentioned ports are unavailable.
* Run `run/test_client.sh`. Fix the options if mentioned ports are unavailable.


## Source files
* `app/capstore_app.py` — a particular application which have on_response() calling from server.py.
* `app/capstore_model.py` — a model (for PostgreSQL) to store the information about cars.
* `src/server.py` — a socket server which can pick up any response module (an application).
* `src/test_client.py` — a program with client which make simple requests to server and prints the server answer.
* `src/create_db.py` — code to create database (PostgreSQL) schema. Just for an intermediate test.


## Notes
A Python file with an application must be located in the same directory where carserver.py script starts. For more details see `run/server.sh` please.
