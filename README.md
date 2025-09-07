# Time-of-Flight 3D Environment Mapper
Motorized ToF scanner built with the **TI MSP-EXP432E401Y**, **VL53L1X** sensor, and a **28BYJ-48** stepper motor.  
Distance data are streamed over UART and rendered as a 3D point cloud/line-set in **Python + Open3D**.

> Course: COMPENG 2DX3 (McMaster University) — 2024  
> Author: Ian (Sungkyun) Cho

## Overview
This project builds a **3D indoor map** using an infrared **Time-of-Flight (ToF)** sensor mounted on a small stepper motor.  
At each **11.25°** increment (16 steps), the sensor measures distance; the PC converts the polar measurement to Cartesian coordinates and renders the scene live in **Open3D**.

- Sensor ↔ MCU: **I²C @ 400 kHz**
- MCU ↔ PC: **UART @ 115200 bps (8-N-1)**
- PC (receiver): **Python 3.8+** using `pyserial`, `numpy`, `open3d`

## Features
- Start/stop with physical push buttons, LED status (PN0/PN1)
- Motor-synchronized sampling with per-step dwell for accuracy
- Real-time point cloud and line-set visualization
- Simple CSV/XYZ export for post-processing
