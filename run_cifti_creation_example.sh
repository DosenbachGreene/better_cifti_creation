#!/bin/bash

# run --help for more options
docker run -it --rm \
    -v $(pwd)/input:/input \ # Mount inputs to the docker image
    -v $(pwd)/output:/output \ # Mount outputs to the docker image
    vanandrew/better_cifti_creation \ # Call docker image
    --tmask /input/vc38671_NEW_TMASK.txt \ # Define location of tmask relative to docker image
    --TR 2.2 \ # Define TR
    --fcprocessed_dir /input/vc38671 \ # Define fc-processed directory relative to docker image
    --subcort_mask /input/subcortical_mask_LR_333.nii \ # Define sub-cortical mask relative to docker image
    --fs_LR_surfdir /input/MSC01 \ # Define fs_LR_surfdir relative to docker image
    --medial_mask_L /input/MSC01.L.atlasroi.32k_fs_LR.shape.gii \ # Define medial mask relative to docker image
    --medial_mask_R /input/MSC01.R.atlasroi.32k_fs_LR.shape.gii

singularity run \
-B /data/cn4/dgreene/Patients/PediatricMSC/MSCPI05/Functionals/vc42936:/input/fcprocessed_dir \
-B /data/cn4/dgreene/Patients/PediatricMSC/MSCPI05/Functionals/vc42936:/input/tmask_dir \
-B [subcortical mask dir]:/input/subcort_mask_dir \
-B [fs_lr surf dir]:/input/fs_lr_surf_dir \
-B [medial mask dir]:/input/medial_mask_dir \
-B [output dir]:/output \
/data/nil-bluearc/GMT/Singularity/better_cifti_creation.img \
--fcprocessed_suffix _faln_dbnd_xr3d_uwrp_atl_bpss_resid \
--unprocessed_suffix _faln_dbnd_xr3d_uwrp_atl \
--run bold2 \
--TR 1.1 \
--tmask vc42936_b1_tmask.txt
--subcort_mask [filename of subcortical mask].nii
