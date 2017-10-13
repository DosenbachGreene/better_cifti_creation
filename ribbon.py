#!/usr/bin/env python3

import os
import glob

def create(settings):
    """
        Create ribbon from surface data
    """
    # define directories for surface files
    print('Creating Ribbon...')
    Native = os.path.join(settings['fs_LR_surfdir'],'Native')
    Ribbon = os.path.join(settings['output'],'Ribbon')
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
        print('Processing {}...'.format(side))
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
    print('Ribbon Creation Done.')

    # return 333 ribbon
    return '{}/{}.ribbon_333.nii.gz'.format(Ribbon,sub),sub
