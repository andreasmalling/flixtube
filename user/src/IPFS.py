import subprocess

class Ipfs:
    def __init__(self):
        subprocess.run(["ipfs", "init"])

    def run_daemon(self):
        subprocess.Popen(["ipfs", "daemon"])

    def bootstrap_local(self):
        address = "/dnsaddr/bootstrap/tcp/4001/ipfs/QmfFKpMNi5RZweU5HnCH4NPwRrMDg4uRkEHcnFXAG9hEbm"
        subprocess.run(["ipfs", "bootstrap", "rm", "all"])
        subprocess.run(["ipfs", "bootstrap", "add", address])

    def bootstrap_default(self):
        subprocess.run(["ipfs", "bootstrap", "add", "default"])

    def add(self, path):
        subprocess.run(["ipfs", "add", "-r", "-Q", path])

    def gateway_public(self, public=True):
        if public:
            ip = "0.0.0.0"
        else:
            ip = "127.0.0.1"
        subprocess.run(["ipfs", "config", "Addresses.Gateway", "/ip4/" + ip + "/tcp/8080"])