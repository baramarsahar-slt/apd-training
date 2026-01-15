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

# --- לוגיקה בעברית (Hebrew Logic) ---
HE_VOCAB = {
    # חפצים: (שם, מין) -> 'm' זכר, 'f' נקבה
    "objects": {
        "עט": "m", 
        "עיפרון": "m", 
        "מחק": "m", 
        "דף": "m", 
        "ספר": "m", 
        "שלט": "m", 
        "טוש": "m", 
        "מפתח": "m",
        "מחברת": "f", 
        "כוס": "f", 
        "קופסה": "f", 
        "מדבקה": "f", 
        "קוביה": "f", 
        "צלחת": "f"
    },
    # תארים: (זכר, נקבה)
    "adjectives": {
        "red": ("אדום", "אדומה"),
        "blue": ("כחול", "כחולה"),
        "green": ("ירוק", "ירוקה"),
        "yellow": ("צהוב", "צהובה"),
        "black": ("שחור", "שחורה"),
        "white": ("לבן", "לבנה"),
        "big": ("גדול", "גדולה"),
        "small": ("קטן", "קטנה")
    }
}

class SentenceGenerator:
    def __init__(self, language="en", trainee_gender="Male"):
        self.language = language
        self.trainee_gender = trainee_gender 
        
        # --- ENGLISH DATA ---
        self.en_default_objects = ["red pen", "blue pen", "pencil", "notebook", "keys", "cup"]
        self.en_actions_simple = [
            "put the {obj} inside the box", "lift the {obj}", "touch the {obj}", 
            "push the {obj} away", "point to the {obj}"
        ]
        self.en_actions_complex = [
            "gently rotate the {obj} clockwise", "flip the {obj} over quickly", 
            "place the {obj} behind the box", "tap the {obj} three times"
        ]

        # --- HEBREW DATA ---
        self.he_default_objects = "עט אדום, עט כחול, מחק, מחברת, כוס, מפתח"
        
        self.he_actions_simple = [
            ("שים את", "שימי את", "בתוך הקופסה"),
            ("הרם את", "הרימי את", ""),
            ("גע ב", "געי ב", ""), 
            ("הזז את", "הזיזי את", "הצידה"),
            ("הצבע על", "הצביעי על", "")
        ]
        
        self.he_actions_complex = [
            ("סובב את", "סובבי את", "בזהירות"),
            ("הפוך את", "הפכי את", "במהירות"),
            ("הנח את", "הניחי את", "מאחורי הקופסה"),
            ("הקש על", "הקישי על", "פעמיים")
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

            if len(instructions) == 1: sent = instructions
