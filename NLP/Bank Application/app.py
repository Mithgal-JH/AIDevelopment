from flask import Flask, jsonify, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)


def build_dataset() -> pd.DataFrame:
    """Create a 30-row churn training dataset."""
    data = {
        "Age": [
            22, 25, 27, 29, 31, 33, 35, 37, 39, 41,
            24, 26, 28, 30, 32, 34, 36, 38, 40, 42,
            23, 27, 31, 35, 39, 43, 45, 47, 49, 51
        ],
        "Monthly_Income": [
            1800, 2200, 2500, 2800, 3200, 3600, 4000, 4500, 5000, 5500,
            2000, 2300, 2600, 3000, 3400, 3800, 4200, 4700, 5200, 5800,
            1900, 2700, 3300, 4100, 4900, 6000, 6500, 7000, 7600, 8200
        ],
        "Years_With_Company": [
            1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
            1, 2, 2, 3, 3, 4, 4, 5, 5, 6,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        ],
        "Num_Products": [
            1, 1, 1, 2, 2, 2, 2, 3, 3, 3,
            1, 1, 2, 2, 2, 3, 3, 3, 3, 4,
            1, 2, 2, 3, 3, 3, 4, 4, 4, 4
        ],
        "Credit_Score": [
            520, 540, 560, 580, 600, 620, 640, 660, 680, 700,
            530, 550, 570, 590, 610, 630, 650, 670, 690, 710,
            525, 565, 605, 645, 685, 720, 740, 760, 780, 800
        ],
        "Support_Calls": [
            8, 7, 7, 6, 6, 5, 5, 4, 4, 3,
            8, 7, 6, 6, 5, 5, 4, 4, 3, 2,
            9, 7, 6, 5, 4, 3, 2, 2, 1, 1
        ],
        # 0 = Stay, 1 = Leave
        "Churn": [
            1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
            1, 1, 1, 1, 1, 0, 0, 0, 0, 0,
            1, 1, 1, 0, 0, 0, 0, 0, 0, 0
        ],
    }
    return pd.DataFrame(data)


def train_model() -> LogisticRegression:
    df = build_dataset()
    x = df[
        [
            "Age",
            "Monthly_Income",
            "Years_With_Company",
            "Num_Products",
            "Credit_Score",
            "Support_Calls",
        ]
    ]
    y = df["Churn"]
    model = LogisticRegression(max_iter=2000)
    model.fit(x, y)
    return model


model = train_model()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    required_fields = [
        "age",
        "monthly_income",
        "years_with_company",
        "num_products",
        "credit_score",
        "support_calls",
    ]

    missing = [field for field in required_fields if field not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        customer = pd.DataFrame(
            [
                {
                    "Age": float(payload["age"]),
                    "Monthly_Income": float(payload["monthly_income"]),
                    "Years_With_Company": float(payload["years_with_company"]),
                    "Num_Products": float(payload["num_products"]),
                    "Credit_Score": float(payload["credit_score"]),
                    "Support_Calls": float(payload["support_calls"]),
                }
            ]
        )
    except (TypeError, ValueError):
        return jsonify({"error": "All input values must be numeric."}), 400

    prediction = int(model.predict(customer)[0])
    leave_prob = float(model.predict_proba(customer)[0][1])
    label = "Leave" if prediction == 1 else "Stay"
    return jsonify({"prediction": label, "leave_probability": round(leave_prob, 3)})


if __name__ == "__main__":
    app.run(debug=True)
