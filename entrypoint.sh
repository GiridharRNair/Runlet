#!/bin/bash
set -e

# Delegate the memory controller down to isolate's cgroup root (see Dockerfile).
# cgroup v2 refuses to enable a controller in subtree_control while the cgroup
# still has processes attached directly to it, so move ourselves into a leaf
# cgroup first (same trick isolate's own isolate-cg-keeper daemon uses).
mkdir -p /sys/fs/cgroup/init /sys/fs/cgroup/isolate
echo $$ > /sys/fs/cgroup/init/cgroup.procs
echo +memory > /sys/fs/cgroup/cgroup.subtree_control
echo +memory > /sys/fs/cgroup/isolate/cgroup.subtree_control

for i in $(seq 0 9); do
    isolate --cg --init --box-id=$i
done

exec python3 -m fastapi run app/main.py --host 0.0.0.0 --port 8000
