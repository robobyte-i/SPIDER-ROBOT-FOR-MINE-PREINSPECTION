# SPIDER-ROBOT-FOR-MINE-PREINSPECTION
---

# 🐾 SLAM-Based 4-Legged Robot for Mine Pre-Inspection

## 📌 Project Overview

This project presents a **SLAM-based quadruped robot** designed for **underground mine safety inspection**. The robot autonomously navigates hazardous environments, detects unsafe conditions, and provides **real-time data using WiFi communication**.

It replaces risky manual inspection with a **smart robotic solution**, improving miner safety.

---

## 🚨 Problem Statement

Underground mines are dangerous due to:

* Toxic gas accumulation
* Tunnel collapses
* Poor visibility
* Temperature and humidity variations

Manual inspection puts human lives at risk.

---

## 🎯 Objectives

* Develop a **4-legged robot** for uneven terrain navigation
* Implement **SLAM for mapping and localization**
* Monitor environmental conditions:

  * Temperature
  * Humidity
  * Obstacles
  * Vibrations (structural instability)
* Enable **real-time monitoring via WiFi**
* Ensure **safe pre-inspection before human entry**

---

## 🧠 Key Features

* 🐾 **Quadruped locomotion** for rough terrain
* 🗺️ **SLAM-based navigation (GPS-denied environment)**
* 📡 **WiFi-based communication (no RF module)**
* 📷 **Live video streaming**
* 🌡️ **Multi-sensor hazard detection**
* 📊 **Real-time monitoring dashboard**

---

## ⚙️ System Architecture

### 🔌 Hardware Components

* **ESP32 (Main Microcontroller with WiFi)**
* Servo Motors (for 4-legged movement)
* Sensors:

  * Temperature Sensor
  * Humidity Sensor
  * Ultrasonic Sensor
  * Vibration Sensor
* ESP32 Camera Module (for live streaming)
* Battery + Power Regulation Module (LM2596)

---

### 🧩 Software Components

* Arduino IDE / Embedded C
* SLAM Algorithm (2D Mapping Simulation)
* Web-based Monitoring Dashboard
* WiFi Communication (HTTP/Web Server)

---

## 🔄 Workflow

1. Robot is deployed inside the mine
2. ESP32 initializes sensors and WiFi connection
3. Robot performs **SLAM-based mapping**
4. Sensors continuously collect environmental data
5. Live video + data sent via WiFi
6. Supervisor monitors through PC/mobile dashboard
7. Decision taken for safe human entry

---

## 🌐 Communication System

* Uses **ESP32 built-in WiFi**
* Data transmission via:

  * HTTP server
  * Web dashboard
* No external RF modules required

---


## 🧪 Simulation & Demo

🎥 SLAM Simulation:
[https://docs.google.com/file/d/1Hb9VHX2T937x2WWDhWRDRFQzPnjA8wwd/preview](https://docs.google.com/file/d/1Hb9VHX2T937x2WWDhWRDRFQzPnjA8wwd/preview)

🎥 Robot Demo:
[https://docs.google.com/file/d/10LbLqjFx9P_g5-bVa09W9t2YTGyMRln_/preview](https://docs.google.com/file/d/10LbLqjFx9P_g5-bVa09W9t2YTGyMRln_/preview)

---

## 💰 Cost Estimation

| Component            | Cost       |
| -------------------- | ---------- |
| Sensors              | ₹1000      |
| Servo Motors & Frame | ₹2000      |
| ESP32 + Camera       | ₹1000      |
| Power System         | ₹500       |
| **Total**            | **~₹4500** |

---

## 🔮 Future Scope

* Integration of **LiDAR-based SLAM**
* AI-based hazard prediction
* Autonomous path planning
* Mobile app for remote monitoring
* 3D mapping of underground mines

---

## 📚 References

* IEEE Xplore – Mine Safety Monitoring using Robotics (2020)
* Boston Dynamics – Spot Robot Case Study
* CSIRO – Underground Mine Mapping
* Elsevier – Mine Safety Research

---

## 👨‍💻 Team Members

* **Aswin I**
* Madheshwaran
* Antony Richard A

👨‍🏫 **Mentor:** Robert Rajkumar

---

## ⭐ Conclusion

This project demonstrates the use of **ESP32-based robotics and SLAM technology** to create a cost-effective and efficient system for **mine safety inspection**, reducing human risk and improving operational safety.

