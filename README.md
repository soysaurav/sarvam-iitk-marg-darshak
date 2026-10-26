# 🚲 IITK Marg-Darshak: Campus Transit & Obstruction Intelligence

> **Voice-First Campus Roadblock Reporting & Safe Commute Advisor** built with **Sarvam AI** for **IIT Kanpur**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sarvam-iitk-marg-darshak.streamlit.app/)
&nbsp;
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/soysaurav/sarvam-iitk-marg-darshak)

📍 **Live Web Application**: [https://sarvam-iitk-marg-darshak.streamlit.app/](https://sarvam-iitk-marg-darshak.streamlit.app/)

---

## 🌟 Overview & Problem
At IIT Kanpur, heavy rainfall and active construction frequently lead to:
* **Fallen trees** across roads (near Hall 1, Library circle, Health Centre).
* **Severe waterlogging** on cycling tracks and e-rickshaw routes (Airstrip road, Hall 12/13).
* **Trench digging for pipelines** (New SAC food court, Hall 4-5 link).

Ground security guards (SIS), Malis, and cycling students who spot these first speak Hindi or regional dialects and won't fill out English forms. 

**IITK Marg-Darshak** turns raw voice notes into real-time campus route intelligence.

---

## 🚀 Key Features

1. **🎙️ Voice-First Roadblock Reporting**:
   - Guards/students record voice notes in Hindi, English, or Hinglish directly in browser.
   - **Sarvam Saaras (`saaras:v3`)** transcribes spoken speech into vernacular text.
   - **Sarvam AI (`sarvam-105b-conversations`)** extracts road segment, nearest landmark, hazard type, passability for bicycles/foot, and auto-pins it on the campus map with GPS coordinates.

2. **🧭 Smart Campus Commute & Path Suggestion**:
   - Select your starting point and destination from a complete directory of:
     - **Hostels**: Hall 1 through Hall 13, GH1, GH Tower
     - **Academic Area**: Lecture Hall Complex (LHC), PK Kelkar Library, Computer Centre (CC), Faculty Building (FB), SPASE Dept, ACMS
     - **Food Outlets**: Naughty Blenders, Domino's / CCD, Old SAC, Canteens
     - **Amenities**: Health Centre, Main Gate, OAT, Community Centre
   - Checks active roadblocks on your path.
   - Suggests the safest, driest detour.
   - **🔊 Spoken Audio Directions (Bulbul TTS)**: Listen hands-free while cycling!

---

## 🛠️ Tech Stack & Sarvam AI Models
* **Speech-to-Text**: Sarvam AI `saaras:v3` (Indic voice transcription)
* **Reasoning & Natural Hinglish Extraction**: Sarvam AI `sarvam-105b-conversations`
* **Voice Synthesis**: Sarvam AI `bulbul:v2` (Indic Text-to-Speech)
* **Frontend Dashboard**: Streamlit
* **Mapping**: Pydeck & OpenStreetMap centered on IIT Kanpur campus

---

## 🌐 Live Deployment
The application is live on Streamlit Community Cloud:
👉 **[https://sarvam-iitk-marg-darshak.streamlit.app/](https://sarvam-iitk-marg-darshak.streamlit.app/)**
