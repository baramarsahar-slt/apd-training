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
        "inventory_label": "My Objects:",
        "steps_label": "Steps (Commands):",
        "complexity_label": "Complexity:",
        "play_btn": "▶ PLAY NEW INSTRUCTION",
        "reveal_btn": "👁 Reveal Text (Check Answer)",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Session Score",
        "instr_header": "The Instruction Was:",
        "guide_expander": "ℹ️ Object List Guide",
        "guide_text": "**For Auditory Discrimination:** Enter items separated by commas. In Hebrew, simple list is supported.",
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
        "inventory_label": "רשימת החפצים שלי:",
        "steps_label": "מספר שלבים (הוראות):",
        "complexity_label": "רמת קושי:",
        "play_btn": "▶ השמע הוראה חדשה",
        "reveal_btn": "👁 חשוף את הטקסט (בדיקה)",
        "correct_btn": "✔ הצלחתי",
        "incorrect_btn": "✖ טעיתי",
        "score_label": "ניקוד בסשן הנוכחי",
        "instr_header": "ההוראה הייתה:",
        "guide_expander": "ℹ️ מדריך לכתיבת חפצים",
        "guide_text": "**בעברית:** המערכת מזהה אוטומטית זכר/נקבה עבור מילים נפוצות. מומלץ לכתוב: 'עט אדום, עט כחול, מחק גדול'.",
        "noise_header": "🔊 רעש רקע",
        "noise_caption": "יש להפעיל את הסרטון ולכוון את עוצמת הרעש דרך הנגן.",
        "listen_caption": "טיפ: ניתן לשלוט בעוצמת הקול של הדובר דרך הנגן השחור למעלה."
    }
}

# --- לוגיקה בעברית ---
HE_VOCAB = {
    "objects": {
        "עט": "m", "עיפרון": "m", "מחק": "m", "דף": "m", "ספר": "m", "שלט": "m", "טוש": "m", "מפתח": "m",
        "מחברת": "f", "כוס": "f", "קופסה": "f", "מדבקה": "f", "קוביה": "f", "צלחת": "f"
    },
    "adjectives": {
        "red": ("אדום", "אדומה"), "blue": ("כחול", "כחולה"), "green": ("ירוק", "ירוקה"),
        "yellow": ("צהוב", "צהובה"), "black": ("שחור", "שחורה"), "white": ("לבן", "לבנה"),
        "big": ("גדול", "גדולה"), "small": ("קטן", "קטנה")
    }
}

class SentenceGenerator:
    def __init__(self, language="en", trainee_gender="Male"):
        self.language = language
        self.trainee_gender = trainee_gender 
        
        self.en_default_objects = ["red pen", "blue pen", "pencil", "notebook", "keys", "cup"]
        self.en_actions_simple = [
            "put the {obj} inside the box", "lift the {obj}", "touch the {obj}", 
            "push the {obj} away", "point to the {obj}"
        ]
        self.en_actions_complex = [
            "gently rotate the {obj} clockwise", "flip the {obj} over quickly", 
            "place the {obj} behind the box", "tap the {obj} three times"
        ]

        self.he_default_objects = "עט אדום, עט כחול, מחק, מחברת, כוס, מפתח"
        self.he_actions_simple = [
            ("שים את", "שימי את", "בתוך הקופסה"), ("הרם את", "הרימי את", ""),
            ("גע ב", "געי ב", ""), ("הזז את", "הזיזי את", "הצידה"), ("הצבע על", "הצביעי על", "")
        ]
        self.he_actions_complex = [
            ("סובב את", "סובבי את", "בזהירות"), ("הפוך את", "הפכי את", "במהירות"),
            ("הנח את", "הניחי את", "מאחורי הקופסה"), ("הקש על", "הקישי על", "פעמיים")
        ]

    def get_clean_list(self, user_input):
        items = [x.strip() for x in user_input.split(",") if x.strip()]
        if not items:
            return self.en_default_objects if self.language == "en" else self.he_default_objects.split(", ")
        return items

    def _hebrew_grammar_fix(self, action_template, obj_str):
        cmd = action_template[0] if self.trainee_gender == "Male" else action_template[1]
        suffix = action_template[2]
        return f"{cmd} {obj_str} {suffix}".strip()

    def generate(self, objects_input, steps, complexity):
        objects_list = self.get_clean_list(objects_input)
        instructions = []
        
        if self.language == "en":
            for _ in range(steps):
                if complexity == "Easy":
                    target = random.choice(objects_list)
                    action = random.choice(self.en_actions_simple)
                    instructions.append(action.format(obj=target))
                else:
                    target = random.choice(objects_list)
                    distractor = random.choice(objects_list)
                    type_ = random.choice(["neg", "time", "complex"])
                    if type_ == "neg":
                        act = random.choice(self.en_actions_simple).format(obj=target)
                        instructions.append(f"{act}, but do not touch the {distractor}")
                    elif type_ == "time":
                        act1 = random.choice(self.en_actions_simple).format(obj=distractor)
                        act2 = random.choice(self.en_actions_simple).format(obj=target)
                        instructions.append(f"Before you {act2}, {act1}")
                    else:
                        act = random.choice(self.en_actions_complex).format(obj=target)
                        instructions.append(act)

            if len(instructions) == 1: sent = instructions[0]
            elif len(instructions) == 2: sent = f"{instructions[0]}, and then {instructions[1]}"
            else: sent = f"{instructions[0]}, then {instructions[1]}, and finally {instructions[2]}"
            return sent[0].upper() + sent[1:] + "."

        else: # HEBREW
            for _ in range(steps):
                target = random.choice(objects_list)
                if complexity == "Easy": 
                    act_tuple = random.choice(self.he_actions_simple)
                    instructions.append(self._hebrew_grammar_fix(act_tuple, target))
                else: 
                    distractor = random.choice(objects_list)
                    while distractor == target and len(objects_list) > 1:
                        distractor = random.choice(objects_list)
                    type_ = random.choice(["neg", "time", "complex"])
                    if type_ == "neg": 
                        act_tuple = random.choice(self.he_actions_simple)
                        base = self._hebrew_grammar_fix(act_tuple, target)
                        neg_cmd = "אך אל תגע ב" if self.trainee_gender == "Male" else "אך אל תגעי ב"
                        instructions.append(f"{base}, {neg_cmd}{distractor}")
                    elif type_ == "time": 
                        act_tuple1 = random.choice(self.he_actions_simple) 
                        act_tuple2 = random.choice(self.he_actions_simple) 
                        part1 = self._hebrew_grammar_fix(act_tuple1, distractor)
                        part2 = self._hebrew_grammar_fix(act_tuple2, target)
                        before_word = "לפני שאתה" if self.trainee_gender == "Male" else "לפני שאת"
                        instructions.append(f"{before_word} {part2}, {part1}")
                    else: 
                        act_tuple = random.choice(self.he_actions_complex)
                        instructions.append(self._hebrew_grammar_fix(act_tuple, target))

            if len(instructions) == 1: sent = instructions[0]
            elif len(instructions) == 2: sent = f"{instructions[0]}, ואז {instructions[1]}"
            else: sent = f"{instructions[0]}, אחר כך {instructions[1]}, ולבסוף {instructions[2]}"
            return sent + "."

# --- Safe Async Helper (Fixed for Streamlit) ---
async def _generate_audio(text, voice_name):
    communicate = edge_tts.Communicate(text, voice_name)
    mp3_fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
    return mp3_fp.getvalue()

def get_audio_bytes_safe(text, voice_name):
    # Create a new event loop for this thread to avoid Streamlit conflicts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_audio(text, voice_name))
    finally:
        loop.close()

# --- Main App ---
def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    
    # --- LANGUAGE SELECTOR ---
    lang_code = st.radio("Select Language / בחר שפה:", ["English", "עברית"], horizontal=True)
    lang = "en" if lang_code == "English" else "he"
    txt = UI_TEXT[lang] 

    # RTL Support
    if lang == "he":
        st.markdown("""
        <style>
        .stTextInput, .stTextArea, .stSelectbox, .stButton { direction: rtl; }
        p, h1, h2, h3, li, label, .stRadio { text-align: right; }
        </style>
        """, unsafe_allow_html=True)

    st.title(txt["title"])
    st.markdown("---")

    if 'generator' not in st.session_state: st.session_state.generator = SentenceGenerator()
    if 'current_sentence' not in st.session_state: st.session_state.current_sentence = ""
    if 'audio_bytes' not in st.session_state: st.session_state.audio_bytes = None
    if 'score_correct' not in st.session_state: st.session_state.score_correct = 0
    if 'score_total' not in st.session_state: st.session_state.score_total = 0
    if 'revealed' not in st.session_state: st.session_state.revealed = False

    # --- SIDEBAR ---
    with st.sidebar:
        st.header(txt["config_header"])
        gender_selection = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        
        if gender_selection == "אתה" or gender_selection == "Male":
            logic_gender = "Male"
        else:
            logic_gender = "Female"

        voice_gender = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        if lang == "en":
            voice_id = "en-US-AriaNeural" if voice_gender == "Female" else "en-US-GuyNeural"
        else:
            voice_id = "he-IL-HilaNeural" if voice_gender == "Female" else "he-IL-AvriNeural"

        st.markdown("---")
        with st.expander(txt["guide_expander"], expanded=False):
            st.markdown(txt["guide_text"])

        default_inv = "red pen, blue pen, eraser" if lang == "en" else "עט אדום, עט כחול, מחק, מחברת"
        objects_input = st.text_area(txt["inventory_label"], value=default_inv, height=100)
        
        c1, c2 = st.columns(2)
        with c1: steps = st.selectbox(txt["steps_label"], [1, 2, 3])
        with c2: complexity = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
        
        st.markdown("---")
        st.header(txt["noise_header"])
        st.caption(txt["noise_caption"])
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # --- MAIN AREA ---
    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = SentenceGenerator(language=lang, trainee_gender=logic_gender)
        sentence = gen.generate(objects_input, steps, complexity)
        st.session_state.current_sentence = sentence
        st.session_state.revealed = False
        
        try:
            # Using the Safe wrapper here
            audio_data = get_audio_bytes_safe(sentence, voice_id)
            st.session_state.audio_bytes = audio_data
        except Exception as e:
            st.error(f"Audio Error: {e}")

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format='audio/mp3', start_time=0)
        st.caption(txt["listen_caption"])

    st.markdown("---")

    if st.session_state.current_sentence:
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]):
                st.session_state.revealed = True
                st.rerun()
        
        if st.session_state.revealed:
            st.info(f"{txt['instr_header']} {st.session_state.current_sentence}")
            col1, col2, col3 = st.columns([1,1,3])
            with col1:
                if st.button(txt["correct_btn"]):
                    st.session_state.score_correct += 1
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" 
                    st.session_state.audio_bytes = None
                    st.rerun()
            with col2:
                if st.button(txt["incorrect_btn"]):
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" 
                    st.session_state.audio_bytes = None
                    st.rerun()

    st.metric(label=txt["score_label"], value=f"{st.session_state.score_correct} / {st.session_state.score_total}")

if __name__ == "__main__":
    main()
