#!/bin/bash
set -e

for i in $(seq 0 9); do
    isolate --cg --init --box-id=$i
done

exec python3 -m fastapi run app/main.py --host 0.0.0.0 --port 8000
