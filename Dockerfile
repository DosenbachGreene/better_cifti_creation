# better cifti creation image
FROM vanandrew/dglabimg:v1.00
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# install python3 and nibabel
RUN apt-get update && apt-get install -y --allow-unauthenticated python3 python3-pip && \
    pip3 install nibabel numpy

# Add cifti creation script to /mnt
ADD better_cifti_creation.py /mnt/
ADD goodvoxels.py /mnt/
ADD ribbon.py /mnt/
ADD FreeSurferAllLut.txt /mnt/

# Set Entrypoint
WORKDIR /mnt
ENTRYPOINT ["./better_cifti_creation.py"]
