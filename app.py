import streamlit as st
import random
from gtts import gTTS
from io import BytesIO

# --- הגדרת מחלקת יצירת המשפטים (אותו הגיון) ---
class SentenceGenerator:
    def __init__(self):
        self.default_objects = [
            "blank paper", "sticky note", "grid paper", "notebook", "book",
            "marker", "pencil", "colored pencil", "pen", "TV remote",
            "AC remote", "deck of cards", "eraser", "glasses", "cup"
        ]
        self.colors = ["red", "blue", "green", "yellow", "black", "white", "orange"]
        self.actions = [
            "put the {obj} inside the box",
            "take the {obj} out of the box",
            "place the {obj} on the right side",
            "place the {obj} on the left side",
            "turn over the {obj}",
            "rotate the {obj} 90 degrees",
            "touch the {obj} with your finger",
            "hide the {obj} under the book",
            "tap on the {obj} twice"
        ]

    def generate(self, objects_list, steps, complexity):
        instructions = []
        valid_objects = [obj.strip() for obj in objects_list if obj.strip()]
        if not valid_objects:
            valid_objects = self.default_objects

        for _ in range(steps):
            obj_base = random.choice(valid_objects)
            if complexity == "Hard":
                adj = random.choice(self.colors)
                obj_str = f"{adj} {obj_base}"
            else:
                obj_str = obj_base

            action_template = random.choice(self.actions)
            instruction = action_template.format(obj=obj_str)
            instructions.append(instruction)

        if len(instructions) == 1:
            return instructions[0].capitalize() + "."
        elif len(instructions) == 2:
            return f"{instructions[0].capitalize()}, and then {instructions[1]}."
        else:
            return f"{instructions[0].capitalize()}, then {instructions[1]}, and finally {instructions[2]}."

# --- ממשק האתר (Streamlit) ---
def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    
    st.title("🎧 APD Training - Speech in Noise")
    st.markdown("---")

    # אתחול משתנים בזיכרון (Session State)
    if 'generator' not in st.session_state:
        st.session_state.generator = SentenceGenerator()
    if 'current_sentence' not in st.session_state:
        st.session_state.current_sentence = ""
    if 'audio_bytes' not in st.session_state:
        st.session_state.audio_bytes = None
    if 'score_correct' not in st.session_state:
        st.session_state.score_correct = 0
    if 'score_total' not in st.session_state:
        st.session_state.score_total = 0
    if 'revealed' not in st.session_state:
        st.session_state.revealed = False

    # --- סרגל צד: הגדרות ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # רשימת חפצים
        objects_input = st.text_area(
            "Your Objects (comma separated):", 
            value=", ".join(st.session_state.generator.default_objects),
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            steps = st.selectbox("Steps", [1, 2, 3])
        with col2:
            complexity = st.selectbox("Complexity", ["Easy", "Hard"])
            
        st.markdown("---")
        st.header("🔊 Background Noise")
        st.info("Play this video in the background and adjust volume via the YouTube player controls:")
        # הטמעת נגן יוטיוב כרעש רקע
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # --- אזור מרכזי: אימון ---
    
    # כפתור יצירת משפט
    if st.button("▶ PLAY NEW INSTRUCTION", type="primary", use_container_width=True):
        # יצירת משפט חדש
        obj_list = objects_input.split(",")
        sentence = st.session_state.generator.generate(obj_list, steps, complexity)
        st.session_state.current_sentence = sentence
        
        # יצירת אודיו (TTS)
        tts = gTTS(text=sentence, lang='en')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        st.session_state.audio_bytes = mp3_fp.getvalue()
        
        # איפוס מצב חשיפה
        st.session_state.revealed = False

    # נגן אודיו למשפט
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format='audio/mp3', start_time=0)
        st.caption("Listen to the instruction and perform the action.")

    st.markdown("---")

    # בדיקה ומשוב
    if st.session_state.current_sentence:
        if not st.session_state.revealed:
            if st.button("👁 Reveal Text (Check Answer)"):
                st.session_state.revealed = True
                st.rerun()
        
        if st.session_state.revealed:
            st.subheader("The Sentence Was:")
            st.success(st.session_state.current_sentence)
            
            st.markdown("### Did you get it right?")
            c1, c2, c3 = st.columns([1,1,3])
            with c1:
                if st.button("✔ Correct"):
                    st.session_state.score_correct += 1
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" # איפוס
                    st.session_state.audio_bytes = None
                    st.rerun()
            with c2:
                if st.button("✖ Incorrect"):
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" # איפוס
                    st.session_state.audio_bytes = None
                    st.rerun()

    # הצגת ניקוד
    st.metric(label="Score", value=f"{st.session_state.score_correct} / {st.session_state.score_total}")

if __name__ == "__main__":
    main()
