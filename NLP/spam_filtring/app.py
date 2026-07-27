from collections import Counter

import numpy as np
from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import os

# Get the directory where this script is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Create Flask app with explicit paths for templates and static files
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static'),
    static_url_path='/static'
)


# -------------------------
# 1) Cosine similarity Arabic dataset
# -------------------------
cosine_emails = [
    {"text": "اربح جوائز كبيرة الآن", "label": "Spam"},
    {"text": "احصل على قرض سريع بدون فائدة", "label": "Spam"},
    {"text": "فوز مضمون بالهاتف الجديد", "label": "Spam"},
    {"text": "فرصة لا تعوض للحصول على هاتف مجاني", "label": "Spam"},
    {"text": "اضغط هنا للفوز بجائزة نقدية", "label": "Spam"},
    {"text": "تحصل على بطاقة هدية مجانا اليوم", "label": "Spam"},
    {"text": "اجتماع الفريق غدًا الساعة 10 صباحًا", "label": "Important"},
    {"text": "تقرير المبيعات لشهر سبتمبر", "label": "Important"},
    {"text": "دعوة لحضور مؤتمر التقنية", "label": "Important"},
    {"text": "يرجى مراجعة مستندات المشروع", "label": "Important"},
    {"text": "جدول العمل الأسبوع القادم", "label": "Important"},
    {"text": "تحديث على حالة الطلبية الخاصة بك", "label": "Important"},
]

cosine_corpus = [item["text"] for item in cosine_emails]
cosine_labels = [item["label"] for item in cosine_emails]
cosine_vectorizer = CountVectorizer()
cosine_matrix = cosine_vectorizer.fit_transform(cosine_corpus)


def classify_with_cosine(text: str) -> str:
    new_vec = cosine_vectorizer.transform([text])
    similarities = cosine_similarity(new_vec, cosine_matrix)
    most_similar_idx = int(np.argmax(similarities))
    return cosine_labels[most_similar_idx]


# -------------------------
# 2) Shared English dataset for NB + LR
# -------------------------
email_texts = [
    "Congratulations! You've won a $1,000 gift",
    "Lowest prices on meds, order now",
    "Limited time offer, buy now",
    "You have been selected for a prize",
    "Earn money quickly from home",
    "Get rich fast with this simple trick",
    "Exclusive deal just for you",
    "Click here to claim your reward",
    "Special discount on all products",
    "Win a brand new phone today",
    "Free vacation offer just for you",
    "Act now to receive your bonus",
    "Cheap loans available instantly",
    "You are a lucky winner",
    "Claim your free coupon today",
    "Hot deals on electronics, buy today",
    "This is not a scam, claim now",
    "Unlock your reward by clicking here",
    "Special promotion ends tonight",
    "Double your income easily",
    "Reminder: Team meeting tomorrow at 9AM",
    "Can you review the Q2 report before lunch?",
    "Please find attached the project budget",
    "Let's schedule a meeting for next week",
    "Update on the client project status",
    "Please confirm your attendance",
    "Here is the report you requested",
    "Deadline for submission is Friday",
    "Team lunch has been rescheduled",
    "Kindly review and provide feedback",
    "Meeting agenda for tomorrow attached",
    "Project update and next steps",
    "Please review the attached document",
    "Your appointment is confirmed",
    "Let's finalize the report today",
    "Important notice regarding your account",
    "Client meeting scheduled at 2 PM",
    "Submit your assignment by tonight",
    "Please update the spreadsheet",
    "Follow up on previous discussion",
]

email_labels = ["spam"] * 20 + ["important"] * 20

tfidf_vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
X_all = tfidf_vectorizer.fit_transform(email_texts)

# Keep same split style as your code
X_train, X_test, y_train, y_test = train_test_split(
    X_all, email_labels, test_size=0.25, random_state=1
)

nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)

lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)


def classify_with_nb(text: str) -> str:
    features = tfidf_vectorizer.transform([text])
    return str(nb_model.predict(features)[0])


def classify_with_lr(text: str) -> str:
    features = tfidf_vectorizer.transform([text])
    return str(lr_model.predict(features)[0])


def final_vote(cosine_label: str, nb_label: str, lr_label: str) -> str:
    normalized = [
        "spam" if cosine_label.lower() == "spam" else "important",
        nb_label.lower(),
        lr_label.lower(),
    ]
    return Counter(normalized).most_common(1)[0][0]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/classify", methods=["POST"])
def classify():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter an email/message to classify."}), 400

    cosine_label = classify_with_cosine(text)
    nb_label = classify_with_nb(text)
    lr_label = classify_with_lr(text)
    final_label = final_vote(cosine_label, nb_label, lr_label)

    return jsonify(
        {
            "input": text,
            "cosine_similarity": cosine_label,
            "naive_bayes": nb_label,
            "logistic_regression": lr_label,
            "final_prediction": final_label,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
