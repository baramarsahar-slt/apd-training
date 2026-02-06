import streamlit as st
import random
import edge_tts
import asyncio
import io

# --- UI Text & Localization ---
UI_TEXT = {
    "en": {
        "title": "🎧 APD Training - Speech in Noise",
        "config_header": "⚙️ Configuration",
        "mode_label": "Select Training Mode:",
        "mode_instructions": "1. Instruction Following",
        "mode_sequencing": "2. Auditory Memory (Sequencing)",
        "mode_summarization": "3. Essence Extraction (SVO)",
        "trainee_gender_label": "Trainee Gender (for grammar):",
        "trainee_gender_opts": ["Male", "Female"],
        "voice_gender": "Voice Speaker Gender:",
        "inventory_label": "My Objects (for Instructions):",
        "steps_label": "Steps:",
        "seq_length_label": "Sequence Length:",
        "complexity_label": "Complexity:",
        "play_btn": "▶ PLAY",
        "reveal_btn": "👁 Reveal Text",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Session Score",
        "instr_header": "Full Sentence:",
        "summary_header": "Essential Essence (SVO):",
        "noise_header": "🔊 Background Noise",
        "noise_caption": "Adjust noise volume in the player below.",
        "listen_caption": "Adjust voice volume in the black player above."
    },
    "he": {
        "title": "🎧 אימון עיבוד שמיעתי - דיבור ברעש",
        "config_header": "⚙️ הגדרות אימון",
        "mode_label": "בחר סוג אימון:",
        "mode_instructions": "1. ביצוע הוראות",
        "mode_sequencing": "2. זיכרון שמיעתי (רצף)",
        "mode_summarization": "3. תמצות עיקר המשפט (SVO)",
        "trainee_gender_label": "באיזו דרך לפנות?",
        "trainee_gender_opts": ["אתה", "את"],
        "voice_gender": "קול הדובר:",
        "inventory_label": "רשימת חפצים:",
        "steps_label": "שלבים:",
        "seq_length_label": "אורך רצף:",
        "complexity_label": "רמת קושי:",
        "play_btn": "▶ השמע",
        "reveal_btn": "👁 חשוף טקסט",
        "correct_btn": "✔ הצלחתי",
        "incorrect_btn": "✖ טעיתי",
        "score_label": "ניקוד",
        "instr_header": "המשפט המלא:",
        "summary_header": "תמצית המשפט (SVO):",
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "כוון ווליום רעש בנגן למטה.",
        "listen_caption": "כוון ווליום דובר בנגן למעלה."
    }
}

# --- Data: Sequencing ---
SEQUENCING_VOCAB = ["Cat", "Dog", "Tiger", "Lion", "Elephant", "Kangaroo", "Armadillo", "Rhinoceros", "Bed", "Chair", "Table", "Sofa", "Cabinet", "Recliner", "Ottoman", "Armoire", "Car", "Bus", "Tractor", "Rocket", "Bicycle", "Ambulance", "Helicopter", "Motorcycle", "Bread", "Pear", "Apple", "Pizza", "Spaghetti", "Banana", "Cauliflower", "Watermelon", "Ring", "Watch", "Necklace", "Earring", "Bracelet", "Medallion", "Amulet", "Tiara", "Lamp", "Fan", "Blender", "Toaster", "Microwave", "Dishwasher", "Television", "Humidifier"]

# --- Data: Summarization (SVO) with Complexity ---
# Each template has: Core (Subject+Verb), Clause1 (Easy distractor), Clause2 (Hard distractor)
SVO_TEMPLATES = [
    {
        "subj": "The hungry cat", "verb_full": "jumped over the wall", "core_subj": "The cat", "core_verb": "jumped",
        "c1": "which sat on the fence", 
        "c2": "despite being chased by the dog"
    },
    {
        "subj": "The manager", "verb_full": "approved the request", "core_subj": "The manager", "core_verb": "approved the request",
        "c1": "after reviewing all the files", 
        "c2": "although it was late in the day"
    },
    {
        "subj": "The software update", "verb_full": "was finally released", "core_subj": "The update", "core_verb": "was released",
        "c1": "which was delayed for months", 
        "c2": "due to critical technical errors"
    },
    {
        "subj": "Dr. Smith", "verb_full": "presented his new theory", "core_subj": "Dr. Smith", "core_verb": "presented his theory",
        "c1": "a leading expert in linguistics", 
        "c2": "at the international conference in Paris"
    },
    {
        "subj": "The experiment results", "verb_full": "proved the hypothesis", "core_subj": "The results", "core_verb": "proved the hypothesis",
        "c1": "despite being unexpected", 
        "c2": "which were collected over five years"
    },
    {
        "subj": "The young pilot", "verb_full": "landed the plane safely", "core_subj": "The pilot", "core_verb": "landed the plane",
        "c1": "who was exhausted from the flight", 
        "c2": "amidst the heavy storm and strong winds"
    },
    {
        "subj": "The gardener", "verb_full": "planted the roses", "core_subj": "The gardener", "core_verb": "planted roses",
        "c1": "working under the hot sun", 
        "c2": "before the rain started to fall"
    },
    {
        "subj": "The teacher", "verb_full": "explained the lesson", "core_subj": "The teacher", "core_verb": "explained the lesson",
        "c1": "who noticed the students were confused", 
        "c2": "using a new digital whiteboard"
    }
]

class TrainingGenerator:
    def __init__(self, lang, gender):
        self.lang = lang
        self.gender = gender

    # --- Mode 1: Instructions ---
    def gen_instr(self, inv, steps, comp):
        objs = [x.strip() for x in inv.split(",") if x.strip()] or ["pen", "cup"]
        acts = ["put the {obj} in the box", "touch the {obj}", "lift the {obj}"] if self.lang == "en" else [("שים את", "שימי את", "בקופסה"), ("גע ב", "געי ב", ""), ("הרם את", "הרימי את", "")]
        res = []
        for _ in range(steps):
            o = random.choice(objs)
            if self.lang == "en": 
                if comp == "Hard":
                     # Add distractor logic for hard instructions
                     dist = random.choice(objs)
                     res.append(f"Before you touch the {o}, touch the {dist}")
                else:
                    res.append(random.choice(acts).format(obj=o))
            else: # Hebrew
                a = random.choice(acts)
                v = a[0] if self.gender == "Male" else a[1]
                if comp == "Hard":
                    dist = random.choice(objs)
                    pre = "לפני שאתה" if self.gender == "Male" else "לפני שאת"
                    res.append(f"{pre} נוגע ב{o}, גע ב{dist}")
                else:
                    res.append(f"{v} {o} {a[2]}".strip())
        
        txt = ". ".join(res) + "."
        return txt, txt, ""

    # --- Mode 2: Sequencing ---
    def gen_seq(self, length, voice_id):
        words = random.sample(SEQUENCING_VOCAB, length)
        display = ", ".join(words)
        # Using SSML with pause
        audio = f"<speak><prosody rate='-10%'>{''.join([f'{w} <break time=\"1000ms\"/>' for w in words])}</prosody></speak>"
        return display, audio, ""

    # --- Mode 3: Summarization (SVO) ---
    def gen_svo(self, complexity):
        item = random.choice(SVO_TEMPLATES)
        
        # Easy: Subject + Clause1 + Verb
        if complexity == "Easy":
            full = f"{item['subj']}, {item['c1']}, {item['verb_full']}."
            
        # Hard: Clause2 + Subject + Clause1 + Verb (Double interruption)
        else:
            # Randomly place the second clause at start or end for variety
            if random.random() > 0.5:
                full = f"{item['c2']}, {item['subj']}, {item['c1']}, {item['verb_full']}."
            else:
                full = f"{item['subj']}, {item['c1']}, {item['verb_full']}, {item['c2']}."

        summary = f"{item['core_subj']} {item['core_verb']}."
        return full, full, summary

# --- Audio Engine ---
async def _play(text, voice, rate="+0%"):
    # If text is SSML (sequencing), use it directly. Otherwise apply rate.
    if text.startswith("<speak"): 
        comm = edge_tts.Communicate(text, voice)
    else: 
        comm = edge_tts.Communicate(text, voice, rate=rate)
    
    fp = io.BytesIO()
    async for chunk in comm.stream():
        if chunk["type"] == "audio": fp.write(chunk["data"])
    return fp.getvalue()

def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    lang_code = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
    lang = "en" if lang_code == "English" else "he"
    txt = UI_TEXT[lang]

    if 'audio' not in st.session_state: st.session_state.audio = None
    if 'display' not in st.session_state: st.session_state.display = ""
    if 'summary' not in st.session_state: st.session_state.summary = ""
    if 'revealed' not in st.session_state: st.session_state.revealed = False

    with st.sidebar:
        st.header(txt["config_header"])
        mode = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"], txt["mode_summarization"]])
        st.markdown("---")
        g_sel = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        v_sel = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        v_id = ("en-US-AriaNeural" if v_sel == "Female" else "en-US-GuyNeural") if lang == "en" else ("he-IL-HilaNeural" if v_sel == "Female" else "he-IL-AvriNeural")
        
        # UI Logic for controls
        if mode == txt["mode_instructions"]:
            inv = st.text_area(txt["inventory_label"], value="red pen, blue pen, eraser" if lang == "en" else "עט, מחק", height=100)
            steps = st.selectbox(txt["steps_label"], [1, 2, 3])
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
        
        elif mode == txt["mode_sequencing"]:
            seq_l = st.slider(txt["seq_length_label"], 3, 8, 4)
            
        elif mode == txt["mode_summarization"]:
            # Show complexity also for Summarization
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
        
        st.markdown("---")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, "Male" if g_sel in ["אתה", "Male"] else "Female")
        
        if mode == txt["mode_instructions"]: 
            d, a, s = gen.gen_instr(inv, steps, comp)
            r = "+0%"
        elif mode == txt["mode_sequencing"]: 
            d, a, s = gen.gen_seq(seq_l, v_id)
            r = "-10%" # Rate is ignored for SSML but kept for variable consistency
        else: # Summarization
            d, a, s = gen.gen_svo(comp) # Pass complexity
            r = "+0%"
        
        st.session_state.display, st.session_state.summary, st.session_state.revealed = d, s, False
        with st.spinner("..."): st.session_state.audio = asyncio.run(_play(a, v_id, r))

    if st.session_state.audio: st.audio(st.session_state.audio)

    if st.session_state.display:
        st.markdown("---")
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]): st.session_state.revealed = True; st.rerun()
        else:
            st.write(f"**{txt['instr_header']}**")
            st.info(st.session_state.display)
            if st.session_state.summary:
                st.write(f"**{txt['summary_header']}**")
                st.success(st.session_state.summary)
            c1, c2, _ = st.columns([1,1,3])
            if c1.button(txt["correct_btn"]): st.session_state.display = ""; st.session_state.audio = None; st.rerun()
            if c2.button(txt["incorrect_btn"]): st.session_state.display = ""; st.session_state.audio = None; st.rerun()

if __name__ == "__main__":
    main()
