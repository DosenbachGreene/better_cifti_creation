#!/usr/bin/env python3

"""

    TO-DO Lengthy explaination about what this script does...

"""

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
    try:
        os.mkdir(os.path.join(settings['output'],'Ribbon'))
    except FileExistsError:
        print('Ribbon directory already exists.')
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
    session = os.path.basename(func_run[0]).split('_')[0]

    # convert 4dfp to nifti
    os.system('niftigz_4dfp -n {} /temp/funcvol_temp'.format(func_run[0]))

    # Remove NaNs from data
    os.system('fslmaths /temp/funcvol_temp -nan /temp/funcvol')
    os.remove('/temp/funcvol_temp.nii.gz')

    # convert unprocessed to nifti
    os.system('niftigz_4dfp -n {} /temp/funcvol_unprocessed'.format(unproc_func_run[0]))

    # Test if ribbon already exists for this subject
    ribbon_found = glob.glob(os.path.join(settings['output'],'Ribbon','*.ribbon_{}.nii.gz'.format(settings['space'])))
    if ribbon_found:
        print('Ribbon was already found at {}'.format(ribbon_found[0]))
        # assert that there is a t1 image and grab the subject name from it
        T1image = glob.glob(os.path.join(settings['fs_LR_surfdir'],'*{}*'.format(settings['t1_suffix'])))
        assert T1image, 'T1 image not found for this surface directory'
        subject = os.path.basename(T1image[0]).split('_')[0]

        # assign the found ribbon path
        ribbon_path = ribbon_found[0]
    else:
        # Create ribbon
        ribbon_path,subject = ribbon.create(settings)

    # Collect good voxels
    submask = goodvoxels.collect(settings,ribbon_path,session)

    # Sample volumes to surface, downsample, and smooth
    hem = ['L','R']
    # TO-DO add assertion check for these files in the near-future
    for side in hem:
        midsurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.midthickness.native.surf.gii'.format(subject,side))
        midsurf_LR32k = os.path.join(settings['fs_LR_surfdir'],'fsaverage_LR32k','{}.{}.midthickness.32k_fs_LR.surf.gii'.format(subject,side))
        whitesurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.white.native.surf.gii'.format(subject,side))
        pialsurf = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.pial.native.surf.gii'.format(subject,side))
        nativedefsphere = os.path.join(settings['fs_LR_surfdir'],'Native','{}.{}.sphere.reg.reg_LR.native.surf.gii'.format(subject,side))
        outsphere = os.path.join(settings['fs_LR_surfdir'],'fsaverage_LR32k','{}.{}.sphere.32k_fs_LR.surf.gii'.format(subject,side))

        # Create prefix surface name
        surfname = '{}_{}'.format(session,side)

        # Map hemisphere to surface
        print('Subject {}, Session {}: mapping {} hemisphere data to surface.'.format(subject,session,side))
        os.system('wb_command -volume-to-surface-mapping /temp/funcvol.nii.gz {} {}/surf_timecourses/{}.func.gii -ribbon-constrained {} {} -volume-roi {}'.format(
            midsurf,settings['output'],surfname,whitesurf,pialsurf,submask
        ))

        # Dilate surface
        print('Subject {}, Session {}: dilating {} hemisphere data to surface.'.format(subject,session,side))
        os.system('wb_command -metric-dilate {1}/surf_timecourses/{2}.func.gii {0} 10 {1}/surf_timecourses/{2}_dil10.func.gii'.format(
            midsurf,settings['output'],surfname
        ))

        # Deform
        print('Subject {}, Session {}: deforming {} hemisphere timecourse to 32k fs_LR.'.format(subject,session,side))
        os.system('wb_command -metric-resample {0}/surf_timecourses/{1}_dil10.func.gii {2} {3} ADAP_BARY_AREA {0}/surf_timecourses/{1}_dil10_32k_fs_LR.func.gii -area-surfs {4} {5}'.format(
           settings['output'],surfname,nativedefsphere,outsphere,midsurf,midsurf_LR32k
        ))

        # Smooth
        print('Subject {}, Session {}: Smoothing {} hemisphere surface timecourse.'.format(subject,session,side))
        os.system('wb_command -metric-smoothing {0} {1}/surf_timecourses/{2}_dil10_32k_fs_LR.func.gii {3} {1}/surf_timecourses/{2}_dil10_32k_fs_LR_smooth{3}.func.gii'.format(
            midsurf_LR32k,settings['output'],surfname,settings['smoothnum']
        ))

        # Write final surface file
        print('Subject {}, Session {}: Convert {} hemisphere to XML_BASE64.'.format(subject,session,side))
        os.system('caret_command -file-convert -format-convert XML_BASE64 {}/surf_timecourses/{}_dil10_32k_fs_LR_smooth{}.func.gii'.format(
            settings['output'],surfname,settings['smoothnum']
        ))

        # Remove temp files
        os.remove('{}/surf_timecourses/{}.func.gii'.format(settings['output'],surfname))
        os.remove('{}/surf_timecourses/{}_dil10.func.gii'.format(settings['output'],surfname))
        os.remove('{}/surf_timecourses/{}_dil10_32k_fs_LR.func.gii'.format(settings['output'],surfname))

    # Smooth data in volume within mask
    print('Subject {}, Session {}: Smoothing functional data within volume mask'.format(subject,session))
    os.system('wb_command -volume-smoothing /temp/funcvol.nii.gz {} /temp/funcvol_wROI255.nii.gz -roi {}'.format(
       settings['smoothnum'],settings['subcort_mask']
    ))

    # Remove temp files
    os.remove('/temp/funcvol.nii.gz')
    os.remove('/temp/funcvol_unprocessed.nii.gz')

    # Create cifti timeseries
    print('Subject {}, Session {}: Combining surface and volume data to create cifti timeseries.'.format(subject,session))
    os.system('wb_command '
        '-cifti-create-dense-timeseries {0}/cifti_timeseries_normalwall/{1}_LR_surf_subcort_{7}_32k_fsLR_smooth{2}.dtseries.nii '
        '-volume /temp/funcvol_wROI255.nii.gz {3} '
        '-left-metric {0}/surf_timecourses/{1}_L_dil10_32k_fs_LR_smooth{2}.func.gii '
        '-roi-left {4} '
        '-right-metric {0}/surf_timecourses/{1}_R_dil10_32k_fs_LR_smooth{2}.func.gii '
        '-roi-right {5} '
        '-timestep {6} '
        '-timestart 0'.format(
        settings['output'], # Arg 0
        session, # Arg 1
        settings['smoothnum'], # Arg 2
        settings['subcort_mask'], # Arg 3
        settings['medial_mask_L'], # Arg 4
        settings['medial_mask_R'], # Arg 5
        settings['TR'], # Arg 6
        settings['space'] # Arg 7
    ))

    # Only if smallwall exists
    if settings['sw_medial_mask_L'] != None and settings['sw_medial_mask_R'] != None:
        print('Subject {}, Session {}: Combining surface and volume data to create cifti timeseries (smallwall).'.format(subject,session))
        os.system('wb_command '
            '-cifti-create-dense-timeseries {0}/cifti_timeseries_smallwall/{1}_LR_surf_subcort_{7}_32k_fsLR_smooth{2}.dtseries.nii '
            '-volume /temp/funcvol_wROI255.nii.gz {3} '
            '-left-metric {0}/surf_timecourses/{1}_L_dil10_32k_fs_LR_smooth{2}.func.gii '
            '-roi-left {4} '
            '-right-metric {0}/surf_timecourses/{1}_R_dil10_32k_fs_LR_smooth{2}.func.gii '
            '-roi-right {5} '
            '-timestep {6} '
            '-timestart 0'.format(
            settings['output'], # Arg 0
            session, # Arg 1
            settings['smoothnum'], # Arg 2
            settings['subcort_mask'], # Arg 3
            settings['sw_medial_mask_L'], # Arg 4
            settings['sw_medial_mask_R'], # Arg 5
            settings['TR'], # Arg 6
            settings['space'] # Arg 7
        ))

    # Delete temp files
    os.remove('/temp/funcvol_wROI255.nii.gz')

if __name__ == '__main__':
    # parse arguments to command
    parser = argparse.ArgumentParser(description='This script creates a Cifti for a single session from freesurfer and fcprocessed outputs. All paths are relative to docker container.')
    parser.add_argument('--fcprocessed_dir', required=True, help='Path to fc-processed data (single session of subject)')
    parser.add_argument('--fcprocessed_suffix', default='_b1_faln_dbnd_xr3d_uwrp_atl_bpss_resid', help='suffix of UNSMOOTHED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl_bpss_resid)')
    parser.add_argument('--unprocessed_suffix', default='_b1_faln_dbnd_xr3d_uwrp_atl', help='suffix of UNPROCESSED fc-processed data (Default is _faln_dbnd_xr3d_uwrp_atl)')
    parser.add_argument('--TR', required=True, help='TR of session')
    parser.add_argument('--tmask', required=True, help='Path to tmask')
    parser.add_argument('--subcort_mask', required=True, help='Path to volumetric subcortical mask label file')
    parser.add_argument('--space', default='333', help='Voxel space to write outputs in')
    parser.add_argument('--fs_LR_surfdir', required=True, help='Location of fs_LR-registered surface (Should contain Native and fsaverage_LR32k subfolders with surfaces)')
    parser.add_argument('--t1_suffix', default='_mpr_debias_avgT_111_t88', help='suffix of T1 image (Default is _mpr_debias_avgT_111_t88)')
    parser.add_argument('--medial_mask_L', required=True, help='Left atlas medial wall mask')
    parser.add_argument('--medial_mask_R', required=True, help='Right atlas medial wall mask')
    parser.add_argument('--sw_medial_mask_L', help='small wall medial mask (Left)')
    parser.add_argument('--sw_medial_mask_R', help='small wall medial mask (Right)')
    parser.add_argument('--smoothnum', default=2.55, help='sigma of smoothing kernel to be applied')
    parser.add_argument('--output', default='/output', help='Path to output')

    # parse argumaents into dict
    settings = vars(parser.parse_args())

    # Run main function
    run(settings)
