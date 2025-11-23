# ===============================
# Keyword Research Prototype
# - Input : keywords.csv (column: keyword)
# - Output: clusters.csv + topical_map.html
# ===============================

import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.decomposition import PCA
import hdbscan
from pyvis.network import Network

# -------------------------------
# 1. Load Keywords
# -------------------------------
df = pd.read_csv("keywords.csv")  # make sure file has a column named "keyword"
keywords = df["keyword"].dropna().unique().tolist()

print(f"Loaded {len(keywords)} keywords")

# -------------------------------
# 2. Embeddings
# -------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
embs = model.encode(keywords, show_progress_bar=True)

# Optional: reduce dimensions for clustering
pca = PCA(n_components=50)
embs_red = pca.fit_transform(embs)

# -------------------------------
# 3. Clustering
# -------------------------------
clusterer = hdbscan.HDBSCAN(min_cluster_size=3, metric="euclidean")
labels = clusterer.fit_predict(embs_red)

df_result = pd.DataFrame({"keyword": keywords, "cluster": labels})
df_result.to_csv("clusters.csv", index=False)
print("✅ Clustering complete → saved to clusters.csv")

# -------------------------------
# 4. Build Topical Map
# -------------------------------
net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# assign colors per cluster
clusters = df_result["cluster"].unique()
colors = [
    "#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33A8",
    "#33FFF5", "#9D33FF", "#FF8F33", "#33FF8F", "#8F33FF"
]

# add nodes
for idx, row in df_result.iterrows():
    cluster_id = row["cluster"]
    color = colors[cluster_id % len(colors)] if cluster_id != -1 else "#999999"
    net.add_node(row["keyword"], label=row["keyword"], color=color)

# add edges (connect keywords in same cluster)
for cluster_id in clusters:
    cluster_keywords = df_result[df_result["cluster"] == cluster_id]["keyword"].tolist()
    for i in range(len(cluster_keywords)):
        for j in range(i + 1, len(cluster_keywords)):
            net.add_edge(cluster_keywords[i], cluster_keywords[j], color="#555555")

# save HTML
net.show("topical_map.html")
print("✅ Topical map saved → topical_map.html")
