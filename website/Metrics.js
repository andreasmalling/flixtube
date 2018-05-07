"use strict";

const stream = ["video", "audio"];
var index = {video: 0, audio: 0};

var segmentPattern = /Segment_([0-9]+)/;
var mpdPattern = /ip[fn]s\/[0-9a-zA-Z]+/;

var metricsUrl = "http://metric:8081";

function reportStall(id, player, progress, stallStart) {
    var res = {
        time: progress,
        start: stallStart,
        end: Date.now(),
        mpd: player.getSource().match(mpdPattern)[0],
        ip: id
    };

    sendJson(metricsUrl + "/metrics/stall", res)
        .then((response) => console.log("Stall Server Response", res, response.text()))
        .catch((error) => console.error("Stall Server Error", res, error));
}

function updateMetrics(id, player, streamInfo) {
    var res = {
        "video" : [],
        "audio" : []
    };

    var updated = false;
    stream.forEach(function (streamType) {
        var requests = player.getMetricsFor(streamType).HttpList;

        var reqs = requests.slice(index[streamType]);
        var streamList = [];

        reqs.forEach( function (req) {
            var url = req.url;
            var timestamp = req.trequest.getTime();
            var responseCode = req.responsecode;
            var type = req.type;
            var latency = NaN;
            var download = NaN;
            var ratio = NaN;

            if (responseCode >= 200 && responseCode < 300) {
                latency = Math.abs(req.tresponse.getTime() - timestamp);
                download = Math.abs(req._tfinish.getTime() - req.tresponse.getTime());
                ratio = req._mediaduration / download;
            }

            streamList.push({
                ip: id,
                mpd: player.getSource().match(mpdPattern)[0],
                seg: parseInt(url.match(segmentPattern)[1]),
                timestamp: timestamp,
                type: type,
                responsecode: responseCode,
                latency: latency,
                download: download,
                ratio: ratio
            });

        });

        index[streamType] = requests.length;

        if (streamList.length > 0) {
            updated = true;
            res[streamType] = streamList;
        }
    });

    if (updated) {
        sendJson(metricsUrl + "/metrics", res)
            .then((response) => console.log("Metric Server Response", res, response.text()))
            .catch((error) => console.error("Metric Server Error", res, error));
    }
}

function sendJson(url, data) {
    return fetch(url, {
        body: JSON.stringify(data),
        cache: "no-cache",
        headers: {"content-type": "application/json"},
        method: "POST",
        mode: "cors",
        redirect: "follow",
        referrer: "no-referrer"
    })//.then((response) => response.json()) // parses response to JSON
}