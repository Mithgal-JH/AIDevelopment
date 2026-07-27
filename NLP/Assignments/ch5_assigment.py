from __future__ import annotations
import re
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
CORS(app)  # للسماح بالاتصال من HTML/JS

# ================== البيانات ==================
messages: List[str] = [
    # تحيات
    "مرحبا","أهلا","صباح الخير","مساء الخير","مرحباً بك",
    "سلام","كيف الحال؟","يا هلا","أهلاً وسهلاً","مرحبا صديقي",
    # حالة الطلب
    "أين طلبي؟","تابع طلبي","حالة الطلب","رقم طلبي","هل تم شحن طلبي؟",
    "أريد معرفة حالة طلبي","ما حالة طلبي؟","تتبع الشحنة","هل طلبي في الطريق؟","تحقق من طلبي",
    # تقييم الخدمة
    "خدمتكم ممتازة","أحب خدمتكم","لست راضياً عن طلبي الأخير",
    "تجربة رائعة","محبط من طلبي الأخير","شكراً على الدعم","خدمة رائعة","غير راضٍ عن المنتج",
    "دعم ممتاز","أقدر مساعدتكم السريعة",
    # التوصيل
    "هل لديكم خدمة التوصيل؟","هل يمكن توصيل الطعام للمنزل؟",
    "هل التوصيل متاح في منطقتي؟","ما ساعات التوصيل؟","كم تكلفة التوصيل؟",
    "هل لديكم توصيل نفس اليوم؟","أريد توصيل طلبي الآن","هل التوصيل مجاني؟",
    "أخبرني عن خيارات التوصيل","هل توصلون ليلاً؟",
    # إلغاء الطلب
    "أريد إلغاء طلبي","ألغِ طلبي","أوقف طلبي الآن","كيف ألغي طلبي؟",
    "غيرت رأيي وأريد الإلغاء","هل يمكنني إلغاء الطلب؟","أحتاج لإلغاء طلبي",
    "أوقف الطلب #123","إلغاء الطلب","أريد إلغاء طلبي رقم 456",
    # الاتصال بالمدير
    "أريد التحدث للمدير","هل يمكن الاتصال بالمدير؟","وصلني بالمدير",
    "أحتاج للمدير","كيف أتواصل مع المدير؟","دعني أتكلم مع المشرف",
    "المدير رجاءً","هل يمكن للمدير الاتصال بي؟","لدي شكوى للمدير",
    "أريد رقم المدير"
]

labels: List[str] = [
    # تحيات
    *["greeting"]*10,
    # حالة الطلب
    *["order_status"]*10,
    # تقييم الخدمة
    *["feedback"]*10,
    # التوصيل
    *["delivery_service"]*10,
    # إلغاء الطلب
    *["cancel_order"]*10,
    # الاتصال بالمدير
    *["contact_manager"]*10,
]

# ================== النموذج ==================
vectorizer = TfidfVectorizer(lowercase=True, strip_accents="unicode")
X = vectorizer.fit_transform(messages)

clf = LogisticRegression(max_iter=400, class_weight="balanced", random_state=42)
clf.fit(X, labels)

# ================== الدوال ==================
def predict_intent(message: str) -> str:
    features = vectorizer.transform([message])
    return str(clf.predict(features)[0])

def extract_order_id(message: str) -> str | None:
    match = re.search(r"\b(?:رقم\s*الطلب|#)?\s*(\d{2,8})\b", message)
    if match:
        return match.group(1)
    return None

def build_response(intent: str, message: str) -> Dict[str, str]:
    order_id = extract_order_id(message)

    responses = {
        "greeting": "أهلاً وسهلاً! كيف يمكنني مساعدتك اليوم؟",
        "order_status": (
            f"طلبك #{order_id} قيد التحضير وسيصلك خلال 25-35 دقيقة." if order_id
            else "أستطيع التحقق من حالة طلبك، من فضلك زودني برقم الطلب."
        ),
        "feedback": "شكراً لتقييمك! رأيك يساعدنا على تحسين خدماتنا.",
        "delivery_service": (
            "نعم، نقدم خدمة التوصيل يومياً من 10 صباحاً حتى 11 مساءً. "
            "رسوم التوصيل 2.99$، والتوصيل مجاني للطلبات فوق 30$."
        ),
        "cancel_order": (
            f"يمكنني إلغاء طلبك #{order_id}. الرجاء التأكيد بكتابة: تأكيد إلغاء {order_id}" if order_id
            else "يمكنني مساعدتك في إلغاء طلبك، يرجى تزويدي برقم الطلب."
        ),
        "contact_manager": (
            "يمكنك التواصل مع المدير على الرقم +970-599-XXX-XXX أو البريد manager@jerusalemrestaurant.com"
        ),
    }

    return {
        "intent": intent,
        "reply": responses.get(
            intent,
            "عذراً، لم أفهم. يمكنك السؤال عن حالة الطلب، التوصيل، الإلغاء أو الاتصال بالمدير."
        )
    }

# ================== الراوتات ==================
@app.get("/")
def home():
    return render_template("index.html")  # رابط لملف HTML

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"intent": "unknown", "reply": "الرجاء كتابة رسالة."}), 400

    intent = predict_intent(message)
    return jsonify(build_response(intent, message))

# ================== تشغيل السيرفر ==================
if __name__ == "__main__":
    app.run(debug=True)