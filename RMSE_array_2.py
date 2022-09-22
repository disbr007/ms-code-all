import argparse
import logging
import numpy as np
import os
import random

from osgeo import gdal, osr
import geopandas as gpd
from shapely.geometry import Point

from RasterWrapper import Raster
from logging_utils import create_logger


logger = create_logger(__file__, 'sh')


def raster_bounds(raster_obj):
    '''
    GDAL only version of getting bounds for a single raster.
    '''
#    src = raster_obj.data_src
    gt = raster_obj.geotransform
    ulx = gt[0]
    uly = gt[3]
    lrx = ulx + (gt[1] * raster_obj.x_sz)
    lry = uly + (gt[5] * raster_obj.y_sz)
    
    return ulx, lry, lrx, uly

    
def minimum_bounding_box(raster_objs):
    '''
    Takes a list of DEMs (or rasters) and returns the minimum bounding box of all in
    the order of bounds specified for gdal.Translate.
    dems: list of dems
    '''
    ## Determine minimum bounding box
    ulxs, lrys, lrxs, ulys = list(), list(), list(), list()
    #geoms = list()
    for r in raster_objs:
        ulx, lry, lrx, uly = raster_bounds(r)
        ulxs.append(ulx)
        lrys.append(lry)
        lrxs.append(lrx)
        ulys.append(uly)        
    
    ## Find the smallest extent of all bounding box corners
    ulx = max(ulxs)
    uly = min(ulys)
    lrx = min(lrxs)
    lry = max(lrys)

    projWin = [ulx, uly, lrx, lry]

    return projWin


def calc_rmse(l1, l2):
    '''
    Calculates RMSE of two lists of numbers.
    '''

    diffs = [x - y for x, y in zip(l1, l2)]
    sq_diff = [x**2 for x in diffs]
    mean_sq_diff = sum(sq_diff) / len(sq_diff)
    rmse_val = np.sqrt(mean_sq_diff)
    
    return rmse_val


def sample_random_points(dem1, dem2, n):
    """
    Generates n random points within projWin [ulx, uly, lrx, lry]
    """
    dem1_nodata = dem1.nodata_val
    dem2_nodata = dem2.nodata_val
    
    projWin = minimum_bounding_box([dem1, dem2])
    minx, miny, maxx, maxy = projWin
    
    sample_vals = []
    sample_pts = []
    while len(sample_vals) < n:
        pt = (random.uniform(miny, maxy), random.uniform(minx, maxx))
        val1 = dem1.SamplePoint(pt)
        val2 = dem2.SamplePoint(pt)
        if val1 != dem1_nodata and val2 != dem2_nodata and val1 is not None and val2 is not None:
            sample_vals.append((val1, val2))
            sample_pts.append(pt)
        else:
            pass

    return sample_vals, sample_pts


def dem_RMSE(dem1_p, dem2_p, n, outpath=None):
    """
    Calculate RMSE for two DEMs from
    n sample points
    """
    logging.info('Loading DEMs...')
    dem1 = Raster(dem1_p)
    dem2 = Raster(dem2_p)
    dem1_srs = dem1.prj
    dem2_srs = dem2.prj
    if dem1_srs.IsSame(dem2_srs) != 1:
        logger.warning('SpatialReference mis-match: {} and {}'.format(dem1_srs, dem2_srs))

    logging.info('Sampling points...')
    sample_values, sample_pts = sample_random_points(dem1, dem2, n=n)
    x_vals, y_vals = zip(*sample_values)
    rmse = calc_rmse(x_vals, y_vals)

    if outpath is not None:
        dem1_name = os.path.basename(dem1_p)
        dem2_name = os.path.basename(dem2_p)
        gdf = gpd.GeoDataFrame({dem1_name[:10]: [val1 for (val1, val2) in sample_values],
                                dem2_name[:10]: [val2 for (val1, val2) in sample_values],
                                'err': [val1-val2 for (val1, val2) in sample_values],
                                'geometry': [Point(x, y) for (y, x) in sample_pts]})
        gdf = gdf.set_geometry('geometry')
        # gdf.crs ={'init':'epsg:{}'.format(dem1_epsg)}
        gdf.crs = dem1.prj.wkt
        gdf.to_file(outpath)

    logger.info('Calculated RMSE: {}'.format(rmse))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dem1_path', type=str,
                        help='Path to the first DEM.')
    parser.add_argument('dem2_path', type=str,
                        help='Path to the second DEM.')
    parser.add_argument('-n', '--num_pts', type=int,
                        help='Number of sample points to use for sampling and RMSE calculation. Default 1000')
    # parser.add_argument('-p', '--plot', type=str,
                        # help='Option path to save plots: histogram of differences, scatter of values, map of sample points')
    parser.add_argument('-w', '--write_shp', type=str,
                        help='Optional path to write shapefile of sample points')
    
    args = parser.parse_args()

    dem1_path = args.dem1_path
    dem2_path = args.dem2_path
    n = args.num_pts
    write_shp = args.write_shp

    dem_RMSE(dem1_p=dem1_path, dem2_p=dem2_path, n=n, outpath=write_shp)
