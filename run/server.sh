#!/bin/bash

CUR_DIR=$(dirname "$0")

cd $CUR_DIR/../app && \
carserver.py	--max-connections=32 --buff-size=4096 \
				--response-module=carstore_app --max-read-time=2000 --poll_timeout=1