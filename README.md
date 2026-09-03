# AI Trash Detection and Monitoring System

An AI-powered real-time trash detection and monitoring system developed using **Python, Roboflow, and OpenCV**. The system detects and classifies trash from a live camera feed, visualizes detection data, stores logs for analysis, and sends automatic alerts when trash activity becomes high.

## Project Overview

Improperly disposed waste is a major environmental problem in urban and public areas. Manual monitoring is difficult because humans cannot continuously observe large areas.

This project uses **AI-based computer vision** to provide real-time trash monitoring and help improve waste management.

## Features

**Real-Time Trash Detection**

  * Detects and labels trash using a webcam.
  * Uses a Roboflow YOLO object detection model.

**Data Visualization**

  * Pie chart showing trash type distribution.
  * Line graph showing trash detection trends over time.

 **GUI Dashboard**

  * Built with Tkinter.
  * Start/stop detection.
  * Live detection logs.
  * Image preview.
  * Confidence adjustment.

 **Data Logging**

  * Saves detected images as `.jpg`.
  * Stores detection information in `.txt` files.
  * Records trash type, confidence, and timestamp.

 **InfluxDB Integration**

  * Stores detection data in a time-series database.
  * Supports historical data analysis.

 **Email Alert**

  * Automatically sends an email when high trash activity is detected.

 **Background Processing**

  * Uses Python threading to run detection without freezing the GUI.

##  Technology Stack

| Technology      | Purpose                     |
| --------------- | --------------------------- |
| Python          | Main programming language   |
| Roboflow / YOLO | AI object detection         |
| OpenCV          | Image processing and webcam |
| Tkinter         | GUI development             |
| Matplotlib      | Data visualization          |
| Pillow          | Image display               |
| InfluxDB        | Time-series data storage    |
| SMTP            | Email notifications         |
| Threading       | Background processing       |

## System Workflow

```text
Camera / Webcam
       ↓
   Capture Image
       ↓
OpenCV Image Processing
       ↓
Roboflow YOLO Detection
       ↓
Detect & Classify Trash
       ↓
 ┌─────┼──────────┬───────────┐
 ↓     ↓          ↓           ↓
GUI   Logging   InfluxDB   Email Alert
 ↓
Real-Time Visualization
```

## Monitoring

The system provides real-time information including:

* Detected trash type
* Detection confidence
* Detection timestamp
* Number of detected objects
* Trash type distribution
* Detection trends

<img width="1497" height="617" alt="Screenshot 2026-09-03 234156" src="https://github.com/user-attachments/assets/c0d8d7b7-8f98-4897-81c3-05b4a3b28267" />

<img width="992" height="517" alt="Screenshot 2026-09-03 234330" src="https://github.com/user-attachments/assets/33566d64-b18c-44ea-9605-63c39cc49882" />

## Future Improvements

### Multi-Camera & GPS Integration

The system can be expanded to support multiple CCTV cameras combined with geographical information.

```text
Zone 1 → HIGH Trash → HIGH Priority
Zone 2 → LOW Trash
Zone 3 → MEDIUM Trash → LOW Priority
Zone 4 → LOW Trash
```

This could allow authorities to identify high-priority areas and improve garbage collection planning.


## Project Author

**Shine Lin Htet**
Robotics and Automation System Engineering
Kasetsart University Sriracha Campus

---
