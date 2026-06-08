import feedparser, os
from urllib.parse import quote
import pandas as pd
from datetime import datetime, timezone

keywords = [
    "inteligência artificial",
    '"hub de IA"',
    '"governança de IA"',
    '"inteligência artificial" Brasil',
    '"regulação" "inteligência artificial"',
    '"IA generativa"',
    "machine learning política pública",
    '"soberania digital"',
]

arquivo = "dados/noticias.csv"

linhas = []
for kw in keywords:
    url = f"https://news.google.com/rss/search?q={quote(kw)}&hl=pt-BR&gl=BR&ceid=BR:pt"
    for e in feedparser.parse(url).entries:
        linhas.append({
            "keyword": kw,
            "titulo": e.title,
            "data_pub": e.get("published", ""),
            "fonte": e.get("source", {}).get("title", ""),
            "link": e.link,
            "coletado_em": datetime.now(timezone.utc).isoformat(),
        })

novo = pd.DataFrame(linhas)

if os.path.exists(arquivo):
    antigo = pd.read_csv(arquivo)
    df = pd.concat([antigo, novo]).drop_duplicates(subset="link", keep="first")
else:
    df = novo.drop_duplicates(subset="link")

os.makedirs("dados", exist_ok=True)
df.to_csv(arquivo, index=False)
print(f"{len(novo)} coletadas nesta rodada, {len(df)} no total acumulado")
