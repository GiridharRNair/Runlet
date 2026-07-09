#!/bin/bash
set -e

# Delegate the memory controller down to isolate's cgroup root (see Dockerfile)
# so isolate can create per-box memory-accounted subgroups under it.
mkdir -p /sys/fs/cgroup/isolate
echo +memory > /sys/fs/cgroup/cgroup.subtree_control
echo +memory > /sys/fs/cgroup/isolate/cgroup.subtree_control

for i in $(seq 0 9); do
    isolate --cg --init --box-id=$i
done

exec python3 -m fastapi run app/main.py --host 0.0.0.0 --port 8000
