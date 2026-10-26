import os
import json
import base64
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="IITK Marg-Darshak | Campus Transit & Roadblock Copilot",
    page_icon="🚲",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #1d3557;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 15px;
        color: #457b9d;
        margin-bottom: 20px;
    }
    .option-card {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: 0.2s;
    }
    .blockage-card {
        background-color: #ffffff;
        border-left: 5px solid #e63946;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .route-safe {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
    }
    .route-blocked {
        background-color: #ffebee;
        border-left: 5px solid #c62828;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Get Sarvam AI Client
def get_sarvam_client():
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        return None
    try:
        from sarvamai import SarvamAI
        return SarvamAI(api_subscription_key=api_key)
    except Exception:
        return None

# Comprehensive IIT Kanpur Landmarks Database
CAMPUS_LOCATIONS = {
    # Hostels
    "Hall 1": {"lat": 26.5142, "lon": 80.2315, "zone": "Hostel Zone"},
    "Hall 2": {"lat": 26.5135, "lon": 80.2310, "zone": "Hostel Zone"},
    "Hall 3": {"lat": 26.5125, "lon": 80.2305, "zone": "Hostel Zone"},
    "Hall 4": {"lat": 26.5118, "lon": 80.2300, "zone": "Hostel Zone"},
    "Hall 5": {"lat": 26.5108, "lon": 80.2295, "zone": "Hostel Zone"},
    "Hall 7": {"lat": 26.5090, "lon": 80.2285, "zone": "Hostel Zone"},
    "Hall 8": {"lat": 26.5080, "lon": 80.2290, "zone": "Hostel Zone"},
    "Hall 9": {"lat": 26.5065, "lon": 80.2315, "zone": "Hostel Zone"},
    "Hall 10": {"lat": 26.5058, "lon": 80.2325, "zone": "Hostel Zone"},
    "Hall 11": {"lat": 26.5068, "lon": 80.2305, "zone": "Hostel Zone"},
    "Hall 12": {"lat": 26.5075, "lon": 80.2310, "zone": "Hostel Zone"},
    "Hall 13": {"lat": 26.5085, "lon": 80.2320, "zone": "Hostel Zone"},
    "Girls Hostel 1 (GH1)": {"lat": 26.5148, "lon": 80.2345, "zone": "Hostel Zone"},
    "GH Tower": {"lat": 26.5152, "lon": 80.2350, "zone": "Hostel Zone"},

    # Academic & Research
    "Lecture Hall Complex (LHC)": {"lat": 26.5120, "lon": 80.2340, "zone": "Academic Area"},
    "PK Kelkar Library": {"lat": 26.5118, "lon": 80.2338, "zone": "Academic Area"},
    "Computer Centre (CC)": {"lat": 26.5112, "lon": 80.2342, "zone": "Academic Area"},
    "Faculty Building (FB)": {"lat": 26.5125, "lon": 80.2350, "zone": "Academic Area"},
    "SPASE Department": {"lat": 26.5115, "lon": 80.2335, "zone": "Academic Area"},
    "Advanced Centre for Materials Science (ACMS)": {"lat": 26.5108, "lon": 80.2330, "zone": "Academic Area"},
    "Core Labs / Tutorial Complex": {"lat": 26.5122, "lon": 80.2345, "zone": "Academic Area"},
    "Flight Lab & Airstrip": {"lat": 26.5195, "lon": 80.2315, "zone": "Research Facilities"},

    # Food Outlets & Canteens
    "Naughty Blenders (New SAC)": {"lat": 26.5128, "lon": 80.2325, "zone": "Food & Recreation"},
    "Domino's / CCD (New SAC)": {"lat": 26.5130, "lon": 80.2326, "zone": "Food & Recreation"},
    "Old SAC / Dosa Plaza": {"lat": 26.5136, "lon": 80.2330, "zone": "Food & Recreation"},
    "Hall 1 Canteen": {"lat": 26.5142, "lon": 80.2315, "zone": "Food & Recreation"},
    "Hall 4 Canteen": {"lat": 26.5118, "lon": 80.2300, "zone": "Food & Recreation"},
    "Campus Restaurant / Main Gate Market": {"lat": 26.5160, "lon": 80.2365, "zone": "Commercial Area"},

    # Campus Key Amenities
    "Health Centre (Emergency Care)": {"lat": 26.5138, "lon": 80.2355, "zone": "Amenities"},
    "Main Gate (GT Road Exit)": {"lat": 26.5165, "lon": 80.2370, "zone": "Campus Gate"},
    "Open Air Theatre (OAT)": {"lat": 26.5132, "lon": 80.2335, "zone": "Recreation"},
    "Community Centre": {"lat": 26.5150, "lon": 80.2360, "zone": "Amenities"}
}

# Initial realistic IITK Blockages
INITIAL_BLOCKAGES = [
    {
        "id": "BLK-101",
        "segment": "Hall 1 to PK Kelkar Library Turn",
        "hazard": "Fallen Neem Tree & Waterlogging",
        "reported_by": "Security Guard (SIS Post 4)",
        "lat": 26.5130,
        "lon": 80.2328,
        "passable_cycle": False,
        "passable_foot": True,
        "passable_erickshaw": False,
        "voice_transcript": "हॉल 1 से लाइब्रेरी वाले मोड़ पर बड़ा नीम का पेड़ गिर गया है और पानी भरा है, साइकिल भी नहीं निकल पाएगी।",
        "advice": "Avoid Library Circle. Commuters from Hall 1-3 should take road behind Faculty Building.",
        "status": "Blocked"
    },
    {
        "id": "BLK-102",
        "segment": "New SAC (Naughty Blenders / Domino's) to Hall 5 Road",
        "hazard": "Sewer Line Construction Digging",
        "reported_by": "Hall 5 Student Voice Note",
        "lat": 26.5115,
        "lon": 80.2310,
        "passable_cycle": False,
        "passable_foot": False,
        "passable_erickshaw": False,
        "voice_transcript": "नया सैक (New SAC) से हॉल 5 जाने वाली सड़क पर गहरी खुदाई चल रही है पाइपलाइन के लिए। रास्ता पूरी तरह बंद है।",
        "advice": "Use Hall 4 perimeter link road to reach New SAC food court.",
        "status": "Blocked"
    }
]

# Session State for Blockages
if "blockages" not in st.session_state:
    st.session_state.blockages = INITIAL_BLOCKAGES.copy()

# -------------------------------------------------------------
# Top Header
# -------------------------------------------------------------
st.markdown('<div class="main-title">🚲 IITK Marg-Darshak</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">IIT Kanpur Campus Roadblock Intelligence & Safe Transit Copilot | Powered by Sarvam AI</div>', unsafe_allow_html=True)

# Connection indicator
has_key = bool(os.getenv("SARVAM_API_KEY"))
if has_key:
    st.success("✅ Sarvam AI Connected (Speech-to-Text & Reasoning Live)")
else:
    st.warning("⚠️ Running in offline demo mode. Configure SARVAM_API_KEY in `.env` for live calls.")

# -------------------------------------------------------------
# TWO CLEAR MAIN OPTIONS IN THE BEGINNING
# -------------------------------------------------------------
st.write("### What would you like to do?")
action_choice = st.radio(
    "Select an option:",
    [
        "🎙️ Option 1: Inform / Report a Roadblock using Voice",
        "🧭 Option 2: Check Active Blockages & Plan Safe Route"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# =============================================================
# OPTION 1: RECORD VOICE NOTE & REPORT ROADBLOCK
# =============================================================
if "Option 1" in action_choice:
    st.subheader("🎙️ Report an Obstruction using Voice (Guards / Students / Staff)")
    st.write("Spotted a fallen tree, heavy water blockage, or construction digging? **Hold and speak** in Hindi or English. Sarvam AI will process your audio and mark the blockage on the campus map.")

    # Native Audio Recorder
    audio_val = st.audio_input("🔴 Click to record voice note (Hold & Speak, then Stop):")

    col_btn, col_sample = st.columns([1, 2])
    
    # Process Recorded Audio
    if audio_val is not None:
        st.audio(audio_val, format="audio/wav")
        if st.button("🚀 Process My Voice with Sarvam AI", type="primary"):
            client = get_sarvam_client()
            if not client:
                st.error("SARVAM_API_KEY required in .env for live audio transcription.")
            else:
                with st.spinner("Step 1/2: Sarvam Saaras AI transcribing your spoken voice..."):
                    try:
                        audio_bytes = audio_val.getvalue()
                        stt_res = client.speech_to_text.transcribe(
                            file=("voice_report.wav", audio_bytes, "audio/wav"),
                            model="saaras:v3"
                        )
                        transcript = stt_res.transcript
                        st.info(f"🗣️ **Voice Transcribed by Sarvam Saaras:** \"{transcript}\"")

                        with st.spinner("Step 2/2: Sarvam-105B extracting blockage telemetry & campus coordinates..."):
                            prompt = f"""You are the IIT Kanpur Transit Intelligence parser.
Extract the road blockage information from this voice transcript in JSON:
Transcript: "{transcript}"

Return JSON ONLY:
{{
  "segment": "Campus road segment (e.g., Hall 12 road or Library circle)",
  "hazard": "Fallen Tree / Waterlogging / Construction Digging",
  "lat": 26.5125,
  "lon": 80.2330,
  "passable_cycle": false,
  "passable_foot": true,
  "advice": "1 short sentence detour advice for cyclists"
}}"""
                            res = client.chat.completions(
                                model="sarvam-105b-conversations",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=120
                            )
                            text_out = res.choices[0].message.content
                            if "```json" in text_out:
                                text_out = text_out.split("```json")[1].split("```")[0].strip()
                            elif "```" in text_out:
                                text_out = text_out.split("```")[1].split("```")[0].strip()

                            parsed = json.loads(text_out)
                            
                            new_blk = {
                                "id": f"BLK-{len(st.session_state.blockages)+101}",
                                "segment": parsed.get("segment", "Campus Roadway, IIT Kanpur"),
                                "hazard": parsed.get("hazard", "Obstruction / Waterlogging"),
                                "reported_by": "Voice Note (Citizen / Guard)",
                                "lat": float(parsed.get("lat", 26.5125)),
                                "lon": float(parsed.get("lon", 80.2330)),
                                "passable_cycle": bool(parsed.get("passable_cycle", False)),
                                "passable_foot": bool(parsed.get("passable_foot", True)),
                                "passable_erickshaw": False,
                                "voice_transcript": transcript,
                                "advice": parsed.get("advice", "Please use parallel campus perimeter route."),
                                "status": "Blocked"
                            }
                            
                            st.session_state.blockages.insert(0, new_blk)
                            st.success("🎉 Voice note processed! New obstruction added and pinned to the IIT Kanpur map below.")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error processing audio: {e}")

    # Fallback Sample Text / Voice simulation
    with st.expander("Or enter text manually if mic is unavailable:"):
        manual_report = st.text_input(
            "Enter blockage note (Hindi or English):",
            value="हेल्थ सेंटर रोड पर बड़ा पेड़ गिर गया है, रास्ता पूरी तरह बंद है।"
        )
        if st.button("Submit Text Report"):
            client = get_sarvam_client()
            if client:
                with st.spinner("Extracting with Sarvam-105B..."):
                    try:
                        prompt = f"""Extract road blockage in JSON from: "{manual_report}".
Return JSON ONLY:
{{
  "segment": "Campus road segment",
  "hazard": "Fallen Tree / Waterlogging / Construction",
  "lat": 26.5138,
  "lon": 80.2355,
  "passable_cycle": false,
  "passable_foot": false,
  "advice": "Use alternate route"
}}"""
                        res = client.chat.completions(
                            model="sarvam-105b-conversations",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=100
                        )
                        text_out = res.choices[0].message.content
                        if "```json" in text_out:
                            text_out = text_out.split("```json")[1].split("```")[0].strip()
                        elif "```" in text_out:
                            text_out = text_out.split("```")[1].split("```")[0].strip()
                        parsed = json.loads(text_out)
                        
                        st.session_state.blockages.insert(0, {
                            "id": f"BLK-{len(st.session_state.blockages)+101}",
                            "segment": parsed.get("segment", "Campus Road"),
                            "hazard": parsed.get("hazard", "Roadblock"),
                            "reported_by": "Text Report",
                            "lat": float(parsed.get("lat", 26.5138)),
                            "lon": float(parsed.get("lon", 80.2355)),
                            "passable_cycle": False,
                            "passable_foot": False,
                            "passable_erickshaw": False,
                            "voice_transcript": manual_report,
                            "advice": parsed.get("advice", "Take detour"),
                            "status": "Blocked"
                        })
                        st.success("Roadblock added to map!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error: {err}")

# =============================================================
# OPTION 2: CHECK BLOCKAGES & PLAN SAFE ROUTE
# =============================================================
else:
    st.subheader("🧭 Check Blockages & Suggest Best Path")
    st.write("Going to lectures, labs, or food outlets? Select your starting point and destination:")

    c_from, c_to, c_mode = st.columns([2, 2, 1.5])
    locations_list = sorted(list(CAMPUS_LOCATIONS.keys()))
    
    with c_from:
        start_point = st.selectbox("📍 Starting From:", locations_list, index=locations_list.index("Hall 12"))
    with c_to:
        destination = st.selectbox("🎯 Destination:", locations_list, index=locations_list.index("Lecture Hall Complex (LHC)"))
    with c_mode:
        commute_mode = st.selectbox("🚴 Commute Mode:", ["Bicycle 🚲", "On Foot 🚶", "E-Rickshaw 🛺"])

    if st.button("🔍 Check Route Status & Suggest Path", type="primary"):
        start_coords = CAMPUS_LOCATIONS[start_point]
        dest_coords = CAMPUS_LOCATIONS[destination]
        
        # Check if direct line or nearby blockages exist
        relevant_blockages = []
        for b in st.session_state.blockages:
            min_lat = min(start_coords["lat"], dest_coords["lat"]) - 0.003
            max_lat = max(start_coords["lat"], dest_coords["lat"]) + 0.003
            min_lon = min(start_coords["lon"], dest_coords["lon"]) - 0.003
            max_lon = max(start_coords["lon"], dest_coords["lon"]) + 0.003
            
            if min_lat <= b["lat"] <= max_lat and min_lon <= b["lon"] <= max_lon:
                relevant_blockages.append(b)

        client = get_sarvam_client()
        
        if relevant_blockages:
            st.markdown(f'<div class="route-blocked"><h3>⚠️ Direct Route Impeded by {len(relevant_blockages)} Roadblock(s)</h3></div>', unsafe_allow_html=True)
            for rb in relevant_blockages:
                st.error(f"🚫 **Hazard at {rb['segment']}**: {rb['hazard']} (Reported by: {rb['reported_by']})")
                st.caption(f"💡 Recommended Detour: {rb['advice']}")
            
            # AI Detour Generation via Sarvam-105B
            if client:
                with st.spinner("Sarvam AI calculating optimal campus detour..."):
                    try:
                        prompt = f"""You are IIT Kanpur's smart campus transit copilot.
Student wants to travel from: {start_point} to {destination} on {commute_mode}.
Active obstructions: {[r['segment'] + ': ' + r['hazard'] for r in relevant_blockages]}.

In 2 short sentences, provide the safest, driest detour route using real IIT Kanpur landmarks (like Faculty Building back road, Core Labs path, SAC perimeter, or Hall 1 link).
Keep it direct and helpful."""
                        res = client.chat.completions(
                            model="sarvam-105b-conversations",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=100
                        )
                        ai_detour = res.choices[0].message.content
                        st.success(f"🤖 **Sarvam AI Detour Advisory:**\n\n{ai_detour}")
                        
                        # Spoken Audio Button for Cycling Student
                        if st.button("🔊 Listen to Detour (Hands-Free for Cycling)"):
                            try:
                                tts_res = client.text_to_speech.convert(
                                    text=ai_detour,
                                    language_code="hi-IN",
                                    model="bulbul:v2"
                                )
                                if tts_res.audios:
                                    audio_bytes = base64.b64decode(tts_res.audios[0])
                                    st.audio(audio_bytes, format="audio/wav")
                            except Exception:
                                st.info("Audio broadcast available when TTS is configured.")
                    except Exception as e:
                        st.info(f"AI Path suggestion: Avoid {relevant_blockages[0]['segment']}. Proceed via Faculty Building perimeter.")
            else:
                st.info(f"💡 **Suggested Alternate Path:** Avoid {relevant_blockages[0]['segment']}. Take the parallel link road via Faculty Building / Library back lane.")

        else:
            st.markdown(f'<div class="route-safe"><h3>✅ Path Clear from {start_point} to {destination}</h3><p>No active trees down, waterlogging, or construction reported on this segment.</p></div>', unsafe_allow_html=True)
            st.balloons()

# -------------------------------------------------------------
# IIT KANPUR MAP & RED DOTS EXPLANATION / MANAGEMENT
# -------------------------------------------------------------
st.divider()
st.subheader("📍 Live IIT Kanpur Campus Roadblock Map")

# Clear explanation of red dots + management controls
col_map_info, col_map_ctrl = st.columns([3, 1])
with col_map_info:
    st.markdown("""
    ℹ️ **What are the red dots on the map?**
    The **red dots** represent **currently reported roadblocks** on campus (fallen trees, waterlogged areas, or construction trenches).
    """)
with col_map_ctrl:
    if st.button("🧹 Clear All Roadblocks"):
        st.session_state.blockages = []
        st.rerun()

if st.session_state.blockages:
    map_df = pd.DataFrame([
        {
            "lat": b["lat"],
            "lon": b["lon"]
        }
        for b in st.session_state.blockages
    ])
    st.map(map_df, zoom=15)
    
    st.write("#### 📋 Active Obstruction Details:")
    for b in st.session_state.blockages:
        st.markdown(f'<div class="blockage-card"><strong>🔴 {b["segment"]}</strong> — {b["hazard"]}<br><span style="color: #666; font-size: 13px;">Reported via: {b["reported_by"]} | Detour: {b["advice"]}</span></div>', unsafe_allow_html=True)
else:
    st.info("🟢 No active roadblocks! All campus roads are currently open and clear.")
    # Show clean campus map centered on IIT Kanpur
    clean_center_df = pd.DataFrame([{"lat": 26.5123, "lon": 80.2329}])
    st.map(clean_center_df, zoom=15)
