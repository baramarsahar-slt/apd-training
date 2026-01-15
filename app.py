import streamlit as st
import random
import edge_tts
import asyncio
import io

# --- Sentence Generator Logic (Same as before) ---
class SentenceGenerator:
    def __init__(self):
        self.default_objects = [
            "red pen", "blue pen", "red marker", "blue marker",
            "thick eraser", "thin eraser", 
            "lined paper", "graph paper", "blank paper"
        ]
        
        self.actions_simple = [
            "put the {obj} inside the box",
            "lift the {obj}",
            "touch the {obj}",
            "push the {obj} away",
            "hold the {obj} in your hand",
            "point to the {obj}"
        ]

        self.actions_complex = [
            "gently rotate the {obj} clockwise",
            "flip the {obj} over quickly",
            "place the {obj} behind the box",
            "tap the {obj} three times",
            "hide the {obj} under your hand",
            "move the {obj} to the edge of the table"
        ]

    def get_clean_list(self, user_input):
        items = [x.strip() for x in user_input.split(",") if x.strip()]
        if not items:
            return self.default_objects
        return items

    def generate(self, objects_input, steps, complexity):
        objects_list = self.get_clean_list(objects_input)
        instructions = []
        
        def get_target_and_distractor():
            if len(objects_list) >= 2:
                return random.sample(objects_list, 2)
            elif len(objects_list) == 1:
                return objects_list[0], objects_list[0]
            else:
                return "object", "object"

        for _ in range(steps):
            if complexity == "Easy":
                target = random.choice(objects_list)
                action = random.choice(self.actions_simple)
                instructions.append(action.format(obj=target))
            else:
                target, distractor = get_target_and_distractor()
                struct_type = random.choice(["temporal", "negative", "complex_verb"])

                if struct_type == "temporal":
                    part1 = random.choice(self.actions_simple).format(obj=distractor)
                    part2 = random.choice(self.actions_simple).format(obj=target)
                    if random.random() > 0.5:
                        instructions.append(f"Before you {part2}, {part1}")
                    else:
                        instructions.append(f"After you {part1}, {part2}")
                        
                elif struct_type == "negative":
                    act = random.choice(self.actions_simple).format(obj=target)
                    instructions.append(f"{act}, but do not touch the {distractor}")
                    
                else:
                    act = random.choice(self.actions_complex).format(obj=target)
                    instructions.append(act)

        final_sentence = ""
        if len(instructions) == 1:
            final_sentence = instructions[0]
        elif len(instructions) == 2:
            final_sentence = f"{instructions[0]}, and then {instructions[1]}"
        else:
            final_sentence = f"{instructions[0]}, then {instructions[1]}, and finally {instructions[2]}"

        return final_sentence[0].upper() + final_sentence[1:] + "."

# --- Async Helper for Edge TTS ---
async def get_audio_bytes(text, voice_name):
    communicate = edge_tts.Communicate(text, voice_name)
    mp3_fp = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
    return mp3_fp.getvalue()

# --- Streamlit Interface ---
def main():
    st.set_page_config(page_title="APD Training", layout="wide")
    
    st.title("🎧 APD Training - Speech in Noise")
    st.markdown("---")

    # Session State
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

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Voice Selection
        st.markdown("**1. Voice Settings:**")
        voice_gender = st.selectbox("Select Voice Gender:", ["Female", "Male"])
        # Mapping to Microsoft Edge Neural Voices
        voice_id = "en-US-AriaNeural" if voice_gender == "Female" else "en-US-GuyNeural"

        st.markdown("---")
        
        # Instructions
        with st.expander("ℹ️ Object List Guide", expanded=False):
            st.markdown("""
            **For Auditory Discrimination:**
            Enter similar items with one distinguishing feature.
            * `red pen, blue pen`
            * `thick eraser, thin eraser`
            """)

        st.markdown("**2. Inventory:**")
        objects_input = st.text_area(
            "My Objects:", 
            value="red pen, blue pen, red marker, thick eraser, thin eraser, lined paper, graph paper",
            height=100
        )
        
        st.markdown("**3. Difficulty:**")
        c1, c2 = st.columns(2)
        with c1:
            steps = st.selectbox("Steps", [1, 2, 3])
        with c2:
            complexity = st.selectbox("Complexity", ["Easy", "Hard"])
        
        st.markdown("---")
        st.header("🔊 Background Noise")
        st.caption("Use the video player volume to adjust noise level.")
        st.video("https://www.youtube.com/watch?v=cXjUCkLG-sg")

    # --- MAIN AREA ---
    
    # Play Button
    if st.button("▶ PLAY NEW INSTRUCTION", type="primary", use_container_width=True):
        # 1. Generate Text
        sentence = st.session_state.generator.generate(objects_input, steps, complexity)
        st.session_state.current_sentence = sentence
        st.session_state.revealed = False
        
        # 2. Generate Audio (Async)
        try:
            audio_data = asyncio.run(get_audio_bytes(sentence, voice_id))
            st.session_state.audio_bytes = audio_data
        except Exception as e:
            st.error(f"Audio Error: {e}")

    # Audio Player
    if st.session_state.audio_bytes:
        st.markdown("##### 🔊 Instruction Audio:")
        st.audio(st.session_state.audio_bytes, format='audio/mp3', start_time=0)
        st.caption("Tip: Use the volume button on the player above to adjust the voice volume.")

    st.markdown("---")

    # Feedback
    if st.session_state.current_sentence:
        if not st.session_state.revealed:
            if st.button("👁 Reveal Text (Check Answer)"):
                st.session_state.revealed = True
                st.rerun()
        
        if st.session_state.revealed:
            st.info(f"📝 **Instruction:** {st.session_state.current_sentence}")
            
            col1, col2, col3 = st.columns([1,1,3])
            with col1:
                if st.button("✔ Correct"):
                    st.session_state.score_correct += 1
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" 
                    st.session_state.audio_bytes = None
                    st.rerun()
            with col2:
                if st.button("✖ Incorrect"):
                    st.session_state.score_total += 1
                    st.session_state.current_sentence = "" 
                    st.session_state.audio_bytes = None
                    st.rerun()

    # Score
    st.metric(label="Session Score", value=f"{st.session_state.score_correct} / {st.session_state.score_total}")

if __name__ == "__main__":
    main()
