 === 1️⃣ Imports ===
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# === 2️⃣ Load model ===
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# === 3️⃣ Load data ===
csv_path = r"C:\Users\syede\OneDrive\Documents\Woos 301.csv"
df = pd.read_csv(csv_path)

# Pastikan ada kolum "URL" atau ubah nama ikut fail sebenar
urls_404 = df['URL'].astype(str).tolist()

# === 4️⃣ URL cadangan (pilihan destinasi) ===
candidate_urls = [
    "https://yours.co/products",
    "https://yours.co/pages/about-us",
]

# === 5️⃣ Encode semua URL ===
cand_embeddings = model.encode(candidate_urls, convert_to_tensor=True)

# === 6️⃣ Cari padanan terbaik bagi setiap URL 404 ===
best_matches = []
for url in urls_404:
    query_embedding = model.encode(url, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, cand_embeddings)
    best_idx = cosine_scores.argmax().item()
    best_url = candidate_urls[best_idx]
    best_score = cosine_scores[0][best_idx].item()
    best_matches.append({
        "404_URL": url,
        "Best_Match_URL": best_url,
        "Similarity_Score": round(best_score, 4)
    })

# === 7️⃣ Simpan hasil ke CSV ===
output_df = pd.DataFrame(best_matches)
output_path = r"C:\file-path.csv"
output_df.to_csv(output_path, index=False)

print(f"Hasil disimpan ke: {output_path}")
