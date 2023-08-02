# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set the desired hostname
ARG HOSTNAME=127.0.0.1
RUN echo "$HOSTNAME" > /etc/hostname


# Install required dependencies (Python, pip, gcc, musl-dev, bash)
RUN apt-get update && apt-get install -y python3 python3-pip gcc musl-dev bash
RUN ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1
# Copy rmr libraries from the builder image (assuming the build image is already available in your environment)
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.6.0 /usr/local/lib64/librmr* /usr/local/lib64/
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.6.0 /usr/local/bin/rmr* /usr/local/bin/

# RMR setup
RUN mkdir -p /opt/route/
COPY local.rt /opt/route/local.rt
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
ENV RMR_SEED_RT /opt/route/local.rt

# Install Python dependencies
COPY setup.py /tmp
COPY LICENSE /tmp/
RUN pip3 install /tmp
RUN pip3 install ricxappframe
RUN pip3 install --force-reinstall redis==3.0.1
ENV PYTHONUNBUFFERED 1

# Copy the application source code
COPY src/ /src

# Set the working directory inside the container
# WORKDIR /src
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Specify the command to run when the container starts
# CMD ["python3", "main.py"]
CMD PYTHONPATH=/src:/usr/lib/python3.7/site-packages/:$PYTHONPATH run-tp.py