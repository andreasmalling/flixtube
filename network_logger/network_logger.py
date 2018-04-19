import docker  # install docker not docker-py
import sys
from pymongo import MongoClient
from time import sleep

IMAGE = 'andreasmalling/ft_user'
BASEURL = 'unix://var/run/docker.sock'
pull_rate = 1 #default pull rate, NOTE: time between pulls is about 2 seconds higher than pull_rate, depending in CPU speed

if __name__ == '__main__':

    if len(sys.argv) > 1:
        pull_rate = int(sys.argv[1])

    mongo_client = MongoClient("mongo", 27017)          # use this in docker network
    # mongo_client = MongoClient("127.0.0.1", 27017)    # use this in testing
    db = mongo_client["flixtube_db"]

    while True:
        client = docker.DockerClient(base_url=BASEURL)
        containers = client.containers.list()
        insertList = []
        for container in containers:
            if container.attrs['Config']['Image'] != IMAGE:
                continue
            ip = container.attrs['NetworkSettings']['Networks']['flixtube_default']['IPAddress']
            val = container.stats(decode=True, stream=False)
            data = {'ip': ip,
                    'ts': val['read'],
                    'net': val['networks']['eth0']}
            insertList += [data]
        if (len(insertList) > 0):
            db['network'].insert_many(insertList)
            insertList = []
        sleep(pull_rate)
