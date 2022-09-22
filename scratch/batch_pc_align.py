# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 15:34:04 2019

@author: disbr007
"""

import os
import glob
import subprocess
from subprocess import PIPE, STDOUT


def batch_point2dem(src_dir, dryrun):
    '''
    Run point2dem in batch on cluster using qsub
    src_dir: dir holding subdirs of paired 
    dryrun: flag to just print commands with no job submission
    '''
     ## List subdirectory names   
    pairs = os.listdir(src_dir)
    
    for pair_dir in pairs:
        ## Get DEMs in date order
        # dem1, dem2 = get_dems(src_dir, pair_dir)

        dems_dir = os.path.join(src_dir, pair_dir)
        trans_pattern = os.path.join(dems_dir, '*trans_source.tif')
        trans_source_files = glob.glob(trans_pattern)
        ## Ensure trans_source file found
        if len(trans_source_files) > 0:

            ## Should be the only trans_source
            ## Can add checking the basename for matching a dem name
            trans_source = trans_source_files[0]
            trans_source_name = os.path.basename(trans_source).split('.')[0].split('-trans')[0]
            prefix = os.path.join(dems_dir, trans_source_name)
            ## Build cmd
            cmd = 'qsub -v p1="{}",p2="{}" ~/scratch/code/coreg/qsub_point2dem.sh'.format(trans_source, prefix)

            if dryrun:
                print(cmd)
            else:
#                p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
#                output = p.stdout.read()
                print('tried')
        else:
            print('No trans_source file found. Skipping: {}'.format(pair_dir))
            
            
src_dir = r'V:\pgc\data\scratch\jeff\coreg\data\pairs'

batch_point2dem(src_dir, dryrun=True)