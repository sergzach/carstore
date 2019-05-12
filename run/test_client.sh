#!/bin/bash

CUR_DIR=$(dirname "$0")

cd $CUR_DIR/../src && python3 -m pytest test_client.py