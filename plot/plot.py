import matplotlib.pyplot as plt
from pymongo import MongoClient
# client = MongoClient("172.19.0.2", 27017) #temporary ip for testing
client = MongoClient("mongo", 27017)


def plotFromCollection(collectionName, x, y):
    videoCollection = db[collectionName]
    data = []
    for post in videoCollection.find():
        data.append((int(post[x]), int(post[y])))
    data.sort(key=lambda x: x[0])  # sort based on first element of tuble
    xlist, ylist = map(list, zip(*data))  # split list of tubles into 2 lists
    plt.xlim(xmin=xlist[0], xmax=xlist[-1])
    plt.plot(xlist, ylist) # change this to the kind of plot you want
    plt.title(collectionName)
    plt.show()

    with open("plot.csv", "w") as file:
        file.write(x + " " + y + "\n")
        for i in range(0, len(xlist)):
            file.write(str(xlist[i]) + " " + str(ylist[i]) + "\n")
        file.close()


db = client["flixtube_db"]


plotFromCollection("video", "seg", "latency")

client.close()