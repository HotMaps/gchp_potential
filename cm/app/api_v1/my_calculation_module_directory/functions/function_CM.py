#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 14:17:49 2019

@author: anovelli
"""
from grass_session import Session
from grass.script import core as gcore
import os
from matplotlib import colors
import numpy as np
from osgeo import gdal




CLRS_SUN = "#F19B03 #F6B13D #F9C774 #FDDBA3 #FFF0CE".split()
CMAP_SUN = colors.LinearSegmentedColormap.from_list('solar', CLRS_SUN)


def create_gis_db(path):
    if  os.path.exists(path) == False:
        os.mkdir(path,0o777)
    return
    

    
def create_location(gisdb, location, rasters, vectors, grass_data):
    with Session(gisdb = gisdb, location = location,
                 create_opts=rasters['ground_temp_raster']):
        # import file
       print(gcore.parse_command("g.gisenv", flags="s"))
        
       gcore.run_command("r.import", input = rasters["ground_temp_raster"],
                          output="ground_temp_raster")
       gcore.run_command("r.import", input = rasters["ground_conductivity"],
                          output="ground_conductivity")
       
       gcore.run_command("r.mapcalc", overwrite=True, 
                         expression="ground_temp_raster = "
                         "ground_temp_raster / 10.")

    grass_data["ground_conductivity"] = "ground_conductivity"
    grass_data["ground_temp_raster"] = "ground_temp_raster"

    return grass_data   
    
    
def create_grass_data(grass_data, factor):
    for fkey, fvalue in factor.items():
        grass_data[fkey] = fvalue
    return grass_data


def grass_compute_potential(grass_data, gisdb, location, mapset, create_opts):
    with Session(gisdb= gisdb, location = location , mapset= mapset,
                 create_opts = create_opts):
        print(f"Compute GCHP potential: {grass_data}")
        gcore.run_command("g.region", raster=grass_data["ground_temp_raster"])
        gcore.run_command('r.green.gshp.theoretical', **grass_data)
        gcore.run_command('r.out.gdal', input=grass_data['energy'],
                          output=os.path.join(gisdb,
                                              '%s.tif' % grass_data['energy']),
                          format='GTiff', flags='c',
                          createopt="COMPRESS=DEFLATE",
                          overwrite=True)
                          

def quantile_colors(array, output_suitable, proj, transform,
                    qnumb=6,
                    no_data_value=0,
                    no_data_color=(0, 0, 0, 255),
                    gtype=gdal.GDT_Byte,
                    options='compress=DEFLATE TILED=YES TFW=YES'
                            ' ZLEVEL=9 PREDICTOR=1',
                    round_decimals=-2,
                    unit="MWh/year",
                    string_potential = "Geothermal Potential"):
    """Generate a GTiff categorical raster map based on quantiles
    values.
    "symbology": [
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"50","label":"50MWh"},
        {"red":100,"green":150,"blue":10,"opacity":0.5,"value":"150MWh","label":"150MWh"},
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"200MWh","label":"200MWh"},
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"250MWh","label":"250MWh"}
    ]
    """
    if np.isnan(no_data_value):
        valid = ~np.isnan(array)
    else:
        valid = array != no_data_value
    
    qvalues, quantiles = quantile(array[valid], qnumb=qnumb,
                                  round_decimals=round_decimals)

    symbology = [
            {"red": no_data_color[0],
             "green": no_data_color[1],
             "blue": no_data_color[2],
             "opacity": no_data_color[3],
             "value": no_data_value,
             "label": "no data"},
            ]

    # create a categorical derived map
    array_cats = np.zeros_like(array, dtype=np.uint8)
    qv0 = quantiles[0] - 1.
    array_cats[~valid] = 0
    for i, (qk, qv) in enumerate(zip(qvalues[1:], quantiles[1:])):
        label = ("{qv0} {unit} < {string_potential} <= {qv1} {unit}"
                 "").format(qv0=qv0, qv1=qv, unit=unit, 
                   string_potential = string_potential)
        print(label)
        qindex = (qv0 < array) & (array <= qv)
        array_cats[qindex] = i + 1
        qv0 = qv
        symbology.append(dict(value=int(i + 1), label=label))

    # create a color table
    ct = gdal.ColorTable()
    
    if no_data_value !=0:
        no_data_value = 0
    
    ct.SetColorEntry(no_data_value, no_data_color)
    for i, (clr, symb) in enumerate(zip(CMAP_SUN(qvalues), symbology[1:])):
        r, g, b, a = (np.array(clr) * 255).astype(np.uint8)
        ct.SetColorEntry(i+1, (r, g, b, a))
        symb.update(dict(red=int(r), green=int(g), blue=int(b),
                         opacity=int(a)))

    # create a new raster map
    gtiff_driver = gdal.GetDriverByName('GTiff')
    ysize, xsize = array_cats.shape

    out_ds = gtiff_driver.Create(output_suitable,
                                 xsize, ysize,
                                 1, gtype,
                                 options.split())
    out_ds.SetProjection(proj)
    out_ds.SetGeoTransform(transform)

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(no_data_value)
    out_ds_band.SetColorTable(ct)
    out_ds_band.WriteArray(array_cats)
    out_ds.FlushCache()
    
    del out_ds
    return symbology


def quantile(array, qnumb=6, round_decimals=-2):
    # define the quantile limits
    qvalues, qstep = np.linspace(0, 1., qnumb, retstep=True)

    quantiles = np.quantile(array, qvalues)
    # round the number
    while True:
        q0 = np.round(quantiles, round_decimals)
        if len(set(q0)) != len(quantiles):
            print("Increase decimals")
            round_decimals += 1
        else:
            break

    return qvalues, q0                        
        
    
    