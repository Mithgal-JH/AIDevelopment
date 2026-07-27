from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# -------- intents باستخدام Regex مرن --------
intents = {

    "add_drop":
    r"(سحب|انسحاب|إضافة|استبدال|تسجيل).*?(مادة|مواد|مساق)?|(مادة|مساق).*?(سحب|إضافة)",

    "postpone":
    r"(تأجيل|إرجاء|توقف).*?(دراسة)?|كيف.*?(أؤجل|تأجيل)",

    "exams":
    r"(امتحان|اختبار).*?(نهائي)?|(علامة|نتيجة).*?(امتحان)?",

    "warning":
    r"(تحذير).*?(أكاديمي)?|(معدل).*?(تراكمي).*?(منخفض)?",

    "graduation":
    r"(تخرج|شهادة).*?(بكالوريوس)?|ما.*?(شروط).*?(التخرج)",

    "excellence":
    r"(منحة|تفوق).*?(جامعة)?|(معدل).*?(95)"
}

# -------- responses مختصرة --------
responses = {

    "add_drop":
    "يمكن السحب أو الإضافة خلال الأسبوع الأول دون خسارة الرسوم، وبعد ذلك وحتى الأسبوع العاشر تظهر المادة بعلامة W.",

    "postpone":
    "يمكن تأجيل الدراسة لمدة لا تتجاوز سنتين، ويجب تقديم الطلب خلال الأسبوع الأول من الفصل.",

    "exams":
    "علامة المساق تشمل أعمال الفصل وامتحان نهائي، ويمكن طلب مراجعة العلامة خلال 3 أيام.",

    "warning":
    "يوجه تحذير أكاديمي إذا انخفض المعدل التراكمي عن 65% أو المعدل التخصصي عن 70%.",

    "graduation":
    "للتخرج يجب إنهاء جميع المواد بنجاح ومعدل عام 65% ومعدل تخصصي 70% مع التدريب الميداني.",

    "excellence":
    "منحة التفوق تمنح إذا كان المعدل الفصلي 95% أو أكثر وكان الطالب ناجحاً في 15 ساعة."
}

# -------- تحية --------
greetings = r"(مرحبا|أهلا|السلام عليكم)"


# -------- منطق الرد --------
def get_bot_response(message):

    msg = message.strip()

    if msg == "مسح":
        return "تم مسح المحادثة."

    if msg == "خروج":
        return "تم إغلاق البوت."

    # التحية
    if re.search(greetings, msg, re.IGNORECASE):
        return "مرحبًا بك في المساعد الأكاديمي لجامعة بوليتكنك فلسطين."

    # البحث في intents
    for intent, pattern in intents.items():

        if re.search(pattern, msg, re.IGNORECASE):

            return responses[intent]

    return "لم أفهم السؤال. يمكنك السؤال عن السحب والإضافة أو التأجيل أو الامتحانات أو التخرج."


# -------- routes --------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    message = request.form.get("message")

    response = get_bot_response(message)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
