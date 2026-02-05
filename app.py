import streamlit as st
import random
import edge_tts
import asyncio
import io

# --- מילונים ושפות (Dictionaries & Localization) ---

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
        "play_btn": "▶ PLAY NEW TRACK",
        "reveal_btn": "👁 Reveal Text (Check Answer)",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Session Score",
        "instr_header": "The Content Was:",
        "guide_expander": "ℹ️ Object List Guide",
        "guide_text": "**For Instructions Mode:** Enter items separated by commas.",
        "noise_header": "🔊 Background Noise",
        "noise_caption": "Use the video player volume to adjust noise level.",
        "listen_caption": "Tip: Use the volume button on the player above to adjust the voice volume."
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
        "play_btn": "▶ השמע תרגיל חדש",
        "reveal_btn": "👁 חשוף את הטקסט (בדיקה)",
        "correct_btn": "✔ הצלחתי",
        "incorrect_btn": "✖ טעיתי",
        "score_label": "ניקוד בסשן הנוכחי",
        "instr_header": "התוכן שהושמע:",
        "guide_expander": "ℹ️ מדריך לכתיבת חפצים",
        "guide_text": "**לאימון הוראות:** מומלץ לכתוב: 'עט אדום, עט כחול, מחק גדול'. באימון זיכרון המערכת משתמשת במאגר מובנה.",
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "יש להפעיל את הסרטון ולכוון את עוצמת הרעש דרך הנגן.",
        "listen_caption": "טיפ: ניתן לשלוט בעוצמת הקול של הדובר דרך הנגן השחור למעלה."
    }
}

# --- מאגר מילים לאימון זיכרון (Sequencing) ---
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
            return ["red pen", "blue pen", "pencil", "notebook", "keys", "cup"] if self.language == "en" else ["עט", "מחק", "מחברת"]
        return items

    def _hebrew_grammar_fix(self, action_template, obj_str):
        cmd = action_template[0] if self.trainee_gender == "Male" else action_template[1]
        suffix = action_template[2]
        return f"{cmd} {obj_str} {suffix}".strip()

    def generate_instruction(self, objects_input, steps, complexity):
        objects_list = self.get_clean_list(objects_input)
        instructions = []
        
        # English simple actions
        en_simple = ["put the {obj} inside the box", "lift the {obj}", "touch the {obj}", "push the {obj} away", "point to the {obj}"]
        en_complex = ["gently rotate the {obj} clockwise", "flip the {obj} over quickly", "place the {obj} behind the box", "tap the {obj} three times"]
        
        # Hebrew simple actions
        he_simple = [("שים את", "שימי את", "בתוך הקופסה"), ("הרם את", "הרימי את", ""), ("גע ב", "געי ב", ""), ("הזז את", "הזיזי את", "הצידה"), ("הצבע על", "הצביעי על", "")]
        he_complex = [("סובב את", "סובבי את", "בזהירות"), ("הפוך את", "הפכי את", "במהירות"), ("הנח את", "הניחי את", "מאחורי הקופסה"), ("הקש על", "הקישי על", "פעמיים")]

        for _ in range(steps):
            target = random.choice(objects_list)
            if self.language == "en":
                if complexity == "Easy":
                    instructions.append(random.choice(en_simple).format(obj=target))
                else:
                    dist = random.choice(objects_list)
                    type_ = random.choice(["neg", "time", "complex"])
                    if type_ == "neg": instructions.append(f"{random.choice(en_simple).format(obj=target)}, but do not touch the {dist}")
                    elif type_ == "time": instructions.append(f"Before you {random.choice(en_simple).format(obj=target)}, {random.choice(en_simple).format(obj=dist)}")
                    else: instructions.append(random.choice(en_complex).format(obj=target))
            else:
                if complexity == "Easy":
                    instructions.append(self._hebrew_grammar_fix(random.choice(he_simple), target))
                else:
                    dist = random.choice(objects_list)
                    type_ = random.choice(["neg", "time", "complex"])
                    if type_ == "neg": instructions.append(f"{self._hebrew_grammar_fix(random.choice(he_simple), target)}, אך אל תגע ב{dist}" if self.trainee_gender == "Male" else f"{self._hebrew_grammar_fix(random.choice(he_simple), target)}, אך אל תגעי ב{dist}")
                    elif type_ == "time": instructions.append(f"{'לפני שאתה' if self.trainee_gender == 'Male' else 'לפני שאת'} {self._hebrew_grammar_fix(random.choice(he_simple), target)}, {self._hebrew_grammar_fix(random.choice(he_simple), dist)}")
                    else: instructions.append(self._hebrew_grammar_fix(random.choice(he_complex), target))

        if self.language == "en":
            if len(instructions) == 1: sent = instructions[0]
            elif len(instructions) == 2: sent = f"{instructions[0]}, and then {instructions[1]}"
            else: sent = f"{instructions[0]}, then {instructions[1]}, and finally {instructions[2]}"
            res = sent[0].upper() + sent[1:] + "."
        else:
            if len(instructions) == 1: sent = instructions[0]
            elif len(instructions) == 2: sent = f"{instructions[0]}, ואז {instructions[1]}"
            else: sent = f"{instructions[0]}, אחר כך {instructions[1]}, ולבסוף {instructions[2]}"
            res = sent + "."
        return res, res

    def generate_sequence(self, length, voice_id):
        selected = random.sample(SEQUENCING_VOCAB_EN, length)
        display_text = ", ".join(selected)
        
        # כניסה למצב SSML קשוח כדי למנוע הקראת תגיות
        audio_parts = []
        for word in selected:
            audio_parts.append(f"{word} <break time='1500ms'/>")
        
        inner_content = "".join(audio_parts)
        # הפורמט הזה מחייב את המנוע להתייחס לזה כאל SSML
        ssml_text = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
<voice name='{voice_id}'>
<prosody rate='-20%'>
{inner_content}
</prosody>
</voice>
</speak>"""
        return display_text, ssml_text

# --- מנוע האודיו ---
async def _generate_audio_task(text, voice_name):
    # אם הטקסט מתחיל בתגית speak, אנחנו לא מעבירים rate כפרמטר חיצוני
    if text.strip().startswith("<speak"):
        communicate = edge_tts.Communicate(text) # ה-voice כבר בפנים
    else:
        communicate = edge_tts.Communicate(text, voice_name, rate="+0%")
    
    mp3_fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
    return mp3_fp.getvalue()

def get_audio_bytes_safe(text, voice_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_audio_task(text, voice_name))
    finally:
        loop.close()

# --- ממשק Streamlit ---
def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    lang_code = st.radio("Select Language / בחר שפה:", ["English", "עברית"], horizontal=True)
    lang = "en" if lang_code == "English" else "he"
    txt = UI_TEXT[lang] 

    if lang == "he":
        st.markdown("<style> .stTextInput, .stTextArea, .stSelectbox, .stButton, .stSlider { direction: rtl; } p, h1, h2, h3, li, label, .stRadio, .stMarkdown { text-align: right; } </style>", unsafe_allow_html=True)

    st.title(txt["title"])
    st.markdown("---")

    if 'current_text_display' not in st.session_state: st.session_state.current_text_display = ""
    if 'audio_bytes' not in st.session_state: st.session_state.audio_bytes = None
    if 'score_correct' not in st.session_state: st.session_state.score_correct = 0
    if 'score_total' not in st.session_state: st.session_state.score_total = 0
    if 'revealed' not in st.session_state: st.session_state.revealed = False

    with st.sidebar:
        st.header(txt["config_header"])
        mode_key = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"]])
        is_sequencing = (mode_key == txt["mode_sequencing"])
        st.markdown("---")
        gender_selection = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        logic_gender = "Male" if (gender_selection in ["אתה", "Male"]) else "Female"
        voice_gender = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        
        if lang == "en": voice_id = "en-US-AriaNeural" if voice_gender == "Female" else "en-US-GuyNeural"
        else: voice_id = "he-IL-HilaNeural" if voice_gender == "Female" else "he-IL-AvriNeural"

        st.markdown("---")
        if not is_sequencing:
            objects_input = st.text_area(txt["inventory_label"], value="red pen, blue pen, eraser" if lang == "en" else "עט אדום, עט כחול, מחק", height=100)
            c1, c2 = st.columns(2)
            with c1: steps = st.selectbox(txt["steps_label"], [1, 2, 3])
            with c2: complexity = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
        else:
            seq_length = st.slider(txt["seq_length_label"], 3, 8, 4)
        
        st.markdown("---")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(language=lang, trainee_gender=logic_gender)
        if is_sequencing:
            display, audio_text = gen.generate_sequence(seq_length, voice_id)
        else:
            display, audio_text = gen.generate_instruction(objects_input, steps, complexity)
        
        st.session_state.current_text_display = display
        st.session_state.revealed = False
        
        with st.spinner("Generating audio..."):
            audio_data = get_audio_bytes_safe(audio_text, voice_id)
            st.session_state.audio_bytes = audio_data

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes)

    if st.session_state.current_text_display:
        st.markdown("---")
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]):
                st.session_state.revealed = True
                st.rerun()
        if st.session_state.revealed:
            st.info(f"{txt['instr_header']} {st.session_state.current_text_display}")
            col1, col2, _ = st.columns([1,1,3])
            with col1:
                if st.button(txt["correct_btn"]):
                    st.session_state.score_correct += 1
                    st.session_state.score_total += 1
                    st.session_state.current_text_display = ""; st.session_state.audio_bytes = None
                    st.rerun()
            with col2:
                if st.button(txt["incorrect_btn"]):
                    st.session_state.score_total += 1
                    st.session_state.current_text_display = ""; st.session_state.audio_bytes = None
                    st.rerun()

    st.metric(label=txt["score_label"], value=f"{st.session_state.score_correct} / {st.session_state.score_total}")

if __name__ == "__main__":
    main()
