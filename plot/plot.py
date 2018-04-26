import matplotlib.pyplot as plt
import pymongo
import statistics
import dateutil
import time
from pathlib import Path

# collections
VIDEO = "video"
AUDIO = "audio"
WAIT = "wait"
PERSONA = "persona"
NETWORK = "network"
PATH = "output/"


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

    plot_user_data_seg("latency", users, AUDIO)
    plot_user_data_seg("download", users, AUDIO)
    plot_user_data_seg("latency", users, VIDEO)
    plot_user_data_seg("download", users, VIDEO)

    plot_user_data_time("latency", users, AUDIO)
    plot_user_data_time("download", users, AUDIO)
    plot_user_data_time("latency", users, VIDEO)
    plot_user_data_time("download", users, VIDEO)

    plot_network_data_time("rx_bytes", users)
    plot_network_data_time("tx_bytes", users)
    plot_network_data_time("rx_packets", users)
    plot_network_data_time("tx_packets", users)

    plot_network_data_hist("rx_bytes", "tx_bytes", users)
    plot_network_data_hist("rx_packets", "tx_packets", users)

    # TODO add export to .csv

    # close mongo client
    client.close()


def plot_user_data_seg(yname, users, collection):
    last_seg = db[AUDIO].find_one(sort=[("seg", pymongo.DESCENDING)])["seg"]
    segments = [x for x in range(last_seg+1)]
    for user in users:
        user[yname] = [0 for i in range(last_seg+1)] #maybe change 0 to something else?????????
        for res in db[collection].find({"ip": user["ip"]}).sort("seg", pymongo.ASCENDING):
            if res["seg"] < len(user[yname]):
                user[yname][res["seg"]] = res[yname]
        plt.plot(segments, user[yname], color="green")
    #mean
    means = [statistics.mean([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, means, color="red", label="mean")

    #stdev
    stdev = [statistics.stdev([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, stdev, color="blue", label="stdev")

    plt.legend()
    plt.title(collection + " " + yname + " per segments")
    plt.xlabel("segment number")
    plt.ylabel(yname)

    plt.savefig(PATH + collection + "_" + yname + "_seg.png")
    plt.show()


def plot_user_data_time(yname, users, collection):
    for user in users:
        cursor = db[collection].find({"ip": user["ip"]}).sort("timestamp", pymongo.ASCENDING)
        xs = []
        ys = []
        sum = 0
        for elem in cursor:
            xs += [elem["timestamp"]]
            sum += elem[yname]
            ys += [sum]
        plt.plot(xs, ys)
    plt.title(collection + " " + yname + " over time")
    plt.xlabel("time")
    plt.ylabel(yname)
    plt.savefig(PATH + collection + "_" + yname + "_time.png")
    plt.show()



def plot_network_data_time(yname, users):
    for user in users:
        xs = []
        ys = []
        for res in db[NETWORK].find({"ip": user["ip"]}).sort("ts", pymongo.ASCENDING):
            xs += [int(time.mktime(dateutil.parser.parse(res["ts"]).timetuple()))]
            ys += [res["net"][yname]]
        plt.plot(xs, ys)
    plt.title("network " + yname)
    plt.savefig(PATH + "network_" + yname + "_time.png")
    plt.xlabel("time")
    plt.ylabel(yname[3:])
    plt.show()


def plot_network_data_hist(yname1, yname2, users):
    xs = [str(i) + ": " + users[i]["type"] for i in range(len(users))]
    ys1 = []
    ys2 = []
    for user in users:
        res = db[NETWORK].find_one({"ip": user["ip"]}, sort=[("ts", pymongo.DESCENDING)])
        ys1 += [res["net"][yname1]]
        ys2 += [res["net"][yname2]]
    plt.bar(xs, ys1, color="blue", width=-0.4, align="edge", label=yname1)
    plt.bar(xs, ys2, color="red", width=0.4, align="edge", label=yname2)
    plt.legend()
    plt.title("network histogram " + yname1 + " & " + yname2)
    plt.xlabel("users")
    plt.ylabel(yname1[3:])
    plt.savefig(PATH + "network_" + yname1 + "_" + yname2 + "_hist.png")

    plt.show()


if __name__ == "__main__":
    main()
