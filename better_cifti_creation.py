#!/usr/bin/env python3

import argparse
import subprocess

# parse arguments to command
parser = argparse.ArgumentParser(description='This script creates a Cifti for a single session from freesurfer and fcprocessed outputs.')
parser.add_argument('--tmask', required=True, help='Path to tmask')
parser.add_argument('--fcprocessed', required=True, help='Path to UNSMOOTHED fc-processed data')
parser.add_argument('--fcprocessed_suffix', default='_faln_dbnd_xr3d_uwrp_atl_bpss_resid', help='suffix of UNSMOOTHED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl_bpss_resid)')
parser.add_argument('--output', required=True, help='Path to output')
parser.add_argument('--subcort_mask', required=True, help='Path to volumetric subcortical mask label file')
parser.add_argument('--fs_LR_surfdir', required=True, help='Location of fs_LR-registered surface')
parser.add_argument('--medial_mask_L', required=True, help='Left atlas medial wall mask')
parser.add_argument('--medial_mask_R', required=True, help='Right atlas medial wall mask')
parser.add_argument('--sw_medial_mask_L', help='small wall medial mask (Left)')
parser.add_argument('--sw_medial_mask_R', help='small wall medial mask (Right)')
parser.add_argument('--smoothnum', default=2.55, help='sigma of smoothing kernel to be applied')
args = parser.parse_args()

# create relavant directories in output folder

