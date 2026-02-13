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
        "mode_chronology": "4. Chronological Ordering",
        "trainee_gender_label": "Trainee Gender:",
        "trainee_gender_opts": ["Male", "Female"],
        "voice_gender": "Voice Speaker Gender:",
        "inventory_label": "Objects (for Instructions):",
        "steps_label": "Steps:",
        "seq_length_label": "Sequence Length:",
        "complexity_label": "Complexity:",
        "play_btn": "▶ PLAY NEW",
        "reveal_btn": "👁 Reveal Text",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Score",
        "history_label": "Session Log:",
        "clear_history": "🗑️ Clear",
        "instr_header": "Full Sentence:",
        "summary_header": "Target Essence (SVO):",
        "chrono_markers_header": "Time Markers:",
        "chrono_order_header": "Correct Order:",
        "noise_header": "🔊 Background Noise",
        "table_cols": ["#", "Mode", "Level", "Result"]
    },
    "he": {
        "title": "🎧 אימון עיבוד שמיעתי - דיבור ברעש",
        "config_header": "⚙️ הגדרות אימון",
        "mode_label": "בחר סוג אימון:",
        "mode_instructions": "1. ביצוע הוראות",
        "mode_sequencing": "2. זיכרון שמיעתי (רצף)",
        "mode_summarization": "3. תמצות עיקר המשפט (SVO)",
        "mode_chronology": "4. סידור כרונולוגי (סדר פעולות)",
        "trainee_gender_label": "פנייה למתאמן/ת:",
        "trainee_gender_opts": ["אתה", "את"],
        "voice_gender": "קול הדובר:",
        "inventory_label": "רשימת חפצים:",
        "steps_label": "שלבים:",
        "seq_length_label": "אורך רצף:",
        "complexity_label": "רמת קושי:",
        "play_btn": "▶ השמע תרגיל חדש",
        "reveal_btn": "👁 חשוף תשובה",
        "correct_btn": "✔ הצלחתי",
        "incorrect_btn": "✖ טעיתי",
        "score_label": "ניקוד מצטבר",
        "history_label": "תיעוד ביצועים:",
        "clear_history": "🗑️ נקה",
        "instr_header": "המשפט המלא:",
        "summary_header": "תמצית המשפט (SVO):",
        "chrono_markers_header": "מילות קישור:",
        "chrono_order_header": "סדר ביצוע נכון:",
        "noise_header": "🔊 רעש רקע",
        "table_cols": ["#", "סוג", "רמה", "תוצאה"]
    }
}

# --- DATABASE: SVO (Summarization) ---
# Format: {"text": "Full sentence", "core": "Core SVO"}
SVO_DB = {
    "he": {
        "Easy": [
            # Home
            {"text": "האמא, שישבה במטבח, קילפה תפוח.", "core": "האמא קילפה תפוח"},
            {"text": "הילד, ששיחק בחדר, בנה מגדל.", "core": "הילד בנה מגדל"},
            {"text": "החתול, שישן על הספה, תפס זבוב.", "core": "החתול תפס זבוב"},
            {"text": "הסבתא, בזמן שצפתה בטלוויזיה, סרגה סוודר.", "core": "הסבתא סרגה סוודר"},
            {"text": "המרק, שהתבשל על האש, גלש על הגז.", "core": "המרק גלש"},
            # Work
            {"text": "המנהל, שנכנס לחדר, ביטל את הישיבה.", "core": "המנהל ביטל ישיבה"},
            {"text": "המורה, שנכנסה לכיתה, סגרה את הדלת.", "core": "המורה סגרה דלת"},
            {"text": "הטכנאי, שתיקן את המחשב, ביקש תשלום.", "core": "הטכנאי ביקש תשלום"},
            # Health
            {"text": "הרופא, שבדק את הילד, רשם תרופה.", "core": "הרופא רשם תרופה"},
            {"text": "האחות, שמדדה חום, חייכה לחולה.", "core": "האחות חייכה"},
            # Errands
            {"text": "הנהג, שעצר ברמזור, צפר למכונית.", "core": "הנהג צפר"},
            {"text": "המוכר, ששקל את הפירות, הדפיס חשבונית.", "core": "המוכר הדפיס חשבונית"},
            {"text": "השוטר, שעמד בצומת, כיוון את התנועה.", "core": "השוטר כיוון תנועה"},
            {"text": "הכספומט, שהיה בפינה, בלע את הכרטיס.", "core": "הכספומט בלע כרטיס"}
        ],
        "Hard": [
            # Home
            {"text": "העוגה החגיגית, שהוכנה במיוחד למסיבה, נשרפה בתנור.", "core": "העוגה נשרפה"},
            {"text": "המפתח הרזרבי, שהוחבא מתחת לשטיח הכניסה, נאבד אתמול.", "core": "המפתח נאבד"},
            {"text": "הכלב של השכנים, שלמרבה הצער השתחרר מהרצועה, הפחיד את הילדים.", "core": "הכלב הפחיד ילדים"},
            # Work
            {"text": "הדו\"ח השנתי, שהתעכב בדפוס בגלל תקלה טכנית, פורסם הבוקר.", "core": "הדו\"ח פורסם"},
            {"text": "הסטודנט החדש, שישב בסוף הכיתה ולא הקשיב, נכשל במבחן.", "core": "הסטודנט נכשל"},
            {"text": "המייל החשוב, שנשלח למנהל בטעות ללא הקובץ, נמחק מהשרת.", "core": "המייל נמחק"},
            # Health
            {"text": "תוצאות הבדיקה, שהגיעו מהמעבדה באיחור של יומיים, היו תקינות.", "core": "התוצאות תקינות"},
            {"text": "האחות במיון, שלמרות העומס הרב שמרה על רוגע, קיבלה את הפצועים.", "core": "האחות קיבלה פצועים"},
            {"text": "הניתוח המורכב, שנמשך שעות רבות בחדר הניתוח, הסתיים בהצלחה.", "core": "הניתוח הסתיים"},
            # Errands
            {"text": "החבילה מהדואר, שנשלחה מחו\"ל לפני כחודש ימים, אבדה בדרך.", "core": "החבילה אבדה"},
            {"text": "המכונית האדומה, שניסתה לעקוף את המשאית בפראות, ירדה לשוליים.", "core": "המכונית ירדה"},
            {"text": "הטיסה ללונדון, שהמריאה באיחור בגלל מזג האוויר, נחתה בשלום.", "core": "הטיסה נחתה"},
            {"text": "כרטיס האשראי, שבוטל על ידי הבנק מחשש לגניבה, נמצא בארנק.", "core": "הכרטיס נמצא"}
        ]
    },
    "en": {
        "Easy": [
            {"text": "The mother, sitting in the kitchen, peeled an apple.", "core": "Mother peeled apple"},
            {"text": "The boy, playing in his room, built a tower.", "core": "Boy built tower"},
            {"text": "The cat, sleeping on the sofa, caught a fly.", "core": "Cat caught fly"},
            {"text": "The soup, cooking on the stove, boiled over.", "core": "Soup boiled over"},
            {"text": "The manager, entering the room, cancelled the meeting.", "core": "Manager cancelled meeting"},
            {"text": "The teacher, walking into class, closed the door.", "core": "Teacher closed door"},
            {"text": "The doctor, checking the child, prescribed medicine.", "core": "Doctor prescribed medicine"},
            {"text": "The nurse, taking a pulse, smiled at the patient.", "core": "Nurse smiled"},
            {"text": "The driver, stopping at the light, honked the horn.", "core": "Driver honked"},
            {"text": "The cashier, weighing the fruit, printed a receipt.", "core": "Cashier printed receipt"}
        ],
        "Hard": [
            {"text": "The birthday cake, baked specifically for the party, burned in the oven.", "core": "Cake burned"},
            {"text": "The spare key, hidden under the welcome mat, was lost yesterday.", "core": "Key was lost"},
            {"text": "The neighbor's dog, which unfortunately got off the leash, scared the children.", "core": "Dog scared children"},
            {"text": "The annual report, delayed due to technical errors, was published this morning.", "core": "Report was published"},
            {"text": "The new student, sitting in the back row ignoring the lesson, failed the test.", "core": "Student failed"},
            {"text": "The important email, sent to the boss without the attachment, was deleted.", "core": "Email was deleted"},
            {"text": "The test results, arriving from the lab two days late, were normal.", "core": "Results were normal"},
            {"text": "The ER nurse, remaining calm despite the chaos, admitted the patients.", "core": "Nurse admitted patients"},
            {"text": "The package, sent from abroad a month ago, was lost in transit.", "core": "Package was lost"},
            {"text": "The red car, trying to overtake the truck recklessly, went off the road.", "core": "Car went off road"}
        ]
    }
}

# --- DATABASE: Chronology ---
# Format: {"text": "Full sentence", "markers": "Before/After", "order": "1. First\n2. Second"}
CHRONO_DB = {
    "he": {
        "Easy": [
            # Home
            {"text": "לפני שאתה נכנס הביתה, נגב את הרגליים.", "markers": "לפני", "order": "1. לנגב רגליים\n2. להיכנס"},
            {"text": "אחרי שתסיים לאכול, שים את הצלחת בכיור.", "markers": "אחרי", "order": "1. לאכול\n2. צלחת בכיור"},
            {"text": "בזמן שהדוד דולק, תכין את הבגדים למקלחת.", "markers": "בזמן", "order": "בו זמנית: דוד דולק + הכנת בגדים"},
            {"text": "כבה את האור בסלון אחרי שכולם הלכו לישון.", "markers": "אחרי", "order": "1. כולם ישנים\n2. לכבות אור"},
            # Work
            {"text": "לפני תחילת המבחן, כבה את הטלפון.", "markers": "לפני", "order": "1. לכבות טלפון\n2. להתחיל מבחן"},
            {"text": "אחרי שתכתוב את המייל, לחץ על שלח.", "markers": "אחרי", "order": "1. לכתוב\n2. לשלוח"},
            {"text": "שמור את הקובץ לפני שתסגור את המחשב.", "markers": "לפני", "order": "1. לשמור\n2. לסגור"},
            # Health
            {"text": "לפני שאתה בולע כדור, שתה מים.", "markers": "לפני", "order": "1. לשתות\n2. לבלוע"},
            {"text": "שטוף את הפצע לפני שתשים פלסטר.", "markers": "לפני", "order": "1. לשטוף\n2. פלסטר"},
            # Errands
            {"text": "לפני שתחצה את הכביש, הבט לכל הצדדים.", "markers": "לפני", "order": "1. להביט\n2. לחצות"},
            {"text": "שלם לנהג אחרי שעלית לאוטובוס.", "markers": "אחרי", "order": "1. לעלות\n2. לשלם"},
            {"text": "הוצא כסף לפני שתכנס לחנות.", "markers": "לפני", "order": "1. להוציא כסף\n2. להיכנס"}
        ],
        "Hard": [
            # Home
            {"text": "אחרי שהאורחים ילכו, נשטוף כלים, אבל קודם נכניס את האוכל למקרר.", "markers": "אחרי, קודם", "order": "1. אורחים הולכים\n2. אוכל למקרר\n3. לשטוף כלים"},
            {"text": "אל תוציא את העוגה מהתבנית לפני שהיא התקררה לגמרי.", "markers": "לפני (שלילה)", "order": "1. עוגה מתקררת\n2. להוציא"},
            {"text": "לפני שתפעיל מכונת כביסה, בדוק כיסים, ואל תשכח להוסיף מרכך.", "markers": "לפני", "order": "1. לבדוק כיסים\n2. להוסיף מרכך\n3. להפעיל"},
            # Work
            {"text": "לפני שליחת המייל למנהל, צרף את הקובץ, אך וודא קודם לכן שתיקנת שגיאות.", "markers": "לפני, קודם לכן", "order": "1. לתקן שגיאות\n2. לצרף קובץ\n3. לשלוח"},
            {"text": "אחרי שתצא מהפגישה, שלח סיכום לצוות, אבל קודם התקשר ללקוח.", "markers": "אחרי, קודם", "order": "1. לצאת מפגישה\n2. להתקשר ללקוח\n3. לשלוח סיכום"},
            # Health
            {"text": "אל תקום מהמיטה לפני שהאחות תמדוד לך לחץ דם, וגם אז עשה זאת לאט.", "markers": "לפני (שלילה)", "order": "1. מדידת לחץ דם\n2. לקום"},
            {"text": "אחרי שתסיים את האנטיביוטיקה, גש לרופא, אך לפני כן קבע תור.", "markers": "אחרי, לפני כן", "order": "1. לסיים תרופה\n2. לקבוע תור\n3. לגשת לרופא"},
            # Errands
            {"text": "אחרי שתצא מהחניון, פנה ימינה, אבל קודם לכן שלם במכונה.", "markers": "אחרי, קודם לכן", "order": "1. לשלם\n2. לצאת\n3. לפנות"},
            {"text": "לפני שתתחיל בנסיעה, חגור חגורה, אך עשה זאת רק אחרי שכוונת מראות.", "markers": "לפני, אחרי", "order": "1. לכוון מראות\n2. לחגור\n3. לנסוע"},
            {"text": "הזמן את המונית אחרי שהתארגנת, אך לפני שירדת לרחוב.", "markers": "אחרי, לפני", "order": "1. להתארגן\n2. להזמין\n3. לרדת לרחוב"}
        ]
    },
    "en": {
        "Easy": [
            {"text": "Before you enter the house, wipe your feet.", "markers": "Before", "order": "1. Wipe feet\n2. Enter"},
            {"text": "After you finish eating, put the plate in the sink.", "markers": "After", "order": "1. Finish eating\n2. Plate in sink"},
            {"text": "While the boiler is on, prepare your clothes.", "markers": "While", "order": "Simultaneous"},
            {"text": "Before starting the test, turn off your phone.", "markers": "Before", "order": "1. Turn off phone\n2. Start test"},
            {"text": "After you write the email, click send.", "markers": "After", "order": "1. Write\n2. Send"},
            {"text": "Save the file before you close the laptop.", "markers": "Before", "order": "1. Save\n2. Close"},
            {"text": "Before swallowing the pill, drink water.", "markers": "Before", "order": "1. Drink\n2. Swallow"},
            {"text": "Wash the wound before putting on a bandage.", "markers": "Before", "order": "1. Wash\n2. Bandage"},
            {"text": "Before crossing the street, look both ways.", "markers": "Before", "order": "1. Look\n2. Cross"},
            {"text": "Pay the driver after you get on the bus.", "markers": "After", "order": "1. Get on\n2. Pay"}
        ],
        "Hard": [
            {"text": "After the guests leave, we'll wash dishes, but first put the food in the fridge.", "markers": "After, First", "order": "1. Guests leave\n2. Food in fridge\n3. Wash dishes"},
            {"text": "Don't take the cake out before it cools down completely.", "markers": "Before (Not)", "order": "1. Cool down\n2. Take out"},
            {"text": "Before starting the machine, check pockets and don't forget to add softener.", "markers": "Before", "order": "1. Check pockets\n2. Add softener\n3. Start"},
            {"text": "Before sending the email, attach the file, but first check for errors.", "markers": "Before, First", "order": "1. Check errors\n2. Attach file\n3. Send"},
            {"text": "After leaving the meeting, send a summary, but call the client first.", "markers": "After, First", "order": "1. Leave meeting\n2. Call client\n3. Send summary"},
            {"text": "Don't get out of bed before the nurse checks your blood pressure.", "markers": "Before (Not)", "order": "1. Check BP\n2. Get up"},
            {"text": "After finishing the antibiotics, see the doctor, but make an appointment first.", "markers": "After, First", "order": "1. Finish meds\n2. Appointment\n3. See doctor"},
            {"text": "After leaving the garage, turn right, but pay at the machine first.", "markers": "After, First", "order": "1. Pay\n2. Leave\n3. Turn right"},
            {"text": "Before driving, fasten your seatbelt, but only after adjusting the mirrors.", "markers": "Before, After", "order": "1. Adjust mirrors\n2. Fasten belt\n3. Drive"},
            {"text": "Call the taxi after you get ready, but before you go downstairs.", "markers": "After, Before", "order": "1. Get ready\n2. Call taxi\n3. Go downstairs"}
        ]
    }
}

# --- Sequencing Vocabulary ---
SEQUENCING_VOCAB = ["Cat", "Dog", "Table", "Chair", "Car", "Bus", "Bread", "Apple", "Ring", "Watch", "Lamp", "Fan", "Book", "Pen", "Cup", "Key", "Shirt", "Shoe", "Door", "Wall"]

class TrainingGenerator:
    def __init__(self, lang, gender):
        self.lang = lang
        self.gender = gender

    def gen_instr(self, inv, steps, comp):
        objs = [x.strip() for x in inv.split(",") if x.strip()] or ["pen", "cup"]
        if self.lang == "en":
            acts = ["put the {obj} in the box", "touch the {obj}", "lift the {obj}"]
            res = []
            for _ in range(steps):
                o = random.choice(objs)
                res.append(random.choice(acts).format(obj=o))
        else:
            acts = [("שים את", "שימי את", "בקופסה"), ("גע ב", "געי ב", ""), ("הרם את", "הרימי את", "")]
            res = []
            for _ in range(steps):
                o = random.choice(objs)
                a = random.choice(acts)
                v = a[0] if self.gender == "Male" else a[1]
                res.append(f"{v} {o} {a[2]}".strip())
        
        txt = ". ".join(res) + "."
        return txt, txt, "", "", ""

    def gen_seq(self, length, voice_id):
        words = random.sample(SEQUENCING_VOCAB, length)
        display = ", ".join(words)
        # Natural pause using periods
        audio_text = ".  ".join(words) + "." 
        return display, audio_text, "", "", ""

    def gen_svo(self, complexity):
        # Retrieve from DB
        pool = SVO_DB[self.lang][complexity]
        item = random.choice(pool)
        return item["text"], item["text"], item["core"], "", ""

    def gen_chrono(self, complexity):
        # Retrieve from DB
        pool = CHRONO_DB[self.lang][complexity]
        item = random.choice(pool)
        return item["text"], item["text"], "", item["markers"], item["order"]

async def _play(text, voice, rate="+0%"):
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

    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, "Male" if g_sel in ["אתה", "Male"] else "Female")
        
        if mode == txt["mode_instructions"]: 
            d, a, s, m, o = gen.gen_instr(inv, steps, comp); r = "+0%"
        elif mode == txt["mode_sequencing"]: 
            d, a, s, m, o = gen.gen_seq(seq_l, v_id); r = "-20%"
        elif mode == txt["mode_summarization"]: 
            d, a, s, m, o = gen.gen_svo(comp); r = "+0%"
        else: 
            d, a, s, m, o = gen.gen_chrono(comp); r = "+0%"
        
        st.session_state.display = d
        st.session_state.summary = s
        st.session_state.markers = m
        st.session_state.order = o
        st.session_state.revealed = False
        st.session_state.curr_mode = mode.split(".")[1].strip()
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
                
            if st.session_state.markers:
                c1, c2 = st.columns(2)
                with c1: st.write(f"**{txt['chrono_markers_header']}**"); st.warning(st.session_state.markers)
                with c2: st.write(f"**{txt['chrono_order_header']}**"); st.success(st.session_state.order)
            
            c1, c2, _ = st.columns([1,1,3])
            if c1.button(txt["correct_btn"]):
                st.session_state.score += 1; st.session_state.total += 1
                st.session_state.history.append({"mode": st.session_state.curr_mode, "level": st.session_state.curr_level, "result": "✅"})
                st.session_state.display = ""; st.session_state.audio = None; st.rerun()
            if c2.button(txt["incorrect_btn"]):
                st.session_state.total += 1
                st.session_state.history.append({"mode": st.session_state.curr_mode, "level": st.session_state.curr_level, "result": "❌"})
                st.session_state.display = ""; st.session_state.audio = None; st.rerun()

    st.markdown("---")
    st.metric(txt["score_label"], f"{st.session_state.score} / {st.session_state.total}")
    
    if st.session_state.history:
        st.subheader(txt["history_label"])
        df = pd.DataFrame(st.session_state.history)
        df.columns = txt["table_cols"][1:]
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
        if st.button(txt["clear_history"]):
            st.session_state.history = []; st.session_state.score = 0; st.session_state.total = 0; st.rerun()

if __name__ == "__main__":
    main()
