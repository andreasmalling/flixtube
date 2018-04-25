import matplotlib.pyplot as plt
import pymongo
import statistics

# collections
VIDEO = "video"
AUDIO = "audio"
WAIT = "wait"
PERSONA = "persona"
NETWORK = "network"

# init mongo client
client = pymongo.MongoClient("localhost", 27017) #temporary ip for testing
# client = pymongo.MongoClient("mongo", 27017)
db = client["flixtube_db"]

# export csv:
#
# with open("plot.csv", "w") as file:
#     file.write(x + " " + y + "\n")
#     for i in range(0, len(xlist)):
#         file.write(str(xlist[i]) + " " + str(ylist[i]) + "\n")
#     file.close()


def main():
    users = [persona for persona in db[PERSONA].find()]

    plot_user_data("latency", users, AUDIO)
    plot_user_data("download", users, AUDIO)
    plot_user_data("latency", users, VIDEO)
    plot_user_data("download", users, VIDEO)
    # plot_network_data()

    # plotFromCollection("video", "seg", "latency")

    # close mongo client
    client.close()


def plot_user_data(yname , users, collection):
    last_seg = db[AUDIO].find_one(sort=[("seg", pymongo.DESCENDING)])["seg"]
    segments = [x for x in range(last_seg+1)]
    for user in users:
        user[yname] = [0 for i in range(last_seg+1)] #maybe change 0 to something else?????????
        for res in db[collection].find({"ip": user["ip"]}).sort("seg", pymongo.ASCENDING):
            if res["seg"] < len(user[yname]):
                user[yname][res["seg"]] = res[yname]
        plt.plot(segments, user[yname], label=user["type"], color="green")
    #mean
    means = [statistics.mean([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, means, color="red")

    #stdev
    stdev = [statistics.stdev([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, stdev, color="blue")

    plt.title(collection + " " + yname)

    plt.show()

def plot_network_data():
    pass


if __name__ == "__main__":
    main()
