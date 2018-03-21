import matplotlib.pyplot as plt
from pymongo import MongoClient
client = MongoClient("172.19.0.2", 27017) #temporary ip for testing


def plotFromCollection(collectionName, x, y):
    videoCollection = db[collectionName]
    data = []
    for post in videoCollection.find():
        data.append((int(post[x]), int(post[y])))
    data.sort(key=lambda x: x[0])  # sort based on first element of tuble
    xlist, ylist = map(list, zip(*data))  # split list of tubles into 2 lists
    plt.xlim(xmin=xlist[0], xmax=xlist[-1])
    print(xlist)
    print(xlist[-1])
    plt.plot(xlist, ylist) #change this to the kind of plot you want
    plt.title(collectionName)
    plt.show()

db = client["flixtube_db"]


plotFromCollection("video", "timestamp", "latency")

client.close()