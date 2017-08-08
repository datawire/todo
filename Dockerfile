FROM datawire/ambassador-envoy:latest

# This Dockerfile is set up to install all the application-specific stuff into
# /application.
#
# NOTE: If you don't know what you're doing, it's probably a mistake to
# blindly hack up this file.

# We need curl, pip, and dnsutils (for nslookup).
RUN apt-get update && apt-get -q install -y \
    curl \
    dnsutils

ENTRYPOINT [ "/usr/local/bin/envoy" ]
CMD [ "-c", "/etc/envoy/envoy.json" ]
