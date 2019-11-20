import tempfile
import unittest
from werkzeug.exceptions import NotFound
import os
#os.chdir("/home/anovelli/Documents/hotmaps/gchp_potential/cm")
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
from app.constant import INPUTS_CALCULATION_MODULE
from app.api_v1.my_calculation_module_directory.input_data_function import PATH
from app.api_v1.my_calculation_module_directory.functions import function_CM as f
from osgeo import gdal
import numpy as np


UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(),
'hotmaps', 'cm_files_uploaded')

OUTPUT_DIRECTORY = os.path.join(tempfile.gettempdir(),
'hotmaps', 'cm_files_output')

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)
    
    
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)
    os.chmod(OUTPUT_DIRECTORY, 0o777)
    

def load_input():
    """
    Load the input values in the file constant.py
    :return a dictionary with the imput values
    """
    inputs_parameter = {}
    for inp in INPUTS_CALCULATION_MODULE:
        inputs_parameter[inp['input_parameter_name']] = inp['input_value']
    
    return inputs_parameter


def load_raster():
    """
    Load the raster file for testing
    :return a dictionary with the raster file paths
    """
    inputs_raster_selection = {}
    for rkey, rname in (("land_surface_temperature", "land_surface_temperature.tif"),
                        ("ground_conductivity", "ground_conductivity.tiff")):
        raster_lst_path = os.path.join("tests/data/raster", rname)
        # simulate copy from HTAPI to CM
        save_path = os.path.join(UPLOAD_DIRECTORY, rname)
        copyfile(raster_lst_path, save_path)
        inputs_raster_selection[rkey] = save_path
    return inputs_raster_selection


def load_vector():
    """
    Load the raster file for testing
    :return a dictionary with the raster file paths
    """
    inputs_vector_selection = {}
    return inputs_vector_selection




class TestAPI(unittest.TestCase):


    def setUp(self):
        self.app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app,)

    def tearDown(self):

        self.ctx.pop()


    def test_compute(self):
        rasters = load_raster()
        factor = load_input()

        # register the calculation module a
        payload = {
            "inputs_raster_selection": rasters,
            "inputs_parameter_selection": factor,
        }
        rv, json = self.client.post("computation-module/compute/", 
                                    data=payload)
        self.assertEqual(rv.status_code, 200)
        """
        {'result': {'name': 'CM - Shallow geothermal potential',
            'raster_layers': [{'name': 'Classified GSHP potential expressed in '
                                       'MWh/y',
                               'path': '/var/tmp/713651f0-d29a-46de-8d42-66f541ca7abd.tif',

        """
        self.assertTrue(json["result"]["raster_layers"][0]["path"].endswith(".tif"))
        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    #TestAPI.test_compute('test')
