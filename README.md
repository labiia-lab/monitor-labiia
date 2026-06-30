<div align="center">

# `<labiia_lab>` · Monitor de Notícias - IA e Eleições

**Monitoramento automático da cobertura midiática sobre inteligência artificial nas eleições brasileiras de 2026.**

[![GitHub Pages](https://img.shields.io/badge/painel-online-4945FE?style=flat-square)](https://larissacodes.github.io/monitor-labiia/)
[![Coleta automática](https://img.shields.io/badge/coleta-2x%20ao%20dia-4945FE?style=flat-square)](.github/workflows/monitor.yml)
[![Python](https://img.shields.io/badge/Python-3.11-15151F?style=flat-square&logo=python&logoColor=white)](coletar.py)
[![GitHub Actions](https://img.shields.io/badge/automação-GitHub%20Actions-15151F?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/monitor.yml)

[Ver o painel](https://larissacodes.github.io/monitor-labiia/) · [Como funciona](#como-funciona) · [Estrutura](#estrutura-do-repositório)

</div>

---

## Sobre

O monitor acompanha de forma contínua como a imprensa brasileira cobre o uso de inteligência artificial nas eleições de 2026. O sistema coleta notícias duas vezes ao dia, classifica cada matéria por seis dimensões de análise e apresenta o resultado em um painel interativo. Toda a operação roda sem servidor próprio, na infraestrutura gratuita do GitHub.

O projeto integra o **Eixo B (Política e Sociedade)** do laboratório e segue a lógica do relatório de pesquisa sobre IA e eleições: em vez de classificar cada notícia numa única gaveta temática, trata as eleições como objeto único e marca cada matéria em várias dimensões ao mesmo tempo.

## Como funciona

O fluxo de dados percorre quatro etapas encadeadas:

```
Google News RSS  →  coletar.py  →  dados/noticias.csv  →  index.html
    (busca)        (classifica)      (armazena)            (visualiza)
```

| Etapa | O que acontece |
|-------|----------------|
| **Coleta** | `coletar.py` consulta os feeds RSS do Google Notícias, uma busca por palavra-chave |
| **Triagem** | descarta matérias anteriores a 2026, fontes fora do escopo nacional e duplicatas por link |
| **Classificação** | cada título recebe marcações de mecanismo, modelo de linguagem, plataforma, agente e valência, mais um grau de vínculo com IA |
| **Armazenamento** | os resultados vão para um CSV versionado no próprio repositório |
| **Visualização** | o painel lê o CSV e monta gráficos e filtros no navegador |

A automação amarra tudo: o GitHub Actions roda o coletor de doze em doze horas, grava o CSV atualizado e o GitHub Pages publica a versão nova do painel a cada alteração. A cada execução, o coletor também revisa o corpus já acumulado: reclassifica matérias antigas que não tenham as colunas atuais e reaplica os filtros de triagem, de modo que o histórico acompanhe a versão vigente do classificador.

## O que o monitor procura

A coleta se organiza em **sete recortes temáticos**, cada um com seu conjunto de palavras-chave:

| Recorte | Foco da busca |
|---------|---------------|
| **Regulação e TSE** | resoluções, propaganda eleitoral, justiça eleitoral |
| **Deepfakes e conteúdo sintético** | vídeo e áudio falsos, conteúdo sintético |
| **Desinformação e checagem** | fake news, desinformação eleitoral, agências de checagem |
| **Plataformas e chatbots** | ChatGPT, Gemini, Grok, redes sociais, IA generativa em campanha |
| **Campanhas e candidatos** | marketing eleitoral, segmentação de eleitores |
| **Integridade e democracia** | urnas, manipulação eleitoral, democracia |
| **Violência política de gênero** | deepfakes sexuais, imagens falsas e ataques a candidatas |

Cada notícia coletada passa por um **classificador léxico** que lê o título e marca cinco dimensões:

- **Mecanismo de IA** — deepfake, chatbot, microtargeting, bots, copywriting, recomendação, auditoria
- **Modelo de linguagem** — ChatGPT/OpenAI, Gemini/Google, Claude/Anthropic, Grok/xAI, Perplexity, DeepSeek, Llama/Meta, Mistral, Copilot/Microsoft
- **Plataforma** — WhatsApp, Telegram, TikTok, X/Twitter, Meta, YouTube, Kwai, IA nativa
- **Agente principal** — Estado, plataforma, campanha, sociedade civil, cidadão, agente estrangeiro
- **Valência narrativa** — regulação, caso concreto, alerta, análise, ceticismo, otimismo

Além das cinco dimensões, cada matéria recebe um **grau de vínculo com IA** (forte ou fraco), que indica o quanto o título deixa explícita a relação com inteligência artificial. O painel exibe apenas as matérias de vínculo forte. O recorte de violência política de gênero tem critério próprio: a matéria só entra quando o título traz, ao mesmo tempo, um termo de IA e um termo de gênero.

A classificação é conservadora por desenho. Como o RSS entrega apenas o título, o classificador marca somente o que aparece de forma explícita, o que favorece a precisão sobre a cobertura.

## O painel

O painel lê o CSV diretamente do repositório e monta toda a visualização no navegador, sem processamento no servidor. Segue a identidade visual do laboratório, com IBM Plex Sans, JetBrains Mono e o índigo da marca.

- **Filtros combináveis** por recorte, dimensão, fonte e busca textual
- **Volume por semana** em barras clicáveis, que filtram o período
- **Barras de análise** para mecanismo, modelo de linguagem, plataforma, agente e valência
- **Mapa de calor** com cruzamento configurável entre quaisquer duas dimensões
- **Lista de matérias** com link para a fonte original e etiquetas de recorte, modelo e mecanismo
- **Layout adaptado ao celular**, com os filtros recolhidos num painel retrátil

## Estrutura do repositório

```
monitor-labiia/
├── coletar.py              # coleta + triagem + classificação
├── index.html              # painel interativo (GitHub Pages)
├── favicon.svg             # ícone do painel
├── requirements.txt        # dependências Python
├── dados/
│   └── noticias.csv        # corpus acumulado
└── .github/workflows/
    └── monitor.yml         # automação (cron de 12h)
```

## Stack

`Python` · `feedparser` · `pandas` · `GitHub Actions` · `GitHub Pages` · `HTML/CSS/JS` · `PapaParse`

## Limitações

- **Classificação só pelo título** — o RSS não entrega o corpo da matéria, então o classificador trabalha com pouco texto
- **Recorte por busca** — o recorte vem da busca que trouxe a matéria, não de uma leitura do conteúdo
- **Dependência do Google Notícias** — a cobertura reflete o que o serviço indexa nos feeds RSS

---

<div align="center">

Dados via Google News RSS · classificação por regras léxicas · atualização automática por GitHub Actions

**`<labiia_lab>`** · Eixo Política e Sociedade

</div>
