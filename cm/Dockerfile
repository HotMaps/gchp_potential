#
# hotmaps/cm image Dockerfile
#
FROM jeanmariealder/gchp_image
MAINTAINER Pietro Zambelli <pietro.zambelli@eurac.edu>
ENV PACKAGES="\
    ca-certificates \
    supervisor \
    " \
    GRASSBIN="grass78"

# Create main directories
RUN mkdir -p /cm && \
    mkdir -p /data && \
    mkdir -p /var/log/supervisor

COPY . /cm
WORKDIR /cm

# Add the packages
RUN echo "Install main packages";\
    apt-get update && \
    apt-get upgrade --yes && \
    apt-get install $PACKAGES --yes && \
    apt-get install python3-pip python3-gdal --yes && \
    python3 -m pip install wheel && \
    python3 -m pip install -r requirements.txt


# setup volume
VOLUME /data

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80
# Start processes
CMD ["/usr/bin/supervisord"]


