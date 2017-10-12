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
