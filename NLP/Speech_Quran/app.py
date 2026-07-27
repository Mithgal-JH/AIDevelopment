from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from enum import Enum
import time
import re

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ===== البيانات =====
SURAH = {
    "al_kawthar": [
        "انا اعطيناك الكوثر",
        "فصل لربك وانحر",
        "ان شانئك هو الابتر"
    ],
    "al_ikhlas": [
        "قل هو الله احد",
        "الله الصمد",
        "لم يلد ولم يولد",
        "ولم يكن له كفوا احد"
    ],
    "al_nasr": [
        "اذا جاء نصر الله والفتح",
        "ورأيت الناس يدخلون في دين الله افواجا",
        "فسبح بحمد ربك واستغفره",
        "انه كان توابا"
    ]
}


# ===== تطبيع النص العربي =====
def normalize(text):
    # إزالة التشكيل
    text = re.sub(r'[\u0617-\u061A\u064B-\u065F]', '', text)
    # توحيد الهمزات
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ؤئ]', 'ء', text)
    # توحيد الياء
    text = re.sub(r'ى', 'ي', text)
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ===== الحالات =====
class State(Enum):
    IDLE = "idle"
    READING = "reading"
    FINISHED = "finished"


# ===== الأحداث =====
class Event(Enum):
    START = "start"
    CORRECT = "correct"
    WRONG = "wrong"


# ===== تخزين المستخدمين =====
users = {}

def get_user(ip):
    if ip not in users:
        users[ip] = {
            "state": State.IDLE,
            "surah": None,
            "step": 0,
            "start_time": None
        }
    return users[ip]


# ===== آلة الحالات =====
def transition(user, event, payload=None):
    state = user["state"]

    # ===== IDLE =====
    if state == State.IDLE:
        if event == Event.START:
            surah = payload.get("surah")

            if surah not in SURAH:
                return {"status": "error"}

            user["state"] = State.READING
            user["surah"] = surah
            user["step"] = 0
            user["start_time"] = time.time()

            return {
                "status": "started",
                "message": "ابدأ التلاوة الآن",
                "ayah_number": 1
            }

    # ===== READING =====
    elif state == State.READING:
        if event == Event.CORRECT:
            user["step"] += 1

            if user["step"] == len(SURAH[user["surah"]]):
                total_time = round(time.time() - user["start_time"], 2)

                user["state"] = State.IDLE
                user["step"] = 0

                return {
                    "status": "win",
                    "message": f"احسنت 🎉 (الوقت: {total_time} ثانية)"
                }

            return {
                "status": "ok",
                "message": "احسنت ✅",
                "ayah_number": user["step"] + 1
            }

        elif event == Event.WRONG:
            return {
                "status": "wrong",
                "message": "حاول مرة اخرى ❌"
            }

    return {"status": "error"}


# ===== الواجهات =====

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.post("/start")
async def start(req: Request):
    data = await req.json()
    ip = req.client.host

    user = get_user(ip)

    # إعادة تعيين المستخدم دائماً عند الضغط على ابدأ
    user["state"] = State.IDLE
    user["step"] = 0
    user["surah"] = None
    user["start_time"] = None

    return transition(user, Event.START, data)


@app.post("/check")
async def check(req: Request):
    data = await req.json()
    text = data.get("text", "").strip()
    ip = req.client.host

    user = get_user(ip)

    if user["state"] != State.READING:
        return {"status": "error", "message": "اختر سورة أولاً"}

    surah = user["surah"]
    step = user["step"]
    expected = SURAH[surah]

    # مقارنة النص بعد التطبيع
    normalized_text = normalize(text)
    normalized_expected = normalize(expected[step])

    if step < len(expected) and normalized_expected in normalized_text:
        return transition(user, Event.CORRECT)
    else:
        return transition(user, Event.WRONG)