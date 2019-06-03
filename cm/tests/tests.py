import tempfile
import unittest
from werkzeug.exceptions import NotFound
import os
#os.chdir("/home/anovelli/Documents/hotmaps/gchp_potential/cm")
from app import create_app
import os.path
from shutil import copyfile
#from .test_client import TestClient
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


def load_raster(raster):
    """
    Load the raster file for testing
    :return a dictionary with the raster file paths
    """
    raster_file_path = os.path.join("tests/data/raster", raster)
    # simulate copy from HTAPI to CM
    save_path = os.path.join(UPLOAD_DIRECTORY, raster)
    copyfile(raster_file_path, save_path)
    inputs_raster_selection = {}
    inputs_raster_selection["ground_temp_raster"] = save_path
    return inputs_raster_selection


def load_vector(vector):
    """
    Load the raster file for testing
    :return a dictionary with the raster file paths
    """
    
    vector_file_path = os.path.join("tests/data/vector", vector)
    # simulate copy from HTAPI to CM
    
    path = "tests/data/vector"
    
    save_path = os.path.join(UPLOAD_DIRECTORY, vector)
    for files in os.listdir(os.path.split(vector_file_path)[0]):
        save_path_shapefile = os.path.join(UPLOAD_DIRECTORY, files)
        copyfile(os.path.join(path,files), save_path_shapefile)
    
    inputs_vector_selection = {}
    inputs_vector_selection["termomap"] = save_path
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
        rasters = load_raster(raster="land_surface_temperature.tif")
        vectors = load_vector(vector="thermomap.shp")
        
        factor = load_input()
        
        grass_data = {
            "power": "geo_power",
            "energy": "geo_energy"
            }
        f.create_gis_db(path = PATH)
        pid = os.getpid()
        loc = "tmp_%i" % pid
        grass_data = f.create_location(gisdb = PATH,
                                   location = loc, 
                                   rasters =  rasters,
                                   vectors = vectors, 
                                   grass_data = grass_data)        
        
        grass_data = f.create_grass_data(grass_data = grass_data,
                                     factor = factor)
        
        f.grass_compute_potential(grass_data = grass_data,
                              gisdb = PATH,
                              location = loc,
                              mapset = "potential",
                              create_opts = "")
        
        ds = gdal.Open(os.path.join(PATH,'%s.tif' % grass_data['energy']))
    
        f.quantile_colors(array = ds.ReadAsArray(),
                          output_suitable =  os.path.join(OUTPUT_DIRECTORY, "{}.tif".format("output")),
                                        proj=ds.GetProjection(),
                                        transform=ds.GetGeoTransform(),
                                        qnumb=6,
                                        no_data_value=np.nan,
                                        gtype=gdal.GDT_Byte,
                                        unit="MWh/year",
                                        options='compress=DEFLATE TILED=YES '
                                                'TFW=YES '
                                                'ZLEVEL=9 PREDICTOR=1')
#        raster_file_path = 'tests/data/raster_for_test.tif'
#        # simulate copy from HTAPI to CM
#        save_path = UPLOAD_DIRECTORY+"/raster_for_test.tif"
#        copyfile(raster_file_path, save_path)
#
#        inputs_raster_selection = {}
#        inputs_parameter_selection = {}
#        inputs_vector_selection = {}
#        inputs_raster_selection["heat_tot_curr_density"]  = save_path
#        inputs_vector_selection["heating_technologies_eu28"]  = {}
#        inputs_parameter_selection["reduction_factor"] = 2
#
#        # register the calculation module a
#        payload = {"inputs_raster_selection": inputs_raster_selection,
#                   "inputs_parameter_selection": inputs_parameter_selection,
#                   "inputs_vector_selection": inputs_vector_selection}
#
#
#        rv, json = self.client.post('computation-module/compute/', data=payload)
#
#        self.assertTrue(rv.status_code == 200)

if __name__ == "__main__":
 #   ipdb.set_trace()
    TestAPI.test_compute('test')
