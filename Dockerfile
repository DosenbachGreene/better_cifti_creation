# better cifti creation image
FROM vanandrew/dglabimg
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# install python3 and nibabel
RUN apt-get update && apt-get install -y --allow-unauthenticated python3 python3-pip && \
    pip3 install nibabel numpy

# Set Entrypoint
WORKDIR /mnt
ENTRYPOINT ["./better_cifti_creation.py"]
