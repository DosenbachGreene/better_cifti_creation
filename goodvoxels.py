#!/usr/bin/env python3

import nibabel
import numpy
import os
import subprocess

def collect(settings,ribbon_path,session):
    """
        TO-DO Explaination of what this function does
    """
    # set goodvoxel settings (expose this to user in future?)
    neighsmooth = 5
    factor = 0.5

    # load tmask
    tmask = numpy.loadtxt(settings['tmask']).astype(bool)

    # load functional volume nifti
    img = nibabel.nifti1.load('/temp/funcvol_unprocessed.nii.gz')
    data = img.get_data()

    # apply tmask and save mean image
    data_mean = numpy.mean(data[:,:,:,tmask],axis=3)
    img_mean = nibabel.nifti1.Nifti1Image(data_mean,img.affine,header=img.header)
    nibabel.nifti1.save(img_mean,'/temp/funcvol_mean.nii.gz')

    # apply tmask and save std image
    data_std = numpy.std(data[:,:,:,tmask],axis=3)
    img_std = nibabel.nifti1.Nifti1Image(data_std,img.affine,header=img.header)
    nibabel.nifti1.save(img_std,'/temp/funcvol_sd1.nii.gz')

    # more fslmaths stuff...
    os.system('fslmaths /temp/funcvol_sd1 -div /temp/funcvol_mean /temp/funcvol_cov')
    os.system('fslmaths /temp/funcvol_cov -mas {} /temp/funcvol_cov_ribbon'.format(ribbon_path))
    p1 = subprocess.Popen(['fslstats', '/temp/funcvol_cov_ribbon', '-M'],stdout=subprocess.PIPE,universal_newlines=True)
    ribmean = float(p1.communicate()[0])
    os.system('fslmaths /temp/funcvol_cov_ribbon -div {} /temp/funcvol_cov_ribbon_norm'.format(ribmean))
    os.system('fslmaths /temp/funcvol_cov_ribbon_norm -bin -s {} /temp/funcvol_SmoothNorm'.format(neighsmooth))
    os.system('fslmaths /temp/funcvol_cov_ribbon_norm -s {0} -div /temp/funcvol_SmoothNorm -dilD /temp/funcvol_cov_ribbon_norm_s{0}'.format(neighsmooth))
    os.system('fslmaths /temp/funcvol_cov -div {} -div /temp/funcvol_cov_ribbon_norm_s{} -uthr 1000 /temp/funcvol_cov_norm_modulate'.format(ribmean,neighsmooth))
    os.system('fslmaths /temp/funcvol_cov_norm_modulate -mas {} /temp/funcvol_cov_norm_modulate_ribbon'.format(ribbon_path))
    p2 = subprocess.Popen(['fslstats','/temp/funcvol_cov_norm_modulate_ribbon','-S'],stdout=subprocess.PIPE,universal_newlines=True)
    final_ribstd = float(p2.communicate()[0])
    p3 = subprocess.Popen(['fslstats','/temp/funcvol_cov_norm_modulate_ribbon','-M'],stdout=subprocess.PIPE,universal_newlines=True)
    final_ribmean = float(p3.communicate()[0])
    upper = final_ribmean + (final_ribstd * factor)
    os.system('fslmaths /temp/funcvol_mean -bin /temp/funcvol_mask')
    os.system('fslmaths /temp/funcvol_cov_norm_modulate -thr {} -bin -sub /temp/funcvol_mask -mul -1 {}/goodvoxels/{}_goodvoxels'.format(upper,settings['output'],session))

    # delete temp files
    os.remove('/temp/funcvol_mean.nii.gz')
    os.remove('/temp/funcvol_sd1.nii.gz')
    os.remove('/temp/funcvol_cov.nii.gz')
    os.remove('/temp/funcvol_cov_ribbon.nii.gz')
    os.remove('/temp/funcvol_cov_ribbon_norm.nii.gz')
    os.remove('/temp/funcvol_SmoothNorm.nii.gz')
    os.remove('/temp/funcvol_cov_ribbon_norm_s{}.nii.gz'.format(neighsmooth))
    os.remove('/temp/funcvol_cov_norm_modulate.nii.gz')
    os.remove('/temp/funcvol_cov_norm_modulate_ribbon.nii.gz')
    os.remove('/temp/funcvol_mask.nii.gz')

    # return submask
    return '{}/goodvoxels/{}_goodvoxels.nii.gz'.format(settings['output'],session)
