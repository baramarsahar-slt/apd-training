import streamlit as st
import random
import edge_tts
import asyncio
import io
import pandas as pd

# --- UI Text & Localization ---
UI_TEXT = {
    "en": {
        "title": "🎧 APD Training - Speech in Noise",
        "config_header": "⚙️ Configuration",
        "mode_label": "Select Training Mode:",
        "mode_instructions": "1. Instruction Following",
        "mode_sequencing": "2. Auditory Memory (Sequencing)",
        "mode_summarization": "3. Essence Extraction (SVO)",
        "mode_chronology": "4. Chronological Ordering", # New
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
        "chrono_markers_header": "Time/Logic Markers:", # New
        "chrono_order_header": "Correct Execution Order:", # New
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
        "mode_chronology": "4. סידור כרונולוגי (סדר פעולות)", # New
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
        "chrono_markers_header": "מילות קישור וזמן:", # New
        "chrono_order_header": "סדר הפעולות הנכון:", # New
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "כוון ווליום רעש בנגן למטה.",
        "listen_caption": "כוון ווליום דובר בנגן למעלה.",
        "table_cols": ["מספר", "סוג אימון", "רמה/קושי", "תוצאה"]
    }
}

# --- Data: Sequencing & SVO (Existing) ---
SEQUENCING_VOCAB = ["Cat", "Dog", "Tiger", "Lion", "Elephant", "Kangaroo", "Armadillo", "Rhinoceros", "Bed", "Chair", "Table", "Sofa", "Cabinet", "Recliner", "Ottoman", "Armoire", "Car", "Bus", "Tractor", "Rocket", "Bicycle", "Ambulance", "Helicopter", "Motorcycle", "Bread", "Pear", "Apple", "Pizza", "Spaghetti", "Banana", "Cauliflower", "Watermelon", "Ring", "Watch", "Necklace", "Earring", "Bracelet", "Medallion", "Amulet", "Tiara", "Lamp", "Fan", "Blender", "Toaster", "Microwave", "Dishwasher", "Television", "Humidifier"]
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

# --- Data: Chronological Ordering (New) ---
CHRONO_DATA = {
    "en": {
        "Easy": [
            {"text": "Before you leave the room, turn off the lights.", "markers": "Before", "order": "1. Turn off lights\n2. Leave room"},
            {"text": "After you finish reading, close the book.", "markers": "After", "order": "1. Finish reading\n2. Close book"},
            {"text": "While you wait for the bus, check the schedule.", "markers": "While", "order": "Check schedule + Wait (Simultaneous)"},
            {"text": "Do not open the package before you verify the sender.", "markers": "Before (Not)", "order": "1. Verify sender\n2. Open package"},
            {"text": "Make sure to wash your hands after you touch the dog.", "markers": "After", "order": "1. Touch dog\n2. Wash hands"}
        ],
        "Hard": [
            {"text": "Before you submit the report, check the spelling, but only after you have saved the file.", "markers": "Before, After", "order": "1. Save file\n2. Check spelling\n3. Submit report"},
            {"text": "After you unlock the door, turn off the alarm before taking off your shoes.", "markers": "After, Before", "order": "1. Unlock door\n2. Turn off alarm\n3. Take off shoes"},
            {"text": "Don't eat the cake before you blow out the candles, which happens after we sing happy birthday.", "markers": "Before, After", "order": "1. Sing happy birthday\n2. Blow candles\n3. Eat cake"},
            {"text": "While the water is boiling, chop the vegetables, and then add the spices.", "markers": "While, Then", "order": "1. Boil water + Chop vegetables\n2. Add spices"}
        ]
    },
    "he": {
        "Easy": [
            {"text_m": "לפני שאתה נכנס לחדר, כבה את הטלפון.", "text_f": "לפני שאת נכנסת לחדר, כבי את הטלפון.", "markers": "לפני", "order": "1. לכבות טלפון\n2. להיכנס לחדר"},
            {"text_m": "אחרי שתסיים לקרוא, תייק את המסמך.", "text_f": "אחרי שתסיימי לקרוא, תייקי את המסמך.", "markers": "אחרי", "order": "1. לקרוא\n2. לתייק"},
            {"text_m": "בזמן שאתה מחכה למחשב, הכן דף ועט.", "text_f": "בזמן שאת מחכה למחשב, הכיני דף ועט.", "markers": "בזמן ש...", "order": "להמתין + להכין דף (בו זמנית)"},
            {"text_m": "אל תענה על השאלון לפני שקראת את ההוראות.", "text_f": "אל תעני על השאלון לפני שקראת את ההוראות.", "markers": "לפני (שלילה)", "order": "1. לקרוא הוראות\n2. לענות על שאלון"},
            {"text_m": "רק אחרי שתבדוק את הנתונים, תסיק מסקנות.", "text_f": "רק אחרי שתבדקי את הנתונים, תסיקי מסקנות.", "markers": "אחרי", "order": "1. לבדוק נתונים\n2. להסיק מסקנות"}
        ],
        "Hard": [
            {"text_m": "לפני שתגיש את המטלה, וודא שהוספת מקורות, אך עשה זאת אחרי שתעבור על הכתיב.", "text_f": "לפני שתגישי את המטלה, וודאי שהוספת מקורות, אך עשי זאת אחרי שתעברי על הכתיב.", "markers": "לפני, אחרי", "order": "1. לעבור על כתיב\n2. לוודא מקורות\n3. להגיש מטלה"},
            {"text_m": "אחרי שתצא מהפגישה, שלח סיכום, אבל לפני כן התקשר למנהל.", "text_f": "אחרי שתצאי מהפגישה, שלחי סיכום, אבל לפני כן התקשרי למנהל.", "markers": "אחרי, לפני", "order": "1. לצאת מפגישה\n2. להתקשר למנהל\n3. לשלוח סיכום"},
            {"text_m": "בזמן שהקובץ יורד, פתח את המייל, ולאחר מכן שמור את הקובץ בתיקייה.", "text_f": "בזמן שהקובץ יורד, פתחי את המייל, ולאחר מכן שמרי את הקובץ בתיקייה.", "markers": "בזמן ש..., לאחר מכן", "order": "1. הורדה + פתיחת מייל\n2. שמירה בתיקייה"},
            {"text_m": "אל תצא להפסקה לפני שסיימת את הדו\"ח, שאותו עליך להתחיל אחרי השיחה.", "text_f": "אל תצאי להפסקה לפני שסיימת את הדו\"ח, שאותו עליך להתחיל אחרי השיחה.", "markers": "לפני (שלילה), אחרי", "order": "1. שיחה\n2. כתיבת דו\"ח\n3. יציאה להפסקה"}
        ]
    }
}

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
        return txt, txt, "", "", ""

    def gen_seq(self, length, voice_id):
        words = random.sample(SEQUENCING_VOCAB, length)
        display = ", ".join(words)
        audio = f"<speak><prosody rate='-10%'>{''.join([f'{w} <break time=\"1000ms\"/>' for w in words])}</prosody></speak>"
        return display, audio, "", "", ""

    def gen_svo(self, complexity):
        item = random.choice(SVO_TEMPLATES)
        if complexity == "Easy": full = f"{item['subj']}, {item['c1']}, {item['verb_full']}."
        else:
            if random.random() > 0.5: full = f"{item['c2']}, {item['subj']}, {item['c1']}, {item['verb_full']}."
            else: full = f"{item['subj']}, {item['c1']}, {item['verb_full']}, {item['c2']}."
        summary = f"{item['core_subj']} {item['core_verb']}."
        return full, full, summary, "", ""

    # --- Mode 4: Chronology (New) ---
    def gen_chrono(self, complexity):
        # Select data based on language and complexity
        pool = CHRONO_DATA[self.lang][complexity]
        item = random.choice(pool)
        
        # Handle gender for Hebrew text selection
        if self.lang == "he":
            full_text = item["text_m"] if self.gender == "Male" else item["text_f"]
        else:
            full_text = item["text"]
            
        return full_text, full_text, "", item["markers"], item["order"]

async def _play(text, voice, rate="+0%"):
    if text.startswith("<speak"): comm = edge_tts.Communicate(text, voice)
    else: comm = edge_tts.Communicate(text, voice, rate=rate)
    fp = io.BytesIO()
    async for chunk in comm.stream():
        if chunk["type"] == "audio": fp.write(chunk["data"])
    return fp.getvalue()

def update_history(mode, level, is_correct):
    res_symbol = "✅" if is_correct else "❌"
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
    if 'markers' not in st.session_state: st.session_state.markers = ""
    if 'order' not in st.session_state: st.session_state.order = ""
    if 'revealed' not in st.session_state: st.session_state.revealed = False
    if 'score' not in st.session_state: st.session_state.score = 0
    if 'total' not in st.session_state: st.session_state.total = 0
    if 'history' not in st.session_state: st.session_state.history = []
    
    # Store current config
    if 'curr_mode' not in st.session_state: st.session_state.curr_mode = ""
    if 'curr_level' not in st.session_state: st.session_state.curr_level = ""

    with st.sidebar:
        st.header(txt["config_header"])
        mode = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"], txt["mode_summarization"], txt["mode_chronology"]])
        st.markdown("---")
        g_sel = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        v_sel = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        v_id = ("en-US-AriaNeural" if v_sel == "Female" else "en-US-GuyNeural") if lang == "en" else ("he-IL-HilaNeural" if v_sel == "Female" else "he-IL-AvriNeural")
        
        level_desc = ""
        # UI Control Logic
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
            
        elif mode == txt["mode_chronology"]:
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
            level_desc = f"{comp}"
        
        st.markdown("---")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # Main Play Button
    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, "Male" if g_sel in ["אתה", "Male"] else "Female")
        
        # Generator Routing
        if mode == txt["mode_instructions"]: 
            d, a, s, m, o = gen.gen_instr(inv, steps, comp)
            r = "+0%"
        elif mode == txt["mode_sequencing"]: 
            d, a, s, m, o = gen.gen_seq(seq_l, v_id)
            r = "-10%"
        elif mode == txt["mode_summarization"]: 
            d, a, s, m, o = gen.gen_svo(comp)
            r = "+0%"
        else: # Chronology
            d, a, s, m, o = gen.gen_chrono(comp)
            r = "+0%"
        
        # Save State
        st.session_state.display = d
        st.session_state.summary = s
        st.session_state.markers = m
        st.session_state.order = o
        st.session_state.revealed = False
        st.session_state.curr_mode = mode.split(".")[1].strip()
        st.session_state.curr_level = level_desc
        
        with st.spinner("..."): st.session_state.audio = asyncio.run(_play(a, v_id, r))

    if st.session_state.audio: st.audio(st.session_state.audio)

    # Feedback Section
    if st.session_state.display:
        st.markdown("---")
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]): st.session_state.revealed = True; st.rerun()
        else:
            # 1. Full Sentence
            st.write(f"**{txt['instr_header']}**")
            st.info(st.session_state.display)
            
            # 2. Specific Feedback per Mode
            if st.session_state.summary: # SVO
                st.write(f"**{txt['summary_header']}**")
                st.success(st.session_state.summary)
                
            if st.session_state.markers: # Chronology
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**{txt['chrono_markers_header']}**")
                    st.warning(st.session_state.markers)
                with c2:
                    st.write(f"**{txt['chrono_order_header']}**")
                    st.success(st.session_state.order)
            
            # 3. Grading
            c1, c2, _ = st.columns([1,1,3])
            if c1.button(txt["correct_btn"]):
                st.session_state.score += 1
                st.session_state.total += 1
                update_history(st.session_state.curr_mode, st.session_state.curr_level, True)
                st.session_state.display = ""; st.session_state.audio = None; st.rerun()
                
            if c2.button(txt["incorrect_btn"]):
                st.session_state.total += 1
                update_history(st.session_state.curr_mode, st.session_state.curr_level, False)
                st.session_state.display = ""; st.session_state.audio = None; st.rerun()

    # Score & History
    st.markdown("---")
    st.metric(txt["score_label"], f"{st.session_state.score} / {st.session_state.total}")
    
    if st.session_state.history:
        st.subheader(txt["history_label"])
        df = pd.DataFrame(st.session_state.history)
        df.columns = txt["table_cols"][1:] 
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
        
        if st.button(txt["clear_history"]):
            st.session_state.history = []
            st.session_state.score = 0; st.session_state.total = 0; st.rerun()

if __name__ == "__main__":
    main()
