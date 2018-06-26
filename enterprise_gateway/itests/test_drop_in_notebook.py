import pytest
import urllib
import nbformat
import re
from enterprise_gateway.client.gateway_client import GatewayClient
import os

@pytest.fixture(scope='class')
def read_in_notebook():

    #TODO  - change to explicit directory instead of single notebook file
    url = 'file://'+os.getcwd()+'/enterprise_gateway/itests/notebooks/.ipynb_checkpoints/sample_notebook.ipynb'

    try:
        # Python 3
        response = urllib.request.urlopen(url).read().decode()
    except:
        # Python 2
        response = urllib.urlopen(url).read().decode()

    notebook = nbformat.reads(response, as_version=4)

    return notebook


@pytest.fixture(scope='class')
def get_param_list():
    param_list = []
    testname_list = []
    for i in read_in_notebook()['cells']:
        if not i['source'] or not i['metadata']['regex']:
            print("Notebook file has empty source or output fields")
        elif i['metadata']['regex']:
            param_list.append((i['metadata']['name'], i['source'], i['metadata']['regex']))
            testname_list.append(i['metadata']['name'])
        else:
            if 'text' in i['outputs'][0]:
                param_list.append((i['metadata']['name'], i['source'], i['outputs'][0]['text']))
            else:
                param_list.append((i['metadata']['name'], i['source'], i['outputs'][0]['data']['text/plain']))
            testname_list.append(i['metadata']['name'])

    return {"cell list": param_list, "testnames": testname_list}


@pytest.fixture(scope='class')
def setup_kernel(request):

    KERNELSPEC = read_in_notebook()['metadata']['kernelspec']['name']

    gateway_client = GatewayClient()
    request.cls.active_kernel = gateway_client.start_kernel(KERNELSPEC)
    yield

    gateway_client.shutdown_kernel(request.cls.active_kernel)


@pytest.mark.usefixtures('setup_kernel')
class TestNoteBook():
    parameters = get_param_list()

    @pytest.mark.parametrize('testname, question, answer', parameters['cell list'], ids=parameters['testnames'])
    def test_cell(self, testname, question, answer):
        result = self.active_kernel.execute(question)
        assert re.search(answer, result)




