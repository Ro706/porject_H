require('dotenv').config();
const express = require('express');
const connectToMongo = require('./db');
const cors = require('cors');

connectToMongo();
const app = express();
const port = process.env.PORT || 5800;

app.use(cors());
app.use(express.json());
const axios = require('axios');
const FormData = require('form-data');
const multer = require('multer');
const upload = multer();

app.use("/api/auth", require("./routes/auth"));



app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});


app.get('/', (req, res) => {
    res.send("Hello World");
});