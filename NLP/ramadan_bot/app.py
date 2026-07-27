from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np
import pandas as pd

app = Flask(__name__)

# تحميل نموذج AraBERT (يعطي embeddings عربية أفضل)
MODEL_NAME = "aubmindlab/bert-base-arabertv2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def _mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).type_as(last_hidden_state)
    masked = last_hidden_state * mask
    summed = masked.sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


@torch.no_grad()
def embed(texts):
    if isinstance(texts, str):
        texts = [texts]
    batch = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )
    batch = {k: v.to(device) for k, v in batch.items()}
    out = model(**batch)
    vecs = _mean_pool(out.last_hidden_state, batch["attention_mask"])
    vecs = torch.nn.functional.normalize(vecs, p=2, dim=1)
    return vecs.cpu().numpy()

# تحميل CSV الأسئلة
df = pd.read_csv('questions.csv')  # الأعمدة: question, answer

# تحويل كل سؤال إلى embedding
embeddings = embed(df["question"].tolist())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get('question') or (request.get_json(silent=True) or {}).get('question', '')
    if not question:
        return jsonify({'answer': 'من فضلك اكتب سؤالك ثم أرسله.'})

    q_vec = embed(question)[0]
    sims = embeddings @ q_vec
    idx = int(np.argmax(sims))
    best_score = float(sims[idx])

    if best_score < 0.65:  # threshold lowered for better matching
        return jsonify({'answer': 'عذراً، لا أملك إجابة مناسبة على هذا السؤال. حاول سؤالاً آخر أو استخدم كلمات أبسط.'})

    return jsonify({'answer': df['answer'].iloc[idx]})

if __name__ == "__main__":
    app.run(debug=True)