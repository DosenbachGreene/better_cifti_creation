#!/bin/bash

docker run -it --rm \
    -v $(pwd):/mnt \
    -v $(pwd)/tmp:/tmp \
    -v $(pwd)/input:/input \
    -v $(pwd)/output:/output \
    vanandrew/better_cifti_creation \
    --tmask /data/nil-bluearc/GMT/Andrew/MSC/MSC01/COHORTSELECT/vc38671_NEW_TMASK.txt \
    --fcprocessed_dir /input/vc38671 \
    --subcort_mask /data/nil-bluearc/GMT/Ortega/MSC-Stuff/MSC_subcortical_mask_native_freesurf_222/MSC01/subcortical_mask_LR_222.nii \
    --fs_LR_surfdir /data/nil-bluearc/GMT/Laumann/MSC/MSM_nativeresampled2_TYNDC/MSC01 \
    --medial_mask_L /data/nil-bluearc/GMT/Laumann/MSC/MSM_nativeresampled2_TYNDC/MSC01/fsaverage_LR32k/MSC01.L.atlasroi.32k_fs_LR.shape.gii \
    --medial_mask_R /data/nil-bluearc/GMT/Laumann/MSC/MSM_nativeresampled2_TYNDC/MSC01/fsaverage_LR32k/MSC01.R.atlasroi.32k_fs_LR.shape.gii
