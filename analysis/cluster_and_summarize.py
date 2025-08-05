import os
import json
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from gpt4all import GPT4All

# Initialize GPT4All model
gpt_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")  # Adjust if needed

def load_titles_from_file(filepath):
    """Extract titles or summaries from various signal files."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {filepath}: {e}")
        return []

    titles = []
    for item in data:
        if "title" in item:
            titles.append(item["title"].strip())
        elif "summary" in item:
            titles.append(item["summary"].strip())
    return [t for t in titles if t]

def interpret_topic_with_llm(model, keywords):
    prompt = (
        f"You are a helpful assistant. Interpret what people might be discussing "
        f"if the keywords are: {', '.join(keywords)}.\n"
        f"Summarize the discussion in one sentence. Be clear, concise, and insightful."
    )
    try:
        with model.chat_session():
            response = model.generate(prompt, max_tokens=100, temp=0.7)
        return response.strip() if response else "⚠️ Empty response"
    except Exception as e:
        print(f"⚠️ GPT4All failed to interpret topic: {e}")
        return "⚠️ Interpretation failed."

def cluster_titles(titles, company_name):
    print(f"🔧 Running BERTopic for {company_name}...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    topic_model = BERTopic(embedding_model=embedding_model, min_topic_size=2, verbose=True)
    topics, _ = topic_model.fit_transform(titles)

    topic_counts = {t: topics.count(t) for t in set(topics) if t != -1}
    print(f"📊 Found {len(topic_counts)} meaningful topics (excluding outliers)")

    output_file = f"data/{company_name.lower().replace(' ', '_')}_topics.txt"
    try:
        with open(output_file, "w") as f:
            for topic_num in sorted(topic_counts, key=topic_counts.get, reverse=True):
                topic_words = topic_model.get_topic(topic_num)
                if not topic_words:
                    f.write(f"⚠️ Topic {topic_num}: No keywords found\n")
                    f.write("📝 Interpretation: ⚠️ Interpretation failed.\n\n")
                    continue
                top_words = [word for word, _ in topic_words]
                interpretation = interpret_topic_with_llm(gpt_model, top_words)
                f.write(f"Topic {topic_num} ({topic_counts[topic_num]} posts): {', '.join(top_words)}\n")
                f.write(f"📝 Interpretation: {interpretation}\n\n")
        print(f"✅ Topics and interpretations saved to {output_file}\n")
    except Exception as e:
        print(f"❌ Failed to save topics for {company_name}: {e}")

def main():
    print("📂 Scanning for JSON files in /data...")
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("❌ 'data' directory does not exist.")
        return

    companies = ["Grip Security", "Wiz", "AppOmni", "Valence Security"]
    for company in companies:
        print(f"\n📄 Processing topics for: {company}")
        company_key = company.lower().replace(" ", "_")
        all_titles = []

        # Load from all three sources
        for source in ["reddit", "news", "signals"]:
            filepath = os.path.join(data_dir, f"{company_key}_{source}.json")
            if os.path.exists(filepath):
                titles = load_titles_from_file(filepath)
                all_titles.extend(titles)
            else:
                print(f"⚠️ Missing {source} file for {company}")

        if all_titles:
            cluster_titles(all_titles, company)
        else:
            print(f"⚠️ No usable content found for {company}")

if __name__ == "__main__":
    main()
