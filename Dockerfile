#
# Build our container that runs Splunk Lab with the AWS S3 Logs addin
#

FROM python:3

WORKDIR /mnt

#
# Get our requirements out of the way so a code change doesn't force a re-run of this.
#
COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY . .

COPY bin/entrypoint.sh /


ENTRYPOINT ["/entrypoint.sh"]


