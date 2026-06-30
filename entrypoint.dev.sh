#!/bin/bash
set -e

for i in $(seq 0 9); do
    isolate --init --box-id=$i
done

echo "JavaScript: $(node -v 2>&1)"
echo "Python: $(python3 -V 2>&1)"
echo "C++: $(g++ --version | head -n 1)"
echo "Java: $(java -version 2>&1 | head -n 1)"

exec python3 -m fastapi dev app/main.py --host 0.0.0.0 --port 8000