const axios = require("axios");
require("dotenv").config();

// Function to identify crop disease via POST request
// const identifyCropDisease = async () => {
//   try {
//     const postData = {
//       images: [
//         "https://th.bing.com/th/id/OIP.t8AQW0CuN3zKiGr75sIfhwHaFj?rs=1&pid=ImgDetMain",
//       ],
//       similar_images: true,
//     };

//     const postResponse = await axios.post(process.env.DATA_URL, postData, {
//       headers: {
//         "Content-Type": "application/json",
//         "Api-Key": process.env.API_KEY,
//       },
//     });

//     console.log(
//       "Full POST Response:",
//       JSON.stringify(postResponse.data, null, 2)
//     );

//     // Extract access token and disease name
//     const accessToken = postResponse.data?.access_token;
//     const diseaseName =
//       postResponse.data?.result?.disease?.suggestions?.[0]?.name;

//     if (accessToken && diseaseName) {
//       console.log("Access Token:", accessToken);
//       console.log("Disease Name:", diseaseName);
//       await getCropDiseaseInfo(accessToken, diseaseName);
//     } else {
//       console.log("Access token or disease name not found.");
//     }
//   } catch (error) {
//     console.error(
//       "Error in POST request:",
//       error.response
//         ? JSON.stringify(error.response.data, null, 2)
//         : error.message
//     );
//   }
// };

let dp;
// Function to fetch detailed crop disease info via GET request
// const getCropDiseaseInfo = async (accessToken, diseaseName) => {
//     try {
//       // Define the URL for the GET request
//       const getUrl = `${process.env.DATA_URL}/${accessToken}?details=description,treatment,symptoms,severity,spreading&language=en`;
  
//       // Make the GET request
//       const getResponse = await axios.get(getUrl, {
//         headers: {
//           "Api-Key": process.env.API_KEY,
//         },
//       });
  
//       console.log("GET Response:", JSON.stringify(getResponse.data, null, 2));
  
//       // Extract disease data from the response
//       const diseaseData = getResponse.data?.result?.disease?.suggestions?.[0];
  
//       // Check if disease data is available
//       if (diseaseData) {
//         const diseaseName = diseaseData.name;
//         const severityDescription = diseaseData.details?.severity;
//         const diseaseSymptoms = diseaseData.details?.symptoms;
//         const diseaseProbability = diseaseData.probability;
  
//         dp = diseaseProbability;

//         console.log(`Disease Name: ${diseaseName}`);
//         console.log(`Severity: ${severityDescription}`);
//         console.log(`Probability of Occurrence: ${diseaseProbability * 100}%`);
  
//         // Log symptoms if available
//         if (diseaseSymptoms && Object.keys(diseaseSymptoms).length > 0) {
//           console.log("Symptoms:");
//           for (let symptom in diseaseSymptoms) {
//             console.log(`${symptom}: ${diseaseSymptoms[symptom]}`);
//           }
//         } else {
//           console.log("No symptoms data available.");
//         }
//       } else {
//         console.log("Disease data is not available.");
//       }
//     } catch (error) {
//       console.error("Error in GET request:", error.message);
//     }
//   }; 

// Example coordinates (you can replace these with actual inputs)
const latitude = 19.076; // Example: Mumbai
const longitude = 72.8777;

const getWeatherData = async (latitude, longitude) => {
  try {
    const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,is_day,precipitation,rain,snowfall,weather_code,wind_speed_10m`;

    const weatherResponse = await axios.get(weatherUrl);
    console.log("Weather Data:", JSON.stringify(weatherResponse.data, null, 2));
  } catch (error) {
    console.error(
      "Error fetching weather data:",
      error.response
        ? JSON.stringify(error.response.data, null, 2)
        : error.message
    );
  }
};


getWeatherData(latitude, longitude);

// identifyCropDisease();

// let baseDosage = 100;
