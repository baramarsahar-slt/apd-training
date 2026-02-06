import streamlit as st
import random
import edge_tts
import asyncio
import io
import pandas as pd # נדרש עבור טבלת המעקב

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
        "history_label": "Training Log (Current Session):",
        "clear_history": "🗑️ Clear Log",
        "instr_header": "Full Sentence:",
        "summary_header": "Essential Essence (SVO):",
        "noise_header": "🔊 Background Noise",
        "noise_caption": "Adjust noise volume in the player below.",
        "listen_caption": "Adjust voice volume in the black player above.",
        "table_cols": ["Time", "Mode", "Level", "Result"]
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
        "score_label": "ניקוד מצטבר",
        "history_label": "תיעוד ביצועים (סשן נוכחי):",
        "clear_history": "🗑️ נקה היסטוריה",
        "instr_header": "המשפט המלא:",
        "summary_header": "תמצית המשפט (SVO):",
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "כוון ווליום רעש בנגן למטה.",
        "listen_caption": "כוון ווליום דובר בנגן למעלה.",
        "table_cols": ["מספר", "סוג אימון", "רמה/קושי", "תוצאה"]
    }
}

# --- Data: Sequencing ---
SEQUENCING_VOCAB = ["Cat", "Dog", "Tiger", "Lion", "Elephant", "Kangaroo", "Armadillo", "Rhinoceros", "Bed", "Chair", "Table", "Sofa", "Cabinet", "Recliner", "Ottoman", "Armoire", "Car", "Bus", "Tractor", "Rocket", "Bicycle", "Ambulance", "Helicopter", "Motorcycle", "Bread", "Pear", "Apple", "Pizza", "Spaghetti", "Banana", "Cauliflower", "Watermelon", "Ring", "Watch", "Necklace", "Earring", "Bracelet", "Medallion", "Amulet", "Tiara", "Lamp", "Fan", "Blender", "Toaster", "Microwave", "Dishwasher", "Television", "Humidifier"]

# --- Data: Summarization (SVO) ---
SVO_TEMPLATES = [
    {"subj": "The hungry cat", "verb_full": "jumped over the wall", "core_subj": "The cat", "core_verb": "jumped", "c1": "which sat on the fence", "c2": "despite being chased by the dog"},
    {"subj": "The manager", "verb_full": "approved the request", "core_subj": "The manager", "core_verb": "approved the request", "c1": "after reviewing all the files", "c2": "although it was late in the day"},
    {"subj": "The software update", "verb_full": "was finally released", "core_subj": "The update", "core_verb": "was released", "c1": "which was delayed for months", "c2": "due to critical technical errors"},
    {"subj": "Dr. Smith", "verb_full": "presented his new theory", "core_subj": "Dr. Smith", "core_verb": "presented his theory", "c1": "a leading expert in linguistics", "c2": "at the international conference in Paris"},
    {"subj": "The experiment results", "verb_full": "proved the hypothesis", "core_subj": "The results", "core_verb": "proved the hypothesis", "c1": "despite being unexpected", "c2": "which were collected over five years"},
    {"subj": "The young pilot", "verb_full": "landed the plane safely", "core_subj": "The pilot", "core_verb": "landed the plane", "c1": "who was exhausted from the flight", "c2": "amidst the heavy storm and strong winds"},
    {"subj": "The gardener", "verb_full": "planted the roses", "core_subj": "The gardener", "core_verb": "planted roses", "c1": "working under the hot sun", "c2": "before the rain started to fall"},
    {"subj": "The teacher", "verb_full": "explained the lesson", "core_subj": "The teacher", "core_verb": "explained the lesson", "c1": "who noticed the students were confused", "c2": "using a new digital whiteboard"}
]

class TrainingGenerator:
    def __init__(self, lang, gender):
        self.lang = lang
        self.gender = gender

    def gen_instr(self, inv, steps, comp):
        objs = [x.strip() for x in inv.split(",") if x.strip()] or ["pen", "cup"]
        acts = ["put the {obj} in the box", "touch the {obj}", "lift the {obj}"] if self.lang == "en" else [("שים את", "שימי את", "בקופסה"), ("גע ב", "געי ב", ""), ("הרם את", "הרימי את", "")]
        res = []
        for _ in range(steps):
            o = random.choice(objs)
            if self.lang == "en": 
                if comp == "Hard":
                     dist = random.choice(objs)
                     res.append(f"Before you touch the {o}, touch the {dist}")
                else:
                    res.append(random.choice(acts).format(obj=o))
            else:
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

    def gen_seq(self, length, voice_id):
        words = random.sample(SEQUENCING_VOCAB, length)
        display = ", ".join(words)
        audio = f"<speak><prosody rate='-10%'>{''.join([f'{w} <break time=\"1000ms\"/>' for w in words])}</prosody></speak>"
        return display, audio, ""

    def gen_svo(self, complexity):
        item = random.choice(SVO_TEMPLATES)
        if complexity == "Easy": full = f"{item['subj']}, {item['c1']}, {item['verb_full']}."
        else:
            if random.random() > 0.5: full = f"{item['c2']}, {item['subj']}, {item['c1']}, {item['verb_full']}."
            else: full = f"{item['subj']}, {item['c1']}, {item['verb_full']}, {item['c2']}."
        summary = f"{item['core_subj']} {item['core_verb']}."
        return full, full, summary

async def _play(text, voice, rate="+0%"):
    if text.startswith("<speak"): comm = edge_tts.Communicate(text, voice)
    else: comm = edge_tts.Communicate(text, voice, rate=rate)
    fp = io.BytesIO()
    async for chunk in comm.stream():
        if chunk["type"] == "audio": fp.write(chunk["data"])
    return fp.getvalue()

def update_history(mode, level, is_correct):
    res_symbol = "✅" if is_correct else "❌"
    # Store simple dictionary
    st.session_state.history.append({
        "mode": mode,
        "level": level,
        "result": res_symbol
    })

def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    lang_code = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)
    lang = "en" if lang_code == "English" else "he"
    txt = UI_TEXT[lang]

    # Initialize State
    if 'audio' not in st.session_state: st.session_state.audio = None
    if 'display' not in st.session_state: st.session_state.display = ""
    if 'summary' not in st.session_state: st.session_state.summary = ""
    if 'revealed' not in st.session_state: st.session_state.revealed = False
    if 'score' not in st.session_state: st.session_state.score = 0
    if 'total' not in st.session_state: st.session_state.total = 0
    if 'history' not in st.session_state: st.session_state.history = []
    
    # Store current config to log later
    if 'curr_mode' not in st.session_state: st.session_state.curr_mode = ""
    if 'curr_level' not in st.session_state: st.session_state.curr_level = ""

    with st.sidebar:
        st.header(txt["config_header"])
        mode = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"], txt["mode_summarization"]])
        st.markdown("---")
        g_sel = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        v_sel = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        v_id = ("en-US-AriaNeural" if v_sel == "Female" else "en-US-GuyNeural") if lang == "en" else ("he-IL-HilaNeural" if v_sel == "Female" else "he-IL-AvriNeural")
        
        level_desc = ""
        if mode == txt["mode_instructions"]:
            inv = st.text_area(txt["inventory_label"], value="red pen, blue pen, eraser" if lang == "en" else "עט, מחק", height=100)
            steps = st.selectbox(txt["steps_label"], [1, 2, 3])
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
            level_desc = f"{steps} Steps, {comp}"
        elif mode == txt["mode_sequencing"]:
            seq_l = st.slider(txt["seq_length_label"], 3, 8, 4)
            level_desc = f"{seq_l} Items"
        elif mode == txt["mode_summarization"]:
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
            level_desc = f"{comp}"
        
        st.markdown("---")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # Main Play Button
    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, "Male" if g_sel in ["אתה", "Male"] else "Female")
        
        if mode == txt["mode_instructions"]: 
            d, a, s = gen.gen_instr(inv, steps, comp)
            r = "+0%"
        elif mode == txt["mode_sequencing"]: 
            d, a, s = gen.gen_seq(seq_l, v_id)
            r = "-10%"
        else: 
            d, a, s = gen.gen_svo(comp)
            r = "+0%"
        
        st.session_state.display, st.session_state.summary, st.session_state.revealed = d, s, False
        # Save context for logging
        st.session_state.curr_mode = mode.split(".")[1].strip() # Clean name
        st.session_state.curr_level = level_desc
        
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
            
            # Button Logic with Logging
            if c1.button(txt["correct_btn"]):
                st.session_state.score += 1
                st.session_state.total += 1
                update_history(st.session_state.curr_mode, st.session_state.curr_level, True)
                st.session_state.display = ""; st.session_state.audio = None
                st.rerun()
                
            if c2.button(txt["incorrect_btn"]):
                st.session_state.total += 1
                update_history(st.session_state.curr_mode, st.session_state.curr_level, False)
                st.session_state.display = ""; st.session_state.audio = None
                st.rerun()

    # --- Score & History Section ---
    st.markdown("---")
    st.metric(txt["score_label"], f"{st.session_state.score} / {st.session_state.total}")
    
    if st.session_state.history:
        st.subheader(txt["history_label"])
        # Create DataFrame for nice display
        df = pd.DataFrame(st.session_state.history)
        # Rename columns for display based on language
        df.columns = txt["table_cols"][1:] # Skip 'Time' or Number, just use Mode/Level/Result
        
        # Add index + 1 to show trial number
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
        
        if st.button(txt["clear_history"]):
            st.session_state.history = []
            st.session_state.score = 0
            st.session_state.total = 0
            st.rerun()

if __name__ == "__main__":
    main()
