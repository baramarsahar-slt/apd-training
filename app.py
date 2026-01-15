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
        "trainee_gender_label": "Trainee Gender (for grammar):", # English label
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
        # --- השינוי שביקשת כאן ---
        "trainee_gender_label": "באיזו דרך לפנות עם הוראות בשפה העברית?",
        "trainee_gender_opts": ["אתה", "את"],
        # -------------------------
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
    "objects": {
        "עט": "m", "עיפרון": "m", "מחק": "m", "דף": "m", "ספר": "m", "שלט": "m", "טוש": "m", "מפתח": "m",
        "מחברת": "f", "כוס": "f", "קופסה": "f", "מדבקה": "
