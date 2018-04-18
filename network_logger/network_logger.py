import docker # install docker not docker-py
from multiprocessing import Pool

client = docker.from_env()
containers = client.containers.list()

IMAGE = 'andreasmalling/ft_user'

for container in containers:
    stream = container.stats(decode=True, stream=True)
    if not container.attrs['Config']['Image'] == IMAGE:
        continue
    ip = container.attrs['NetworkSettings']['Networks']['flixtube_default']['IPAddress']
    for val in stream:
        print(val['networks']['eth0'])
        print(val['read'])