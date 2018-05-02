import datetime
import matplotlib
import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymongo
import statistics
import dateutil
import time

# collections
VIDEO = "video"
AUDIO = "audio"
WAIT = "wait"
PERSONA = "persona"
NETWORK = "network"

BEHAVIOURS = ["BINGE", "INCOGNITO", "SKIPPER", "IDLE", "LEECHER"]
COLORDIC = {
    "BINGE": "blue",
    "INCOGNITO": "green",
    "SKIPPER": "red",
    "IDLE" : "cyan",
    "LEECHER" : "magenta"
}
# init mongo client
client = pymongo.MongoClient("localhost", 27017) #temporary ip for testing
# client = pymongo.MongoClient("mongo", 27017)
db = client["flixtube_db"]


def main():
    print("ready")
    global PATH
    PATH = "output/" + datetime.datetime.now().isoformat('_') + "/"
    os.mkdir(PATH)
    users = [persona for persona in db[PERSONA].find()]
    users_no_idle = list(filter(lambda x: x["type"] != "IDLE", users))

    # give users identifying number
    for i in range(len(users)):
        users[i]["num"] = i

    # behaviour average plots
    users_b = []
    for i in range(len(BEHAVIOURS)):
        tmp = list(filter(lambda x: x["type"] == BEHAVIOURS[i], users))
        if tmp:
            users_b += [tmp]

    print("plotting user data for segments")
    plot_user_data_seg("latency", users_no_idle, AUDIO)
    plot_user_data_seg("download", users_no_idle, AUDIO)
    plot_user_data_seg("latency", users_no_idle, VIDEO)
    plot_user_data_seg("download", users_no_idle, VIDEO)

    print("plotting user data over time")
    plot_user_data_time("latency", users_no_idle, AUDIO)
    plot_user_data_time("download", users_no_idle, AUDIO)
    plot_user_data_time("latency", users_no_idle, VIDEO)
    plot_user_data_time("download", users_no_idle, VIDEO)

    print("plotting network data over time")
    plot_network_data_time("rx_bytes", users)
    plot_network_data_time("tx_bytes", users)
    plot_network_data_time("rx_packets", users)
    plot_network_data_time("tx_packets", users)

    print("plotting network histogram")
    plot_network_data_hist("rx_bytes", "tx_bytes", users)
    plot_network_data_hist("rx_packets", "tx_packets", users)

    print("plotting user data for segments per role")
    plot_user_data_seg_role("latency", users_b, AUDIO)
    plot_user_data_seg_role("download", users_b, AUDIO)
    plot_user_data_seg_role("latency", users_b, VIDEO)
    plot_user_data_seg_role("download", users_b, VIDEO)

    print("plotting network histogram per role")
    plot_network_data_hist_role("rx_bytes", "tx_bytes", users_b)
    plot_network_data_hist_role("rx_packets", "tx_packets", users_b)

    # close mongo client
    client.close()


def plot_user_data_seg(yname, users, collection):
    csv = CSVBuilder()
    last_seg = db[AUDIO].find_one(sort=[("seg", pymongo.DESCENDING)])["seg"]
    segments = [x for x in range(last_seg+1)]
    csv.add_plot("segments", segments)
    for user in users:
        user[yname] = [0 for i in range(last_seg+1)] #maybe change 0 to something else?????????
        for res in db[collection].find({"ip": user["ip"], "responsecode": 200}).sort("seg", pymongo.ASCENDING):
            if res["seg"] < len(user[yname]):
                user[yname][res["seg"]] = res[yname]
        plt.plot(segments, user[yname], color="green")
        csv.add_plot(str(user["num"]), user[yname])
    #mean
    means = [statistics.mean([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, means, color="red", label="mean")
    csv.add_plot("means", means)

    #stdev
    stdev = [statistics.stdev([user[yname][i] for user in users]) for i in range(last_seg+1)]
    plt.plot(segments, stdev, color="blue", label="stdev")
    csv.add_plot("stdev", stdev)

    plt.title(collection + " " + yname + " per segments")
    plt.legend()
    plt.xlabel("segment number")
    plt.ylabel(yname)

    path = PATH + collection + "_" + yname + "_seg"
    csv.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def plot_user_data_seg_role(yname, users_b, collection):
    csv = CSVBuilder()
    last_seg = db[AUDIO].find_one(sort=[("seg", pymongo.DESCENDING)])["seg"]
    segments = [x for x in range(last_seg+1)]
    csv.add_plot("segments", segments)
    for role in users_b:
        for user in role:
            user[yname] = [0 for i in range(last_seg+1)] #maybe change 0 to something else?????????
            for res in db[collection].find({"ip": user["ip"], "responsecode": 200}).sort("seg", pymongo.ASCENDING):
                if res["seg"] < len(user[yname]):
                    user[yname][res["seg"]] = res[yname]
        means = [statistics.mean([user[yname][i] for user in role]) for i in range(last_seg+1)]
        plt.plot(segments, means, label="mean:"+role[0]["type"])
        csv.add_plot("mean:"+role[0]["type"], means)

        stdev = [statistics.stdev([user[yname][i] for user in role]) for i in range(last_seg+1)]
        plt.plot(segments, stdev, color="blue", label="stdev:"+role[0]["type"])
        csv.add_plot("stdev:"+role[0]["type"], stdev)

    plt.title(collection + " " + yname + " per segments")
    plt.legend()
    plt.xlabel("segment number")
    plt.ylabel(yname)

    path = PATH + collection + "_" + yname + "_seg_role"
    csv.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def plot_user_data_time(yname, users, collection):
    csv = CSVBuilder()
    for user in users:
        cursor = db[collection].find({"ip": user["ip"], "responsecode": 200}).sort("timestamp", pymongo.ASCENDING)
        xs = []
        ys = []
        cum = 0
        for elem in cursor:
            xs += [elem["timestamp"]]
            cum += elem[yname]
            ys += [cum]
        plt.plot(xs, ys, label=user_name(user), color=COLORDIC[user["type"]])
        csv.add_plot("x" + str(user["num"]), xs)
        csv.add_plot("y" + str(user["num"]), ys)
    plt.title(collection + " " + yname + " over time")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel("time")
    plt.ylabel(yname)
    path = PATH + collection + "_" + yname + "_time"
    csv.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def plot_network_data_time(yname, users):
    csv = CSVBuilder()
    for user in users:
        xs = []
        ys = []
        for res in db[NETWORK].find({"ip": user["ip"]}).sort("ts", pymongo.ASCENDING):
            xs += [int(time.mktime(dateutil.parser.parse(res["ts"]).timetuple()))]
            ys += [res["net"][yname]]
        plt.plot(xs, ys, label=user_name(user), color=COLORDIC[user["type"]])
        csv.add_plot("x" + str(user["num"]), xs)
        csv.add_plot("y" + str(user["num"]), ys)
    plt.title("network " + yname)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.xlabel("time")
    plt.ylabel(yname[3:])
    path = PATH + "network_" + yname + "_time"
    csv.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def plot_network_data_hist(yname1, yname2, users):
    csv = CSVBuilder()
    xs = [user_name(user) for user in users]
    ys1 = []
    ys2 = []
    csv.add_plot("users", xs)
    for user in users:
        res = db[NETWORK].find_one({"ip": user["ip"]}, sort=[("ts", pymongo.DESCENDING)])
        ys1 += [res["net"][yname1]]
        ys2 += [res["net"][yname2]]
    csv.add_plot("rx", ys1)
    csv.add_plot("tx", ys2)
    plt.bar(xs, ys1, color="blue", width=-0.4, align="edge", label=yname1)
    plt.bar(xs, ys2, color="red", width=0.4, align="edge", label=yname2)
    plt.title("network histogram " + yname1 + " & " + yname2)
    plt.legend()
    plt.xlabel("users")
    plt.xticks(rotation=45)
    plt.ylabel(yname1[3:])
    path = PATH + "network_" + yname1 + "_" + yname2 + "_hist"
    csv.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def plot_network_data_hist_role(yname1, yname2, users_b):
    csv_m = CSVBuilder()
    csv_s = CSVBuilder()
    xs = [role[0]["type"] for role in users_b]
    ys1_m = []
    ys2_m = []
    ys1_s = []
    ys2_s = []
    csv_m.add_plot("users", xs)
    csv_s.add_plot("users", xs)
    for role in users_b:
        ys1 = []
        ys2 = []
        for user in role:
            res = db[NETWORK].find_one({"ip": user["ip"]}, sort=[("ts", pymongo.DESCENDING)])
            ys1 += [res["net"][yname1]]
            ys2 += [res["net"][yname2]]
        ys1_m += [statistics.mean(ys1)]
        ys2_m += [statistics.mean(ys2)]
        ys1_s += [statistics.stdev(ys1)]
        ys2_s += [statistics.stdev(ys2)]

    csv_m.add_plot("rx", ys1_m)
    csv_m.add_plot("tx", ys2_m)
    plt.bar(xs, ys1_m, color="blue", width=-0.4, align="edge", label=yname1)
    plt.bar(xs, ys2_m, color="red", width=0.4, align="edge", label=yname2)
    plt.title("network histogram " + yname1 + " & " + yname2)
    plt.legend()
    plt.xlabel("users")
    plt.xticks(rotation=45)
    plt.ylabel(yname1[3:])
    path = PATH + "network_" + yname1 + "_" + yname2 + "_hist_role_mean"
    csv_m.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()

    csv_s.add_plot("rx", ys1_s)
    csv_s.add_plot("tx", ys2_s)
    plt.bar(xs, ys1_s, color="blue", width=-0.4, align="edge", label=yname1)
    plt.bar(xs, ys2_s, color="red", width=0.4, align="edge", label=yname2)
    plt.title("network histogram " + yname1 + " & " + yname2)
    plt.legend()
    plt.xlabel("users")
    plt.xticks(rotation=45)
    plt.ylabel(yname1[3:])
    path = PATH + "network_" + yname1 + "_" + yname2 + "_hist_role_stdev"
    csv_s.export(path + ".csv")
    plt.savefig(path + ".png", bbox_inches='tight')
    plt.gcf().clear()


def user_name(user):
    return str(user["num"]) + ":" + user["type"]


class CSVBuilder:
    def __init__(self):
        self.names = []
        self.data_lists = []
        self.longest_list = 0

    def add_plot(self, name, data):
        self.names += [name]
        self.data_lists += [data]
        if len(data) > self.longest_list:
            self.longest_list = len(data)

    def export(self, filename):
        with open(filename, "w") as file:

            # write axis names
            for name in self.names:
                file.write(name + " ")
            else:
                file.write("\n")

            # write data
            for i in range(self.longest_list):
                for data_list in self.data_lists:
                    if i < len(data_list):
                        file.write(str(data_list[i]) + " ")
                    else:
                        file.write("NaN ")
                else:
                    file.write("\n")
            file.close()


if __name__ == "__main__":
    main()
    print("job complete")
