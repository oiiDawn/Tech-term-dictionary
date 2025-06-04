import requests
import json
import re
import math
import torch
import torch.nn.functional as F
from nltk.tokenize import sent_tokenize
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics.pairwise import cosine_similarity
from factscore_local.factscorer import FactScorer

from prompt import PROMPT

# === Load models ===
device = torch.device("cpu")

sim_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
sim_model = BertModel.from_pretrained("bert-base-uncased").to(device)

nli_tokenizer = AutoTokenizer.from_pretrained("roberta-large-mnli")
nli_model = AutoModelForSequenceClassification.from_pretrained(
    "roberta-large-mnli").to(device)

fs = FactScorer(openai_key="./api_key.txt")

fact_tokenizer = AutoTokenizer.from_pretrained("manueldeprada/FactCC")
fact_model = AutoModelForSequenceClassification.from_pretrained(
    "manueldeprada/FactCC").to(device)

MAX_ITER = 5


class THRESHOLD:
    SMOG = 14
    SIM = 0.7
    CONT = 0.5
    FACT = 0.5

# === Ollama ===


def query_ollama(system_prompt, user_prompt, model='llama3.2'):
    response = requests.post(
        'http://localhost:11434/api/chat',
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True
        },
        stream=True
    )
    content = ""
    for line in response.iter_lines():
        if line:
            try:
                json_data = json.loads(line)
                content += json_data.get("message", {}).get("content", "")
            except json.JSONDecodeError:
                continue
    return content.strip()


# === Classification ===
def classify_term(term):
    system = "You are a classification assistant that assigns a given term to one of the 7 privacy-related categories."
    user = (
        f"Given the term '{term}', choose the most suitable category from the following:\n\n"
        + "\n".join(f"- {cat}" for cat in PROMPT) +
        "\n\nOnly return the category name."
    )
    result = query_ollama(system, user)
    category = next(
        (cat for cat in PROMPT if cat.lower() in result.lower()), None)
    return category


# === Evaluate metrics ===
def smog_index(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    polysyllable_count = len([word for word in re.findall(r'\w+', text) if count_syllables(word) >= 3])
    if sentence_count >= 3:
        smog = 1.0430 * math.sqrt(polysyllable_count * (30 / sentence_count)) + 3.1291
        return round(smog, 2)
    else:
        return 0.0


def count_syllables(word):
    word = word.lower()
    count = len(re.findall(r'[aeiouy]+', word))
    return max(count, 1)


def find_contradictions(context, explanation, threshold=THRESHOLD.CONT):
    explanation_sentences = sent_tokenize(explanation)
    contradictory_pairs = []
    for e_sent in explanation_sentences:
        inputs = nli_tokenizer(
            e_sent, context, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = nli_model(**inputs)
            probs = F.softmax(outputs.logits, dim=1).squeeze()
        contradiction_prob = probs[0].item()  # index 0 == contradiction
        if contradiction_prob > threshold:
            contradictory_pairs.append(e_sent)
    return contradictory_pairs


def compute_similarity(text1, text2):
    inputs1 = sim_tokenizer(text1, return_tensors="pt",
                            truncation=True, padding=True)
    inputs2 = sim_tokenizer(text2, return_tensors="pt",
                            truncation=True, padding=True)
    with torch.no_grad():
        output1 = sim_model(**inputs1).last_hidden_state[:, 0, :]
        output2 = sim_model(**inputs2).last_hidden_state[:, 0, :]
    return cosine_similarity(output1, output2).item()


# def fact_score(term, explanation):
#     # fs.register_knowledge_source(name_of_your_knowledge_source,
#     #                              data_path=path_to_jsonl_file,
#     #                              db_path=path_to_output_db_file)
#
#     # now, when you compute a score, specify knowledge source to use
#     out = fs.get_score([term], [explanation])
#     return out["score"]


def check_fact(snippet, generation):
    input_dict = fact_tokenizer(snippet, generation, max_length=512, padding='max_length', truncation=True, return_tensors='pt')
    logits = fact_model(**input_dict).logits
    pred_prob = F.softmax(logits, dim=1).squeeze()
    pred = logits.argmax(dim=1)
    return pred_prob[0].item()
    # return fact_model.config.id2label[pred.item()] # prints: INCORRECT

# === Evaluation and improvement ===


def evaluate_and_improve(term, initial_explanation, context_text, snippet):
    explanation = initial_explanation

    best_explanation = explanation
    best_score = -1000
    best_iteration = -1
    metrics_list = []

    for i in range(MAX_ITER):
        print(f"\n🔁 Iteration {i + 1}")

        smog = smog_index(explanation)
        sim = compute_similarity(explanation, context_text)
        contradiction = find_contradictions(context_text, explanation)
        fact = check_fact(snippet, explanation)

        metrics_list.append(
            {"smog": smog, "sim": sim, "contradiction": len(contradiction), "fact": fact})

        score = (sim - THRESHOLD.SIM) + (THRESHOLD.SMOG - smog) / THRESHOLD.SMOG - \
            1000 * len(contradiction) + 10 * (fact - THRESHOLD.FACT)
        if score > best_score:
            best_explanation = explanation
            best_score = score
            best_iteration = i

        print(f"🟢 SMOG Index: {smog:.2f}")
        print(f"🟢 Similarity: {sim:.3f}")
        print(f"🟢 Contradiction: {len(contradiction)}")
        print(f"🟢 Fact: {fact:.2f}")

        if smog <= THRESHOLD.SMOG and sim >= THRESHOLD.SIM and len(contradiction) == 0 and fact >= THRESHOLD.FACT:
            print("✅ Explanation meets quality criteria early.")
            return explanation, metrics_list, best_iteration

        feedback = f"The current explanation needs improvement in the following areas:\n"
        if smog > THRESHOLD.SMOG:
            feedback += "- Aim for simpler language and shorter sentences to improve readability.\n"
        if sim < THRESHOLD.SIM:
            feedback += "- Ensure the explanation aligns more closely with the context provided.\n"
        if len(contradiction) > 0:
            for explanation_sent in contradiction:
                feedback += (
                    f"The following explanation contradicts the context:\n"
                    f"Explanation: \"{explanation_sent}\"\n\n"
                    f"Please revise the explanation so that it no longer contradicts the context.\n"
                )
        if fact < THRESHOLD.FACT:
            feedback += "Please revise the explanation so that it is factually accurate and clearly supported by the context. Do not add external knowledge. Keep the explanation concise and easy to understand.\n"
        feedback += f"\nPlease revise the explanation of {term} based on the above suggestions to improve readability, accuracy, relevance and factually accurate."
        explanation = query_ollama(
            "You are a privacy assistant improving text quality. Do not say the changes you made.", feedback)

    print(f"\n⚠️ Max iterations reached. Returning best explanation found.")
    return best_explanation, metrics_list, best_iteration
