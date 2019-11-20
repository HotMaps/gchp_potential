#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:37:50 2019

@author: anovelli

 gcore.run_command("v.import", input="/tmp/hotmaps/cm_files_uploaded/thermomap.shp", layer="thermomap", output="f", overwrite=True)
 gcore.run_command("v.import", input="/tmp/hotmaps/cm_files_uploaded/thermomap.shp", layer="termomap",  output="d")
"""
import os
import tempfile
#INPUT_CALCULATION_MODULE = [{"path" : "/home/gis_db"
#                            }]


PATH = os.path.join(tempfile.gettempdir(), "gis_db")
os.makedirs(PATH, exist_ok=True)
