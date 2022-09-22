# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 22:03:41 2020

@author: disbr007
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import geopandas as gpd
import numpy as np


from misc_utils.plotting_utils import y_fmt



tks_path = r'E:\disbr007\umn\ms\shapefile\tk_loc\digitized_thaw_slumps.shp'
tks_ret_p = r'E:\disbr007\umn\ms\shapefile\tk_loc\digitized_thaw_slumps_headwall_retreat.shp'

tks = gpd.read_file(tks_path)
tks['area'] = tks.geometry.area

tks = tks.dropna()

pairs = gpd.sjoin(tks, tks)
pairs = pairs[pairs['id_left']!=pairs['id_right']]
pairs = pairs[pairs['obs_year_left']==2013]
pairs.drop(columns=['index_right'], inplace=True)

ret = gpd.read_file(tks_ret_p)

pair_ret = gpd.sjoin(pairs, ret, how='inner')

(m, b) = np.polyfit(pair_ret['area_left'], pair_ret['ret_dist']/2, 1)
yp = np.polyval([m, b], pair_ret['area_left'])


plt.style.use('ggplot')
fig, ax = plt.subplots(1,1, figsize=(7,7))
ax.scatter(pair_ret['area_left'], pair_ret['ret_dist']/2)
ax.plot(pair_ret['area_left'], yp)
ax.set_title('Relationship of Area to Retreat Distance')
ax.get_xaxis().set_major_formatter(
    mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.set_xlabel('Slump area in 2013 ($m^2$)')
ax.set_ylabel('Annual retreat rate in 2015 ($m$)')
plt.savefig(r'E:\disbr007\umn\nr8107\figures\fig_ex\area_retreat_relationship.png')