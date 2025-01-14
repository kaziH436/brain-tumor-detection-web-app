// Global flag to prevent infinite POST requests
let isPredicting = false;
let lastPrediction = "";
let webcam;
let model;
let maxPredictions;
let labelContainer;
let isWebcamOn = false;  // Flag to check if webcam is on

// Initialize webcam
async function initWebcam() {
    const modelURL = "https://teachablemachine.withgoogle.com/models/9m79q9dos/model.json";
    const metadataURL = "https://teachablemachine.withgoogle.com/models/9m79q9dos/metadata.json";
    
    try {
        model = await tmImage.load(modelURL, metadataURL);
        maxPredictions = model.getTotalClasses();
        console.log("Model loaded successfully");
    } catch (error) {
        console.error("Error loading model:", error);
    }

    const flip = true;
    webcam = new tmImage.Webcam(200, 200, flip);
    await webcam.setup();
    await webcam.play();
    window.requestAnimationFrame(loop);
    
    document.getElementById("webcam-container").appendChild(webcam.canvas);
    labelContainer = document.getElementById("label-container");
}

// Update and classify webcam frame
async function loop() {
    webcam.update();
    await predict();
    window.requestAnimationFrame(loop);
}

// Toggle webcam on/off
function toggleWebcam() {
    if (isWebcamOn) {
        webcam.stop();
        document.getElementById("start-webcam-btn").textContent = "Start Webcam";
    } else {
        initWebcam();
        document.getElementById("start-webcam-btn").textContent = "Stop Webcam";
    }
    isWebcamOn = !isWebcamOn;
}

// Take a picture and classify it
async function takePicture() {
    if (!isWebcamOn) return;

    const canvas = webcam.canvas;
    const imageData = canvas.toDataURL("image/jpeg");

    const prediction = await model.predict(canvas);
    const highestPrediction = prediction.reduce((prev, current) => (prev.probability > current.probability) ? prev : current);

    const tumorName = highestPrediction.className;

    // Save the prediction and image data to the server
    savePrediction(imageData, tumorName);

    labelContainer.innerHTML = `Prediction: ${tumorName}`;
    alert(`Took a picture with the tumor type: ${tumorName}`);

}


function sendPredictionToFlask(prediction, imageData) {
    fetch('http://127.0.0.1:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prediction: prediction, 
        image_data: imageData
      })
    })
    .then(response => response.json())
    .then(data => console.log('Success:', data))
    .catch((error) => console.error('Error:', error));
  }


// Save prediction to the database
async function savePrediction(imageData, tumorName) {
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prediction: tumorName,
                image_data: imageData,
            }),
        });

        const result = await response.json();
        console.log('Prediction saved:', result);
    } catch (error) {
        console.error('Error saving prediction:', error);
    }
}
// Show previous predictions with images
function showPreviousPredictions() {
    fetch('/predictions')
        .then(response => response.json())
        .then(predictions => {
            const predictionsContainer = document.getElementById("predictions-container");
            predictionsContainer.innerHTML = '';  // Clear previous predictions

            // Loop through predictions and display them
            predictions.forEach(prediction => {
                const imageElement = document.createElement("img");
                imageElement.src = `/uploads/${prediction[1]}`;  // Image filename from database
                imageElement.alt = "Tumor Image";

                const tumorTypeElement = document.createElement("p");
                tumorTypeElement.textContent = `Tumor Type: ${prediction[2]}`;  // Tumor type from database

                predictionsContainer.appendChild(imageElement);
                predictionsContainer.appendChild(tumorTypeElement);
            });
        })
        .catch(error => {
            console.error("Error fetching previous predictions:", error);
        });
}

// Go back to webcam page
function goBack() {
    document.getElementById("predictions-page").style.display = 'none';
    document.querySelector('.container').style.display = 'block';
}
