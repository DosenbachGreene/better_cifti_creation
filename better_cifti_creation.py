#!/usr/bin/env python3

import argparse
import subprocess
import os
import glob
import nibabel

# parse arguments to command
parser = argparse.ArgumentParser(description='This script creates a Cifti for a single session from freesurfer and fcprocessed outputs.')
parser.add_argument('--fcprocessed_dir', required=True, help='Path to UNSMOOTHED fc-processed data (single session of subject)')
parser.add_argument('--fcprocessed_suffix', default='_b1_faln_dbnd_xr3d_uwrp_atl_bpss_resid', help='suffix of UNSMOOTHED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl_bpss_resid)')
parser.add_argument('--unprocessed_suffix', default='_b1_faln_dbnd_xr3d_uwrp_atl', help='suffix of UNPROCESSED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl)')
parser.add_argument('--tmask', required=True, help='Path to tmask')
parser.add_argument('--subcort_mask', required=True, help='Path to volumetric subcortical mask label file')
parser.add_argument('--fs_LR_surfdir', required=True, help='Location of fs_LR-registered surface (Should contain Native and fsaverage_LR32k subfolders with surfaces)')
parser.add_argument('--t1_suffix', default='_mpr_debias_avgT_111_t88', help='suffix of T1 image (Default is _mpr_debias_avgT_111_t88)')
parser.add_argument('--medial_mask_L', required=True, help='Left atlas medial wall mask')
parser.add_argument('--medial_mask_R', required=True, help='Right atlas medial wall mask')
parser.add_argument('--sw_medial_mask_L', help='small wall medial mask (Left)')
parser.add_argument('--sw_medial_mask_R', help='small wall medial mask (Right)')
parser.add_argument('--smoothnum', default=2.55, help='sigma of smoothing kernel to be applied')
parser.add_argument('--output', default='/output', help='Path to output; Relative to Docker container')

# parse argumaents into dict
settings = vars(parser.parse_args())

# create relevant directories in output folder
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
if settings['sw_medial_mask_L'] != None and settings['sw_medial_mask_R'] != None:
    try:
        os.mkdir(os.path.join(settings['output'],'cifti_timeseries_smallwall'))
    except FileExistsError:
        print('cifti_timeseries_smallwall directory already exists.')

# get the functional bold runs and concatenate them
# TO-DO, Just grab bold1 folder for now
func_run = glob.glob(os.path.join(settings['fcprocessed_dir'],'bold1','*{}.4dfp.img'.format(settings['fcprocessed_suffix'])))
assert func_run, 'functional bold run not found for session.'
unproc_func_run = glob.glob(os.path.join(settings['fcprocessed_dir'],'bold1','*{}.4dfp.img'.format(settings['unprocessed_suffix'])))
assert unproc_func_run, 'unprocessed bold run not found for session.'

# convert 4dfp to nifti
os.system('niftigz_4dfp -n {} /tmp/funcvol_temp'.format(func_run[0]))

# Remove NaNs from data
os.system('fslmaths /tmp/funcvol_temp -nan /tmp/funcvol')
os.remove('/tmp/funcvol_temp.nii.gz')

# convert unprocessed to nifti
os.system('niftigz_4dfp -n {} /tmp/funcvol_unprocessed'.format(unproc_func_run[0]))

# define directories for surface files
print('Creating Ribbon...')
Native = os.path.join(settings['fs_LR_surfdir'],'Native')
Ribbon = os.path.join(settings['fs_LR_surfdir'],'Ribbon')
try: # try to create the ribbon directory
    os.mkdir(Ribbon)
except FileExistsError:
    print('Ribbon directory already exists.')
T1image = glob.glob(os.path.join(settings['fs_LR_surfdir'],'*{}*'.format(settings['t1_suffix'])))
assert T1image, 'T1 image not found for this surface directory'

# grab the subject name from the T1 image
sub = os.path.basename(T1image[0]).split('_')[0]

# find relevant surface files
white_native_surf = list(map(os.path.splitext, # split rootname and extension
                    list(map(os.path.basename, # grab only filename
                    glob.glob(os.path.join(Native,'*.white.native.surf.gii'))))))
assert len(white_native_surf) == 2, 'Missing white native surface file(s)'
pial_native_surf = list(map(os.path.splitext, # split rootname and extension
                   list(map(os.path.basename, # grab only filename
                   glob.glob(os.path.join(Native,'*.pial.native.surf.gii'))))))
assert len(pial_native_surf) == 2, 'Missing pial native surface file(s)'

# define Ribbon and Mask Values
GreyRibbonValue = ['3','42']
WhiteMaskValue = ['2','41']
white_native_surf_gii = ['{}.gii'.format(white_native_surf[0][0]), '{}.gii'.format(white_native_surf[1][0])]
white_native_surf_nii_gz = ['{}.nii.gz'.format(white_native_surf[0][0]), '{}.nii.gz'.format(white_native_surf[1][0])]
pial_native_surf_gii = ['{}.gii'.format(pial_native_surf[0][0]), '{}.gii'.format(pial_native_surf[1][0])]
pial_native_surf_nii_gz = ['{}.nii.gz'.format(pial_native_surf[0][0]), '{}.nii.gz'.format(pial_native_surf[1][0])]

# Process left/right hemi
hemi = ['L','R']
for idx, side in enumerate(hemi):
    os.system('wb_command -create-signed-distance-volume {} {} {}'.format(
       os.path.join(Native,white_native_surf_gii[idx]),
       T1image[0],
       os.path.join(Ribbon,white_native_surf_nii_gz[idx])
       ))
    os.system('wb_command -create-signed-distance-volume {} {} {}'.format(
       os.path.join(Native,pial_native_surf_gii[idx]),
       T1image[0],
       os.path.join(Ribbon,pial_native_surf_nii_gz[idx])
       ))
    os.system('fslmaths {} -thr 0 -bin -mul 255 {}'.format(
        os.path.join(Ribbon,white_native_surf_nii_gz[idx]),
        os.path.join(Ribbon,'{}.{}.white_thr0.native.nii.gz'.format(sub,side))
        ))
    os.system('fslmaths {} -bin {}'.format(
        os.path.join(Ribbon,'{}.{}.white_thr0.native.nii.gz'.format(sub,side)),
        os.path.join(Ribbon,'{}.{}.white_thr0.native.nii.gz'.format(sub,side))
        ))
    os.system('fslmaths {} -uthr 0 -abs -bin -mul 255 {}'.format(
        os.path.join(Ribbon,pial_native_surf_nii_gz[idx]),
        os.path.join(Ribbon,'{}.{}.pial_uthr0.native.nii.gz'.format(sub,side))
        ))
    os.system('fslmaths {} -bin {}'.format(
        os.path.join(Ribbon,'{}.{}.pial_uthr0.native.nii.gz'.format(sub,side)),
        os.path.join(Ribbon,'{}.{}.pial_uthr0.native.nii.gz'.format(sub,side))
        ))
    os.system('fslmaths {} -mas {} -mul 255 {}'.format(
        os.path.join(Ribbon,'{}.{}.pial_uthr0.native.nii.gz'.format(sub,side)),
        os.path.join(Ribbon,'{}.{}.white_thr0.native.nii.gz'.format(sub,side)),
        os.path.join(Ribbon,'{}.{}.ribbon.nii.gz'.format(sub,side))
        ))
    os.system('fslmaths {} -bin -mul {} {}'.format(
        os.path.join(Ribbon,'{}.{}.ribbon.nii.gz'.format(sub,side)),
        GreyRibbonValue[idx],
        os.path.join(Ribbon,'{}.{}.ribbon.nii.gz'.format(sub,side))
        ))
    os.remove(os.path.join(Ribbon,white_native_surf_nii_gz[idx]))
    os.remove(os.path.join(Ribbon,'{}.{}.white_thr0.native.nii.gz'.format(sub,side)))
    os.remove(os.path.join(Ribbon,pial_native_surf_nii_gz[idx]))
    os.remove(os.path.join(Ribbon,'{}.{}.pial_uthr0.native.nii.gz'.format(sub,side)))

# combine left/right ribbon
os.system('fslmaths {0}/{1}.L.ribbon.nii.gz -add {0}/{1}.R.ribbon.nii.gz {0}/{1}.ribbon.nii.gz'.format(Ribbon,sub))
os.remove('{}/{}.L.ribbon.nii.gz'.format(Ribbon,sub))
os.remove('{}/{}.R.ribbon.nii.gz'.format(Ribbon,sub))
os.system('wb_command -volume-label-import {0}/{1}.ribbon.nii.gz /mnt/FreeSurferAllLut.txt {0}/{1}.ribbon.nii.gz -discard-others -unlabeled-value 0'.format(Ribbon,sub))

# convert to 4dfp/333 space
os.system('niftigz_4dfp -4 {0}/{1}.ribbon {0}/{1}.ribbon'.format(Ribbon,sub))
os.system('t4img_4dfp none {0}/{1}.ribbon {0}/{1}.ribbon_333'.format(Ribbon,sub))
os.system('niftigz_4dfp -n {0}/{1}.ribbon_333 {0}/{1}.ribbon_333'.format(Ribbon,sub))
