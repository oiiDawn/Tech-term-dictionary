import logging

from flask import Flask, request, jsonify

from prompt import PROMPT
from llama import classify_term, query_ollama, evaluate_and_improve

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route("/query", methods=["POST"])
def main():
    data = request.json
    term = data.get("term", "")
    title = data.get("title", "")
    description = data.get("description", "")
    snippet = data.get("snippet", "")
    category = classify_term(term)
    if not category:
        print("无法分类该术语。")
        return

    logging.debug(f"🧠 Classification: {term} → {category}")

    context_prompt = PROMPT[category].format(term=term, title=title, description=description, snippet=snippet)
    initial_explanation = query_ollama("You are a privacy policy assistant.", context_prompt)

    final_explanation, metrics_list, best_iteration = evaluate_and_improve(term, initial_explanation, context_prompt, snippet)

    logging.debug("\n📘 Final explanation: \n")
    logging.debug(final_explanation)

    return jsonify({"explanation": final_explanation, "metrics_list": metrics_list, "best_iteration": best_iteration})

