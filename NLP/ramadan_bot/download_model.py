from sentence_transformers import SentenceTransformer


def main() -> None:
    # Downloads (first run) and caches the model.
    SentenceTransformer("sentence-transformers/bert-base-nli-mean-tokens")
    print("Model downloaded (or already cached).")


if __name__ == "__main__":
    main()

