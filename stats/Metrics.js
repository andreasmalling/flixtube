"use strict";

var index = {video: 0, audio: 0};
const stream = ["video", "audio"];

function calculateHTTPMetrics(streamtype, requests) {
    var reqs = requests.slice(index[streamtype]);
    var res = [];

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

        res.push({
            url: url,
            timestamp: timestamp,
            type: type,
            responsecode: responseCode,
            latency: latency,
            download: download,
            ratio: ratio
        });

    });

    index[streamtype] = requests.length;
    return res;
}

function updateMetrics(id, player, streamInfo) {
    var res = {
        "id" : id,
        "video" : "",
        "audio": ""
    };

    var updated = false;
    stream.forEach(function (streamType) {
        var metrics = player.getMetricsFor(streamType);
        res[streamType] = calculateHTTPMetrics(streamType, metrics.HttpList);
        if (res[streamType].length > 0) {
            updated = true;
        }
    });

    if (updated) {
        sendJson("http://localhost:8081/metrics", res)
            .then((jsonRes) => console.log("SendJson Response:", jsonRes))
            .catch((error) => console.error(res));
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
    }).then((response) => response.json()) // parses response to JSON
}