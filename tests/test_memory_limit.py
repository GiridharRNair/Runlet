import os
import pytest
from conftest import execute

USE_CGROUPS = os.getenv("USE_CGROUPS", "true").strip().lower() == "true"

MEMORY_BOMB = """\
data = bytearray(400 * 1024 * 1024)
print(len(data))"""


@pytest.mark.skipif(
    not USE_CGROUPS, reason="Memory limit is only enforced when USE_CGROUPS=True"
)
def test_mle_when_cgroups_enabled(client):
    result = execute(client, "python", MEMORY_BOMB)
    assert result["status"] == "MLE"
