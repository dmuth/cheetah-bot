#
# Build our container that runs Splunk Lab with the AWS S3 Logs addin
#

FROM python:3

WORKDIR /mnt

COPY * .
RUN pip install -r ./requirements.txt

COPY bin/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]


