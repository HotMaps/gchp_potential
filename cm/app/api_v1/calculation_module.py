from osgeo import gdal
from ..helper import generate_output_file_tif, create_zip_shapefiles
import logging
import time
import warnings
import os
import secrets
import shutil
import subprocess
from pprint import pprint

import numpy as np

from .my_calculation_module_directory.input_data_function import PATH
from .my_calculation_module_directory.functions import function_CM as f
from ..constant import CM_NAME


# set a logger
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")


def check_rasters(rasters):
    """Raise a ValueError if the raster file does not exists or
    if it is not readable by gdalinfo.
    """
    for rname, rpath in rasters.items():
        if not os.path.exists(rpath):
            raise ValueError(f"The raster layer: {rname} "
                             f"does not exists in: {rpath}")
        print(f"The raster layer: {rname} with path: {rpath} exists!")
        cmd = f"gdalinfo {rpath}"
        ginfo = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 shell=True)
        rc = ginfo.wait()
        stdout, stderr = ginfo.communicate()
        print(f"\n\n===\nexecuted command:\n    $ {cmd}"
              f"\nreturn code:           {rc}\n---"
              f"\nstderr:\n{stderr.decode()}\n---"
              f"\nstdout:\n{stdout.decode()}\n---\n\n")
        if rc > 0:
            raise ValueError("gdalinfo is not able to read the raster layer: "
                             f"{rname} - located in {rpath}, the error is:\n"
                             f"{stdout}\n===\n")

""" Entry point of the calculation module function"""

#TODO: CM provider must "change this code"
#TODO: CM provider must "not change input_raster_selection,output_raster  1 raster input => 1 raster output"
#TODO: CM provider can "add all the parameters he needs to run his CM
#TODO: CM provider can "return as many indicators as he wants"
def calculation(output_directory, 
                inputs_raster_selection, 
                inputs_parameter_selection):
    #TODO the folowing code must be changed by the code of the calculation module
    
    """
    the main function
    """

    # generate the output raster file
    output_raster1 = generate_output_file_tif(output_directory)
    
    # genereta folder for GRASS computations
    f.create_gis_db(path = PATH)
    
    # create a unique token => location for each request to avoid
    # that a second user overwrite the input of a first user with
    # a cocurrent work
    tok = secrets.token_urlsafe(8)
    loc = f"tmp_{tok}"

    #retrieve the raster inputs layes
    rasters = {
            "ground_temp_raster" : inputs_raster_selection["land_surface_temperature"],
            "ground_conductivity" : inputs_raster_selection["ground_conductivity"]
            }
    
    #retrieve the inputs layes
    vectors = {
            # "termomap": inputs_vector_selection["thermomap"]
            }

    #retrieve the inputs all input defined in the signature
    factor = {
              "heating_season_value" :inputs_parameter_selection["heating_season_value"],
              "ground_capacity_value":inputs_parameter_selection["ground_capacity_value"],
              "borehole_radius" :inputs_parameter_selection["borehole_radius"],
              "borehole_resistence" :inputs_parameter_selection["borehole_resistence"],
              "borehole_length" :inputs_parameter_selection["borehole_length"],
              "pipe_radius" :inputs_parameter_selection["pipe_radius"],
              "number_pipes" :inputs_parameter_selection["number_pipes"],
              "grout_conductivity" :inputs_parameter_selection["grout_conductivity"],
              "fluid_limit_temperature" :inputs_parameter_selection["fluid_limit_temperature"],
              "lifetime" :inputs_parameter_selection["lifetime"]      
              }
    
    if factor["borehole_resistence"] is None:
        factor["borehole_resistence"] = "nan"

    grass_data = {
            "power": "geo_power",
            "energy": "geo_energy"
            }
    
    # check raster inputs:
    check_rasters(rasters)
    
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
    
    symbology = f.quantile_colors(array = ds.ReadAsArray(),
                                   output_suitable =  output_raster1,
                                        proj=ds.GetProjection(),
                                        transform=ds.GetGeoTransform(),
                                        qnumb=6,
                                        no_data_value=np.nan,
                                        gtype=gdal.GDT_Byte,
                                        unit="MWh/year",
                                        options='compress=DEFLATE TILED=YES '
                                                'TFW=YES '
                                                'ZLEVEL=9 PREDICTOR=1')
    
    res = [{"name": "Classified GSHP potential expressed in {}".format("MWh/y"),
             "path": output_raster1,
             "type": "custom",
             "symbology": symbology
             }]

    result = dict()
    result['name'] = CM_NAME
    result['raster_layers'] = res
    
    # remove grass gis directory
    shutil.rmtree(os.path.join(PATH, loc))
    pprint(result)
    LOGGER.info(f"Computation result for biomass is: {result}")
    return result
