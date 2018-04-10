import subprocess

class Ipfs:
    def __init__(self):
        subprocess.run(["ipfs", "init"])

    def run_daemon(self):
        subprocess.Popen(["ipfs", "daemon"])

    def bootstrap_local(self):
        address = "/dnsaddr/bootstrap/tcp/4001/ipfs/QmRuQ3sSxtuJBHYKJnLcYDFK4RVELydNDJ9F2vPg9Uj1H3"
        subprocess.run(["ipfs", "bootstrap", "rm", "all"])
        subprocess.run(["ipfs", "bootstrap", "add", address])

    def bootstrap_default(self):
        subprocess.run(["ipfs", "bootstrap", "add", "default"])

    def add(self, path):
        subprocess.run(["ipfs", "add", path])