"use strict";

// const ipfsAPI = require("ipfs-api");
// const ipfs = ipfsAPI("localhost", "5001", {protocol: "http"});

const express = require("express");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const mongo_url = "mongodb://mongo:27017/flixtube_db";
const app = express();

// DB constants
const DBNAME = "flixtube_db";
const VIDEOCOLLECTION = "video";
const AUDIOCOLLECTION = "audio";
const WAITCOLLECTION = "wait";

const OK = 200;
const BADREQ = 420;

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

app.get("/", function (req, res, next) {
   res.send("IT JUST WORKS");
});


app.post("/metrics", function (req, res, ignore) {   // ignore = next (?)
    var json = req.body;
    try {
        if (flixtube_db !== null) {

            json.audio.forEach(function (elem) {
                insertInDatabase(AUDIOCOLLECTION, elem);
            });

            json.video.forEach(function (elem) {
                insertInDatabase(VIDEOCOLLECTION, elem);
            });
        }
        res.sendStatus(OK);
    } catch (err) {
        res.status(BADREQ).send("database error: " +  err.toString());
    }
});

app.post("/metrics/wait", function (req, res, ignore) { //ignore = next
    try {
        var json = req.body;
        insertInDatabase(WAITCOLLECTION, json);
        res.sendStatus(OK);
    } catch (err) {
        res.status(BADREQ).send("database error: " +  err.toString());
    }
});

// app.post("/metrics/network", function (req, res, ignore) {
//     try {
//
//     } catch (err) {
//
//     }
//
// })

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
    var dbo = db.db(DBNAME);
    database = db;
    flixtube_db = dbo;
    createCollection(VIDEOCOLLECTION);
    createCollection(AUDIOCOLLECTION);
    createCollection(WAITCOLLECTION);
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