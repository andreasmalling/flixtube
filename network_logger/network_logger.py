from multiprocessing import Pool
import docker  # install docker not docker-py
from pymongo import MongoClient

IMAGE = 'andreasmalling/ft_user'
BASEURL = 'unix://var/run/docker.sock' #todo change this to wherever it is mounted to


def stream_container(id):
    local_client = docker.DockerClient(base_url=BASEURL)
    container = local_client.containers.get(id)
    stream = container.stats(decode=True, stream=True)
    if container.attrs['Config']['Image'] == IMAGE:
        ip = container.attrs['NetworkSettings']['Networks']['flixtube_default']['IPAddress']
        # client = MongoClient("mongo", 27017) #todo use this in docker network
        mongo_client = MongoClient("127.0.0.1", 27017)
        db = mongo_client["flixtube_db"]

        # read stream
        for val in stream:
            data = {'ip': ip,
                    'ts': val['read'],
                    'net': val['networks']['eth0']}
            db['network'].insert_one(data)


if __name__ == '__main__':
    client = docker.DockerClient(base_url=BASEURL)
    containers = client.containers.list()
    ids = [c.id for c in containers]
    try:
        pool = Pool()
        pool.map(stream_container, ids)
    finally:
        pool.close()
