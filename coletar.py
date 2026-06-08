import feedparser, os
from urllib.parse import quote
import pandas as pd
from datetime import datetime, timezone

# Laboratório de IA: TODA palavra-chave cruza o tema do eixo com inteligência artificial.
EIXOS = {
    "IA e Método": [
        '"inteligência artificial" pesquisa',
        '"IA generativa"',
        '"modelos de linguagem"',
        '"aprendizado de máquina" ciência',
        '"métodos computacionais" "inteligência artificial"',
    ],
    "Eleições": [
        '"inteligência artificial" eleições',
        '"deepfake" eleição',
        '"IA" desinformação eleitoral',
        '"inteligência artificial" campanha política',
        '"IA" integridade eleitoral',
    ],
    "Sustentabilidade": [
        '"inteligência artificial" clima',
        '"IA" sustentabilidade',
        '"inteligência artificial" meio ambiente',
        '"IA" transição energética',
        '"inteligência artificial" monitoramento ambiental',
    ],
    "Democracia": [
        '"inteligência artificial" democracia',
        '"IA" esfera pública',
        '"inteligência artificial" políticas públicas',
        '"IA" participação cidadã',
        '"inteligência artificial" transparência governo',
    ],
    "Ética e Regulação": [
        '"ética" "inteligência artificial"',
        '"regulação" "inteligência artificial"',
        '"governança de IA"',
        '"viés algorítmico"',
        '"inteligência artificial" proteção de dados',
    ],
    "Sociedade e Cultura": [
        '"inteligência artificial" sociedade',
        '"IA" desigualdade',
        '"inteligência artificial" trabalho',
        '"IA" educação',
        '"inteligência artificial" cultura',
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
