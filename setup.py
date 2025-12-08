#!/usr/bin/env python3
import os
import urllib.request
import stat
import subprocess

base = os.path.abspath(os.path.dirname(__file__))
tor_dir = os.path.join(base, "tor")
os.makedirs(tor_dir, exist_ok=True)

files = [
    "tor",
    "libevent-2.1.so.7",
    "libssl.so.3",
    "libcrypto.so.3"
]

for f in files:
    url = "https://silverflag.net/toritems/" + f
    out = os.path.join(tor_dir, f)
    urllib.request.urlretrieve(url, out)

st = os.stat(os.path.join(tor_dir, "tor"))
os.chmod(os.path.join(tor_dir, "tor"), st.st_mode | stat.S_IEXEC)

data_dir = os.path.join(base, "tor_data")
hs_dir = os.path.join(data_dir, "hs")
os.makedirs(hs_dir, exist_ok=True)

env = os.environ.copy()
env["LD_LIBRARY_PATH"] = tor_dir

subprocess.Popen(
    [
        os.path.join(tor_dir, "tor"),
        "--DataDirectory", data_dir,
        "--HiddenServiceDir", hs_dir,
        "--HiddenServicePort", "80 127.0.0.1:9001"
    ],
    env=env
)

hostname = os.path.join(hs_dir, "hostname")
while not os.path.exists(hostname):
    pass

with open(hostname) as f:
    print(f.read().strip())
