import streamlit as st
import random
import edge_tts
import asyncio
import io
import pandas as pd

UI_TEXT = {
    "en": {
        "title": "🎧 APD Training - Speech in Noise",
        "config_header": "⚙️ Configuration",
        "mode_label": "Select Training Mode:",
        "mode_instructions": "1. Instruction Following",
        "mode_sequencing": "2. Auditory Memory (Sequencing)",
        "mode_summarization": "3. Essence Extraction (SVO)",
        "mode_chronology": "4. Chronological Ordering",
        "mode_closure": "5. Auditory Closure (Semantic)",
        "mode_passage": "6. Passage Comprehension",
        "trainee_gender_label": "Trainee Gender:",
        "trainee_gender_opts": ["Male", "Female"],
        "voice_gender": "Voice Speaker Gender:",
        "inventory_label": "Objects:",
        "steps_label": "Steps:",
        "seq_length_label": "Sequence Length:",
        "complexity_label": "Complexity:",
        "play_btn": "▶ PLAY NEW",
        "reveal_btn": "👁 Reveal Target",
        "correct_btn": "✔ Correct",
        "incorrect_btn": "✖ Incorrect",
        "score_label": "Score",
        "history_label": "Session Log:",
        "clear_history": "🗑️ Clear",
        "instr_header": "Full Text:",
        "summary_header": "Target Element:",
        "chrono_markers_header": "Time Markers:",
        "chrono_order_header": "Correct Order:",
        "questions_header": "Comprehension Questions:",
        "answers_header": "Missing Words:",
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
        "mode_closure": "5. סגירות שמיעתית (השלמת חסר)",
        "mode_passage": "6. הבנת קטע משמיעה",
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
        "summary_header": "מילת המטרה / תמצית:",
        "chrono_markers_header": "מילות קישור:",
        "chrono_order_header": "סדר ביצוע נכון:",
        "questions_header": "שאלות הבנה:",
        "answers_header": "מילים חסרות:",
        "noise_header": "🔊 רעש רקע",
        "table_cols": ["#", "סוג", "רמה", "תוצאה"]
    }
}

PASSAGE_DB = {
    "he": [
        {"audio": "הדבורים חיוניות למערכת האקולוגית מכיוון שהן אחראיות על בְּלִיפּ של צמחים רבים. בלעדיהן, יבול הפירות והירקות בעולם ירד בצורה בְּלִיפּ. תהליך זה מתרחש כאשר הדבורה עוברת מפרח לפרח ואוספת בְּלִיפּ. למרבה הצער, בשנים האחרונות אוכלוסיית הדבורים נמצאת בסכנת הכחדה.", "display": "הדבורים חיוניות למערכת האקולוגית מכיוון שהן אחראיות על ____ של צמחים רבים. בלעדיהן, יבול הפירות והירקות בעולם ירד בצורה ____. תהליך זה מתרחש כאשר הדבורה עוברת מפרח לפרח ואוספת ____. למרבה הצער, בשנים האחרונות אוכלוסיית הדבורים נמצאת בסכנת הכחדה.", "questions": "1. מהו התפקיד המרכזי של הדבורים שמוזכר בקטע?\n2. מה יקרה ליבול העולמי אם הדבורים ייעלמו?", "answers": "האבקה | משמעותית/דרסטית | צוף/אבקנים"},
        {"audio": "המהפכה התעשייתית החלה בבריטניה במאה ה-18 ושינתה לחלוטין את ה בְּלִיפּ האנושית. המצאת מנוע ה בְּלִיפּ אפשרה ייצור המוני של סחורות במפעלים. בעקבות זאת, אנשים רבים עזבו את הכפרים ועברו לגור ב בְּלִיפּ כדי למצוא עבודה. מעבר מהיר זה גרם לצפיפות רבה ותנאי מחיה בְּלִיפּ.", "display": "המהפכה התעשייתית החלה בבריטניה במאה ה-18 ושינתה לחלוטין את ה____ האנושית. המצאת מנוע ה____ אפשרה ייצור המוני של סחורות במפעלים. בעקבות זאת, אנשים רבים עזבו את הכפרים ועברו לגור ב____ כדי למצוא עבודה. מעבר מהיר זה גרם לצפיפות רבה ותנאי מחיה ____.", "questions": "1. איזו המצאה טכנולוגית אפשרה את המעבר לייצור המוני?\n2. מדוע אנשים עזבו את אזורי הכפר?", "answers": "היסטוריה/חברה | קיטור | ערים | קשים/גרועים"},
        {"audio": "כוכב הלכת מאדים מסקרן מדענים במשך עשרות שנים בגלל הדמיון שלו ל בְּלִיפּ. רוברטים שנשלחו לחקור את פני השטח גילו ערוצים יבשים, המעידים שבעבר זרמו שם בְּלִיפּ. כיום, האטמוספרה של מאדים דלילה מאוד ואינה מאפשרת בְּלִיפּ של בני אדם ללא חליפות חלל. המטרה הבאה של סוכנויות החלל היא להנחית שם בְּלִיפּ בעשורים הקרובים.", "display": "כוכב הלכת מאדים מסקרן מדענים במשך עשרות שנים בגלל הדמיון שלו ל____. רוברטים שנשלחו לחקור את פני השטח גילו ערוצים יבשים, המעידים שבעבר זרמו שם ____. כיום, האטמוספרה של מאדים דלילה מאוד ואינה מאפשרת ____ של בני אדם ללא חליפות חלל. המטרה הבאה של סוכנויות החלל היא להנחית שם ____ בעשורים הקרובים.", "questions": "1. אילו עדויות נמצאו לכך שמאדים היה שונה בעבר?\n2. מה מונע מבני אדם לחיות כיום על מאדים ללא ציוד מיוחד?", "answers": "כדור הארץ | מים/נהרות | נשימה/הישרדות | אסטרונאוטים/בני אדם"},
        {"audio": "גילוי האנטיביוטיקה בתחילת המאה ה-20 נחשב לאחת מפריצות הדרך החשובות ב בְּלִיפּ. לפני תגלית זו, אפילו זיהום בְּלִיפּ יכול היה להיות קטלני. הפניצילין, שהתגלה כמעט בטעות, מחסל ביעילות בְּלִיפּ מחוללי מחלות. עם זאת, כיום ישנה דאגה עולמית מפני התפתחות של בְּלִיפּ לתרופות אלו בגלל שימוש יתר.", "display": "גילוי האנטיביוטיקה בתחילת המאה ה-20 נחשב לאחת מפריצות הדרך החשובות ב____. לפני תגלית זו, אפילו זיהום ____ יכול היה להיות קטלני. הפניצילין, שהתגלה כמעט בטעות, מחסל ביעילות ____ מחוללי מחלות. עם זאת, כיום ישנה דאגה עולמית מפני התפתחות של ____ לתרופות אלו בגלל שימוש יתר.", "questions": "1. מה הייתה הסכנה בזיהומים לפני תחילת המאה ה-20?\n2. מאיזו תופעה חדשה חוששים הרופאים כיום?", "answers": "רפואה/היסטוריה | פשוט/קל | חיידקים | עמידות"},
        {"audio": "שינה מספקת חיונית לתפקוד תקין של ה בְּלִיפּ והגוף. במהלך שלב שנת החלום, המוח מעבד את ה בְּלִיפּ שנאסף במהלך היום ומקבע אותו בזיכרון. חוסר שינה כרוני עלול להוביל לפגיעה ב בְּלִיפּ ולעלייה בסיכון לתחלואה פיזית. מומחים ממליצים על שבע עד שמונה בְּלִיפּ שינה רצופות בלילה למבוגר.", "display": "שינה מספקת חיונית לתפקוד תקין של ה____ והגוף. במהלך שלב שנת החלום, המוח מעבד את ה____ שנאסף במהלך היום ומקבע אותו בזיכרון. חוסר שינה כרוני עלול להוביל לפגיעה ב____ ולעלייה בסיכון לתחלואה פיזית. מומחים ממליצים על שבע עד שמונה ____ שינה רצופות בלילה למבוגר.", "questions": "1. מה תפקידו של המוח במהלך שנת החלום?\n2. אילו שתי השלכות שליליות יש לחוסר שינה כרוני?", "answers": "מוח | מידע | ריכוז/קשב | שעות"},
        {"audio": "בתקופות של אינפלציה, ערך ה בְּלִיפּ נשחק והמחירים של מוצרי צריכה בסיסיים עולים. הבנק המרכזי מנסה בדרך כלל לבלום את התופעה על ידי העלאת ה בְּלִיפּ. צעד זה מייקר את ההלוואות וגורם לאנשים ולחברות להוציא פחות בְּלִיפּ. המטרה הסופית היא להקטין את ה בְּלִיפּ במשק וכך לעצור את עליית המחירים.", "display": "בתקופות של אינפלציה, ערך ה____ נשחק והמחירים של מוצרי צריכה בסיסיים עולים. הבנק המרכזי מנסה בדרך כלל לבלום את התופעה על ידי העלאת ה____. צעד זה מייקר את ההלוואות וגורם לאנשים ולחברות להוציא פחות ____. המטרה הסופית היא להקטין את ה____ במשק וכך לעצור את עליית המחירים.", "questions": "1. מה קורה לערך הכסף בזמן אינפלציה?\n2. מה המטרה של ייקור ההלוואות במשק?", "answers": "כסף/מטבע | ריבית | כסף/כספים | ביקוש"},
        {"audio": "התחממות כדור הארץ גורמת להמסה מואצת של ה בְּלִיפּ בקטבים. תהליך זה מוביל לעלייה במפלס מי ה בְּלִיפּ ומאיים על ערי חוף רבות בעולם מהצפה. כדי למנוע אסון אקולוגי, מדינות חתמו על אמנות לצמצום פליטת גזי בְּלִיפּ. המעבר לאנרגיות מתחדשות, כמו אנרגיית ה בְּלִיפּ, הוא צעד הכרחי במאבק זה.", "display": "התחממות כדור הארץ גורמת להמסה מואצת של ה____ בקטבים. תהליך זה מוביל לעלייה במפלס מי ה____ ומאיים על ערי חוף רבות בעולם מהצפה. כדי למנוע אסון אקולוגי, מדינות חתמו על אמנות לצמצום פליטת גזי ____. המעבר לאנרגיות מתחדשות, כמו אנרגיית ה____, הוא צעד הכרחי במאבק זה.", "questions": "1. מהו האיום המרכזי שמרחף מעל ערי חוף?\n2. איזה צעד מעשי נדרש כדי להילחם בהתחממות, על פי הקטע?", "answers": "קרחונים | ים | חממה | שמש/רוח"},
        {"audio": "התזונה הים-תיכונית נחשבת לאחת הדיאטות ה בְּלִיפּ ביותר בעולם. היא מבוססת על צריכה גבוהה של ירקות, פירות, ושמן בְּלִיפּ. מחקרים מראים שתזונה כזו מפחיתה משמעותית את הסיכון למחלות בְּלִיפּ. בנוסף, היא מעודדת צריכת דגים ועוף על פני בשר בְּלִיפּ, מה שתורם לאיזון הכולסטרול בדם.", "display": "התזונה הים-תיכונית נחשבת לאחת הדיאטות ה____ ביותר בעולם. היא מבוססת על צריכה גבוהה של ירקות, פירות, ושמן ____. מחקרים מראים שתזונה כזו מפחיתה משמעותית את הסיכון למחלות ____. בנוסף, היא מעודדת צריכת דגים ועוף על פני בשר ____, מה שתורם לאיזון הכולסטרול בדם.", "questions": "1. מהם המרכיבים העיקריים שעליהם מבוססת התזונה הים-תיכונית?\n2. מדוע הדיאטה הזו תורמת לאיזון הכולסטרול?", "answers": "בריאות/מומלצות | זית | לב/כלי דם | אדום/בקר"},
        {"audio": "בינה מלאכותית משנה בקצב מהיר את הדרך שבה אנו עובדים וצורכים בְּלִיפּ. אלגוריתמים מתקדמים מסוגלים לנתח כמויות עצומות של בְּלִיפּ בתוך שניות בודדות. למרות היתרונות הרבים, ישנם חששות כבדים לגבי פגיעה ב בְּלִיפּ של אזרחים וכן מאובדן מקומות עבודה. הרגולטורים בעולם מנסים כעת לנסח בְּלִיפּ שיגבילו את השימוש הלא מבוקר בטכנולוגיה זו.", "display": "בינה מלאכותית משנה בקצב מהיר את הדרך שבה אנו עובדים וצורכים ____. אלגוריתמים מתקדמים מסוגלים לנתח כמויות עצומות של ____ בתוך שניות בודדות. למרות היתרונות הרבים, ישנם חששות כבדים לגבי פגיעה ב____ של אזרחים וכן מאובדן מקומות עבודה. הרגולטורים בעולם מנסים כעת לנסח ____ שיגבילו את השימוש הלא מבוקר בטכנולוגיה זו.", "questions": "1. מהי היכולת המרכזית של האלגוריתמים המוזכרת בקטע?\n2. מדוע רגולטורים מנסים להתערב בתחום זה?", "answers": "מידע/תוכן | נתונים/מידע | פרטיות | חוקים/תקנות"},
        {"audio": "הלווייתן הכחול הוא בעל החיים הגדול ביותר שחי אי פעם על פני ה בְּלִיפּ. למרות ממדיו העצומים, הוא ניזון בעיקר מפלנקטון וסרטנים בְּלִיפּ. הוא לוכד את מזונו על ידי סינון כמות אדירה של בְּלִיפּ דרך מזיפות מיוחדות בפיו. לרוע המזל, ציד מסחרי אינטנסיבי במאה ה-20 הביא את הלווייתן הכחול לסף בְּלִיפּ.", "display": "הלווייתן הכחול הוא בעל החיים הגדול ביותר שחי אי פעם על פני ה____. למרות ממדיו העצומים, הוא ניזון בעיקר מפלנקטון וסרטנים ____. הוא לוכד את מזונו על ידי סינון כמות אדירה של ____ דרך מזיפות מיוחדות בפיו. לרוע המזל, ציד מסחרי אינטנסיבי במאה ה-20 הביא את הלווייתן הכחול לסף ____.", "questions": "1. כיצד צד הלווייתן את מזונו הזעיר?\n2. מה הייתה ההשפעה של בני האדם על בעל חיים זה?", "answers": "כדור הארץ/עולם | קטנים/זעירים | מים | הכחדה"}
    ],
    "en": [
        {"audio": "Bees are essential to the ecosystem because they are responsible for the Bleep of many plants. Without them, the global yield of fruits and vegetables would drop Bleep. This process occurs when a bee moves from flower to flower, collecting Bleep. Unfortunately, in recent years, the bee population has been in danger of extinction.", "display": "Bees are essential to the ecosystem because they are responsible for the ____ of many plants. Without them, the global yield of fruits and vegetables would drop ____. This process occurs when a bee moves from flower to flower, collecting ____. Unfortunately, in recent years, the bee population has been in danger of extinction.", "questions": "1. What is the main role of bees mentioned in the text?\n2. What will happen to the global crop yield if bees disappear?", "answers": "pollination | significantly/drastically | nectar/pollen"},
        {"audio": "The Industrial Revolution began in Britain in the 18th century and completely changed human Bleep. The invention of the Bleep engine allowed for the mass production of goods in factories. Consequently, many people left rural areas and moved to the Bleep to find work. This rapid transition caused severe overcrowding and Bleep living conditions.", "display": "The Industrial Revolution began in Britain in the 18th century and completely changed human ____. The invention of the ____ engine allowed for the mass production of goods in factories. Consequently, many people left rural areas and moved to the ____ to find work. This rapid transition caused severe overcrowding and ____ living conditions.", "questions": "1. Which technological invention allowed the shift to mass production?\n2. Why did people leave the rural areas?", "answers": "history/society | steam | city/cities | harsh/poor"},
        {"audio": "The planet Mars has intrigued scientists for decades due to its similarity to Bleep. Rovers sent to explore its surface discovered dry channels, indicating that Bleep once flowed there. Today, the Martian atmosphere is very thin and does not allow human Bleep without spacesuits. The next goal of space agencies is to land Bleep there in the coming decades.", "display": "The planet Mars has intrigued scientists for decades due to its similarity to ____. Rovers sent to explore its surface discovered dry channels, indicating that ____ once flowed there. Today, the Martian atmosphere is very thin and does not allow human ____ without spacesuits. The next goal of space agencies is to land ____ there in the coming decades.", "questions": "1. What evidence was found showing Mars was different in the past?\n2. What prevents humans from living on Mars today without special equipment?", "answers": "Earth | water/rivers | breathing/survival | humans/astronauts"},
        {"audio": "The discovery of antibiotics in the early 20th century is considered one of the most important breakthroughs in Bleep. Before this discovery, even a Bleep infection could be fatal. Penicillin, discovered almost by accident, effectively destroys disease-causing Bleep. However, today there is global concern regarding the development of Bleep to these drugs due to overuse.", "display": "The discovery of antibiotics in the early 20th century is considered one of the most important breakthroughs in ____. Before this discovery, even a ____ infection could be fatal. Penicillin, discovered almost by accident, effectively destroys disease-causing ____. However, today there is global concern regarding the development of ____ to these drugs due to overuse.", "questions": "1. What was the danger of infections before the early 20th century?\n2. What new phenomenon are doctors concerned about today?", "answers": "medicine/history | simple/minor | bacteria | resistance"},
        {"audio": "Adequate sleep is essential for the proper functioning of the Bleep and body. During the REM sleep stage, the brain processes the Bleep gathered throughout the day and consolidates it into memory. Chronic sleep deprivation can lead to impaired Bleep and an increased risk of physical illness. Experts recommend seven to eight Bleep of continuous sleep per night for an adult.", "display": "Adequate sleep is essential for the proper functioning of the ____ and body. During the REM sleep stage, the brain processes the ____ gathered throughout the day and consolidates it into memory. Chronic sleep deprivation can lead to impaired ____ and an increased risk of physical illness. Experts recommend seven to eight ____ of continuous sleep per night for an adult.", "questions": "1. What is the brain's role during the dream stage of sleep?\n2. What are two negative consequences of chronic sleep deprivation?", "answers": "brain | information | concentration/attention | hours"},
        {"audio": "During periods of inflation, the value of Bleep erodes, and the prices of basic consumer goods rise. The central bank usually attempts to halt this phenomenon by raising the Bleep. This step makes loans more expensive, causing people and companies to spend less Bleep. The ultimate goal is to reduce the Bleep in the market, thereby stopping the price hikes.", "display": "During periods of inflation, the value of ____ erodes, and the prices of basic consumer goods rise. The central bank usually attempts to halt this phenomenon by raising the ____. This step makes loans more expensive, causing people and companies to spend less ____. The ultimate goal is to reduce the ____ in the market, thereby stopping the price hikes.", "questions": "1. What happens to the value of money during inflation?\n2. What is the purpose of making loans more expensive in the economy?", "answers": "money/currency | interest | money/funds | demand"},
        {"audio": "Global warming is causing the accelerated melting of the Bleep at the poles. This process leads to a rise in Bleep levels and threatens many coastal cities around the world with flooding. To prevent an ecological disaster, countries have signed treaties to reduce the emission of Bleep gases. Transitioning to renewable energy, such as Bleep energy, is a necessary step in this struggle.", "display": "Global warming is causing the accelerated melting of the ____ at the poles. This process leads to a rise in ____ levels and threatens many coastal cities around the world with flooding. To prevent an ecological disaster, countries have signed treaties to reduce the emission of ____ gases. Transitioning to renewable energy, such as ____ energy, is a necessary step in this struggle.", "questions": "1. What is the main threat hovering over coastal cities?\n2. What practical step is required to fight global warming according to the text?", "answers": "ice/glaciers | sea/water | greenhouse | solar/wind"},
        {"audio": "The Mediterranean diet is considered one of the most Bleep diets in the world. It is based on a high consumption of vegetables, fruits, and Bleep oil. Studies show that such a diet significantly reduces the risk of Bleep diseases. Additionally, it encourages consuming fish and poultry over Bleep meat, contributing to balanced cholesterol levels in the blood.", "display": "The Mediterranean diet is considered one of the most ____ diets in the world. It is based on a high consumption of vegetables, fruits, and ____ oil. Studies show that such a diet significantly reduces the risk of ____ diseases. Additionally, it encourages consuming fish and poultry over ____ meat, contributing to balanced cholesterol levels in the blood.", "questions": "1. What are the main components the Mediterranean diet is based on?\n2. Why does this diet contribute to balancing cholesterol?", "answers": "healthy/recommended | olive | heart/cardiovascular | red/beef"},
        {"audio": "Artificial intelligence is rapidly changing the way we work and consume Bleep. Advanced algorithms can analyze massive amounts of Bleep within mere seconds. Despite the many benefits, there are heavy concerns regarding the infringement of citizens' Bleep and the loss of jobs. Regulators worldwide are currently trying to draft Bleep that will restrict the unchecked use of this technology.", "display": "Artificial intelligence is rapidly changing the way we work and consume ____. Advanced algorithms can analyze massive amounts of ____ within mere seconds. Despite the many benefits, there are heavy concerns regarding the infringement of citizens' ____ and the loss of jobs. Regulators worldwide are currently trying to draft ____ that will restrict the unchecked use of this technology.", "questions": "1. What is the core capability of the algorithms mentioned in the text?\n2. Why are regulators trying to intervene in this field?", "answers": "information/content | data/information | privacy | laws/regulations"},
        {"audio": "The blue whale is the largest animal to ever live on Bleep. Despite its massive size, it feeds primarily on plankton and tiny Bleep. It catches its food by filtering an enormous amount of Bleep through special baleen plates in its mouth. Unfortunately, intensive commercial whaling in the 20th century brought the blue whale to the brink of Bleep.", "display": "The blue whale is the largest animal to ever live on ____. Despite its massive size, it feeds primarily on plankton and tiny ____. It catches its food by filtering an enormous amount of ____ through special baleen plates in its mouth. Unfortunately, intensive commercial whaling in the 20th century brought the blue whale to the brink of ____.", "questions": "1. How does the whale catch its tiny food?\n2. What was the impact of humans on this animal?", "answers": "Earth/the planet | crustaceans/crabs | water | extinction"}
    ]
}

SVO_DB = {
    "he": {
        "Easy": [
            {"text": "האמא, שישבה במטבח, קילפה תפוח.", "core": "האמא קילפה תפוח"},
            {"text": "הילד, ששיחק בחדר, בנה מגדל.", "core": "הילד בנה מגדל"},
            {"text": "החתול, שישן על הספה, תפס זבוב.", "core": "החתול תפס זבוב"},
            {"text": "השכן, שגר ממול, השקה את הגינה.", "core": "השכן השקה גינה"},
            {"text": "הטלוויזיה, שעבדה כל הלילה, התקלקלה בבוקר.", "core": "הטלוויזיה התקלקלה"},
            {"text": "המרק, שהתבשל בסיר, גלש על הגז.", "core": "המרק גלש"},
            {"text": "הכביסה, שהייתה תלויה בחוץ, התייבשה בשמש.", "core": "הכביסה התייבשה"},
            {"text": "הדלת, שטרקו אותה חזק, ננעלה מבפנים.", "core": "הדלת ננעלה"},
            {"text": "האורחים, שהגיעו מרחוק, הביאו מתנה.", "core": "האורחים הביאו מתנה"},
            {"text": "התינוק, שהתעורר משנתו, בכה בקול.", "core": "התינוק בכה"},
            {"text": "המורה, שנכנסה לכיתה, סגרה את הדלת.", "core": "המורה סגרה דלת"},
            {"text": "המנהל, שישב במשרד, חתם על המסמך.", "core": "המנהל חתם על מסמך"},
            {"text": "הסטודנט, שלמד למבחן, סיכם את החומר.", "core": "הסטודנט סיכם חומר"},
            {"text": "המזכירה, שענתה לטלפון, קבעה פגישה.", "core": "המזכירה קבעה פגישה"},
            {"text": "המחשב, שעשה עדכון, הופעל מחדש.", "core": "המחשב הופעל מחדש"},
            {"text": "הרופא, שבדק את הילד, רשם תרופה.", "core": "הרופא רשם תרופה"},
            {"text": "האחות, שמדדה חום, חייכה לחולה.", "core": "האחות חייכה"},
            {"text": "הפצע, שדמם מעט, נחבש בתחבושת.", "core": "הפצע נחבש"},
            {"text": "הנהג, שעצר ברמזור, צפר למכונית.", "core": "הנהג צפר למכונית"},
            {"text": "השוטר, שעמד בצומת, כיוון את התנועה.", "core": "השוטר כיוון תנועה"}
        ],
        "Hard": [
            {"text": "העוגה החגיגית, שהוכנה במיוחד למסיבת יום ההולדת, נשרפה בתנור.", "core": "העוגה נשרפה"},
            {"text": "המפתח הרזרבי, שהוחבא מתחת לשטיח הכניסה, נאבד אתמול.", "core": "המפתח נאבד"},
            {"text": "הכלב של השכנים, שלמרבה הצער השתחרר מהרצועה, הפחיד את הילדים.", "core": "הכלב הפחיד ילדים"},
            {"text": "המקרר הישן, שהרעיש מאוד במשך כל השבוע האחרון, הפסיק לעבוד.", "core": "המקרר הפסיק לעבוד"},
            {"text": "השטיח בסלון, שהתלכלך מבוץ בגלל הגשם, נשלח לניקוי.", "core": "השטיח נשלח לניקוי"},
            {"text": "המנורה בחדר השינה, שהבהבה כל הזמן והפריעה לישון, נשרפה פתאום.", "core": "המנורה נשרפה"},
            {"text": "הדוד החשמלי, ששכחנו אותו דולק מאז הבוקר, חימם את המים.", "core": "הדוד חימם מים"},
            {"text": "הספה החדשה, שקנינו במבצע מיוחד לפני החג, הגיעה קרועה.", "core": "הספה הגיעה קרועה"},
            {"text": "העציץ במרפסת, שנבל בגלל החום הכבד של הקיץ, פרח מחדש.", "core": "העציץ פרח"},
            {"text": "החלון במטבח, שנשאר פתוח בזמן הסופה החזקה, נשבר לרסיסים.", "core": "החלון נשבר"},
            {"text": "הדו\"ח השנתי, שהתעכב בדפוס בגלל תקלה טכנית, פורסם הבוקר.", "core": "הדו\"ח פורסם"},
            {"text": "הסטודנט החדש, שישב בשורה האחרונה ולא הקשיב, נכשל במבחן.", "core": "הסטודנט נכשל"},
            {"text": "המדפסת במשרד, שנתקעה שוב ושוב במהלך היום, תוקנה לבסוף.", "core": "המדפסת תוקנה"},
            {"text": "המייל החשוב, שנשלח למנהל בטעות ללא הקובץ, נמחק מהשרת.", "core": "המייל נמחק"},
            {"text": "תוצאות הבדיקה, שהגיעו מהמעבדה באיחור של יומיים, היו תקינות.", "core": "התוצאות תקינות"},
            {"text": "האחות במיון, שלמרות העומס הרב שמרה על רוגע, קיבלה את הפצועים.", "core": "האחות קיבלה פצועים"},
            {"text": "הניתוח המורכב, שנמשך שעות רבות בחדר הניתוח, הסתיים בהצלחה.", "core": "הניתוח הסתיים"},
            {"text": "החבילה מהדואר, שנשלחה מחו\"ל לפני כחודש ימים, אבדה בדרך.", "core": "החבילה אבדה"},
            {"text": "המכונית האדומה, שניסתה לעקוף את המשאית בפראות, ירדה לשוליים.", "core": "המכונית ירדה לשוליים"},
            {"text": "הטיסה ללונדון, שהמריאה באיחור בגלל מזג האוויר, נחתה בשלום.", "core": "הטיסה נחתה בשלום"}
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
CHRONO_DB = {
    "he": {
        "Easy": [
            {"text": "לפני שאתה נכנס הביתה, נגב את הרגליים.", "markers": "לפני", "order": "1. לנגב רגליים\n2. להיכנס"},
            {"text": "אחרי שתסיים לאכול, שים את הצלחת בכיור.", "markers": "אחרי", "order": "1. לאכול\n2. צלחת בכיור"},
            {"text": "בזמן שהדוד דולק, תכין את הבגדים למקלחת.", "markers": "בזמן", "order": "בו זמנית: דוד דולק + הכנת בגדים"},
            {"text": "כבה את האור בסלון אחרי שכולם הלכו לישון.", "markers": "אחרי", "order": "1. כולם ישנים\n2. לכבות אור"},
            {"text": "לפני תחילת המבחן, כבה את הטלפון.", "markers": "לפני", "order": "1. לכבות טלפון\n2. להתחיל מבחן"},
            {"text": "אחרי שתכתוב את המייל, לחץ על שלח.", "markers": "אחרי", "order": "1. לכתוב\n2. לשלוח"},
            {"text": "שמור את הקובץ לפני שתסגור את המחשב.", "markers": "לפני", "order": "1. לשמור\n2. לסגור"},
            {"text": "לפני שאתה בולע כדור, שתה מים.", "markers": "לפני", "order": "1. לשתות\n2. לבלוע"},
            {"text": "שטוף את הפצע לפני שתשים פלסטר.", "markers": "לפני", "order": "1. לשטוף\n2. פלסטר"},
            {"text": "לפני שתחצה את הכביש, הבט לכל הצדדים.", "markers": "לפני", "order": "1. להביט\n2. לחצות"},
            {"text": "שלם לנהג אחרי שעלית לאוטובוס.", "markers": "אחרי", "order": "1. לעלות\n2. לשלם"},
            {"text": "הוצא כסף לפני שתכנס לחנות.", "markers": "לפני", "order": "1. להוציא כסף\n2. להיכנס"}
        ],
        "Hard": [
            {"text": "אחרי שהאורחים ילכו, נשטוף כלים, אבל קודם נכניס את האוכל למקרר.", "markers": "אחרי, קודם", "order": "1. אורחים הולכים\n2. אוכל למקרר\n3. לשטוף כלים"},
            {"text": "אל תוציא את העוגה מהתבנית לפני שהיא התקררה לגמרי.", "markers": "לפני (שלילה)", "order": "1. עוגה מתקררת\n2. להוציא"},
            {"text": "לפני שתפעיל מכונת כביסה, בדוק כיסים, ואל תשכח להוסיף מרכך.", "markers": "לפני", "order": "1. לבדוק כיסים\n2. להוסיף מרכך\n3. להפעיל"},
            {"text": "לפני שליחת המייל למנהל, צרף את הקובץ, אך וודא קודם לכן שתיקנת שגיאות.", "markers": "לפני, קודם לכן", "order": "1. לתקן שגיאות\n2. לצרף קובץ\n3. לשלוח"},
            {"text": "אחרי שתצא מהפגישה, שלח סיכום לצוות, אבל קודם התקשר ללקוח.", "markers": "אחרי, קודם", "order": "1. לצאת מפגישה\n2. להתקשר ללקוח\n3. לשלוח סיכום"},
            {"text": "אל תקום מהמיטה לפני שהאחות תמדוד לך לחץ דם, וגם אז עשה זאת לאט.", "markers": "לפני (שלילה)", "order": "1. מדידת לחץ דם\n2. לקום"},
            {"text": "אחרי שתסיים את האנטיביוטיקה, גש לרופא, אך לפני כן קבע תור.", "markers": "אחרי, לפני כן", "order": "1. לסיים תרופה\n2. לקבוע תור\n3. לגשת לרופא"},
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

CLOSURE_DB = {
    "he": {
        "Easy": [
            ("יורד גשם חזק, קח איתך", "מטריה", ""),
            ("כדי לנעול את הדלת, השתמש ב", "מפתח", ""),
            ("השמש זורחת תמיד ב", "מזרח", ""),
            ("חתכתי את העגבנייה בעזרת", "סכין", ""),
            ("הכלב נבח כל הלילה וגרם ל", "רעש", ""),
            ("אני עייף מאוד, אני הולך ל", "ישון", ""),
            ("כשקר בחוץ כדאי ללבוש", "מעיל", ""),
            ("הציפור עפה גבוה ב", "שמיים", ""),
            ("כדי לקנות בסופר צריך לשלם ב", "כסף", ""),
            ("הדג שוחה בתוך ה", "מים", ""),
            ("המורה כותבת על הלוח בעזרת", "גיר", ""),
            ("לפני האוכל חובה לשטוף", "ידיים", ""),
            ("מי שמצייר ציורים הוא", "צייר", ""),
            ("התינוק בוכה כי הוא", "רעב", ""),
            ("כדי להתקשר לאמא אני צריך את ה", "טלפון", ""),
            ("במקום סוכר שתיתי קפה", "מר", ""),
            ("הרכבת נוסעת על גבי ה", "מסילה", ""),
            ("הספרייה היא מקום מלא ב", "ספרים", ""),
            ("כשהרמזור אדום המכונית חייבת ל", "עצור", ""),
            ("ביום הולדת מדליקים נרות על ה", "עוגה", ""),
            ("רופא שיניים מטפל ב", "שיניים", ""),
            ("הפרה אוכלת עשב ונותנת", "חלב", ""),
            ("כדי לראות טוב יותר מרכיבים", "משקפיים", ""),
            ("כשחם מפעילים את ה", "מזגן", ""),
            ("הנגר בונה רהיטים מ", "עץ", ""),
            ("הפועל דופק מסמרים עם", "פטיש", ""),
            ("צבע הדם הוא", "אדום", ""),
            ("אחרי יום ראשון מגיע יום", "שני", ""),
            ("כדי לאפות לחם צריך קודם ללוש את ה", "בצק", ""),
            ("הצמח צריך מים ושמש כדי ל", "גדול", ""),
            ("הדבורה מייצרת בכוורת", "דבש", ""),
            ("שחקן כדורגל בועט ב", "כדור", ""),
            ("הנעל שומרת על כף ה", "רגל", ""),
            ("מי שנוהג במטוס הוא ה", "טייס", ""),
            ("כשהשעון המעורר מצלצל צריך ל", "קום", ""),
            ("המקרר שומר שהאוכל יישאר", "קר", ""),
            ("אחרי הקיץ מגיעה עונת ה", "סתיו", ""),
            ("את הפסולת זורקים לתוך ה", "פח", ""),
            ("את המרק אוכלים בעזרת", "כף", ""),
            ("השמש שוקעת בכל ערב ב", "מערב", ""),
            ("תפוח עץ הוא סוג של", "פרי", ""),
            ("כדי לשטוף את הגוף משתמשים במים ו", "סבון", ""),
            ("השמיכה שומרת עלינו בלילה מה", "קור", ""),
            ("הילד למד לקרוא ול", "כתוב", ""),
            ("כדי לעלות לקומה שנייה משתמשים ב", "מדרגות", ""),
            ("מי שבונה קירות הוא ה", "בנאי", ""),
            ("התלמיד הכין את שיעורי ה", "בית", ""),
            ("בחג חנוכה מדליקים", "חנוכיה", ""),
            ("הירח מופיע בשמיים ב", "לילה", ""),
            ("החלבון בביצה הוא החלק ה", "לבן", "")
        ],
        "Hard": [
            ("למרות שהשקיע שעות רבות בהכנות למבחן, הוא בכל זאת", "נכשל", ""),
            ("לאור הממצאים החדשים שהתגלו במעבדה, הוחלט לשנות את כיוון ה", "מחקר", ""),
            ("כדי להתגבר על ה", "פחד", "שלו קהל, הוא לקח קורס במשחק."),
            ("הוא סירב לשתף פעולה עם החקירה ושמר על זכות ה", "שתיקה", "שלו."),
            ("בגלל הקיצוצים החריפים בתקציב החברה, ההנהלה נאלצה לפטר", "עובדים", ""),
            ("החוזה נחתם רק לאחר ששני הצדדים הגיעו ל", "פשרה", "הוגנת."),
            ("התרופה הניסיונית גרמה לתופעות לוואי חמורות, ולכן ה", "טיפול", "הופסק מיד."),
            ("כדי להוכיח את טענתו בבית המשפט, עורך הדין הציג", "ראיות", "חדשות."),
            ("במקום להתעמת איתו ישירות, היא העדיפה להעביר את המסר ב", "רמיזה", ""),
            ("המשבר הכלכלי העולמי הוביל לעלייה חדה באחוזי ה", "אבטלה", ""),
            ("השופט פסק כי הנאשם פעל בסבירות ומתוך הגנה", "עצמית", ""),
            ("לאחר משא ומתן ממושך אל תוך הלילה, נחתם לבסוף ה", "הסכם", ""),
            ("מערכת החיסון של הגוף פועלת נגד", "חיידקים", "שחודרים מבחוץ."),
            ("האדריכל הגיש לעירייה את ה", "תוכניות", "לאישור בניית המגדל."),
            ("החוקר הגיע למסקנה שהנתונים אינם תומכים ב", "השערה", "המקורית שלו."),
            ("בגלל החשש מהדלפת המידע הרגיש, הישיבה הוגדרה כסודית ו", "סגורה", ""),
            ("חוסר ההסכמה בין חברי הוועדה הוביל לעיכוב משמעותי בקבלת ה", "החלטה", ""),
            ("הסופר הצעיר זכה לשבחים רבים מהמבקרים על ה", "ספר", "הראשון שהוציא."),
            ("על אף שהראיות היו נסיבתיות בלבד, חבר המושבעים הכריז שהוא", "אשם", ""),
            ("החברה פרסמה אזהרת רווח בעקבות ירידה דרסטית ב", "מכירות", "השנה."),
            ("הוא ניסה להסתיר את האמת, אך שפת הגוף שלו הסגירה את ה", "שקר", "שלו."),
            ("הממשלה אישרה חבילת סיוע דחופה כדי לסייע ל", "חקלאים", "שנפגעו בבצורת."),
            ("בעידן הדיגיטלי, שמירה על פרטיות הפכה לאחד ה", "אתגרים", "המשמעותיים ביותר."),
            ("על מנת לשפר את איכות הסביבה, העירייה מעודדת שימוש בתחבורה", "ציבורית", ""),
            ("הפרופסור הידוע הוזמן לשאת את הרצאת ה", "פתיחה", "בכנס הבינלאומי."),
            ("התנאי הקריטי לקבלת המלגה הוא ממוצע ציונים", "גבוה", "במיוחד."),
            ("מחירי הדיור המשיכו לעלות למרות מאמצי הממשלה לקרר את ה", "שוק", ""),
            ("החולה דיווח על הקלה משמעותית בכאב כבר לאחר המנה ה", "ראשונה", "של התרופה."),
            ("התנהגותו התוקפנית לאורך זמן גרמה לבידודו ה", "חברתי", "בכיתה."),
            ("כדי למנוע תקלות עתידיות, יש לבצע תחזוקה", "מונעת", "במכונות האלו."),
            ("הביקורת הקשה שספג בעיתונות הובילה בסופו של דבר ל", "התפטרות", "שלו מהתפקיד."),
            ("השקעה במניות טכנולוגיה נחשבת לעתים להשקעה בעלת סיכון", "גבוה", "יחסית."),
            ("המהנדסים גילו שהקריסה נבעה מפגם חמור ביסודות ה", "מבנה", ""),
            ("חופש הביטוי הוא זכות יסוד בכל חברה", "דמוקרטית", ""),
            ("לצורך הפקת האנרגיה הסולארית נדרש מספר רב של", "קולטנים", "על הגג."),
            ("הדיון נדחה לשבוע הבא עקב היעדרותו הלא צפויה של עורך ה", "דין", ""),
            ("השפעת הרשתות החברתיות על דימוי הגוף של בני נוער היא נושא", "מדאיג", "מאוד."),
            ("החברה הכריזה על ריקול לכל הרכבים מהדגם הזה עקב בעיה ב", "בלמים", ""),
            ("שיבוץ המורים בבתי הספר נעשה בהתאם לאזור ה", "מגורים", "שלהם."),
            ("למרות גילו הצעיר, הוא גילה בגרות רבה והפגין יכולת", "מנהיגות", "מרשימה."),
            ("הטכנולוגיה החדשה מאפשרת אבחון רפואי מהיר ומדויק יותר של", "מחלות", ""),
            ("בעקבות תלונות הצרכנים, החברה החליטה לשנות את אריזת ה", "מוצר", ""),
            ("השופט דחה את העתירה וקבע כי ההליכים התנהלו בצורה", "חוקית", ""),
            ("המסע הקשה במדבר דרש מהם סיבולת פיזית ונפשית כא", "אחת", ""),
            ("השינוי באקלים גורם לתופעות מזג אוויר", "קיצוניות", "ברחבי העולם."),
            ("הפרויקט הוקפא עד לקבלת כל האישורים הנדרשים מטעם ה", "משרד", "להגנת הסביבה."),
            ("הזדקנות האוכלוסייה מציבה בפני מערכת הבריאות", "אתגר", "כלכלי עצום."),
            ("שילוב נשים בתפקידי מפתח בחברה הוא יעד", "אסטרטגי", "של ההנהלה."),
            ("המתחרה הצעיר הצליח להפתיע את כולם ושבר את ה", "שיא", "העולמי."),
            ("הגנה על זכויות יוצרים חיונית לעידוד ה", "יצירה", "האמנותית והמדעית.")
        ]
    },
    "en": {
        "Easy": [
            ("It's raining outside, take an", "umbrella", ""),
            ("To unlock the door, use the", "key", ""),
            ("The sun always rises in the", "east", ""),
            ("I cut the tomato with a", "knife", ""),
            ("The dog barked all night making a lot of", "noise", "")
        ],
        "Hard": [
            ("Despite studying for hours, he still", "failed", "the test."),
            ("Due to the new findings, they changed the direction of the", "research", ""),
            ("To overcome his stage", "fright", "he took acting classes."),
            ("He refused to cooperate and maintained his right to", "silence", ""),
            ("Because of budget cuts, the company had to fire several", "employees", "")
        ]
    }
}

SEQUENCING_VOCAB = ["Cat", "Dog", "Table", "Chair", "Car", "Bus", "Bread", "Apple", "Ring", "Watch", "Lamp", "Fan", "Book", "Pen", "Cup", "Key", "Shirt", "Shoe", "Door", "Wall"]

# --- SMART SHUFFLE ENGINE ---
def get_smart_random_item(db_name, lang, complexity=None):
    state_key = f"pool_{db_name}_{lang}_{complexity}" if complexity else f"pool_{db_name}_{lang}"
    if state_key not in st.session_state or len(st.session_state[state_key]) == 0:
        if db_name == "SVO": pool = SVO_DB[lang][complexity].copy()
        elif db_name == "CHRONO": pool = CHRONO_DB[lang][complexity].copy()
        elif db_name == "CLOSURE": pool = CLOSURE_DB[lang][complexity].copy()
        elif db_name == "PASSAGE": pool = PASSAGE_DB[lang].copy()
        random.shuffle(pool)
        st.session_state[state_key] = pool
    return st.session_state[state_key].pop()

class TrainingGenerator:
    def __init__(self, lang, gender):
        self.lang = lang
        self.gender = gender

    def gen_instr(self, inv, steps, comp):
        objs = [x.strip() for x in inv.split(",") if x.strip()] or ["pen", "cup"]
        acts = [("שים את", "שימי את", "בקופסה"), ("גע ב", "געי ב", "")] if self.lang == "he" else ["put the {obj} in the box"]
        res = []
        for _ in range(steps):
            if self.lang == "he":
                a = random.choice(acts)
                res.append(f"{a[0] if self.gender == 'Male' else a[1]} {random.choice(objs)} {a[2]}".strip())
            else: res.append(f"touch the {random.choice(objs)}")
        txt = ". ".join(res) + "."
        return txt, txt, "", "", "", ""

    def gen_seq(self, length, voice_id):
        words = random.sample(SEQUENCING_VOCAB, length)
        display = ", ".join(words)
        audio_text = ".  ".join(words) + "." 
        return display, audio_text, "", "", "", ""

    def gen_svo(self, complexity):
        item = get_smart_random_item("SVO", self.lang, complexity)
        return item["text"], item["text"], item["core"], "", "", ""

    def gen_chrono(self, complexity):
        item = get_smart_random_item("CHRONO", self.lang, complexity)
        return item["text"], item["text"], "", item["markers"], item["order"], ""

    def gen_closure(self, complexity):
        item = get_smart_random_item("CLOSURE", self.lang, complexity)
        p1, target, p2 = item
        bleep = "בְּלִיפּ" if self.lang == "he" else "Bleep"
        return f"{p1} ____ {p2}".strip(), f"{p1} {bleep}. . . {p2}".strip(), target, "", "", ""

    def gen_passage(self):
        item = get_smart_random_item("PASSAGE", self.lang)
        return item["display"], item["audio"], "", "", "", {"questions": item["questions"], "answers": item["answers"]}

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

    for key in ['audio', 'display', 'summary', 'markers', 'order', 'passage_qa', 'revealed', 'score', 'total', 'history', 'curr_mode', 'curr_level']:
        if key not in st.session_state: st.session_state[key] = None if key == 'audio' else ([] if key == 'history' else (0 if key in ['score', 'total'] else ("" if key not in ['revealed', 'passage_qa'] else (False if key == 'revealed' else None))))

    with st.sidebar:
        st.header(txt["config_header"])
        mode = st.radio(txt["mode_label"], [txt["mode_instructions"], txt["mode_sequencing"], txt["mode_summarization"], txt["mode_chronology"], txt["mode_closure"], txt["mode_passage"]])
        st.markdown("---")
        g_sel = st.selectbox(txt["trainee_gender_label"], txt["trainee_gender_opts"])
        v_sel = st.selectbox(txt["voice_gender"], ["Female", "Male"])
        v_id = ("en-US-AriaNeural" if v_sel == "Female" else "en-US-GuyNeural") if lang == "en" else ("he-IL-HilaNeural" if v_sel == "Female" else "he-IL-AvriNeural")
        
        level_desc = "Standard"
        if mode == txt["mode_instructions"]:
            inv = st.text_area(txt["inventory_label"], value="red pen, blue pen" if lang == "en" else "עט, מחק", height=100)
            steps = st.selectbox(txt["steps_label"], [1, 2, 3])
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
            level_desc = f"{steps} Steps, {comp}"
        elif mode == txt["mode_sequencing"]:
            seq_l = st.slider(txt["seq_length_label"], 3, 8, 4)
            level_desc = f"{seq_l} Items"
        elif mode in [txt["mode_summarization"], txt["mode_chronology"], txt["mode_closure"]]:
            comp = st.selectbox(txt["complexity_label"], ["Easy", "Hard"])
            level_desc = f"{comp}"
        
        st.markdown("---")

    if st.button(txt["play_btn"], type="primary", use_container_width=True):
        gen = TrainingGenerator(lang, "Male" if g_sel in ["אתה", "Male"] else "Female")
        
        if mode == txt["mode_instructions"]: d, a, s, m, o, pqa = gen.gen_instr(inv, steps, comp); r = "+0%"
        elif mode == txt["mode_sequencing"]: d, a, s, m, o, pqa = gen.gen_seq(seq_l, v_id); r = "-20%"
        elif mode == txt["mode_summarization"]: d, a, s, m, o, pqa = gen.gen_svo(comp); r = "+0%"
        elif mode == txt["mode_chronology"]: d, a, s, m, o, pqa = gen.gen_chrono(comp); r = "+0%"
        elif mode == txt["mode_closure"]: d, a, s, m, o, pqa = gen.gen_closure(comp); r = "+0%"
        elif mode == txt["mode_passage"]: d, a, s, m, o, pqa = gen.gen_passage(); r = "+0%"
        
        st.session_state.display, st.session_state.summary, st.session_state.markers, st.session_state.order, st.session_state.passage_qa = d, s, m, o, pqa
        st.session_state.revealed = False
        st.session_state.curr_mode, st.session_state.curr_level = mode.split(".")[1].strip(), level_desc
        
        with st.spinner("..."): st.session_state.audio = asyncio.run(_play(a, v_id, r))

    if st.session_state.audio: st.audio(st.session_state.audio)

    if st.session_state.display:
        st.markdown("---")
        if not st.session_state.revealed:
            if st.button(txt["reveal_btn"]): st.session_state.revealed = True; st.rerun()
        else:
            st.write(f"**{txt['instr_header']}**"); st.info(st.session_state.display)
            if st.session_state.summary: st.write(f"**{txt['summary_header']}**"); st.success(st.session_state.summary)
            if st.session_state.markers:
                c1, c2 = st.columns(2)
                with c1: st.write(f"**{txt['chrono_markers_header']}**"); st.warning(st.session_state.markers)
                with c2: st.write(f"**{txt['chrono_order_header']}**"); st.success(st.session_state.order)
            if st.session_state.passage_qa:
                st.write(f"**{txt['questions_header']}**"); st.warning(st.session_state.passage_qa["questions"])
                st.write(f"**{txt['answers_header']}**"); st.success(st.session_state.passage_qa["answers"])
            
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
        if st.button(txt["clear_history"]): st.session_state.history = []; st.session_state.score = 0; st.session_state.total = 0; st.rerun()

if __name__ == "__main__":
    main()
