#!/bin/bash

docker run -it --rm \
    -v $(pwd):/mnt \
    -v $(pwd)/tmp:/tmp \
    -v $(pwd)/input:/input \
    -v $(pwd)/output:/output \
    vanandrew/better_cifti_creation \
    --tmask /input/vc38671_NEW_TMASK.txt \
    --TR 2.2 \
    --fcprocessed_dir /input/vc38671 \
    --subcort_mask /input/subcortical_mask_LR_333.nii \
    --fs_LR_surfdir /input/MSC01 \
    --medial_mask_L /input/MSC01.L.atlasroi.32k_fs_LR.shape.gii \
    --medial_mask_R /input/MSC01.R.atlasroi.32k_fs_LR.shape.gii
