import os
import pytest
import uuid

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope="module")
def docker_compose_file(pytestconfig):
   return os.path.join(str(pytestconfig.rootdir), "alm-ansible-rm-docker-compose.yml")

@pytest.fixture
def get_uuid():
   return str(uuid.uuid1())


