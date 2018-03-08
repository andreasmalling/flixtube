"use strict";

const ipfsAPI = require("ipfs-api");
const ipfs = ipfsAPI("localhost", "5001", {protocol: "http"});

var path;

const express = require("express");
const fileUpload = require("express-fileupload");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const mongo_url = "mongodb://localhost:27017/flixtube_db";
const app = express();

// default options
app.use(fileUpload());

app.use(bodyParser.json());

// Allow CORS
app.use(function (ignore, res, next) {  //ignore req
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.get("/", function (ignore, res) {   // ignore = req
    res.writeHead(200, {"Content-Type": "text/html"});
    res.write("<form ref=\"uploadForm\" id=\"uploadForm\" action=\"upload\" method=\"post\" encType=\"multipart/form-data\">");
    res.write("<input type=\"file\" name=\"sampleFile\"><br>");
    res.write("<input type=\"submit\">");
    res.write("</form>");
    return res.end();
});

app.post("/upload", function (req, res, ignore) {   // ignore = next (?)
    if (!req.files) {
        return res.status(400).send("No files were uploaded.");
    }

    ipfs.add(req.files.sampleFile.data, function (err, files) {
        if (err) {
            console.log(err);
        }

        console.log(files);
        files.forEach(function (file) {
            path = file.path;
            console.log(path);
        });
        res.send("File uploaded! Available at <a href=\"http://ipfs.io/ipfs/" + path + "\">" + path + "</a>");
    });

});

//mongo db vars
var database = null;
var flixtube_db = null;


app.post("/metrics", function (req, res, ignore) {   // ignore = next (?)
    var json = req.body;
    console.log(json);
    if (flixtube_db !== null) {
        //do db things
        flixtube_db.collection("metrics").insertOne(json, function (err, ignore) { // ignore res
            if (err) {
                throw err;
            }
            console.log("inserted document in db");
        });
    }
    res.send(req.body);
});

app.listen(8081);

// create mongo db collection instance

MongoClient.connect(mongo_url, function (err, db) {
    if (err) {
        throw err;
    }
    database = db;
    var dbo = db.db("flixtube_db");
    flixtube_db = dbo;
    dbo.createCollection("metrics", function (err, ignore) { // ignore res
        if (err) {
            throw err;
        }
        console.log("collection created!");
    });
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