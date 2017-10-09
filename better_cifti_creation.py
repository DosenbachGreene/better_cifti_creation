#!/usr/bin/env python3

import argparse
import subprocess
import os

# parse arguments to command
parser = argparse.ArgumentParser(description='This script creates a Cifti for a single session from freesurfer and fcprocessed outputs.')
parser.add_argument('--tmask', required=True, help='Path to tmask')
parser.add_argument('--fcprocessed', required=True, help='Path to UNSMOOTHED fc-processed data (single session of subject)')
parser.add_argument('--fcprocessed_suffix', default='_faln_dbnd_xr3d_uwrp_atl_bpss_resid', help='suffix of UNSMOOTHED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl_bpss_resid)')
parser.add_argument('--output', default='/output', help='Path to output; Relative to Docker container')
parser.add_argument('--subcort_mask', required=True, help='Path to volumetric subcortical mask label file')
parser.add_argument('--fs_LR_surfdir', required=True, help='Location of fs_LR-registered surface')
parser.add_argument('--medial_mask_L', required=True, help='Left atlas medial wall mask')
parser.add_argument('--medial_mask_R', required=True, help='Right atlas medial wall mask')
parser.add_argument('--sw_medial_mask_L', help='small wall medial mask (Left)')
parser.add_argument('--sw_medial_mask_R', help='small wall medial mask (Right)')
parser.add_argument('--smoothnum', default=2.55, help='sigma of smoothing kernel to be applied')

# parse argumaents into dict
settings = vars(parser.parse_args())

# create relavant directories in output folder
try:
    os.mkdir(os.path.join(settings['output'],'surf_timecourses'))
except FileExistsError:
    print('surf_timecourses directory already exists.')
try:
    os.mkdir(os.path.join(settings['output'],'cifti_timeseries_normalwall'))
except FileExistsError:
    print('cifti_timeseries_normalwall directory already exists.')
try:
    os.mkdir(os.path.join(settings['output'],'goodvoxels'))
except FileExistsError:
    print('goodvoxels directory already exists.')
if (not settings['sw_medial_mask_L'] == None) and (not settings['sw_medial_mask_R'] == None):
    try:
        os.mkdir(os.path.join(settings['output'],'cifti_timeseries_smallwall'))
    except FileExistsError:
        print('cifti_timeseries_smallwall directory already exists.')

# convert 4dfp to nifti
os.system('niftigz_4dfp')
