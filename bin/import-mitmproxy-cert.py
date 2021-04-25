#!/usr/bin/env python3
#
# This script is used to import the mitmproxy CA so that the Dockerized bot
# can properly talk to mitmproxy.
#

import certifi
import pathlib
import os

caroot = certifi.where()
print("#")
print(f"# Found caroot in this container: {caroot}")
print("#")

#
# Change to the parent directory of our script
#
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(f"{script_dir}/..")

cert = "mitmproxy-ca-cert.pem"

cert = pathlib.Path.cwd() / cert
if not cert.exists():
	raise Exception(f"Cert file {cert} does not exist!\n" 
		+ "\n"
		+ "Please go to the project root in the host machine and run this command: \n"
		+ "\n"
		+ "\tcp ~/.mitmproxy/mitmproxy-ca-cert.pem . \n"
		)

cert = cert.read_text()

#with caroot.open("ab") as output:
with open(caroot, "a") as output:
	output.write(cert)

print(f"# Successfully wrote mitmproxy CA to {caroot}!")


