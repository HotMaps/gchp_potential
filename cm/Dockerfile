#
# hotmaps/cm image Dockerfile
#
#
FROM zarch/alpine-grass-gis:grass77_py3_r74118


MAINTAINER Pietro Zambelli <pietro.zambelli@eurac.edu>


ENV PACKAGES="\
    ca-certificates \
    "

# Copy app source code
COPY . /cm
WORKDIR /cm

# Add the packages
RUN echo "Install main packages";\
    apk update && \
    apk add --no-cache \
            --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
            --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
            $PACKAGES && \
    pip3 install -r requirements.txt && \
    pip3 install gunicorn && \
    mkdir -p /data && \
    mkdir -p /var/log/supervisor;

# setup volume
VOLUME /data

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

# CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run:application"]

# Start processes
CMD ["/cm/wait-for-it.sh","rabbit:5672","--strict","--timeout=360","--","/usr/bin/supervisord"]


