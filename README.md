# Vehicle License Plate Recognition System

A deep learning-based system for detecting and recognizing Tunisian license plates from vehicle images using YOLOv3 for detection and CNN for character recognition.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Inference](#command-line-inference)
  - [API Server](#api-server)
  - [Testing with Postman](#testing-with-postman)
  - [Testing with cURL](#testing-with-curl)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python:** 3.7+ (3.12 recommended)
- **Operating System:** Windows, Linux, or macOS
- **RAM:** Minimum 4GB (8GB+ recommended)
- **Disk Space:** ~2GB for models and dependencies

---

## Installation

### Step 1: Install Dependencies

```bash
cd Deep-Learning
pip install -r requirements.txt
```

**What gets installed:**
- TensorFlow 2.16+ (for deep learning)
- OpenCV (for image processing)
- NumPy, Matplotlib (for data handling)
- Flask, Flask-CORS (for API server)

### Step 2: Download YOLO Weights File ⚠️ **REQUIRED**

The YOLO weights file is required for license plate detection but is not included due to file size.

1. **Download:** https://www.dropbox.com/s/fxyblp7dezmy2jp/Attachments.zip?dl=0
2. **Extract** the ZIP file
3. **Copy** `lapi.weights` to: `Deep-Learning/Licence_plate_detection/lapi.weights`

### Step 3: Verify Setup

```bash
python check_setup.py
```

This will verify all required files are present.

---

## Configuration

### Required Files

Make sure you have these files:

- ✅ `Licence_plate_detection/lapi.weights` (download required)
- ✅ `Licence_plate_detection/darknet-yolov3.cfg` (included)
- ✅ `Licence_plate_detection/classes.names` (included)
- ✅ `Licence_Plate_Recognition/ocrmodel.h5` (included)

### Directory Structure

```
Deep-Learning/
├── Main-Scripts/
│   ├── object_detection_yolo.py      # License plate detection
│   ├── Hawk_Eye_LP_recognition.py    # Character recognition
│   └── main_vehicle_to_LP.py        # Main pipeline
├── Licence_plate_detection/
│   ├── lapi.weights                  # ⚠️ Download required
│   ├── darknet-yolov3.cfg
│   └── classes.names
├── Licence_Plate_Recognition/
│   ├── ocrmodel.h5                   # OCR model
│   └── LP_extraction_test/           # Test images
├── output/                            # Results saved here
├── uploads/                           # API uploads (auto-cleaned)
├── api_server.py                      # Flask API server
├── test_inference.py                  # Test script
└── check_setup.py                     # Setup verification
```

---

## Usage

### Command Line Inference

#### Option 1: Using Test Script (Recommended)

```bash
python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/48.jpg
```

**Output:** Saved to `output/test_result.jpg`

#### Option 2: Using Main Script

```bash
cd Main-Scripts
python main_vehicle_to_LP.py --image "../Licence_Plate_Recognition/LP_extraction_test/48.jpg"
```

**Output:** Saved to `output/final_image.jpg`

#### Test with Different Images

```bash
# Test image 1
python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/48.jpg

# Test image 2
python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/623.jpg

# Test image 3
python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/109.jpg

# Your own image
python test_inference.py --image "path/to/your/image.jpg"
```

---

### API Server

#### Start the Server

```bash
python api_server.py
```

Server starts on: `http://localhost:5000`

#### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/info` | API information |
| POST | `/recognize` | Recognize license plate |
| GET | `/result_image/<filename>` | Get result image |

---

### Testing with Postman

#### Setup Request

1. **Method:** POST
2. **URL:** `http://localhost:5000/recognize`
3. **Body:** Select `form-data`
4. **Add Key:**
   - Name: `image`
   - Type: **File** (not Text)
   - Value: Select your image file
5. **Optional:** Add `return_image` key with value `"true"` to get image directly

#### Expected Response

```json
{
  "success": true,
  "message": "License plate recognized successfully",
  "result_image": "/result_image/result_your_image.jpg",
  "uploaded_file": "your_image.jpg"
}
```

#### View Result Image

Open in browser or GET request:
```
http://localhost:5000/result_image/result_your_image.jpg
```

---

### Testing with cURL

#### Health Check

```bash
curl http://localhost:5000/health
```

#### Recognize License Plate

```bash
curl -X POST \
  http://localhost:5000/recognize \
  -F "image=@Licence_Plate_Recognition/LP_extraction_test/48.jpg"
```

#### Pretty JSON Output

```bash
curl -X POST \
  http://localhost:5000/recognize \
  -F "image=@Licence_Plate_Recognition/LP_extraction_test/48.jpg" \
  | python -m json.tool
```

#### Get Result Image Directly

```bash
curl -X POST \
  http://localhost:5000/recognize \
  -F "image=@Licence_Plate_Recognition/LP_extraction_test/48.jpg" \
  -F "return_image=true" \
  --output result.jpg
```

#### Download Result Image

```bash
curl http://localhost:5000/result_image/result_48.jpg --output result.jpg
```

#### Windows PowerShell

```powershell
# Health check
curl http://localhost:5000/health

# Test recognition
curl -X POST http://localhost:5000/recognize -F "image=@Licence_Plate_Recognition\LP_extraction_test\48.jpg"
```

---

## Project Structure

### Main Components

1. **License Plate Detection** (`object_detection_yolo.py`)
   - Uses YOLOv3 to detect license plates
   - Extracts license plate region
   - Draws bounding box

2. **License Plate Recognition** (`Hawk_Eye_LP_recognition.py`)
   - Segments license plate into characters
   - Uses CNN model to classify each character
   - Recognizes digits (0-9) and "Tunisia"
   - Overlays recognized text on image

3. **Main Pipeline** (`main_vehicle_to_LP.py`)
   - Combines detection and recognition
   - Processes complete workflow

4. **API Server** (`api_server.py`)
   - RESTful API for HTTP requests
   - Handles image uploads
   - Returns JSON or image responses

---

## Troubleshooting

### Common Issues

#### 1. "YOLO weights file not found"

**Solution:**
- Download `lapi.weights` from Dropbox link
- Place in: `Licence_plate_detection/lapi.weights`
- Verify with: `python check_setup.py`

#### 2. "Could not detect license plate"

**Possible causes:**
- License plate not clearly visible
- Poor image quality
- License plate too small or obstructed

**Solution:**
- Try a different test image
- Ensure good lighting and image quality
- Make sure license plate is clearly visible

#### 3. "ModuleNotFoundError: No module named 'tensorflow'"

**Solution:**
```bash
pip install -r requirements.txt
```

#### 4. "Connection refused" (API)

**Solution:**
- Make sure API server is running: `python api_server.py`
- Check if port 5000 is available
- Verify server started successfully

#### 5. "No image file provided" (API)

**Solution:**
- In Postman, use `form-data` (not raw)
- Key name should be `image` or `file`
- Change key type from "Text" to "File"

#### 6. Python Version Issues

**For Python 3.7-3.8:**
- TensorFlow 2.3.0 may not be available
- Use Python 3.9+ or system Python 3.12

**For Python 3.12:**
- Requirements automatically install compatible versions
- TensorFlow 2.16+ works correctly

#### 7. "IndexError" or "TypeError" Errors

**Solution:**
- These have been fixed in the updated code
- Make sure you're using the latest version of scripts
- Check that all dependencies are up to date

---

## Quick Reference

### Essential Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Verify setup
python check_setup.py

# Test inference
python test_inference.py --image Licence_Plate_Recognition/LP_extraction_test/48.jpg

# Start API server
python api_server.py

# Test API (cURL)
curl -X POST http://localhost:5000/recognize -F "image=@test.jpg"
```

### File Locations

- **Test Images:** `Licence_Plate_Recognition/LP_extraction_test/`
- **Output Results:** `output/`
- **API Uploads:** `uploads/` (auto-cleaned)
- **YOLO Weights:** `Licence_plate_detection/lapi.weights`
- **OCR Model:** `Licence_Plate_Recognition/ocrmodel.h5`

---

## API Response Examples

### Success Response

```json
{
  "success": true,
  "message": "License plate recognized successfully",
  "result_image": "/result_image/result_48.jpg",
  "uploaded_file": "48.jpg"
}
```

### Error Response (No License Plate)

```json
{
  "success": false,
  "error": "Could not detect license plate in the image",
  "message": "The image may not contain a visible license plate. Try a different image with a clearer license plate."
}
```

### Error Response (Invalid File)

```json
{
  "success": false,
  "error": "Invalid file type. Allowed types: png, jpg, jpeg, gif, bmp"
}
```

---

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)

---

## Notes

- The system is designed for **Tunisian license plates**
- Works best with clear, well-lit images
- License plate should be clearly visible and not obstructed
- Processing time: ~2-5 seconds per image (CPU)
- All output images are saved in `output/` directory

---

## Support

For issues or questions:
1. Run `python check_setup.py` to verify setup
2. Check the Troubleshooting section above
3. Review error messages for specific guidance

---

## License

This project is part of the Vehicle Recognition System in Tunisia project.

---

**Ready to start? Begin with Installation Step 1!** 🚀

