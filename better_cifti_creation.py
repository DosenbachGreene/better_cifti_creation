#!/usr/bin/env python3

import argparse
import subprocess
import os
import glob
import ribbon
import goodvoxels

def run(settings):
    """
        Run main function
    """
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

    # grab session name from bold run
    session = os.path.basename(func_run[0].split('_')[0])

    # convert 4dfp to nifti
    #os.system('niftigz_4dfp -n {} /tmp/funcvol_temp'.format(func_run[0]))

    # Remove NaNs from data
    #os.system('fslmaths /tmp/funcvol_temp -nan /tmp/funcvol')
    #os.remove('/tmp/funcvol_temp.nii.gz')

    # convert unprocessed to nifti
    #os.system('niftigz_4dfp -n {} /tmp/funcvol_unprocessed'.format(unproc_func_run[0]))

    # Create ribbon
    #ribbon_path,subject = ribbon.create(settings)
    ribbon_path = '/input/MSC01/Ribbon/MSC01.ribbon_333.nii.gz'
    subject = 'MSC01'

    # Collect good voxels
    #submask = goodvoxels.collect(settings,ribbon_path,session)
    submask = '/output/goodvoxels/vc38671_goodvoxels.nii.gz'

    # Sample volumes to surface, downsample, and smoothnum
    #hem = ['L','R']
    hem = ['L']
    # TO-DO add assertion check for these files in the near-future
    for side in hem:
        midsurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.midthickness.native.surf.gii'.format(subject,side))
        midsurf_LR32k = os.path.join(settings['fs_LR_surfdir'],'fsaverage_LR32k','{}.{}.midthickness.32k_fs_LR.surf.gii'.format(subject,side))
        whitesurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.white.native.surf.gii'.format(subject,side))
        pialsurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.pial.native.surf.gii'.format(subject,side))
        nativedefsphere = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.sphere.reg.reg_LR.native.surf.gii'.format(subject,side))
        outsphere = os.path.join(settings['fs_LR_surfdir'],'fsaverage_LR32k','{}.{}.sphere.32k_fs_LR.surf.gii'.format(subject,side))

        # Create prefix surface name
        surfname = '{}_{}'.format(subject,side)

        # # Map hemisphere to surface
        # print('Subject {}: mapping {} hemisphere data to surface.'.format(subject,side))
        # os.system('wb_command -volume-to-surface-mapping /tmp/funcvol.nii.gz {} {}/surf_timecourses/{}.func.gii -ribbon-constrained {} {} -volume-roi {}'.format(
        #     midsurf,settings['output'],surfname,whitesurf,pialsurf,submask
        # ))
        #
        # # Dilate surface
        # print('Subject {}: dilating {} hemisphere data to surface.'.format(subject,side))
        # os.system('wb_command -metric-dilate {1}/surf_timecourses/{2}.func.gii {0} 10 {1}/surf_timecourses/{2}_dil10.func.gii'.format(
        #     midsurf,settings['output'],surfname
        # ))

        # Deform
        #print('Subject {}: deforming {} hemisphere timecourse to 32k fs_LR.'.format(subject,side))
        #os.system('wb_command -metric-resample {0}/surf_timecourses/{1}_dil10.func.gii {2} {3} ADAP_BARY_AREA {0}/surf_timecourses/{1}_dil10_32k_fs_LR.func.gii -area-surfs {4} {5}'.format(
        #    settings['output'],surfname,nativedefsphere,outsphere,midsurf,midsurf_LR32k
        #))

        # Smooth
        # print('Subject {}: Smoothing {} hemisphere surface timecourse.'.format(subject,side))
        # os.system('wb_command -metric-smoothing {0} {1}/surf_timecourses/{2}_dil10_32k_fs_LR.func.gii {3} {1}/surf_timecourses/{2}_dil10_32k_fs_LR_smooth{3}.func.gii'.format(
        #     midsurf_LR32k,settings['output'],surfname,settings['smoothnum']
        # ))

        # Write final surface file
        os.system('caret_command')

if __name__ == '__main__':
    # parse arguments to command
    parser = argparse.ArgumentParser(description='This script creates a Cifti for a single session from freesurfer and fcprocessed outputs.')
    parser.add_argument('--fcprocessed_dir', required=True, help='Path to fc-processed data (single session of subject)')
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

    # Run main functiona
    run(settings)
