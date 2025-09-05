FROM python:3.12-bookworm

ENV VIRTUALENV="/opt/membership/.venv"
ARG pip="${VIRTUALENV}/bin/pip"
ARG tag="latest"

COPY . /opt/membership

# create user, install apt dependencies as root and setup uwsgi etc.
USER root

RUN set -ex && \
	groupadd -r membership && \
	useradd -r -g membership -m -d /opt/membership membership

COPY uwsgi.ini /etc/uwsgi.ini
WORKDIR /opt/membership

RUN set -ex && \
    chown -R membership:membership /opt/membership

# XXX do we still need this?
RUN chmod g=u /etc/passwd

# all the installations etc can be done using the unprivileged membership user
USER membership

RUN set -ex && \
    python -m venv ${VIRTUALENV} && \
    ${pip} install --upgrade pip setuptools wheel && \
    ${pip} install -r requirements.txt && \
    ${pip} install uwsgi

RUN chmod 755 /opt/membership/*.sh

ENTRYPOINT ["/opt/membership/docker_entrypoint.sh"]
EXPOSE 59999
