# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
	py3-pip

RUN pip install --upgrade jsonpath-ng requests paho-mqtt pyyaml

# Copy root filesystem
COPY rootfs /
