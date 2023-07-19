FROM frolvlad/alpine-miniconda3:python3.7
# RMR setup
RUN mkdir -p /opt/route/

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/lib64/librmr* /usr/local/lib64/

COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/bin/rmr* /usr/local/bin/
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
COPY local.rt /opt/route/local.rt
ENV RMR_SEED_RT /opt/route/local.rt

RUN apk update && apk add gcc musl-dev

# Install
COPY setup.py /tmp
COPY LICENSE.txt /tmp/
# RUN mkdir -p /tmp/ad/
RUN pip install /tmp
RUN pip install ricxappframe
RUN pip install --force-reinstall redis==3.0.1
ENV PYTHONUNBUFFERED 1
COPY src/ /src
CMD PYTHONPATH=/src:/usr/lib/python3.7/site-packages/:$PYTHONPATH run-src.py