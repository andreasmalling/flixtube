function calculateHTTPMetrics(type, requests) {
    var latency = {},
        download = {},
        ratio = {};

    var requestWindow = requests.slice(-20).filter(function (req) {
        return req.responsecode >= 200 && req.responsecode < 300 && req.type === 'MediaSegment' && req._stream === type && !!req._mediaduration;
    }).slice(-4);

    if (requestWindow.length > 0) {
        var latencyTimes = requestWindow.map(function (req) {
            return Math.abs(req.tresponse.getTime() - req.trequest.getTime()) / 1000;
        });

        latency[type] = {
            average: latencyTimes.reduce(function (l, r) {
                return l + r;
            }) / latencyTimes.length,
            high: latencyTimes.reduce(function (l, r) {
                return l < r ? r : l;
            }),
            low: latencyTimes.reduce(function (l, r) {
                return l < r ? l : r;
            }),
            count: latencyTimes.length
        };

        var downloadTimes = requestWindow.map(function (req) {
            return Math.abs(req._tfinish.getTime() - req.tresponse.getTime()) / 1000;
        });

        download[type] = {
            average: downloadTimes.reduce(function (l, r) {
                return l + r;
            }) / downloadTimes.length,
            high: downloadTimes.reduce(function (l, r) {
                return l < r ? r : l;
            }),
            low: downloadTimes.reduce(function (l, r) {
                return l < r ? l : r;
            }),
            count: downloadTimes.length
        };

        var durationTimes = requestWindow.map(function (req) {
            return req._mediaduration;
        });

        ratio[type] = {
            average: (durationTimes.reduce(function (l, r) {
                return l + r;
            }) / downloadTimes.length) / download[type].average,
            high: durationTimes.reduce(function (l, r) {
                return l < r ? r : l;
            }) / download[type].low,
            low: durationTimes.reduce(function (l, r) {
                return l < r ? l : r;
            }) / download[type].high,
            count: durationTimes.length
        };

        return {
            latency: latency,
            download: download,
            ratio: ratio
        };

    }
    return null;
}

function updateMetrics(player, streaminfo, type) {
    var metrics = player.getMetricsFor(type);
    var dashMetrics = player.getDashMetrics();

    if (metrics && dashMetrics && streamInfo) {
        var periodIdx = streamInfo.index;
        var repSwitch = dashMetrics.getCurrentRepresentationSwitch(metrics);
        var bufferLevel = dashMetrics.getCurrentBufferLevel(metrics);
        var maxIndex = dashMetrics.getMaxIndexForBufferType(type, periodIdx);
        var index = player.getQualityFor(type);
        var bitrate = repSwitch ? Math.round(dashMetrics.getBandwidthForRepresentation(repSwitch.to, periodIdx) / 1000) : NaN;
        var droppedFPS = dashMetrics.getCurrentDroppedFrames(metrics) ? dashMetrics.getCurrentDroppedFrames(metrics).droppedFrames : 0;
        var httpMetrics = calculateHTTPMetrics(type, dashMetrics.getHttpRequests(metrics));
    }
}