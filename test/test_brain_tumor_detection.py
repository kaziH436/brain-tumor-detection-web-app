from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os

# Function to ensure Flask is up and running
def wait_for_flask():
    url = "http://127.0.0.1:5000/"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass  # Ignore connection errors
        time.sleep(1)

# Ensure Flask is up before proceeding
wait_for_flask()

# Set up the Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: Run Chromium in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Use webdriver-manager to automatically download and set the path for ChromeDriver
service = Service(ChromeDriverManager().install())

# Create the WebDriver instance with the service and options
driver = webdriver.Chrome(service=service, options=chrome_options)
time.sleep(3)

# Open the Flask app's local URL
driver.get("http://127.0.0.1:5000/")

# Ensure the page loads completely
time.sleep(2)

# Test clicking the "Start Webcam" button
start_webcam_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "start-webcam-btn"))
)
start_webcam_button.click()

# Wait for the webcam to start
time.sleep(2)

# Test clicking the "Take a Picture" button
take_picture_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[text()='Take a Picture']"))
)
take_picture_button.click()

# Wait for the picture to be taken
time.sleep(2)

# Debugging: Check if success message appears
try:
    popup_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "success-message"))
    )
    print("Success message: ", popup_message.text)
    assert "took a picture" in popup_message.text  # Ensure message appears
except Exception as e:
    print("No popup message found or error: ", e)

# Test clicking "Show Previous Predictions"
show_previous_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[text()='Show Previous Predictions']"))
)
show_previous_button.click()

# Wait for predictions to load
time.sleep(2)

# Check if the predictions appear correctly with images
prediction_images = driver.find_elements(By.CSS_SELECTOR, ".prediction-image")
print(f"Found {len(prediction_images)} prediction images.")  # Debugging
assert len(prediction_images) > 0, "No images found in predictions"

# Ensure the image is saved correctly (handling file paths)
image_path = "path/to/save/image.jpg"  # Update this path

# Debugging: Print directory path for image save
print(f"Image will be saved to: {image_path}")

# Make sure the directory exists before saving the image
directory = os.path.dirname(image_path)
if not os.path.exists(directory):
    print(f"Creating directory: {directory}")
    os.makedirs(directory)

# Assuming you have the image object from the Flask app, save it (pseudo code)
# img.save(image_path)

# Close the driver
driver.quit()
