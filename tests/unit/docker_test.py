import pytest
import os
import requests
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

@pytest.fixture
def main_app_url(module_scoped_container_getter):
   """ Wait for the api from ansibl-rm to become responsive """
   request_session = requests.Session()
   retries = Retry(total=10, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
   request_session.mount("http://", HTTPAdapter(max_retries=retries))

   service = module_scoped_container_getter.get("alm-ansible-rm").network_info[0]
   api_url = f"http://{service.hostname}:{service.host_port}/api/v1.0/resource-manager/"
   return api_url

def test_main_service_run(main_app_url):
   result = requests.get(main_app_url+"ui/#/")
   assert result.status_code == 200
   # for later reuse
   os.environ["ARM_URL"] = main_app_url