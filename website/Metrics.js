"use strict";

const stream = ["video", "audio"];
var index = {video: 0, audio: 0};

var segmentPattern = /Segment_([0-9]+)/;
var mpdPattern = /ip[fn]s\/[0-9a-zA-Z]+/;

var waitElement = {stream: "", time: 0};
var isWaiting = false;

var metricsUrl = "http://metric:8081";

function waitStart(streamType) {
    waitElement.time = Date.now();
    waitElement.stream = streamType;
    isWaiting = true;
}

function waitStop(id, player) {
    if (isWaiting) {
        var res = {
            resume: Date.now(),
            stall: waitElement.time,
            stream: waitElement.stream,
            mpd: player.getSource().match(mpdPattern)[0],
            ip: id
        };

        isWaiting = false;

        sendJson(metricsUrl + "/metrics/wait", res)
            .then((response) => console.log("Wait Server Response", res, response.text()))
            .catch((error) => console.error("Wait Server Error", res, error));
    }
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
                seg: url.match(segmentPattern)[1],
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

    // TODO: Add buffer state?
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