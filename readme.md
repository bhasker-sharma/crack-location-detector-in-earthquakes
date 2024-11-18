# Crack Location Detection System

This project provides a Python implementation to locate the crack's epicenter using Time Difference of Arrival (TDoA) technique, leveraging sensor data. It utilizes a set of predefined sensor positions and the propagation speed of vibrations to estimate the crack location.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Algorithm](#algorithm)

## Overview

The **Crack Location Detection System** uses Time Difference of Arrival (TDoA) to estimate the location of a crack based on the arrival times of vibrations detected by multiple sensors. The system calculates the differences in arrival times (TDoA) of vibrations recorded at various sensor locations and uses this data to compute the location of the crack.

### How the Code Works

1. **Initialization**:
   - The `CrackLocator` class initializes with a list of sensor IDs and their corresponding coordinates in Degrees, Minutes, and Seconds (DMS) format.
   - It converts these DMS coordinates to Cartesian coordinates (X, Y) using the Haversine formula for distance calculations on a sphere (Earth).

2. **Conversion Functions**:
   - `dms_to_decimal(dms)`: Converts DMS coordinates to decimal degrees.
   - `_convert_to_xy()`: Converts all sensor coordinates from DMS to XY positions using the Haversine formula.

3. **Crack Location Calculation**:
   - `calculate_crack_location(time_differences, vibration_speed)`: 
     - This method takes the time differences (TDoA) and vibration speed as input.
     - It defines an objective function that computes the squared error between observed and predicted time differences based on a guessed crack location.
     - The `minimize` function from `scipy.optimize` is used to minimize this error, optimizing the crack location.
     - The method returns the estimated crack location in DMS format.

4. **DMS to Lat/Lon Conversion**:
   - `_convert_to_lat_lon(xy)`: Converts XY positions back to latitude and longitude.
   - `_convert_to_dms(decimal_coords)`: Converts latitude and longitude coordinates from decimal degrees to DMS format.

## Usage

1. **Install Dependencies**:
   Ensure you have Python and required libraries installed:
   - `numpy`
   - `scipy`
   - `re`

2. **Running the Code**:
   - Clone this repository or download the `version1.py` file.
   - Navigate to the directory containing `version1.py`.
   - Execute the script:
     ```bash
     python version1.py
     ```
   - Follow the prompts to input the vibration speed and the observed time differences for each sensor.

3. **Input Format**:
   - Vibration Speed: Input the vibration speed in meters per second (m/s).
   - Time Differences: Input the time differences in seconds for each sensor relative to D1 (D1 is used as the reference).

## Algorithm

### Overview:
The algorithm uses the Time Difference of Arrival (TDoA) method to estimate the location of the crack. TDoA is based on the difference in the arrival times of the same signal at different sensor locations. The difference in these arrival times can be used to compute the distance from each sensor to the crack. By knowing the exact positions of the sensors and the difference in arrival times (TDoA), the crack location can be estimated.

### Steps:
1. **Sensor Initialization**:
   - The sensor positions are predefined and converted from DMS to XY (Cartesian) coordinates.
   - XY coordinates are computed using the Haversine formula to account for the spherical shape of the Earth.

2. **Objective Function**:
   - An objective function is defined to minimize the squared error between observed and predicted TDoA values.
   - The predicted TDoA values are calculated using the Euclidean distance between the guessed crack location and each sensor.

3. **Optimization**:
   - The optimization problem is solved using `scipy.optimize.minimize` with the L-BFGS-B algorithm.
   - The optimization attempts to find the crack location that minimizes the error.

4. **Conversion to DMS**:
   - The estimated crack location (in decimal degrees) is converted back to DMS format for easier interpretation.

