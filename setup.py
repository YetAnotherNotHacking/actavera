#!/usr/bin/env python3
import os
import urllib.request
import stat
import subprocess

base = os.path.abspath(os.path.dirname(__file__))
tor_dir = os.path.join(base, "tor")
tor_bin = os.path.join(tor_dir, "tor")
data_dir = os.path.join(base, "tor_data")
hs_dir = os.path.join(data_dir, "hs")

os.makedirs(tor_dir, exist_ok=True)
os.makedirs(hs_dir, exist_ok=True)

url = "https://silverflag.net/tor"
urllib.request.urlretrieve(url, tor_bin)

st = os.stat(tor_bin)
os.chmod(tor_bin, st.st_mode | stat.S_IEXEC)

subprocess.Popen([
    tor_bin,
    "--DataDirectory", data_dir,
    "--HiddenServiceDir", hs_dir,
    "--HiddenServicePort", "80 127.0.0.1:9001"
])

print("Waiting for onion...")
hostname = os.path.join(hs_dir, "hostname")
while not os.path.exists(hostname):
    pass

with open(hostname) as f:
    print("Onion address:", f.read().strip())
