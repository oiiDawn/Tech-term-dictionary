import requests
from collections import defaultdict
import numpy as np

# 你的 Flask 接口地址（改成你的实际端口和路径）
API_URL = "http://127.0.0.1:8000/query"  # 例如 POST /query

# 假设你有一个样本列表，每个是一个 dict
samples = [
    {
        "term": "disclose information",
        "title": "ABC Kids",
        "description": "This is the home of the best Aussie audio for kids, from your ABC. We've got podcasts, we've got games, we've got stories and more. And the best part is, there's something new every day. We can help you start the day right with kids news, relax with a story for your afternoon nap, mix up a deliciously fun Story Salad and get ready for bed with lullabies. Simply say \"Alexa, open ABC Kids\" for the best on-demand kids content, curated for the time of day: • In the morning (7am – Midday), start your day with kids news, podcasts and games • In the afternoon, (Midday – 3pm), hear an Acknowledgement of Country, and wind down with stories and Soundwalks • In the evening (3pm – 7pm), find out what today's Giggles and Riddles will be, listen to a podcast or play Story Salad • At night time (7pm – 7am) the next morning, get ready for bed with Relaxey Time, Lullabies and Bedtime stories. Want to get straight to the stuff you want? To hear a story, just say \"Alexa, ask ABC Kids to tell me a story.\" To hear some lullabies, just say: \"Alexa, ask ABC Kids to play me a lullaby.\" To hear your favourite podcast, you can ask ABC Kids for: • Dino Dome (\"Alexa, ask ABC Kids to play Dino Dome\") • Imagine This (\"Alexa, tell ABC Kids to play Imagine This\") • Noisy by Nature (\"Alexa, ask ABC Kids to play Noisy by Nature\") • Little Yarns (\"Alexa, tell ABC Kids to play Little Yarns\") • Play School: Ears On (\"Alexa, ask ABC Kids to play Play School: Ears On\") • News Time (\"Alexa, tell ABC Kids to play News Time\") • Soundwalks (\"Alexa, ask ABC Kids to play a Soundwalk\") • Story Salad (\"Alexa, tell ABC Kids to play Story Salad\") Need a little help around daily routines? You can ask ABC Kids to help your family: • Brush your teeth (\"Alexa, ask ABC Kids to help me brush my teeth\") • Take a bath (\"Alexa, ask ABC Kids to help me take a bath\" or \"Alexa, tell ABC Kids it's time to have a shower\") • Calm down (\"Alexa, ask ABC Kids to help me calm down\") • Get dressed (\"Alexa, ask ABC Kids to help me get dressed\") • Get ready to leave (\"Alexa, tell ABC Kids it's time to leave\") • Put on your shoes (\"Alexa, ask ABC Kids to help me put on my shoes\") • Shake your sillies out (\"Alexa, tell ABC Kids it's time to shake my sillies out\") • Tidy up (\"Alexa, tell ABC Kids it's time to tidy up\") • Eat a meal (\"Alexa, tell ABC Kids it's time to eat\") • Wash your hands (\"Alexa, ask ABC Kids to help me wash my hands\")",
        "snippet": "The ABC does not commercialise data. If we are required to disclose information, including your personal information, to help us provide services to you, we do not receive any sort of payment for doing this."
    },
    {
        "term": "cookies",
        "title": "nova",
        "description": "You can now play your favourite Nova stations on your Alexa-enabled devices.\n\nIt’s as easy as saying “Alexa, play Nova”.\n\nAlexa can play live radio from all of Nova’s stations and you can even ask what song is playing! Learn more about the ways you can listen to Nova here - https://www.novafm.com.au/listen",
        "snippet": "Cookies may be used to track the pages you have visited, to recognise you when you return to our services, to allow us to personalise our content for you (including but not limited to remembering your preferences regarding your local Nova Entertainment radio station location, news, music, podcasts, events and competitions) and to securely store your personal information."
    },
]

MAX_ITER = 5
metric_accumulator = defaultdict(list)
iteration_counter = defaultdict(int)

for _ in range(25):
    print(f"Batch {_ + 1}")
    for idx, sample in enumerate(samples):
        try:
            print(f"🔄 Running sample {idx + 1}/{len(samples)}: {sample['term']}")

            # 发送 POST 请求
            response = requests.post(API_URL, json=sample, timeout=120)

            if response.status_code != 200:
                print(f"❌ Failed with status code {response.status_code}")
                continue

            result = response.json()

            explanation = result.get("explanation", "")
            metrics = result.get("metrics_list", [])
            iteration = result.get("best_iteration", -1)

            iteration_counter[iteration] += 1
            for i, metric in enumerate(metrics):
                metric_accumulator[f"smog_{i}"].append(metric["smog"])
                metric_accumulator[f"sim_{i}"].append(metric["sim"])
                metric_accumulator[f"contradiction_{i}"].append(metric["contradiction"])
                metric_accumulator[f"fact_{i}"].append(metric["fact"])

        except Exception as e:
            print(f"⚠️ Error for sample {idx + 1}: {e}")

# 🔚 输出平均指标
print("\n📊 Average Metrics per Iteration:")
print(f"{'Iter':<6}{'SMOG':>8}{'Sim':>10}{'Contradictions':>18}{'Fact':>10}")
for i in range(MAX_ITER):
    smogs = metric_accumulator.get(f"smog_{i}", [])
    sims = metric_accumulator.get(f"sim_{i}", [])
    contras = metric_accumulator.get(f"contradiction_{i}", [])
    facts = metric_accumulator.get(f"fact_{i}", [])

    if smogs and sims and contras:
        print(f"{i+1:<6}{np.mean(smogs):>8.2f}{np.mean(sims):>10.3f}{np.mean(contras):>18.2f}{np.mean(facts):>10.3f}")
    else:
        print(f"{i+1:<6}{'-':>8}{'-':>10}{'-':>18}{'-':>10}")

print("\n📊 Iteration Count:")
print(f"{'Iter':<6}{'Count':>10}")
for i in range(MAX_ITER):
    print(f"{i+1:<6}{iteration_counter[i]:>10}")

print()
