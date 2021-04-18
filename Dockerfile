#
# Build our container that runs Splunk Lab with the AWS S3 Logs addin
#

FROM python:3

WORKDIR /mnt

COPY * .

COPY bin/entrypoint.sh /

RUN pip install -r ./requirements.txt

ENTRYPOINT ["/entrypoint.sh"]


