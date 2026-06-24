import feedparser, os, re
from urllib.parse import quote, urlparse
import pandas as pd
from datetime import datetime, timezone

RECORTES = {
    "Regulação e TSE": [
        '"inteligência artificial" eleições TSE',
        '"IA" resolução eleitoral',
        '"justiça eleitoral" inteligência artificial',
        '"TSE" deepfake',
        '"propaganda eleitoral" inteligência artificial',
    ],
    "Deepfakes e conteúdo sintético": [
        '"deepfake" eleição',
        '"deepfake" candidato',
        '"vídeo falso" inteligência artificial eleição',
        '"áudio falso" candidato',
        '"conteúdo sintético" eleitoral',
    ],
    "Desinformação e checagem": [
        '"IA" desinformação eleitoral',
        '"inteligência artificial" fake news eleição',
        '"checagem" inteligência artificial eleição',
        '"desinformação" campanha inteligência artificial',
    ],
    "Plataformas e chatbots": [
        '"chatbot" eleição',
        '"ChatGPT" eleição candidato',
        '"Gemini" eleição',
        '"Claude" inteligência artificial eleição',
        '"Grok" eleição',
        '"redes sociais" inteligência artificial eleição',
        '"WhatsApp" desinformação eleição',
        '"IA generativa" campanha política',
    ],
    "Campanhas e candidatos": [
        '"inteligência artificial" campanha política',
        '"IA" marketing eleitoral',
        '"candidato" inteligência artificial campanha',
        '"segmentação" eleitores inteligência artificial',
    ],
    "Integridade e democracia": [
        '"IA" integridade eleitoral',
        '"inteligência artificial" urnas',
        '"inteligência artificial" democracia eleição',
        '"manipulação" eleitoral inteligência artificial',
    ],
    "Violência política de gênero": [
        '"deepfake" candidata',
        '"deepfake" sexual candidata',
        '"nudes" falsos candidata inteligência artificial',
        '"violência política de gênero" inteligência artificial',
        '"misoginia" inteligência artificial eleição',
        '"imagem falsa" candidata IA',
        '"inteligência artificial" ataque candidata',
    ],
}

# CODEBOOK LÉXICO (subconjunto operacional do protocolo de 21 campos)
# Cada dimensão tem categorias; cada categoria tem termos de correspondência.
# Conservador por construção: marca só o que aparece explícito no título.
# A coleta usa só o título (RSS não traz corpo), então mantém-se enxuto.

MECANISMOS = {
    "deepfake": ["deepfake", "deep fake", "vídeo falso", "video falso", "áudio falso", "audio falso", "conteúdo sintético", "conteudo sintetico", "face swap", "clonagem de voz"],
    "chatbot": ["chatbot", "chatgpt", "gemini", "claude", "grok", "perplexity", "deepseek", "copilot", "llama", "mistral", "le chat", "ia generativa", "assistente virtual"],
    "microtargeting": ["microtargeting", "micro-targeting", "segmentação", "segmentacao", "psicográfico", "psicografico", "dark post"],
    "bots": ["bot", "bots", "automação", "automacao", "perfil falso", "perfis falsos", "rede de perfis"],
    "copywriting": ["copywriting", "geração de texto", "geracao de texto", "redação automática", "texto por ia"],
    "recomendacao": ["recomendação", "recomendacao", "algoritmo de recomendação", "ranqueia", "ranking", "prioriza"],
    "auditoria": ["auditoria", "fiscalização", "fiscalizacao", "rotulagem", "identificação de ia", "selo", "marca d'água", "watermark"],
}

# modelos/empresas de LLM identificados nominalmente no título.
# Dimensão nova, separada das plataformas de distribuição (WhatsApp, etc.),
# porque "qual modelo" e "em qual rede" são perguntas distintas no protocolo.
MODELOS_LLM = {
    "ChatGPT/OpenAI": ["chatgpt", "gpt-4", "gpt-5", "gpt 4", "gpt 5", "openai", "sora", "dall-e", "dall e"],
    "Gemini/Google": ["gemini", "bard", "google ai", "imagen", "veo"],
    "Claude/Anthropic": ["claude", "anthropic"],
    "Grok/xAI": ["grok", "xai"],
    "Perplexity": ["perplexity"],
    "DeepSeek": ["deepseek", "deep seek"],
    "Llama/Meta": ["llama", "meta ai", "meta llama"],
    "Mistral": ["mistral", "le chat"],
    "Copilot/Microsoft": ["copilot", "bing chat"],
}

PLATAFORMAS = {
    "WhatsApp": ["whatsapp", "zap"],
    "Telegram": ["telegram"],
    "TikTok": ["tiktok", "tik tok"],
    "X/Twitter": [" x ", "twitter", " x,", " x.", " x:"],
    "Meta": ["facebook", "instagram", "meta ", "reels"],
    "YouTube": ["youtube", "yt "],
    "Kwai": ["kwai"],
    "IA nativa": ["chatgpt", "gemini", "claude", "grok", "perplexity", "deepseek", "openai", "copilot"],
}

AGENTES = {
    "Estado": ["tse", "tre", "tre-", "justiça eleitoral", "justica eleitoral", "supremo", "stf", "ministro", "governo", "procuradoria", "ministério público", "ministerio publico"],
    "Plataforma": ["meta", "google", "openai", "anthropic", "xai", "tiktok", "big tech", "plataforma"],
    "Campanha": ["candidato", "candidata", "campanha", "pré-candidato", "pre-candidato", "partido", "marqueteiro"],
    "Sociedade civil": ["ong", "organização", "organizacao", "instituto", "associação", "associacao", "its rio", "artigo 19", "conectas"],
    "Cidadão": ["eleitor", "cidadão", "cidadao", "usuário", "usuario", "internauta"],
    "Estrangeiro": ["estados unidos", "eua", "união europeia", "uniao europeia", "internacional", "outro país", "outro pais"],
}

VALENCIA = {
    "regulação": ["tse", "resolução", "resolucao", "norma", "regra", "lei", "proíbe", "proibe", "aprova", "regulamenta", "decisão", "decisao", "obriga", "veta"],
    "caso concreto": ["remove", "remoção", "remocao", "suspende", "condena", "multa", "flagra", "flagrante", "viral", "circula", "circulou", "denúncia", "denuncia", "ação", "acao"],
    "alerta": ["risco", "ameaça", "ameaca", "perigo", "preocupa", "alerta", "vulnerável", "vulneravel"],
    "análise": ["análise", "analise", "estudo", "pesquisa", "entenda", "como funciona", "por que", "diagnóstico", "diagnostico"],
    "ceticismo": ["fracasso", "falha", "ineficaz", "não funciona", "nao funciona", "limite", "questiona"],
    "otimismo": ["oportunidade", "benefício", "beneficio", "potencial", "avanço", "avanco", "ajuda"],
}

# LÉXICO DE VÍNCULO COM IA — abrangente por construção.
# Reúne tudo que, aparecendo no título, indica que a matéria trata de IA:
# termos genéricos, mecanismos, nomes de modelos/empresas, jargão técnico e
# termos emergentes do debate eleitoral (eleitores sintéticos, enxames, etc.).
# Usado para (1) validar o recorte de gênero (precisa de IA + gênero no título)
# e (2) marcar a coluna `vinculo_ia` (forte/fraco) em todas as matérias.
# Levantado a partir de cobertura de imprensa e textos jurídicos de 2025-2026.

IA_VINCULO = [
    # genéricos
    "inteligência artificial", "inteligencia artificial", " ia ", " ia,", " ia.",
    " ia:", " ia)", "(ia", "ia generativa", "ia-generativa", "a.i.", " ai ",
    "artificial intelligence",
    # modelos de linguagem / LLMs
    "llm", "llms", "modelo de linguagem", "modelos de linguagem",
    "grande modelo de linguagem", "grandes modelos de linguagem",
    "modelo de ia", "modelos de ia", "rede neural", "redes neurais",
    "aprendizado de máquina", "aprendizado de maquina", "machine learning",
    "aprendizado profundo", "deep learning", "algoritmo", "algorítmico", "algoritmico",
    # nomes de modelos / produtos / empresas
    "chatgpt", "gpt-4", "gpt-5", "gpt 4", "gpt 5", "openai", "sora", "dall-e", "dall e",
    "gemini", "bard", "imagen", "veo", "google ai",
    "claude", "anthropic", "grok", "xai", "perplexity", "deepseek", "deep seek",
    "llama", "meta ai", "mistral", "le chat", "copilot", "bing chat", "midjourney",
    "stable diffusion", "runway", "elevenlabs", "heygen", "synthesia",
    # mecanismos / conteúdo sintético
    "deepfake", "deep fake", "deepfakes", "fake profundo",
    "conteúdo sintético", "conteudo sintetico", "mídia sintética", "midia sintetica",
    "vídeo falso", "video falso", "áudio falso", "audio falso",
    "vídeo manipulado", "video manipulado", "imagem manipulada", "imagem falsa",
    "voz clonada", "clonagem de voz", "clonagem de imagem", "face swap", "troca de rosto",
    "hiper-realista", "hiper realista", "ultrarrealista", "ultra-realista", "ultra realista",
    "gerado por ia", "gerada por ia", "gerados por ia", "geradas por ia",
    "criado por ia", "criada por ia", "feito por ia", "produzido por ia",
    "manipulação sintética", "manipulacao sintetica",
    # automação / bots / agentes
    "bot", "bots", "robô", "robo", "robôs", "robos", "chatbot", "chatbots",
    "assistente virtual", "agente de ia", "agentes de ia", "agente autônomo",
    "agentes autônomos", "agentes autonomos", "automação", "automacao",
    "perfil falso", "perfis falsos", "perfil automatizado", "rede de perfis",
    "enxame de ia", "enxames de ia", "enxames maliciosos", "milícia digital",
    "milicias digitais", "milícias digitais", "fábrica de fake", "fabrica de fake",
    "eleitor sintético", "eleitores sintéticos", "eleitores sinteticos",
    "persona sintética", "personas sintéticas", "astroturfing",
    # microtargeting / influência
    "microtargeting", "micro-targeting", "segmentação algorítmica", "perfilamento",
    "perfilhamento", "psicográfico", "psicografico",
    # governança / rotulagem (vínculo institucional com IA)
    "rotulagem de ia", "marca d'água", "marca dagua", "watermark", "provedor de ia",
    "provedores de ia", "regulação de ia", "regulacao de ia",
    # termos amplos incluídos a pedido (capturam o ecossistema informacional;
    # aumentam recall mas trazem ruído — "desinformação" e "digital" existem
    # sem IA, então parte do que marcam como "forte" não terá IA de fato).
    "desinformação", "desinformacao", "desinformativo", "desinformativa",
    "digital", "digitais", "fake news", "notícia falsa", "noticia falsa",
    "notícias falsas", "noticias falsas", "checagem", "fact-checking", "fact checking",
]

# termos que indicam recorte de gênero (mulheres na política + violência)
GENERO_TERMOS = [
    "candidata", "deputada", "senadora", "vereadora", "prefeita", "governadora",
    "ministra", "presidenta", "primeira-dama", "primeira dama", "política", "politica",
    "misoginia", "misógino", "misogino", "misógina", "machismo", "machista",
    "sexista", "sexismo", "violência política de gênero", "violencia politica de genero",
    "violência de gênero", "violencia de genero", "violência contra a mulher",
    "violencia contra a mulher", "assédio", "assedio", "nudes", "nude falso",
    "deepfake sexual", "deepfake íntimo", "deepfake intimo", "pornografia",
    "pornô", "porno", "imagem íntima", "imagem intima", "íntima", "intima",
    "exposição", "exposicao", "feminicídio", "feminicidio", "mulher", "mulheres",
    "lei 14.192", "14192",
]


def tem_vinculo_ia(titulo):
    """True se o título contém qualquer termo do léxico de IA."""
    t = _texto_norm(titulo)
    return any(termo in t for termo in IA_VINCULO)

def tem_termo_genero(titulo):
    """True se o título contém qualquer termo do léxico de gênero."""
    t = _texto_norm(titulo)
    return any(termo in t for termo in GENERO_TERMOS)


ANO_MINIMO = 2026

FONTES_BLOQUEADAS = [
    "publico.pt", "observador.pt", "expresso.pt", "sapo.pt", "rtp.pt",
    "dn.pt", "jn.pt", "cmjornal", "eco.sapo", "jornaldenegocios",
    "tsf.pt", "sicnoticias", "noticiasaominuto",
]

def eh_bloqueada(fonte, link):
    alvo = (fonte or "").lower() + " " + (link or "").lower()
    try:
        dom = urlparse(link or "").netloc.lower()
        alvo += " " + dom
    except Exception:
        pass
    return any(b in alvo for b in FONTES_BLOQUEADAS)

def ano_da_data(s):
    if not s:
        return None
    try:
        return pd.to_datetime(s, errors="coerce").year
    except Exception:
        return None

def _texto_norm(s):
    return " " + (s or "").lower() + " "

def _marcar(texto, dicionario):
    """Retorna lista de categorias cujos termos aparecem no texto."""
    achados = []
    for categoria, termos in dicionario.items():
        if any(t in texto for t in termos):
            achados.append(categoria)
    return achados

def classificar(titulo):
    t = _texto_norm(titulo)
    mecanismos = _marcar(t, MECANISMOS)
    modelos = _marcar(t, MODELOS_LLM)
    plataformas = _marcar(t, PLATAFORMAS)
    agentes = _marcar(t, AGENTES)
    valencias = _marcar(t, VALENCIA)

    # valência dominante. "caso concreto" tem precedência sobre "regulação"
    # quando há verbo de ação (remove, suspende, circula), porque o relatório
    # distingue anúncio de norma de uso/abuso/punição efetivos.
    ordem_val = ["caso concreto", "regulação", "alerta", "análise", "ceticismo", "otimismo"]
    val_dominante = next((v for v in ordem_val if v in valencias), "não classificável")

    # agente principal: prioridade Estado > Plataforma > Campanha > demais
    ordem_ag = ["Estado", "Plataforma", "Campanha", "Sociedade civil", "Cidadão", "Estrangeiro"]
    ag_principal = next((a for a in ordem_ag if a in agentes), "não identificado")

    # modelo principal: primeiro modelo citado segue a ordem de declaração
    modelo_principal = modelos[0] if modelos else "não identificado"

    # vínculo com IA: "forte" se há mecanismo, modelo ou termo de IA explícito no
    # título; "fraco" caso contrário (matéria veio pela query, mas o título não
    # deixa o vínculo evidente). Marcador de confiança transversal a todo recorte.
    vinculo = "forte" if (mecanismos or modelos or tem_vinculo_ia(titulo)) else "fraco"

    return {
        "mecanismos": "|".join(mecanismos),
        "modelos_llm": "|".join(modelos),
        "modelo_principal": modelo_principal,
        "plataformas": "|".join(plataformas),
        "agentes": "|".join(agentes),
        "agente_principal": ag_principal,
        "valencias": "|".join(valencias),
        "valencia_dominante": val_dominante,
        "vinculo_ia": vinculo,
        "confianca": "baixa" if not (mecanismos or plataformas or valencias or modelos) else "ok",
    }

arquivo = "dados/noticias.csv"
linhas = []
descartadas_ano = 0
descartadas_fonte = 0
descartadas_genero = 0

for recorte, keywords in RECORTES.items():
    for kw in keywords:
        url = f"https://news.google.com/rss/search?q={quote(kw)}&hl=pt-BR&gl=BR&ceid=BR:pt"
        for e in feedparser.parse(url).entries:
            fonte = e.get("source", {}).get("title", "")
            link = e.link
            data_pub = e.get("published", "")
            titulo = e.title

            if eh_bloqueada(fonte, link):
                descartadas_fonte += 1
                continue

            ano = ano_da_data(data_pub)
            if ano is not None and ano < ANO_MINIMO:
                descartadas_ano += 1
                continue

            # PORTÃO DE CO-OCORRÊNCIA (recorte de gênero):
            # a query de gênero é leniente e pode trazer matéria sobre candidata
            # sem qualquer relação com IA. Para o recorte de gênero entrar no
            # corpus, o título precisa conter SIMULTANEAMENTE um termo de IA e um
            # termo de gênero — assim o episódio cruza, de fato, IA + gênero.
            if recorte == "Violência política de gênero":
                if not (tem_vinculo_ia(titulo) and tem_termo_genero(titulo)):
                    descartadas_genero += 1
                    continue

            registro = {
                "objeto": "Eleições 2026",
                "recorte": recorte,
                "keyword": kw,
                "titulo": titulo,
                "data_pub": data_pub,
                "fonte": fonte,
                "link": link,
                "coletado_em": datetime.now(timezone.utc).isoformat(),
            }
            registro.update(classificar(titulo))
            linhas.append(registro)

novo = pd.DataFrame(linhas)

if os.path.exists(arquivo):
    antigo = pd.read_csv(arquivo)
    df = pd.concat([antigo, novo]).drop_duplicates(subset="link", keep="first")

    # reclassifica linhas antigas que não tenham as colunas do codebook
    cols_cb = ["mecanismos","modelos_llm","modelo_principal","plataformas","agentes","agente_principal","valencias","valencia_dominante","vinculo_ia","confianca"]
    for c in cols_cb:
        if c not in df.columns:
            df[c] = None
    # remove coluna 'genero' de versões anteriores, se existir
    if "genero" in df.columns:
        df = df.drop(columns=["genero"])
    # reclassifica onde faltar valência, modelo OU vínculo de IA (CSV antigo tem
    # valência preenchida mas não tem modelo_principal nem vinculo_ia)
    faltando = (
        df["valencia_dominante"].isna()
        | df["modelo_principal"].isna() | (df["modelo_principal"].astype(str).str.strip() == "")
        | df["vinculo_ia"].isna() | (df["vinculo_ia"].astype(str).str.strip() == "")
    )
    if faltando.any():
        df.loc[faltando, cols_cb] = df.loc[faltando, "titulo"].apply(
            lambda t: pd.Series(classificar(t))
        )

    if "data_pub" in df.columns:
        df = df[df["data_pub"].apply(lambda s: (ano_da_data(s) is None) or (ano_da_data(s) >= ANO_MINIMO))]
    if "fonte" in df.columns and "link" in df.columns:
        df = df[~df.apply(lambda r: eh_bloqueada(r.get("fonte",""), r.get("link","")), axis=1)]
    # aplica o portão de co-ocorrência também ao corpus já existente: matéria de
    # gênero sem IA+gênero no título é removida (limpa coletas anteriores frouxas)
    if "recorte" in df.columns and "titulo" in df.columns:
        antes_g = len(df)
        mask_genero = df["recorte"] == "Violência política de gênero"
        manter = df["titulo"].apply(lambda t: tem_vinculo_ia(t) and tem_termo_genero(t))
        df = df[(~mask_genero) | manter]
        descartadas_genero += antes_g - len(df)
else:
    df = novo.drop_duplicates(subset="link")

os.makedirs("dados", exist_ok=True)

# garante que só matérias com recorte de eleições fiquem no corpus
if "recorte" in df.columns:
    antes = len(df)
    df = df[df["recorte"].notna() & (df["recorte"].astype(str).str.strip() != "")]
    fora_escopo = antes - len(df)
else:
    fora_escopo = 0

df.to_csv(arquivo, index=False)
print(f"{len(novo)} novas | {len(df)} no total | descartadas: {descartadas_ano} por ano, {descartadas_fonte} por fonte, {descartadas_genero} no recorte de gênero (sem IA+gênero), {fora_escopo} fora de escopo")
