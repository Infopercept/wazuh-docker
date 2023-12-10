# Wazuh Docker Copyright (C) 2017, Wazuh Inc. (License GPLv2)
FROM ubuntu:focal

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ARG WAZUH_VERSION
ARG WAZUH_TAG_REVISION
ARG TEMPLATE_VERSION=4.4
ARG FILEBEAT_CHANNEL=filebeat-oss
ARG FILEBEAT_VERSION=7.10.2
ARG WAZUH_FILEBEAT_MODULE="wazuh-filebeat-0.2.tar.gz"

RUN apt-get update && apt install curl apt-transport-https lsb-release gnupg python3-pip -y

COPY config/check_repository.sh /

RUN chmod 775 /check_repository.sh
RUN source /check_repository.sh

RUN apt-get update && \
    apt-get install wazuh-manager=${WAZUH_VERSION}-${WAZUH_TAG_REVISION}

RUN pip3 install requests configparser

RUN curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/${FILEBEAT_CHANNEL}-${FILEBEAT_VERSION}-amd64.deb &&\
    dpkg -i ${FILEBEAT_CHANNEL}-${FILEBEAT_VERSION}-amd64.deb && rm -f ${FILEBEAT_CHANNEL}-${FILEBEAT_VERSION}-amd64.deb && \
    curl -s https://packages.wazuh.com/4.x/filebeat/${WAZUH_FILEBEAT_MODULE} | tar -xvz -C /usr/share/filebeat/module

RUN curl -L https://github.com/aelsabbahy/goss/releases/latest/download/goss-linux-amd64 -o /usr/local/bin/goss && chmod +rx /usr/local/bin/goss

ARG S6_VERSION="v2.2.0.3"
RUN curl --fail --silent -L https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz \
    -o /tmp/s6-overlay-amd64.tar.gz && \
    tar xzf /tmp/s6-overlay-amd64.tar.gz -C / --exclude="./bin" && \
    tar xzf /tmp/s6-overlay-amd64.tar.gz -C /usr ./bin && \
    rm  /tmp/s6-overlay-amd64.tar.gz

# Installing AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN apt install unzip
RUN unzip awscliv2.zip
RUN ./aws/install
RUN apt remove unzip -y

# Install BOTO3
RUN /var/ossec/framework/python/bin/pip3 install boto3

COPY config/etc/ /etc/
COPY config/master.conf /var/ossec/etc/ossec.conf
COPY --chown=root:wazuh config/create_user.py /var/ossec/framework/scripts/create_user.py

COPY config/filebeat.yml /etc/filebeat/

RUN chmod go-w /etc/filebeat/filebeat.yml

ADD https://raw.githubusercontent.com/wazuh/wazuh/$TEMPLATE_VERSION/extensions/elasticsearch/7.x/wazuh-template.json /etc/filebeat
RUN chmod go-w /etc/filebeat/wazuh-template.json

# Prepare permanent data
# Sync calls are due to https://github.com/docker/docker/issues/9547

COPY config/permanent_data.env config/permanent_data.sh /
RUN chmod 755 /permanent_data.sh && \
    sync && /permanent_data.sh && \
    sync && rm /permanent_data.sh

# Adding custom ossec.conf for K8S
COPY config/master.conf /var/ossec/etc/ossec.conf

# 1pass logs Fetcher
COPY config/integrations/1pass-config.properties     /var/ossec/integrations/
COPY config/integrations/1pass-logs.py       /var/ossec/integrations/

# Okta logs Fetcher
COPY config/integrations/okta-config.properties /var/ossec/integrations/
COPY config/integrations/oktalogs.py /var/ossec/integrations/

# Copying Slack script into integrations
COPY ./config/integrations/custom-slack.py /var/ossec/integrations/custom-slack.py
COPY ./config/integrations/custom-slack /var/ossec/integrations/custom-slack

# StrongDM
RUN apt install unzip
RUN curl -L https://app.strongdm.com/releases/cli/linux -o /var/ossec/integrations/sdm.zip
RUN unzip /var/ossec/integrations/sdm.zip -d /var/ossec/integrations/
RUN rm -rf /var/ossec/integrations/sdm.zip
RUN apt remove unzip -y
RUN chmod +xr /var/ossec/integrations/sdm
COPY config/integrations/sdm-logs.sh /var/ossec/integrations/sdm-logs.sh
RUN chmod +xr /var/ossec/integrations/sdm-logs.sh

# Services ports
EXPOSE 55000/tcp 1514/tcp 1515/tcp 514/udp 1516/tcp

ENTRYPOINT [ "/init" ]
