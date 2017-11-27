#!/usr/bin/env python3

import nibabel
import numpy
import os
import subprocess

def collect(settings,ribbon_path,session,temp_dir):
    """
        TO-DO Explaination of what this function does
    """
    # set goodvoxel settings (expose this to user in future?)
    neighsmooth = 5
    factor = 0.5

    # load tmask
    tmask = numpy.loadtxt(settings['tmask']).astype(bool)

    # load functional volume nifti
    img = nibabel.nifti1.load('{}/funcvol_unprocessed.nii.gz'.format(temp_dir))
    data = img.get_data()

    # apply tmask and save mean image
    data_mean = numpy.mean(data[:,:,:,tmask],axis=3)
    img_mean = nibabel.nifti1.Nifti1Image(data_mean,img.affine,header=img.header)
    nibabel.nifti1.save(img_mean,'{}/funcvol_mean.nii.gz'.format(temp_dir))

    # apply tmask and save std image
    data_std = numpy.std(data[:,:,:,tmask],axis=3)
    img_std = nibabel.nifti1.Nifti1Image(data_std,img.affine,header=img.header)
    nibabel.nifti1.save(img_std,'{}/funcvol_sd1.nii.gz'.format(temp_dir))

    # more fslmaths stuff...
    os.system('fslmaths {0}/funcvol_sd1 -div {0}/funcvol_mean {0}/funcvol_cov'.format(temp_dir))
    os.system('fslmaths {0}/funcvol_cov -mas {1} {0}/funcvol_cov_ribbon'.format(temp_dir,ribbon_path))
    p1 = subprocess.Popen(['fslstats', '{}/funcvol_cov_ribbon'.format(temp_dir), '-M'],stdout=subprocess.PIPE,universal_newlines=True)
    ribmean = float(p1.communicate()[0])
    os.system('fslmaths {0}/funcvol_cov_ribbon -div {1} {0}/funcvol_cov_ribbon_norm'.format(temp_dir,ribmean))
    os.system('fslmaths {0}/funcvol_cov_ribbon_norm -bin -s {1} {0}/funcvol_SmoothNorm'.format(temp_dir,neighsmooth))
    os.system('fslmaths {0}/funcvol_cov_ribbon_norm -s {1} -div {0}/funcvol_SmoothNorm -dilD {0}/funcvol_cov_ribbon_norm_s{1}'.format(temp_dir,neighsmooth))
    os.system('fslmaths {0}/funcvol_cov -div {1} -div {0}/funcvol_cov_ribbon_norm_s{2} -uthr 1000 {0}/funcvol_cov_norm_modulate'.format(temp_dir,ribmean,neighsmooth))
    os.system('fslmaths {0}/funcvol_cov_norm_modulate -mas {1} {0}/funcvol_cov_norm_modulate_ribbon'.format(temp_dir,ribbon_path))
    p2 = subprocess.Popen(['fslstats','{}/funcvol_cov_norm_modulate_ribbon'.format(temp_dir),'-S'],stdout=subprocess.PIPE,universal_newlines=True)
    final_ribstd = float(p2.communicate()[0])
    p3 = subprocess.Popen(['fslstats','{}/funcvol_cov_norm_modulate_ribbon'.format(temp_dir),'-M'],stdout=subprocess.PIPE,universal_newlines=True)
    final_ribmean = float(p3.communicate()[0])
    upper = final_ribmean + (final_ribstd * factor)
    os.system('fslmaths {0}/funcvol_mean -bin {0}/funcvol_mask'.format(temp_dir))
    os.system('fslmaths {0}/funcvol_cov_norm_modulate -thr {1} -bin -sub {0}/funcvol_mask -mul -1 {2}/goodvoxels/{3}_goodvoxels'.format(temp_dir,upper,settings['output'],session))

    # delete temp files
    os.remove('{}/funcvol_mean.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_sd1.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_cov.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_cov_ribbon.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_cov_ribbon_norm.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_SmoothNorm.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_cov_ribbon_norm_s{}.nii.gz'.format(temp_dir,neighsmooth))
    os.remove('{}/funcvol_cov_norm_modulate.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_cov_norm_modulate_ribbon.nii.gz'.format(temp_dir))
    os.remove('{}/funcvol_mask.nii.gz'.format(temp_dir))

    # return submask
    return '{}/goodvoxels/{}_goodvoxels.nii.gz'.format(settings['output'],session)
