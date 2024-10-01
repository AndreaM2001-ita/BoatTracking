# Boat Tracking Project ⛵

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Video Tracking](#running-the-video-tracking)
  - [API Endpoints](#api-endpoints)
- [Scripts Overview](#scripts-overview)
- [Configuration](#configuration)

## Introduction

The **Boat Tracking Project** is an advanced system designed to detect, track, and manage boat movements using video analysis. Leveraging state-of-the-art machine learning models like YOLOv8 and DeepSORT, the project processes video feeds to identify and monitor boats, logging essential details into a database for further analysis and reporting.

## Features ✨

- **Real-time Boat Detection and Tracking:** Utilizes YOLOv8 and DeepSORT for efficient boat detection and tracking in video streams.
- **Database Integration:** Logs boat events, including launch and retrieval times, and calculates time spent at sea.
- **API Endpoints:** Provides RESTful APIs to interact with boat data.
- **Model Evaluation:** Tools to evaluate and compare different YOLO models.
- **Detection Reduction and Matching:** Processes and refines detection results to eliminate duplicates and match related events.

## Directory Structure 📂

```
.
└── BoatTracking-clean-up-branch
    ├── README.md
    ├── Setup environment.docx
    ├── compareV4.py
    ├── config.yaml
    ├── database.py
    ├── evaluation.py
    ├── output
    ├── reductionV3.py
    ├── requirements.txt
    ├── serverV2.py
    ├── trainedModels
    │   ├── last.pt
    │   ├── trainedPrototype.pt
    │   ├── trainedPrototypeBoats.pt
    │   ├── trainedPrototypewithCars.pt
    │   └── yolov8n.pt
    ├── trainedPrototypewithCars2.pt
    ├── val
    │   ├── images
    │   │   ├── 01-08-2022 12 C Augusta_frame_0024.jpg
    │   │   ├── ... (additional images)
    │   ├── labels
    │   │   ├── 01-08-2022 12 C Augusta_frame_0024.txt
    │   │   ├── ... (additional labels)
    │   └── labels.cache
    ├── videoTrackingV2.py
    └── videos
```

## Installation 🛠️

Follow the steps below to set up the development environment.

### Prerequisites

- **Anaconda:** Ensure you have [Anaconda](https://www.anaconda.com/products/distribution) installed on your system.
- **Git:** Install [Git](https://git-scm.com/downloads) for version control.

### Setup Steps 📜

1. **Clone the Repository**

   ```bash
   git clone https://github.com/AndreaM2001-ita/BoatTracking.git
   cd BoatTracking-clean-up-branch
   ```

2. **Create and Activate Conda Environment**

   ```bash
   conda create -n boat_tracking_env python=3.10
   conda activate boat_tracking_env
   ```

3. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ultralytics**

   ```bash
   pip install ultralytics
   ```

5. **Download and Configure libomp**

   - **Download:** [libomp140_x86_64](https://www.dllme.com/dll/files/libomp140_x86_64?sort=upload&arch=0x8664)
   - **Unzip:** Extract the downloaded file.
   - **Copy DLL:** Place the `libomp140.dll` into the same directory as `fbgemm.dll`.

     ```plaintext
     C:\Users\*USER*\anaconda3\envs\boat_tracking_env\Lib\site-packages\torch\lib
     ```

6. **Install PyTorch (NVIDIA GPU Users Only)**

   If you have an NVIDIA graphics card, upgrade PyTorch with CUDA support:

   ```bash
   pip3 install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

7. **Install Additional Dependencies**

   ```bash
   pip install EasyDict
   ```

8. **Clone Deep SORT Repository**

   ```bash
   git clone https://github.com/AarohiSingla/Tracking-and-counting-Using-YOLOv8-and-DeepSORT.git
   ```

9. **Configure Deep SORT**

   Copy `Tracker.py` from the BoatTracking folder to Deep SORT:

   ```bash
   cp Tracker.py Tracking-and-counting-Using-YOLOv8-and-DeepSORT/deep_sort/sort/
   ```

## Usage

### Running the Video Tracking

1. **Place Videos**

   Ensure your video files are located in the `videos` directory.

2. **Run the Tracking Script**

```bash
python videoTrackingV2.py
```

   This script will process all `.m4v` videos in the `videos` folder, perform detection and tracking, reduce detections, and match boat events. Results will be saved in the `output` directory.

3. **View Results**

   - **Processed Videos:** Located in the `output` directory.
   - **Detection Results:** Located in the `result_tracks` directory.
   - **Database Entries:** Accessed via the API or directly from the database.

### API Endpoints

The project includes a FastAPI server to interact with the boat tracking data.

1. **Start the Server**

```bash
uvicorn serverV2:app --reload
```

2. **Available Endpoints**

- **Create a Boat Launch Event**

```http
POST /boat/launch/
```

  **Parameters:**

  - `boatID` (int): Unique identifier for the boat.
  - `launchTime` (str): Epoch timestamp of the launch event.

- **Update Boat Retrieval Event**

```http
PUT /boat/retrieve/{boat_id}
```

  **Parameters:**

  - `boat_id` (int): Unique identifier for the boat.
  - `retrievalTime` (str): Epoch timestamp of the retrieval event.
  - `match_id` (int): ID of the matching boat event.

- **Get All Boat Events**

```http
GET /boats/
```

3. **Interactive Documentation**
> Access the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) once the server is running.

## Scripts Overview </>

### `videoTrackingV2.py`

- **Purpose:** Processes video files to detect and track boats using YOLOv8 and DeepSORT.

### `reductionV3.py`

- **Purpose:** Reduces and refines detection results to eliminate duplicates and stationary boats.

### `compareV4.py`

- **Purpose:** Compares and matches boat detection events.

### `evaluation.py`

- **Purpose:** Evaluates trained YOLO models against a dataset.

### `database.py`

- **Purpose:** Manages database interactions using SQLAlchemy.

### `serverV2.py`

- **Purpose:** Implements the FastAPI server for managing boat events.

## Configuration ⚙️

### `config.yaml`

Configure dataset paths and other parameters required for model evaluation and video processing.

```yaml
# Example configuration
dataset:
  train: [project_path]/data
  val: [project_path]/data
  test: [project_path]/data
```

> Ensure the `config.yaml` file is correctly set up with absolute paths to your datasets. This file would be helpful for fine-tuning the model further.
