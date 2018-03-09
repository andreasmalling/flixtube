"use strict";

// const ipfsAPI = require("ipfs-api");
// const ipfs = ipfsAPI("localhost", "5001", {protocol: "http"});

const express = require("express");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const mongo_url = "mongodb://localhost:27017/flixtube_db";
const app = express();

app.use(bodyParser.json());

// Allow CORS
app.use(function (ignore, res, next) {  //ignore req
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

//mongo db vars
var database = null;
var flixtube_db = null;

function insertInDatabase(collection, jsonElem) {
    flixtube_db.collection(collection).insertOne(jsonElem, function (err, ignore) { // ignore res
        if (err) {
            throw err;
        }
        console.log("inserted\n" + JSON.stringify(jsonElem));
    });
}

app.post("/metrics", function (req, res, ignore) {   // ignore = next (?)
    var json = req.body;
    if (flixtube_db !== null) {
        var id = json.id;
        var time = json.time;

        //latency
        json.latency.time = time;
        json.latency.id = id;
        insertInDatabase("latency", json.latency);

        //download
        json.download.time = time;
        json.download.id = id;
        insertInDatabase("download", json.download);

        //ratio
        json.ratio.time = time;
        json.ratio.id = id;
        insertInDatabase("ratio", json.ratio);

    }
    res.send(req.body);
});

app.listen(8081);

// create mongo db collection instance

function createCollection(name) {
    flixtube_db.createCollection(name, function (err, ignore) { // ignore res
        if (err) {
            throw err;
        }
        console.log(name + " collection created!");
    });
}

MongoClient.connect(mongo_url, function (err, db) {
    if (err) {
        throw err;
    }
    var dbo = db.db("flixtube_db");
    database = db;
    flixtube_db = dbo;
    createCollection("latency");
    createCollection("download");
    createCollection("ratio");
});


// handle close
process.stdin.resume();//so the program will not close instantly

function exitHandler(options, err) {
    if (options.cleanup) {
        if (database !== null) {
            database.close();
        }
        console.log("closing db");
    }
    if (err) {
        console.log(err.stack);
    }
    if (options.exit) {
        process.exit();
    }
}

//do something when app is closing
process.on("exit", exitHandler.bind(null, {cleanup: true}));

//catches ctrl+c event
process.on("SIGINT", exitHandler.bind(null, {exit: true}));

// catches "kill pid" (for example: nodemon restart)
process.on("SIGUSR1", exitHandler.bind(null, {exit: true}));
process.on("SIGUSR2", exitHandler.bind(null, {exit: true}));

//catches uncaught exceptions
process.on("uncaughtException", exitHandler.bind(null, {exit: true}));