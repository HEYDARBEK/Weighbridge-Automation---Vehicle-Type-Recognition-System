# Weighbridge Automation - Vehicle Type Recognition System

**Version: 1.0**  
**Date: 07.10.2025**

---

## 🚀 Project Overview

This project is an AI-powered system developed to automatically detect vehicles arriving at a weighbridge using camera images.

The system is designed to identify the following vehicle types:

- Trucks / Semi-trailer Trucks
- Trucks
- Tractors
- Light Trucks / Pickup Trucks
- Empty

The main goal of the system is to automate parts of the weighing process and enable automatic operations such as vehicle classification and type-based processing.

## ⚠️ Project Scope and Limitations

This project was developed specifically for the existing weighbridge and camera system of a particular business. The model was trained using images obtained from this system, taking into account environment-specific conditions such as camera position, viewing angle, and image format.

Therefore, the model and image processing pipeline may not provide the same performance when used with different camera systems or in different environments.

If the system is adapted to a different environment, the dataset may need to be rebuilt, the model retrained, or the image preprocessing pipeline modified.

## ✨ Key Features

- **Automatic Detection:** Continuously monitors a specified folder and automatically processes newly added images.
- **User Interface:** Provides an interface that allows the operator to monitor the system status and view detection results in real time.
- **Flexible Configuration:** The folder to be monitored can be easily changed through a simple `config.txt` file placed next to the executable.
- **Intelligent Preprocessing:** Automatically analyzes the aspect ratio of incoming raw (vertical) or cropped (horizontal) images and selects the appropriate processing method.
- **Persistent Logging:** Maintains both a clean results file (`sonuclar.csv`) for operators and a detailed system log (`sistem_gunlugu.txt`) for technical monitoring.

## 🛠️ Technologies Used

- **Python 3.10**
- **PyTorch & Ultralytics YOLO** (Object Detection Model)
- **OpenCV** (Image Processing)
- **Tkinter** (Graphical User Interface)
- **Watchdog** (Directory Monitoring)

## ⚙️ Installation and Usage

### 1. Environment Setup

All required Python dependencies are listed in `requirements.txt`.

After creating a new virtual environment, install the dependencies using:

```bash
pip install -r requirements.txt
