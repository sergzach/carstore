## Task Description
Write client-server application.

Use case: application which is used in car centers to store information
about sold cars. At first application will be used in a single car center then
all centers in town/city/world will use it to store information. It should be
possible to retrieve info about any sold car by serialNumber.
Clients pass to server an Object “Car” with following attributes:
```
   "ownerName" type="string"
   "serialNumber" type="uint64"
   "modelYear" type="uint64"
   "code" type="string"
   "vehicleCode" type="string"
   "engine"
       "capacity" type="uint16"
       "numCylinders" type="uint8"
       "maxRpm" type="uint16"
       "manufacturerCode" type="char"
   "fuelFigures"
       "speed" type="uint16"
       "mpg" type="float"
       "usageDescription" type="string"
   "performanceFigures"
       "octaneRating" type="uint16"
       "acceleration"
         "mph" type="uint16"
         "seconds" type="float"
   "manufacturer" type="string"   "model" type="string"
   "activationCode" type="string"
```
Server saves the information persistently.


# How to start carstore_app test
* Setup requirements from src: `pip3 install -r requirements.txt`.
* Setup carserver.py from src: `python3 setup.py install`.
* Add environment variables from `run/env.txt`. Fix ports to carserver.py/PostgreSQL for other settings.
* Setup PostgreSQL and adjust `pg_hba.conf` settings as in `run/env.txt` (env. variables start with `CARSTORE__DBPG`).
* Run `cd src && python3 create_db.py` to create a dabase.
* Run `run/server.sh`. Fix the options if mentioned ports are unavailable.
* Run `run/test_client.sh`. Fix the options if mentioned ports are unavailable.


# Source files
* `src/server.py` — a socket server which can pick up any response module (an application).
* `src/capstore_app.py` — a particular application which have on_response() calling from server.py.
* `src/capstore_model.py` — a model (for PostgreSQL) to store the information about cars.
* `src/test_client.py` — a program with client which make simple requests to server and prints the server answer.
* `src/create_db.py` — code to create database (PostgreSQL) schema. Just for an intermediate test.


# Notes
A Python file with an application must be located in the same directory where carserver.py script starts. For more details see `run/server.sh` please.
