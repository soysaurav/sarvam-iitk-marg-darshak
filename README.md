# 🚲 IITK Marg-Darshak: Campus Transit & Obstruction Intelligence

> **Voice-First Campus Roadblock Reporting & Safe Commute Advisor** built with **Sarvam AI** for **IIT Kanpur**.

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
   - Guards/students send voice notes in Hindi/English.
   - **Sarvam AI (`sarvam-105b-conversations`)** extracts road segment, hazard type, passability for bicycles/foot, and auto-pins it on the campus map.

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

## 🛠️ Tech Stack
* **Language & Reasoning AI**: Sarvam AI `sarvam-105b-conversations`
* **Voice Synthesis**: Sarvam AI `bulbul:v2` (Indic Text-to-Speech)
* **Frontend Dashboard**: Streamlit
* **Mapping**: Streamlit Native Map (OpenStreetMap focused on IIT Kanpur @ zoom 15)

---

## 📦 Deployment to Streamlit Community Cloud
1. Push this repository to GitHub.
2. In [share.streamlit.io](https://share.streamlit.io), connect your repo (`app.py`).
3. Under **Advanced settings > Secrets**, add:
   ```toml
   SARVAM_API_KEY = "your_sarvam_api_key"
   ```
4. Click **Deploy**!
