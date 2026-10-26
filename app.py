import os
import re
import json
import base64
import pandas as pd
import streamlit as st
import pydeck as pdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="IITK Marg-Darshak | Campus Transit & Roadblock Copilot",
    page_icon="🚲",
    layout="wide"
)

# Custom Clean Styling
st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #1d3557;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 15px;
        color: #457b9d;
        margin-bottom: 20px;
    }
    .blockage-card {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #dc2626 !important;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    .blockage-card * {
        color: #111827;
    }
    .blockage-title {
        color: #b91c1c !important;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .blockage-detail {
        color: #1f2937 !important;
        font-size: 14px;
        margin-top: 4px;
    }
    .blockage-detail strong {
        color: #111827 !important;
    }
    .blockage-meta {
        color: #4b5563 !important;
        font-size: 13px;
        margin-top: 8px;
        font-weight: 500;
    }
    .badge-landmark {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid #fecaca;
    }
    .route-safe {
        background-color: #e8f5e9;
        color: #1b5e20 !important;
        border-left: 5px solid #2e7d32;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
    }
    .route-safe * {
        color: #1b5e20 !important;
    }
    .route-blocked {
        background-color: #ffebee;
        color: #b71c1c !important;
        border-left: 5px solid #c62828;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
    }
    .route-blocked * {
        color: #b71c1c !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Retrieve Sarvam API Key from environment or Streamlit Cloud Secrets
def get_api_key():
    key = os.getenv("SARVAM_API_KEY")
    if key and key.strip():
        return key.strip()
    try:
        if hasattr(st, "secrets") and "SARVAM_API_KEY" in st.secrets:
            return str(st.secrets["SARVAM_API_KEY"]).strip()
    except Exception:
        pass
    return None

# Helper: Get Sarvam AI Client
def get_sarvam_client():
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        from sarvamai import SarvamAI
        return SarvamAI(api_subscription_key=api_key)
    except Exception:
        return None

# Comprehensive IIT Kanpur Landmarks Database with Accurate GPS Coordinates
CAMPUS_LOCATIONS = {
    # Hostels (Halls of Residence)
    "Hall 1": {"lat": 26.5142, "lon": 80.2315},
    "Hall 2": {"lat": 26.5135, "lon": 80.2310},
    "Hall 3": {"lat": 26.5125, "lon": 80.2305},
    "Hall 4": {"lat": 26.5118, "lon": 80.2300},
    "Hall 5": {"lat": 26.5108, "lon": 80.2295},
    "Hall 6": {"lat": 26.5140, "lon": 80.2355},
    "Hall 7": {"lat": 26.5090, "lon": 80.2285},
    "Hall 8": {"lat": 26.5080, "lon": 80.2290},
    "Hall 9": {"lat": 26.5065, "lon": 80.2315},
    "Hall 10": {"lat": 26.5058, "lon": 80.2325},
    "Hall 11": {"lat": 26.5068, "lon": 80.2305},
    "Hall 12": {"lat": 26.5075, "lon": 80.2310},
    "Hall 13": {"lat": 26.5085, "lon": 80.2320},
    "Girls Hostel 1 (GH1)": {"lat": 26.5148, "lon": 80.2345},
    "GH Tower": {"lat": 26.5152, "lon": 80.2350},

    # Academic & Research
    "Lecture Hall Complex (LHC)": {"lat": 26.5120, "lon": 80.2340},
    "PK Kelkar Library": {"lat": 26.5118, "lon": 80.2338},
    "Computer Centre (CC)": {"lat": 26.5112, "lon": 80.2342},
    "Faculty Building (FB)": {"lat": 26.5125, "lon": 80.2350},
    "SPASE Department": {"lat": 26.5115, "lon": 80.2335},
    "Advanced Centre for Materials Science (ACMS)": {"lat": 26.5108, "lon": 80.2330},
    "Core Labs / Tutorial Complex": {"lat": 26.5122, "lon": 80.2345},
    "Flight Lab & Airstrip": {"lat": 26.5195, "lon": 80.2315},

    # Food Outlets & Student Activity
    "Naughty Blenders (New SAC)": {"lat": 26.5128, "lon": 80.2325},
    "Domino's / CCD (New SAC)": {"lat": 26.5130, "lon": 80.2326},
    "Old SAC / Dosa Plaza": {"lat": 26.5136, "lon": 80.2330},
    "Hall 1 Canteen": {"lat": 26.5142, "lon": 80.2315},
    "Hall 4 Canteen": {"lat": 26.5118, "lon": 80.2300},
    "Campus Restaurant / Main Gate Market": {"lat": 26.5160, "lon": 80.2365},

    # Campus Key Amenities
    "Health Centre (Emergency Care)": {"lat": 26.5138, "lon": 80.2355},
    "Main Gate (GT Road Exit)": {"lat": 26.5165, "lon": 80.2370},
    "Open Air Theatre (OAT)": {"lat": 26.5132, "lon": 80.2335},
    "Community Centre": {"lat": 26.5150, "lon": 80.2360},
    "Visitors Hostel (VH)": {"lat": 26.5160, "lon": 80.2385}
}

# Accurate Multi-Stage Coordinate Resolver for IIT Kanpur Landmarks
def resolve_campus_coordinates(location_str, full_text=""):
    """
    Precisely resolves campus coordinates using multi-stage matching:
    1. Direct exact or normalized canonical match against CAMPUS_LOCATIONS keys
    2. Word-boundary regular expressions (\\b) for multi-digit and single-digit halls (avoids Hall 1 vs Hall 12 collision)
    3. Hindi and English synonyms with strict word boundaries
    4. Safe fallback to campus center
    """
    loc_clean = (location_str or "").strip()
    text_clean = (full_text or "").strip()
    
    # Candidates to evaluate in priority order
    candidates = [loc_clean, f"{loc_clean} {text_clean}".strip()]
    
    # Stage 1: Exact or clean key match
    for cand in candidates:
        if not cand:
            continue
        cand_lower = cand.lower()
        for key, coords in CAMPUS_LOCATIONS.items():
            key_clean = key.lower().split(" (")[0].strip()
            if key.lower() == cand_lower or key_clean == cand_lower:
                return coords["lat"], coords["lon"], key

    # Stage 2: Strict Regex Patterns with Word Boundaries (\\b)
    # Ordered with multi-digit and specific landmarks FIRST to eliminate substring hijacking
    patterns = [
        # Multi-digit Halls (checked first to prevent single-digit false matches)
        (r'\b(hall\s*(?:no\.?|number)?\s*13|h-?13|हॉल\s*(?:no\.?|नंबर)?\s*13|हॉल\s*तेरह|तेरह)\b', "Hall 13"),
        (r'\b(hall\s*(?:no\.?|number)?\s*12|h-?12|हॉल\s*(?:no\.?|नंबर)?\s*12|हॉल\s*बारह|हॉल\s*बारहा|बारह)\b', "Hall 12"),
        (r'\b(hall\s*(?:no\.?|number)?\s*11|h-?11|हॉल\s*(?:no\.?|नंबर)?\s*11|हॉल\s*ग्यारह|ग्यारह)\b', "Hall 11"),
        (r'\b(hall\s*(?:no\.?|number)?\s*10|h-?10|हॉल\s*(?:no\.?|नंबर)?\s*10|हॉल\s*दस|दस)\b', "Hall 10"),

        # Single-digit Halls (strictly isolated with \\b so Hall 1 cannot match Hall 10/11/12/13)
        (r'\b(hall\s*(?:no\.?|number)?\s*9|h-?9|हॉल\s*(?:no\.?|नंबर)?\s*9|हॉल\s*नौ)\b', "Hall 9"),
        (r'\b(hall\s*(?:no\.?|number)?\s*8|h-?8|हॉल\s*(?:no\.?|नंबर)?\s*8|हॉल\s*आठ)\b', "Hall 8"),
        (r'\b(hall\s*(?:no\.?|number)?\s*7|h-?7|हॉल\s*(?:no\.?|नंबर)?\s*7|हॉल\s*सात)\b', "Hall 7"),
        (r'\b(hall\s*(?:no\.?|number)?\s*6|h-?6|हॉल\s*(?:no\.?|नंबर)?\s*6|हॉल\s*छह|हॉल\s*छः)\b', "Hall 6"),
        (r'\b(hall\s*(?:no\.?|number)?\s*5|h-?5|हॉल\s*(?:no\.?|नंबर)?\s*5|हॉल\s*पांच)\b', "Hall 5"),
        (r'\b(hall\s*(?:no\.?|number)?\s*4|h-?4|हॉल\s*(?:no\.?|नंबर)?\s*4|हॉल\s*चार)\b', "Hall 4"),
        (r'\b(hall\s*(?:no\.?|number)?\s*3|h-?3|हॉल\s*(?:no\.?|नंबर)?\s*3|हॉल\s*तीन)\b', "Hall 3"),
        (r'\b(hall\s*(?:no\.?|number)?\s*2|h-?2|हॉल\s*(?:no\.?|नंबर)?\s*2|हॉल\s*दो)\b', "Hall 2"),
        (r'\b(hall\s*(?:no\.?|number)?\s*1\b|h-?1\b|हॉल\s*(?:no\.?|नंबर)?\s*1\b|हॉल\s*एक\b)', "Hall 1"),

        # Girls Hostels
        (r'\b(gh\s*tower|गर्ल्स\s*होस्टल\s*टावर)\b', "GH Tower"),
        (r'\b(gh-?1|girls\s*hostel\s*1|गर्ल्स\s*हॉस्टल|gh)\b', "Girls Hostel 1 (GH1)"),

        # Student Activity & Food (Old SAC checked BEFORE SAC)
        (r'\b(old\s*sac|पुराना\s*सैक|dosa\s*plaza|डोसा\s*प्लाजा)\b', "Old SAC / Dosa Plaza"),
        (r'\b(new\s*sac|नया\s*सैक|naughty\s*blenders?|नॉटी\s*ब्लेंडर्स?|domino\'?s?|डोमिनोज?|ccd)\b', "Naughty Blenders (New SAC)"),
        (r'\b(sac|सैक)\b', "Naughty Blenders (New SAC)"),

        # Academic & Landmarks
        (r'\b(library|kelkar|pk\s*kelkar|लाइब्रेरी|पुस्तकालय)\b', "PK Kelkar Library"),
        (r'\b(lhc|lecture\s*hall(?:\s*complex)?|एलएचसी|लेक्चर\s*हॉल)\b', "Lecture Hall Complex (LHC)"),
        (r'\b(computer\s*cent(?:re|er)|\bcc\b|कंप्यूटर\s*सेंटर)\b', "Computer Centre (CC)"),
        (r'\b(faculty\s*building|\bfb\b|फैकल्टी\s*बिल्डिंग)\b', "Faculty Building (FB)"),
        (r'\b(spase|एसपीएएसई)\b', "SPASE Department"),
        (r'\b(acms|materials\s*science)\b', "Advanced Centre for Materials Science (ACMS)"),
        (r'\b(core\s*labs?|tutorial\s*complex)\b', "Core Labs / Tutorial Complex"),
        (r'\b(airstrip|flight\s*lab|एयरस्ट्रिप|रनवे|runway)\b', "Flight Lab & Airstrip"),
        (r'\b(health\s*cent(?:re|er)|hospital|हेल्थ\s*सेंटर|अस्पताल|dispensary)\b', "Health Centre (Emergency Care)"),
        (r'\b(main\s*gate|gt\s*road|मेन\s*गेट)\b', "Main Gate (GT Road Exit)"),
        (r'\b(oat|open\s*air\s*theat(?:re|er)|ओपन\s*एयर)\b', "Open Air Theatre (OAT)"),
        (r'\b(community\s*cent(?:re|er)|shopping\s*cent(?:re|er)|मार्केट|मार्किट|market)\b', "Community Centre"),
        (r'\b(vh|visitor\'?s?\s*hostel|विजिटर्स\s*होस्टल)\b', "Visitors Hostel (VH)")
    ]

    search_corpus = f"{loc_clean} {text_clean}".lower()
    for pattern, landmark_key in patterns:
        if re.search(pattern, search_corpus, re.IGNORECASE):
            data = CAMPUS_LOCATIONS[landmark_key]
            return data["lat"], data["lon"], landmark_key

    # Safe default: center of IIT Kanpur
    return 26.5123, 80.2329, "IIT Kanpur Campus"

# Start with completely clean state (0 roadblocks, 0 circles)
if "blockages" not in st.session_state:
    st.session_state.blockages = []

# -------------------------------------------------------------
# Top Header
# -------------------------------------------------------------
st.markdown('<div class="main-title">🚲 IITK Marg-Darshak</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">IIT Kanpur Campus Transit Intelligence & Roadblock Monitor | Powered by Sarvam AI</div>', unsafe_allow_html=True)

# Connection indicator
has_key = bool(get_api_key())
if has_key:
    st.success("✅ Sarvam AI Connected")
else:
    st.warning("⚠️ Sarvam API Key missing. Please add `SARVAM_API_KEY` to your Streamlit Cloud Secrets (or local `.env`).")

# -------------------------------------------------------------
# TWO CLEAR MAIN OPTIONS IN THE BEGINNING
# -------------------------------------------------------------
action_choice = st.radio(
    "Choose what you want to do:",
    [
        "🎙️ Option 1: Inform / Report a Roadblock (Voice or Text)",
        "🧭 Option 2: Check Active Blockages & Plan Safe Route"
    ],
    horizontal=True
)

st.divider()

# =============================================================
# OPTION 1: REPORT ROADBLOCK (VOICE OR TEXT)
# =============================================================
if "Option 1" in action_choice:
    st.subheader("📢 Report a Roadblock on Campus")
    st.write("Spotted a fallen tree, waterlogging, or construction digging? Choose how you want to report:")

    input_mode = st.radio("Select input format:", ["🎙️ Audio / Voice Note (Hold & Speak)", "✍️ Text Message (Type)"], horizontal=True)

    # 1A. VOICE NOTE INPUT
    if "Audio" in input_mode:
        st.markdown("""
        **How to record in the browser:**
        * 1️⃣ Click the **microphone icon** once to start recording (do *not* hold down the mouse button).
        * 2️⃣ Speak your report in **Hindi or English** (e.g., *"हॉल 1 और लाइब्रेरी के बीच पेड़ गिर गया है"*).
        * 3️⃣ Click the **stop button (square icon)** when done speaking.
        *(Note: If your browser blocks the mic, make sure to click "Allow" on the padlock icon in the URL bar).*
        """)
        
        audio_val = st.audio_input("Record Voice Note (Click mic, speak, then click stop):")

        if audio_val is not None:
            audio_bytes = audio_val.getvalue()
            audio_hash = hash(audio_bytes)
            
            # Automatically process once when recording is stopped
            if st.session_state.get("last_processed_audio_hash") != audio_hash:
                st.session_state["last_processed_audio_hash"] = audio_hash
                st.audio(audio_val)
                client = get_sarvam_client()
                if not client:
                    st.error("SARVAM_API_KEY required in .env for live audio transcription.")
                else:
                    with st.spinner("🎙️ Audio stopped! Step 1/2: Sarvam Saaras AI transcribing your voice..."):
                        try:
                            raw_mime = getattr(audio_val, "type", "audio/wav") or "audio/wav"
                            raw_name = getattr(audio_val, "name", "voice_report.wav") or "voice_report.wav"
                            
                            stt_res = client.speech_to_text.transcribe(
                                file=(raw_name, audio_bytes, raw_mime),
                                model="saaras:v3"
                            )
                            transcript = stt_res.transcript
                            st.info(f"🗣️ **Voice Transcribed by Sarvam Saaras:** \"{transcript}\"")

                            with st.spinner("Step 2/2: Sarvam-105B extracting coordinates & formatting in Hinglish..."):
                                prompt = f"""You are the IIT Kanpur Transit Intelligence parser.
Extract the road blockage information from this voice transcript.
Select the nearest campus landmark strictly from this IIT Kanpur landmarks list:
- Hall 1, Hall 2, Hall 3, Hall 4, Hall 5, Hall 6, Hall 7, Hall 8, Hall 9, Hall 10, Hall 11, Hall 12, Hall 13
- Girls Hostel 1 (GH1), GH Tower
- Lecture Hall Complex (LHC), PK Kelkar Library, Computer Centre (CC), Faculty Building (FB), SPASE Department, Advanced Centre for Materials Science (ACMS), Core Labs / Tutorial Complex
- Naughty Blenders (New SAC), Domino's / CCD (New SAC), Old SAC / Dosa Plaza
- Health Centre (Emergency Care), Flight Lab & Airstrip, Main Gate (GT Road Exit), Open Air Theatre (OAT), Community Centre, Visitors Hostel (VH)

Transcript: "{transcript}"

Return JSON ONLY:
{{
  "segment": "Specific campus road segment (e.g., Hall 12 Road, Library Turn, New SAC link)",
  "nearest_landmark": "Exact name from the landmark list above",
  "hazard_hinglish": "Detailed hazard description in conversational Hinglish",
  "passable_cycle": false,
  "passable_foot": true,
  "advice_hinglish": "Detour advice in conversational Hinglish"
}}"""
                                res = client.chat.completions(
                                    model="sarvam-105b-conversations",
                                    messages=[{"role": "user", "content": prompt}],
                                    max_tokens=150
                                )
                                text_out = res.choices[0].message.content
                                if "```json" in text_out:
                                    text_out = text_out.split("```json")[1].split("```")[0].strip()
                                elif "```" in text_out:
                                    text_out = text_out.split("```")[1].split("```")[0].strip()

                                parsed = json.loads(text_out)
                                
                                loc_name = parsed.get("nearest_landmark", "") or parsed.get("segment", "")
                                calc_lat, calc_lon, resolved_landmark = resolve_campus_coordinates(loc_name, transcript)
                                
                                new_blk = {
                                    "id": f"BLK-{len(st.session_state.blockages)+1:03d}",
                                    "segment": parsed.get("segment", f"{resolved_landmark} Roadway"),
                                    "landmark": resolved_landmark,
                                    "hazard": parsed.get("hazard_hinglish", parsed.get("hazard", "Obstruction / Waterlogging")),
                                    "reported_by": "Voice Note (Audio)",
                                    "lat": calc_lat,
                                    "lon": calc_lon,
                                    "passable_cycle": bool(parsed.get("passable_cycle", False)),
                                    "passable_foot": bool(parsed.get("passable_foot", True)),
                                    "advice": parsed.get("advice_hinglish", parsed.get("advice", "Alternate route use karein.")),
                                    "status": "Blocked"
                                }
                                
                                st.session_state.blockages.insert(0, new_blk)
                                st.success("🎉 Voice automatically processed and added to map & Option 2 in Hinglish!")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Error processing audio: {e}")
            else:
                st.audio(audio_val)
                st.info("✅ Audio note automatically processed and added to Option 2 and map below.")

    # 1B. TEXT INPUT
    else:
        st.write("Type a brief message in **Hindi or English** describing the location and problem:")
        user_text = st.text_area(
            "Enter Roadblock Details:",
            placeholder="e.g., हॉल 1 और लाइब्रेरी मोड़ के बीच पेड़ गिर गया है और पानी भरा है, साइकिल नहीं निकल पा रही।"
        )
        
        if st.button("🚀 Process Text Report with Sarvam AI", type="primary"):
            if not user_text.strip():
                st.warning("Please enter a message before submitting.")
            else:
                client = get_sarvam_client()
                if not client:
                    st.error("SARVAM_API_KEY required in .env for live AI extraction.")
                else:
                    with st.spinner("Sarvam-105B extracting in Hinglish..."):
                        try:
                            prompt = f"""You are the IIT Kanpur Transit Intelligence parser.
Extract the road blockage information from this text note.
Select the nearest campus landmark strictly from this IIT Kanpur landmarks list:
- Hall 1, Hall 2, Hall 3, Hall 4, Hall 5, Hall 6, Hall 7, Hall 8, Hall 9, Hall 10, Hall 11, Hall 12, Hall 13
- Girls Hostel 1 (GH1), GH Tower
- Lecture Hall Complex (LHC), PK Kelkar Library, Computer Centre (CC), Faculty Building (FB), SPASE Department, Advanced Centre for Materials Science (ACMS), Core Labs / Tutorial Complex
- Naughty Blenders (New SAC), Domino's / CCD (New SAC), Old SAC / Dosa Plaza
- Health Centre (Emergency Care), Flight Lab & Airstrip, Main Gate (GT Road Exit), Open Air Theatre (OAT), Community Centre, Visitors Hostel (VH)

Note: "{user_text}"

Return JSON ONLY:
{{
  "segment": "Specific campus road segment (e.g., Hall 12 Road, Library Turn, New SAC link)",
  "nearest_landmark": "Exact name from the landmark list above",
  "hazard_hinglish": "Hazard description in natural Hinglish",
  "passable_cycle": false,
  "passable_foot": true,
  "advice_hinglish": "Detour advice in natural Hinglish"
}}"""
                            res = client.chat.completions(
                                model="sarvam-105b-conversations",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=150
                            )
                            text_out = res.choices[0].message.content
                            if "```json" in text_out:
                                text_out = text_out.split("```json")[1].split("```")[0].strip()
                            elif "```" in text_out:
                                text_out = text_out.split("```")[1].split("```")[0].strip()

                            parsed = json.loads(text_out)
                            
                            loc_name = parsed.get("nearest_landmark", "") or parsed.get("segment", "")
                            calc_lat, calc_lon, resolved_landmark = resolve_campus_coordinates(loc_name, user_text)
                            
                            new_blk = {
                                "id": f"BLK-{len(st.session_state.blockages)+1:03d}",
                                "segment": parsed.get("segment", f"{resolved_landmark} Roadway"),
                                "landmark": resolved_landmark,
                                "hazard": parsed.get("hazard_hinglish", "Obstruction"),
                                "reported_by": "Text Message",
                                "lat": calc_lat,
                                "lon": calc_lon,
                                "passable_cycle": bool(parsed.get("passable_cycle", False)),
                                "passable_foot": bool(parsed.get("passable_foot", True)),
                                "advice": parsed.get("advice_hinglish", "Alternate route use karein."),
                                "status": "Blocked"
                            }
                            
                            st.session_state.blockages.insert(0, new_blk)
                            st.success("✅ Roadblock added in Hinglish to map & Option 2!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error processing text: {e}")

# =============================================================
# OPTION 2: CHECK BLOCKAGES & PLAN SAFE ROUTE
# =============================================================
else:
    st.subheader("🧭 Check Roadblocks & Plan Safe Commute")

    # Display active reported roadblocks in Hinglish text form right here
    st.markdown("#### 📢 Currently Reported Blockages on Campus (in Hinglish):")
    if st.session_state.blockages:
        for b in st.session_state.blockages:
            st.markdown(f"""
            <div class="blockage-card">
                <div class="blockage-title">🚫 {b['segment']} &nbsp;<span class="badge-landmark">📍 {b.get('landmark', 'IITK Landmark')} ({b['lat']:.4f}, {b['lon']:.4f})</span></div>
                <div class="blockage-detail"><strong>Problem (Hinglish):</strong> {b['hazard']}</div>
                <div class="blockage-detail"><strong>Suggested Detour:</strong> {b['advice']}</div>
                <div class="blockage-meta">Cycle Passable: {'✅ Haan' if b['passable_cycle'] else '❌ Nahi'} | Foot: {'✅ Haan' if b['passable_foot'] else '❌ Nahi'} | Reported: {b['reported_by']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🟢 Abhi campus me koi bhi road blockage reported nahi hai. Sabhi raaste khule hain! (All routes currently clear).")

    st.write("---")
    st.write("#### 🚴 Check My Specific Commute Route:")
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
                st.error(f"🚫 **Hazard at {rb['segment']}**: {rb['hazard']}")
                st.caption(f"💡 Recommended Detour: {rb['advice']}")
            
            # AI Detour Generation via Sarvam-105B
            if client:
                with st.spinner("Sarvam AI calculating optimal campus detour..."):
                    try:
                        prompt = f"""You are IIT Kanpur's campus transit copilot.
Student wants to travel from: {start_point} to {destination} on {commute_mode}.
Active obstructions: {[r['segment'] + ': ' + r['hazard'] for r in relevant_blockages]}.

In 2 short sentences, provide the safest detour route using real IIT Kanpur landmarks (like Faculty Building back road, Core Labs path, or Hall 1 link)."""
                        res = client.chat.completions(
                            model="sarvam-105b-conversations",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=100
                        )
                        ai_detour = res.choices[0].message.content
                        st.success(f"🤖 **Sarvam AI Detour Advisory:**\n\n{ai_detour}")
                        
                        if st.button("🔊 Listen to Detour (Spoken Voice via Bulbul)"):
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
                                st.info("Audio broadcast available with configured TTS.")
                    except Exception as e:
                        st.info(f"AI Path suggestion: Avoid {relevant_blockages[0]['segment']}. Proceed via Faculty Building perimeter.")
            else:
                st.info(f"💡 **Suggested Alternate Path:** Avoid {relevant_blockages[0]['segment']}. Take parallel perimeter road.")

        else:
            st.markdown(f'<div class="route-safe"><h3>✅ Path Clear from {start_point} to {destination}</h3><p>No active roadblocks or waterlogging reported on this route.</p></div>', unsafe_allow_html=True)
            st.balloons()

# -------------------------------------------------------------
# IIT KANPUR MAP (ZERO DOTS/CIRCLES WHEN CLEAN)
# -------------------------------------------------------------
st.divider()
st.subheader("📍 IIT Kanpur Campus Map")

view_state = pdk.ViewState(
    latitude=26.5123,
    longitude=80.2329,
    zoom=15,
    pitch=0
)

if st.session_state.blockages:
    col_info, col_clear = st.columns([3, 1])
    with col_info:
        st.caption("🔴 Red markers indicate currently reported campus roadblocks (auto-centered on latest report):")
    with col_clear:
        if st.button("🧹 Clear All Roadblocks"):
            st.session_state.blockages = []
            st.rerun()

    # Automatically focus the map view on the latest reported blockage
    latest = st.session_state.blockages[0]
    view_state = pdk.ViewState(
        latitude=latest["lat"],
        longitude=latest["lon"],
        zoom=16,
        pitch=0
    )

    map_df = pd.DataFrame([
        {
            "lat": b["lat"],
            "lon": b["lon"],
            "name": b["segment"],
            "pin_label": f"🚫 {b.get('landmark', b['segment'])[:18]}",
            "landmark": b.get("landmark", "Campus Landmark"),
            "hazard": b["hazard"],
            "coords": f"{b['lat']:.4f}, {b['lon']:.4f}"
        }
        for b in st.session_state.blockages
    ])

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["lon", "lat"],
        get_fill_color=[220, 20, 60, 220],
        get_radius=30,
        radius_min_pixels=10,
        radius_max_pixels=25,
        pickable=True
    )

    text_layer = pdk.Layer(
        "TextLayer",
        data=map_df,
        get_position=["lon", "lat"],
        get_text="pin_label",
        get_size=13,
        get_color=[255, 255, 255, 255],
        get_angle=0,
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -14],
        background=True,
        get_background_color=[180, 20, 40, 220]
    )

    deck = pdk.Deck(
        layers=[scatter_layer, text_layer],
        initial_view_state=view_state,
        tooltip={"text": "📍 {landmark}\n🛣️ {name}\n⚠️ {hazard}\n🌐 GPS: {coords}"}
    )
    st.pydeck_chart(deck)
    
    st.write("#### 📋 Active Roadblock List:")
    for idx, b in enumerate(st.session_state.blockages):
        c_desc, c_btn = st.columns([4, 1.2])
        with c_desc:
            st.markdown(f"""
            <div class="blockage-card">
                <div class="blockage-title">🔴 {b["segment"]} &nbsp;<span class="badge-landmark">📍 {b.get('landmark', 'IITK Landmark')} ({b['lat']:.4f}, {b['lon']:.4f})</span></div>
                <div class="blockage-detail"><strong>Problem:</strong> {b["hazard"]}</div>
                <div class="blockage-detail"><strong>Detour Advice:</strong> {b["advice"]}</div>
                <div class="blockage-meta">Reported via: {b["reported_by"]}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_btn:
            st.write("")
            if st.button("✅ Mark Fixed", key=f"fix_btn_{b['id']}_{idx}", help="Click when tree removed, water drained, or road reopened"):
                st.session_state.blockages.pop(idx)
                st.success(f"Road cleared: {b['segment']}")
                st.rerun()

else:
    st.info("🟢 No roadblocks reported yet. All campus roads are currently clear.")
    # Clean map with ZERO circles or dots
    deck_clean = pdk.Deck(
        layers=[],
        initial_view_state=view_state
    )
    st.pydeck_chart(deck_clean)
