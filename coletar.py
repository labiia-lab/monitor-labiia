import feedparser, os
from urllib.parse import quote
import pandas as pd
from datetime import datetime, timezone

# Cada eixo de pesquisa tem sua lista de palavras-chave.
# A chave do dicionário é o nome do eixo (igual ao manual de identidade).
EIXOS = {
    "IA e Método": [
        "inteligência artificial",
        '"governança de IA"',
        '"regulação" "inteligência artificial"',
        '"IA generativa"',
        '"soberania digital"',
    ],
    "Eleições": [
        '"desinformação" eleições',
        '"fake news" eleição Brasil',
        '"urna eletrônica"',
        '"campanha eleitoral" redes sociais',
        '"integridade eleitoral"',
    ],
    "Sustentabilidade": [
        '"transição energética" Brasil',
        '"mudança climática" política',
        '"crédito de carbono"',
        '"justiça climática"',
        '"política ambiental" Brasil',
    ],
    "Democracia": [
        '"democracia" Brasil instituições',
        '"polarização política"',
        '"participação social"',
        '"estado de direito"',
        '"liberdade de imprensa"',
    ],
    "Ética e Regulação": [
        '"ética" "inteligência artificial"',
        '"regulação de plataformas"',
        '"proteção de dados" LGPD',
        '"viés algorítmico"',
        '"moderação de conteúdo"',
    ],
    "Sociedade e Cultura": [
        '"inclusão digital"',
        '"desigualdade digital"',
        '"cultura digital"',
        '"tecnologia e sociedade"',
        '"letramento digital"',
    ],
}

arquivo = "dados/noticias.csv"

linhas = []
for eixo, keywords in EIXOS.items():
    for kw in keywords:
        url = f"https://news.google.com/rss/search?q={quote(kw)}&hl=pt-BR&gl=BR&ceid=BR:pt"
        for e in feedparser.parse(url).entries:
            linhas.append({
                "eixo": eixo,
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
