const { S3Client, GetObjectCommand ,PutObjectCommand} = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const axios = require("axios");
const xml2js = require("xml2js");
const path = require("path");
const upload = multer({ dest: "uploads/" });
const app = express();
app.use(express.json());
app.use(cors());
require('dotenv').config();

const s3Client = new S3Client({
    region: "ap-south-1",
    credentials: {
        accessKeyId: process.env.accessKeyId, // Replace with your AWS access key
        secretAccessKey: process.env.secretAccess, // Replace with your AWS secret key
    }
});
app.get("/health", (req, res) => {
    res.json({ status: "running" });
});
async function getObject(key) {
    const command = new GetObjectCommand({
        Bucket: "privatebucketnodejs",
        Key: key
    });
    return await getSignedUrl(s3Client, command, { expiresIn: 360000 });
}

app.get("/get-image", async (req, res) => {
    try {
        const { filename } = req.query;
        if (!filename) {
            return res.status(400).json({ error: "Filename is required" });
        }
        const url = await getObject(`uploads/user-uploads/${filename}`);    
        res.json({ url });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Error fetching image" });
    }
});

async function uploadObject(file, filename) {
    const fileStream = fs.createReadStream(file.path);
    const command = new PutObjectCommand({
        Bucket: "privatebucketnodejs",
        Key: `uploads/user-uploads/${filename}`,
        Body: fileStream,
        ContentType: file.mimetype
    });
    await s3Client.send(command);
    fs.unlinkSync(file.path);
    return await getObject(`uploads/user-uploads/${filename}`);
}
app.post("/upload", upload.single("file"), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }
        const url = await uploadObject(req.file, req.file.originalname);
        const identificationResult = await identifyCrop(url);

        // Return the response
        res.json({ url, identification: identificationResult });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Error uploading file" });
    }
});
const API_KEY = process.env.API_KEY  // Replace with your API key
// Function to call the identification API
async function identifyCrop(imageUrl) {
    try {
        const response = await axios.post(
            "https://crop.kindwise.com/api/v1/identification",
            {
                images: [imageUrl], // Passing image URL in required format
                similar_images: true
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    "Api-Key": API_KEY
                }
            }
        );
        // console.log("Identification response:", response.data)
        // console.log("Identification response123456:", response.data.result.is_plant.probability)
        if(response.data.result.is_plant.probability < 0.4){
            return "invalid";
        }
        const diseaseDetails = await diseaseDetailsget(response.data.access_token);
        return diseaseDetails;
        // return response.data; // Return API response
    } catch (error) {
        console.error("Error in identification:", error.response?.data || error.message);
        throw new Error("Identification failed");
    }
}
async function diseaseDetailsget(access_token) {
    try {
        const response = await axios.get(
            `https://crop.kindwise.com/api/v1/identification/${access_token}?details=description,treatment,symptoms,severity,spreading&language=en`,
            {
                headers: {
                    "Content-Type": "application/json",
                    "Api-Key": API_KEY
                }
            }
        );
        if(response.data.result.is_plant.probability < 0.4){
            return "invalid";
        }
        // console.log("Disease Details Response:", response.data.result.disease.suggestions);
        const diseaseDetailsjson = await extractDiseaseInfo(response.data);
        console.log("Disease Details Response json:", diseaseDetailsjson);
        return diseaseDetailsjson;// Return API response
    } catch (error) {
        console.error("Error in fetching disease details:", error.response?.data || error.message);
        throw new Error("Disease details retrieval failed");
    }
}
function extractDiseaseInfo(data) {
    if (!data?.result?.disease?.suggestions?.length) {
        return { error: "Invalid data format" };
    }

    const disease = data.result.disease.suggestions[0];
    const details = disease.details;

    return {
        name: disease.name,
        description: details.description,
        symptoms: Object.entries(details.symptoms).map(([key, value]) => ({ [key]: value })),
        severity: details.severity,
        treatment: {
            prevention: details.treatment.prevention,
            chemical: details.treatment["chemical treatment"],
            biological: details.treatment["biological treatment"]
        }
    };
}
const RSS_FEED_URL = "https://news.google.com/rss/search?q=agriculture+India&hl=en-IN&gl=IN&ceid=IN:en";

app.get("/get-agriculture-news", async (req, res) => {
    try {
        const response = await axios.get(RSS_FEED_URL);
        const parser = new xml2js.Parser();
        
        parser.parseString(response.data, (err, result) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: "Error parsing RSS feed" });
            }

            const newsItems = result.rss.channel[0].item.slice(0, 10).map(item => ({
                title: item.title[0],
                link: item.link[0],
                published: item.pubDate ? item.pubDate[0] : "No date available"
            }));

            res.json(newsItems);
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Error fetching news" });
    }
});

app.listen(4000, "0.0.0.0", () => {
    console.log(`Server is running on http://0.0.0.0:${4000}`);
  });
