# better cifti creation image
FROM vanandrew/dglabimg:v1.00
MAINTAINER Andrew Van <vanandrew@wustl.

# Add cifti creation script to /mnt
ADD better_cifti_creation.py /mnt/
ADD goodvoxels.py /mnt/
ADD ribbon.py /mnt/
ADD FreeSurferAllLut.txt /mnt/

# Set Entrypoint
WORKDIR /mnt
ENTRYPOINT ["./better_cifti_creation.py"]
