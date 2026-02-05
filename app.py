import streamlit as st
import random
import edge_tts
import asyncio
import io

# --- מילונים ושפות (UI Text) ---
UI_TEXT = {
    "en": {
        "title": "🎧 APD Training - Speech in Noise",
        "config_header": "⚙️ Configuration",
        "lang_select": "Interface Language / שפת ממשק",
        "trainee_gender_label": "Trainee Gender (for grammar):",
        "trainee_gender_opts": ["Male", "Female"],
        "voice_gender": "Voice Speaker Gender:",
        "mode_label": "Select Training Mode:",
        "mode_instructions": "1. Instruction Following",
        "mode_sequencing": "2. Auditory Memory (Sequencing)",
        "inventory_label": "My Objects:",
        "steps_label": "Steps (Commands):",
        "seq_length_label": "Sequence Length (Items):",
        "complexity_label": "Complexity:",
        "play_btn": "▶ PLAY",
        "reveal_btn": "👁 Reveal Text",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Session Score",
        "instr_header": "Content:",
        "guide_expander": "ℹ️ Instructions Guide",
        "guide_text": "Enter items separated by commas.",
        "noise_header": "🔊 Background Noise",
        "noise_caption": "Use the video player volume to adjust noise level.",
        "listen_caption": "Tip: Use the volume button on the player above to adjust voice volume."
    },
    "he": {
        "title": "🎧 אימון עיבוד שמיעתי - דיבור ברעש",
        "config_header": "⚙️ הגדרות אימון",
        "lang_select": "שפת אימון",
        "trainee_gender_label": "באיזו דרך לפנות עם הוראות בשפה העברית?",
        "trainee_gender_opts": ["אתה", "את"],
        "voice_gender": "קול הדובר (קריין):",
        "mode_label": "בחר סוג אימון:",
        "mode_instructions": "1. ביצוע הוראות עם חפצים",
        "mode_sequencing": "2. זיכרון שמיעתי (רצף מילים)",
        "inventory_label": "רשימת החפצים שלי (לאימון הוראות):",
        "steps_label": "מספר שלבים (הוראות):",
        "seq_length_label": "אורך הרצף (מספר מילים):",
        "complexity_label": "רמת קושי:",
        "play_btn": "▶ השמע תרגיל",
        "reveal_btn": "👁 חשוף טקסט (בדיקה)",
        "correct_btn": "✔ הצלחתי",
        "incorrect_btn": "✖ טעיתי",
        "score_label": "ניקוד בסשן הנוכחי",
        "instr_header": "התוכן שהושמע:",
        "guide_expander": "ℹ️ מדריך לכתיבת חפצים",
        "guide_text": "**לאימון הוראות:** מומלץ לכתוב: 'עט אדום, עט כחול, מחק גדול'.",
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "יש להפעיל את הסרטון ולכוון את עוצמת הרעש דרך הנגן.",
        "listen_caption": "טיפ: ניתן לשלוט בעוצמת הקול של הדובר דרך הנגן השחור למעלה."
    }
}

# --- מאגר 50 מילים לאימון זיכרון ---
SEQUENCING_VOCAB_EN = [
    "Cat", "Dog", "Tiger", "Lion", "Elephant", "Kangaroo", "Armadillo", "Rhinoceros",
    "Bed", "Chair", "Table", "Sofa", "Cabinet", "Recliner", "Ottoman", "Armoire",
    "Car", "Bus", "Tractor", "Rocket", "Bicycle", "Ambulance", "Helicopter", "Motorcycle",
    "Bread", "Pear", "Apple", "Pizza", "Spaghetti", "Banana", "Cauliflower", "Watermelon",
    "Ring", "Watch", "Necklace", "Earring", "Bracelet", "Medallion", "Amulet", "Tiara",
    "Lamp", "Fan", "Blender", "Toaster", "Microwave", "Dishwasher", "Television", "Humidifier"
]

class TrainingGenerator:
    def __init__(self, language="en", trainee_gender="Male"):
        self.language = language
        self.trainee_gender = trainee_gender 

    def get_clean_list(self, user_input):
        items = [x.strip() for x in user_input.split(",") if x.strip()]
        if not items:
            return ["red pen", "blue pen", "pencil", "notebook", "keys", "cup"] if self.language == "en" else ["עט אדום", "עט כחול", "מחק", "מחברת"]
        return items

    def _hebrew_grammar_fix(self, action_template, obj_str):
        cmd = action_template[0] if self.trainee_gender == "Male" else action_template[1]
        suffix = action_template[2]
        return f"{cmd} {obj_str} {suffix}".strip()

    # --- Mode 1: Instructions ---
    def generate_instruction(self, objects_input, steps, complexity):
        objects_list = self.get_clean_list(objects_input)
        instructions = []
        
        # Simple/Complex Logic (Shortened for speed)
        en_simple = ["put the {obj} inside the box", "lift the {obj}", "touch the {obj}"]
        en_complex = ["gently rotate the {obj} clockwise", "flip the {obj} over quickly", "tap the {obj} three times"]
        he_simple = [("שים את", "שימי את", "בקופסה"), ("הרם את", "הרימי את", ""), ("גע ב", "געי ב", "")]
        he_complex = [("סובב את", "סובבי את", "בזהירות"), ("הפוך את", "הפכי את", "מהר"), ("הקש על", "הקישי על", "פעמיים")]

        for _ in range(steps):
            target = random.choice(objects_list)
            if self.language == "en":
                if complexity == "Easy":
                    instructions.append(random.choice(en_simple).format(obj=target))
                else:
                    dist = random.choice(objects_list)
                    type_ = random.choice(["neg", "time"])
                    if type_ == "neg": instructions.append(f"Touch the {target}, but ignore the {dist}")
                    else: instructions.append(f"Before you touch the {target}, touch the {dist}")
            else:
                if complexity == "Easy":
                    instructions.append(self._hebrew_grammar_fix(random.choice(he_simple), target))
                else:
                    dist = random.choice(objects_list)
                    type_ = random.choice(["neg", "time"])
                    if type_ == "neg": instructions.append(f"{self._hebrew_grammar_fix(random.choice(he_simple), target)}, אך אל תגע ב{dist}" if self.trainee_gender == "Male" else f"אך אל תגעי ב{dist}")
                    else: instructions.append(f"לפני {target}, {self._hebrew_grammar_fix(random.choice(he_simple), dist)}")

        text = ". ".join(instructions) + "."
        return text, text

    # --- Mode 2: Sequencing ---
    def generate_sequence(self, length):
        selected = random.sample(SEQUENCING_VOCAB_EN, length)
        display_text = ", ".join(selected)
        
        # TRICK: We use periods to create the 0.5s pause naturally.
        # "Cat. Dog. Fish." creates a perfect distinct pause.
        audio_text = ". ".join(selected) + "." 
        
        return display_text, audio_text

# --- Audio Generation (Optimized) ---
async def _generate_audio_task(text, voice_name, rate_str):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
    mp3_fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
    return mp3_fp.getvalue()

def get_audio_bytes_safe(text, voice_name, rate_str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_audio_task(text, voice_name, rate_str))
    finally:
        loop.close()

# --- Main Interface ---
def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    lang_code = st.radio("Select Language / בחר שפה:", ["English", "עברית"], horizontal=True)
    lang = "en" if lang_code == "English" else "he"
    txt = UI_TEXT[lang] 

    if lang == "he":
        st.markdown("<style> .stTextInput, .stTextArea, .stSelectbox, .stButton, .stSlider { direction: rtl; } p, h1, h2, h3, li, label, .stRadio, .stMarkdown { text-align: right; } </style>", unsafe_allow_html=True)

    st.title(txt["title"])
    st.markdown("---")

    # State
    if 'audio_bytes' not in st.session_state: st.session_state.audio_bytes = None
    if 'display_text' not in st.session_state: st.session_state.display_text = ""
    if 'revealed' not in st.session_state: st.session_state.revealed = False
    if 'score' not in st.session_state: st.session_state.score = 0
    if 'total' not in st.session_state: st.session_state.total = 0

    # Sidebar
    with st.sidebar:
        st.header(txt["config_header"])
        mode = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"]])
        is_seq = (mode == txt["mode_sequencing"])
        
        st.markdown("---")
        
        # Gender settings
        g_sel = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        logic_gender = "Male" if g_sel in ["אתה", "Male"] else "Female"
        
        v_sel = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        if lang == "en": voice = "en-US-AriaNeural" if v_sel == "Female" else "en-US-GuyNeural"
        else: voice = "he-IL-HilaNeural" if v_sel == "Female" else "he-IL-AvriNeural"

        st.markdown("---")
        
        if is_seq:
            # SEQUENCING CONTROLS
            seq_len = st.slider(txt["seq_length_label"], 3, 8, 4)
        else:
            # INSTRUCTIONS CONTROLS
            default_inv = "red pen, blue pen, eraser" if lang == "en" else "עט אדום, עט כחול, מחק"
            objects_input = st.text_area(txt["inventory_label"], value=default_inv, height=100)
            c1, c2 = st.columns(2)
            with c1: steps = st.selectbox(txt["steps_label"], [1, 2, 3])
            with c2: comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])

        st.markdown("---")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # Main Area
    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, logic_gender)
        
        # Logic: Set Text and Speed
        if is_seq:
            display, audio_txt = gen.generate_sequence(seq_len)
            rate = "-10%" # Slightly slower for sequencing
        else:
            display, audio_txt = gen.generate_instruction(objects_input, steps, comp)
            rate = "+0%"  # Normal speed for instructions
            
        st.session_state.display_text = display
        st.session_state.revealed = False
        
        # Generate Audio
        with st.spinner("..."):
            data = get_audio_bytes_safe(audio_txt, voice, rate)
            st.session_state.audio_bytes = data

    # Play Audio
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format='audio/mp3', start_time=0)

    st.markdown("---")

    # Feedback
    if st.session_state.display_text:
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]):
                st.session_state.revealed = True
                st.rerun()
        else:
            st.info(f"{txt['instr_header']} {st.session_state.display_text}")
            c1, c2, _ = st.columns([1,1,3])
            with c1:
                if st.button(txt["correct_btn"]):
                    st.session_state.score += 1; st.session_state.total += 1
                    st.session_state.display_text = ""; st.session_state.audio_bytes = None
                    st.rerun()
            with c2:
                if st.button(txt["incorrect_btn"]):
                    st.session_state.total += 1
                    st.session_state.display_text = ""; st.session_state.audio_bytes = None
                    st.rerun()

    st.metric(txt["score_label"], f"{st.session_state.score} / {st.session_state.total}")

if __name__ == "__main__":
    main()
