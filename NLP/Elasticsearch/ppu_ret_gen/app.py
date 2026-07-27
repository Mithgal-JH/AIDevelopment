# -*- coding: utf-8 -*-
import os, sys, io, logging
import re
from difflib import SequenceMatcher

from flask import Flask, render_template, request, jsonify

# إيقاف رسائل التحديث والرسائل التقنية الخاصة بـ g4f
os.environ['G4F_CHECK_UPDATE'] = 'False'

# كلاس لكتم مخرجات المكتبات في الـ Terminal
class Silence:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

with Silence():
    from elasticsearch import Elasticsearch
    import g4f

app = Flask(__name__)

# إعداد الاتصال بـ Elasticsearch
try:
    es = Elasticsearch("http://localhost:9200")
except Exception as e:
    print(f"❌ خطأ في الاتصال بـ Elasticsearch: {e}")

# قاعدة البيانات المحلية
university_faqs = [
    {"question": "كيف يتم التسجيل؟", "answer": "عبر الموقع الإلكتروني ثم تسليم الأوراق للقبول والتسجيل."},
    {"question": "ما هي الأوراق المطلوبة؟", "answer": "شهادة الثانوية، صورة الهوية، وصور شخصية حديثة."},
    {"question": "كم الرسوم الدراسية؟", "answer": "تبدأ من 500 دينار للفصل وتختلف حسب التخصص."},
    {"question": "هل يوجد تقسيط؟", "answer": "نعم، يمكن دفع رسوم الساعات على ثلاث دفعات."},
    {"question": "ما هي شروط المنح؟", "answer": "معدل فوق 95% للمنحة الكاملة، و90% للمنحة الجزئية."},
    {"question": "خصم الإخوة", "answer": "خصم 15% للأخ الثاني و25% للأخ الثالث."},
    {"question": "مواعيد الدوام", "answer": "من الأحد للخميس، من 8 صباحاً حتى 4 عصراً."},
]

FAQ_KEYWORDS = (
    (
        (
            "تسجيل",
            "قبول",
            "القبول",
            "مسجل",
        ),
        university_faqs[0]["answer"],
    ),
    (
        (
            "أوراق",
            "وثائق",
            "مستندات",
            "مطلوبة",
            "متطلبات",
        ),
        university_faqs[1]["answer"],
    ),
    (
        (
            "رسوم",
            "تكلفة",
            "سعر",
            "السعر",
            "فلوس",
        ),
        university_faqs[2]["answer"],
    ),
    (
        (
            "تقسيط",
            "أقساط",
            "دفعات",
            "التقسيط",
        ),
        university_faqs[3]["answer"],
    ),
    (
        (
            "منح",
            "منحة",
            "البعثة",
            "95",
            "90",
        ),
        university_faqs[4]["answer"],
    ),
    (
        (
            "خصم",
            "إخوة",
            "اخو",
            "الأخ",
            "الاخت",
        ),
        university_faqs[5]["answer"],
    ),
    (
        (
            "دوام",
            " مواعيد ",
            "ساعات",
            "ايام الاسبوع",
            "موعد",
            "اليوم الأحد",
        ),
        university_faqs[6]["answer"],
    ),
)

def setup_db():
    index_name = "uni_db"
    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body={"settings": {"analysis": {"analyzer": {"default": {"type": "arabic"}}}}})
            for i, faq in enumerate(university_faqs):
                es.index(index=index_name, id=i, document=faq)
    except:
        pass


def faq_answer_from_es(user_input):
    """إرجاع إجابة من Elasticsearch عند الإتاحة؛ ولا شيء عند أي فشل (الخدمة لا تعمل أو الفهرس غير جاهز)."""
    try:
        res = es.search(
            index="uni_db",
            query={"match": {"question": {"query": user_input, "fuzziness": "AUTO"}}},
        )
        hits = res["hits"]["hits"]
        if hits and hits[0]["_score"] > 2.0:
            return hits[0]["_source"]["answer"]
    except Exception:
        pass
    return None


def faq_normalize_for_match(text):
    t = "".join(text.split())
    # إزالة علامات ترقيم شائعة دون مساس بالحروف العربية
    return re.sub(r"[\s\-؟!?.,،ـ]+", "", t)


def faq_answer_keyword(user_input):
    """يطابق كلمات مفتاحية عربية شائعة → إجابة ثابتة (لا يعتمد على Elasticsearch ولا على g4f)."""
    u = user_input.strip()
    if not u:
        return None
    for keys, answer in FAQ_KEYWORDS:
        for k in keys:
            if k.strip() and k.strip() in u:
                return answer
    return None


def faq_answer_local(user_input):
    """بديل لا يعتمد على Elasticsearch: مطابقة تقريبية مع قائمة الأسئلة الثابتة."""
    u = faq_normalize_for_match(user_input)
    if not u:
        return None
    best_answer = None
    best_ratio = 0.0
    for faq in university_faqs:
        fq = faq_normalize_for_match(faq["question"])
        ratio = SequenceMatcher(None, u, fq).ratio()
        if fq in u or u in fq:
            ratio = max(ratio, 0.78)
        if ratio > best_ratio:
            best_ratio = ratio
            best_answer = faq["answer"]
    if best_ratio >= 0.5 and best_answer:
        return best_answer
    return None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form.get('message', '').strip()
    if not user_input:
        return jsonify({"answer": "من فضلك اكتب سؤالاً."})

    internal = (
        faq_answer_from_es(user_input)
        or faq_answer_keyword(user_input)
        or faq_answer_local(user_input)
    )
    if internal:
        return jsonify({"answer": f"{internal} (اجابة داخلية)"})

    try:
        with Silence():
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[{"role": "user", "content": f"أجب بالعربية باختصار شديد (أقل من 10 كلمات) عن: {user_input}"}],
                stream=False,
            )
        return jsonify({"answer": f"{response} (اجابة خارجية)"})
    except Exception:
        return jsonify({
            "answer": "عذراً، خدمة الذكاء الاصطناعي الخارجية غير متاحة حالياً. شغّل Elasticsearch على المنفذ 9200 لتفعيل الأسئلة الشائعة من قاعدة البيانات."
        })

if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5001)