import pandas as pd
import matplotlib.pyplot as plt

# ====== 1. BACA CSV ======
df = pd.read_csv(r"your-file-path-download-from-gsc.csv")

print("==== Info Data ====")
print(df.info())
print("\n==== 5 Baris Pertama ====")
print(df.head())

# 🔧 Pastikan nama kolum sesuai (tukar ikut CSV sebenar)
# Contoh kalau dari Google Search Console:
# 'Top queries' -> 'keyword'
# 'Impressions' -> 'impressions'
# 'Clicks' -> 'clicks'
# 'Date' -> 'date'

# Cuba rename automatik kalau match kolum standard GSC
df = df.rename(columns={
    'Top queries': 'keyword',
    'Query': 'keyword',
    'Impressions': 'impressions',
    'Clicks': 'clicks',
    'Date': 'date'
})

# ====== 2. TOP IMPRESSIONS & CLICKS ======
print("\n==== Top 10 by Impressions ====")
print(df.sort_values(by='impressions', ascending=False).head(10)[['keyword', 'impressions', 'clicks']])

print("\n==== Top 10 by Clicks ====")
print(df.sort_values(by='clicks', ascending=False).head(10)[['keyword', 'impressions', 'clicks']])

# ====== 3. BAHAGI MENGIKUT BULAN ======
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.to_period('M')

monthly = df.groupby('month')[['impressions', 'clicks']].sum().reset_index()
print("\n==== Data Bulanan ====")
print(monthly)

plt.figure(figsize=(10,6))
plt.plot(monthly['month'].astype(str), monthly['impressions'], marker='o', label='Impressions')
plt.plot(monthly['month'].astype(str), monthly['clicks'], marker='o', label='Clicks')
plt.title("Impressions & Clicks by Month")
plt.xlabel("Month")
plt.ylabel("Count")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ====== 4. KEYWORD ADA 'POS' ATAU 'POINT OF SALE' ======
mask = df['keyword'].astype(str).str.contains(r'\bpos\b|point of sale', case=False, na=False)
pos_keywords = df[mask].sort_values(by='impressions', ascending=False)

print("\n==== Keyword mengandungi 'pos' atau 'point of sale' ====")
print(pos_keywords[['keyword', 'impressions', 'clicks']])

# ====== 5. (Opsyenal) SIMPAN KE FAIL BARU ======
output_path = r"C:\Users\syede\Downloads\pos_keywords.csv"
pos_keywords.to_csv(output_path, index=False)
print(f"\n✅ Disimpan ke: {output_path}")
