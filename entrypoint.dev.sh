#!/bin/bash
set -e

for i in $(seq 0 9); do
    isolate --init --box-id=$i
done

exec python3 -m fastapi dev app/main.py --host 0.0.0.0 --port 8000