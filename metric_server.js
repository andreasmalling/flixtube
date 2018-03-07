'use strict';

const ipfsAPI = require("ipfs-api");
const ipfs = ipfsAPI("localhost", "5001", {protocol: "http"});

var path;

const express = require("express");
const fileUpload = require("express-fileupload");
const bodyParser = require('body-parser');
var MongoClient = require('mongodb').MongoClient;
var mongo_url = "mongodb://localhost:27017/mydb";
const app = express();

// default options
app.use(fileUpload());

app.use(bodyParser.json());

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

app.post("/metrics", function (req, res, ignore) {   // ignore = next (?)
    console.log(req.body);
    res.send(req.body);
});

app.listen(8081);
MongoClient.connect(mongo_url, function(err, db) {
    if (err) throw err;
    console.log("Database created!");
    db.close();
});