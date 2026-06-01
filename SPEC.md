# SPEC — underscore

**Versão:** 1.0
**Data:** Abril 2026

Especificação técnica do sistema underscore. Complementa o PRD.md com detalhes de implementação, schemas, algoritmos e limitações.

## 1. Arquitetura

underscore é composto por dois módulos independentes:

### 1.1 Módulo de geração de conteúdo

- Executado em conversa com Claude via chat web, sem API
- Guiado pela skill `underscore-post-generator` (ver SKILL.md)
- Entrada: lista de músicas em formato livre
- Saída: um JSON por música, no schema rígido
- Zero integração, zero persistência, zero custo

### 1.2 Gerador de slides (front-end)

- Arquivo HTML único, executado localmente no browser
- Entrada: JSON do post + imagem da capa do álbum
- Saída: 5 arquivos PNG em 1080x1350
- Sem servidor, sem build, sem framework, sem dependência npm

## 2. Schema JSON

Schema fixo. Qualquer alteração quebra o gerador e a skill ao mesmo tempo.

```json
{
  "id": "NNN",
  "song": "string",
  "artist": "string",
  "year": 2024,
  "album": "string",
  "albumCoverHint": "string",
  "slides": {
    "hook": "string",
    "interpretationA": "string",
    "interpretationB": "string",
    "curiosity": {
      "youtube_url": "string",
      "image": "string",
      "gancho": "string",
      "caption": "string",
      "waveform": [0.0]
    },
    "closing": "string"
  },
  "caption": "string"
}
```

### 2.1 Regras de campos

| Campo | Tipo | Regras |
|---|---|---|
| `id` | string | Sempre 3 dígitos com zeros à esquerda ("001" a "999") |
| `song` | string | Nome da música exatamente como aparece no álbum |
| `artist` | string | Nome do artista ou banda |
| `year` | number | Ano de lançamento do álbum, não string |
| `album` | string | Nome do álbum |
| `albumCoverHint` | string | Texto livre indicando onde buscar a capa em alta resolução |
| `slides.hook` | string | 8 a 18 palavras |
| `slides.interpretationA` | string | 700 a 900 caracteres |
| `slides.interpretationB` | string | 700 a 900 caracteres |
| `slides.curiosity` | object | Slide visual (ver 2.3) |
| `slides.closing` | string | 10 a 22 palavras |
| `caption` | string | 300 a 800 caracteres incluindo fontes e hashtags |

### 2.2 Convenções internas

- Citações de letra em inglês vão entre aspas simples: `'No one is in my tree'`. O gerador converte aspas simples em destaque cor de acento italic.
- Nunca usar aspas tipográficas (" "). Aspas retas apenas.
- Quebras de linha em `caption` são preservadas (use `\n` no JSON).
- Nenhum campo aceita HTML.

### 2.3 Objeto `curiosity`

O slide de curiosidade (04 / NOTA TÉCNICA) é visual, no padrão do hook: foto em
duotone + waveform (assinatura de áudio) + gancho/caption alinhados à esquerda.

| Subcampo | Tipo | Regras |
|---|---|---|
| `youtube_url` | string | URL do clipe/áudio da faixa. **Input** do pipeline de waveform. Opcional se `waveform` já vier preenchido. |
| `image` | string | Pista de imagem (still, tema, artista). É **hint** editorial, não é carregada pelo browser (CORS/`file://`); a foto real vem por upload no gerador, com fallback pra capa. |
| `gancho` | string | Headline com o fato mais surpreendente. ≤ 12 palavras. |
| `caption` | string | Detalhe técnico de apoio. ≤ 40 palavras. |
| `waveform` | array | 56 floats 0..1 (RMS normalizado). **Gerado** pelo backend a partir de `youtube_url`. Opcional no JSON: se ausente, o gerador extrai ao vivo; se presente, é usado direto (offline-friendly). |

Convenções de texto em `gancho` e `caption`:

- `*termo*` (asteriscos) vira destaque verde/acento itálico no render. Títulos de
  música, nomes próprios e termos técnicos de impacto. Mesma cor das aspas `'...'`.
- Travessões continuam proibidos (vale a regra geral do projeto).

Waveform: 56 barras simétricas em torno do eixo central, cor de acento do post,
opacidade 0.45→1.0 conforme amplitude. N=56 é fixo, é a assinatura visual do
projeto, não muda entre slides.

Cores do slide: duotone preto (`#0A0A0A`) → acento do post, igual ao hook. A foto
é banda no topo do conteúdo (não full-bleed), seguida da waveform e do texto.

## 3. Algoritmos do front-end

### 3.1 Duotone

Aplicado à capa do álbum no slide 1. Map pixel a pixel da luminância para um gradiente entre duas cores fixas.

```
para cada pixel (r, g, b):
  lum = (0.299*r + 0.587*g + 0.114*b) / 255
  r_saida = dark.r + (light.r - dark.r) * lum
  g_saida = dark.g + (light.g - dark.g) * lum
  b_saida = dark.b + (light.b - dark.b) * lum
```

Valores padrão:
- `dark` = cor de acento do post
- `light` = `#F4F1EA` (off-white)

A imagem é redimensionada para no máximo 1600px na maior dimensão antes do processamento, por performance.

### 3.2 Extração de cor dominante

Algoritmo de sampling quantizado, sem dependência externa.

1. Redimensiona a imagem para 120x120 num canvas temporário
2. Itera pixels em incrementos de 4 bytes (RGBA)
3. Para cada pixel:
   - Descarta se luminância < 35 (muito escuro) ou > 225 (muito claro)
   - Descarta se `max(r,g,b) - min(r,g,b) < 35` (baixa saturação, cinza)
   - Quantiza cada canal em buckets de 32 valores
   - Incrementa contagem do bucket `(qr, qg, qb)`
4. Retorna o bucket com maior frequência
5. Se luminância do resultado < 80, multiplica por fator para clarear (evita cor ilegível como acento)
6. Se nenhum bucket sobreviver, retorna `null` (UI pede escolha manual)

### 3.3 Grain overlay

SVG fractal noise aplicado via pseudo-elemento `::after` em cada slide. Base64 inline no CSS, sem request externo. `mix-blend-mode: overlay` com opacidade 0.65.

Se `mix-blend-mode` causar problema no html2canvas em algum browser, o overlay pode ser desabilitado removendo o bloco `.slide::after`.

### 3.4 Waveform (assinatura de áudio)

Pipeline no backend (`server.py`, endpoint `/waveform`), acionado quando o slide
de curiosidade tem `youtube_url` e não traz `waveform` pronto:

1. `yt-dlp` baixa só o áudio (`bestaudio`) da URL
2. `ffmpeg` reduz a WAV mono 8 kHz 16-bit (leve pra ler em memória)
3. divide a duração total em N=56 blocos iguais
4. RMS por bloco (lê mais limpo que pico bruto)
5. normaliza pelo máximo global (barra mais alta sempre chega a 1.0)
6. arredonda para 3 casas, devolve o array

O áudio é temporário e apagado em seguida; só os 56 números sobrevivem. Cache
por `sha1(url)` evita rebaixar a mesma faixa. O gerador nunca recalcula em render:
lê o array (do JSON ou da resposta do backend) e desenha as barras.

## 4. Layout dos slides

Todos os slides são 1080x1350 (razão 4:5). Medidas abaixo em pixels absolutos.

### 4.1 Slide 1 — hook sobre capa

- Capa em duotone ocupa os primeiros 860px do topo
- Gradiente linear dos últimos 160px da capa desaparece em preto
- Área preta sólida inferior (490px): `accent-bar` (56x4px) + hook + meta-row
- Top-bar flutuante no canto superior com `mix-blend-mode: difference` para legibilidade sobre qualquer capa

### 4.2 Slides 2, 3 — texto

Estrutura idêntica, temas alternam:

- Slide 2 (INTERPRETAÇÃO): tema dark (fundo preto, texto off-white)
- Slide 3 (CAMADA): tema light (fundo off-white, texto preto)

Layout:
- Top-row: id + ano em JetBrains Mono 15px
- Number block: número grande (01, 02) em Bricolage Grotesque 200, 196px / accent-line 72x3px / section-label JetBrains Mono 16px uppercase
- Body: DM Sans 28px, line-height 1.42, letter-spacing -0.007em
- Foot-row: artista/música + assinatura

### 4.2.1 Slide 4 — curiosidade (NOTA TÉCNICA)

Slide visual, fundo preto. Ordem vertical (1080×1350):

- Top-row: underscore + ano
- Número compacto `03` + accent-line + label NOTA TÉCNICA (Bricolage 88px, não o 196px dos slides 2/3, que não cabe junto com a foto)
- Foto em banda duotone: 960×430, preto → acento, `object-fit: cover`
- Waveform: 960×64, 28px abaixo da foto, 56 barras simétricas em cor de acento
- Gancho: Bricolage Grotesque 500, 56px, off-white
- Caption: DM Sans 400, 30px, off-white 62%
- Foot-row: artista/música + assinatura

Gancho e caption ficam num bloco flex (evita overlap com altura variável do
gancho). `*termo*` e `'...'` viram acento itálico.

### 4.3 Slide 5 — encerramento

- Fundo preto
- Top-row com id e "FIM"
- Bloco central: accent-bar 96x6px + outro em Bricolage Grotesque italic 72px
- Foot-row com assinatura maior (36px)

### 4.4 Tipografia

| Fonte | Axis/Peso | Onde |
|---|---|---|
| Bricolage Grotesque | 200 a 800 (variable) | Hook, números, closing, assinatura |
| DM Sans | 400 / 500 | Body, em (italic cor de acento) |
| JetBrains Mono | 400 / 700 | Labels, meta, monospaced |

Todas via Google Fonts carregadas no head com `display=swap`.

### 4.5 Assinatura

Elemento repetido em todo slide. Padrão:

```html
<span class="sig">underscore</span>
```

CSS aplica `_` antes do texto em cor de acento:

```css
.sig::before { content: "_"; color: var(--accent); }
.sig { font-family: 'Bricolage Grotesque'; font-weight: 700; text-transform: lowercase; }
```

## 5. Stack completa

| Componente | Tecnologia | Versão | Origem |
|---|---|---|---|
| Markup | HTML5 | — | Nativo |
| Estilos | CSS3 | — | Nativo |
| Scripts | JavaScript ES2020 | — | Nativo |
| Fontes | Bricolage Grotesque, DM Sans, JetBrains Mono | latest | fonts.googleapis.com |
| Export | html2canvas | 1.4.1 | cdnjs.cloudflare.com |
| Geração de texto | Claude (chat) | Opus 4.7 em diante | claude.ai |

## 6. Fluxo de dados completo

```
┌──────────────────────────────────────────────────┐
│ 1. Lucas envia lista de músicas                 │
│    formato livre, ex: "Paranoid, Black Sabbath"  │
└─────────────┬────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│ 2. Claude executa skill underscore-post-generator│
│    - web_search em múltiplas fontes              │
│    - aplica regras editoriais                    │
│    - gera JSON por música                        │
└─────────────┬────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│ 3. Lucas valida textos e baixa capas dos álbuns │
│    (Discogs, Apple Music)                        │
└─────────────┬────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│ 4. Abre underscore-gerador.html no browser      │
│    - cola JSON                                   │
│    - upload da capa                              │
│    - extrai cor ou define manual                 │
│    - gera slides                                 │
│    - revisa preview                              │
│    - baixa 5 PNGs                                │
└─────────────┬────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│ 5. TikTok: upload do carrossel + cola caption   │
└──────────────────────────────────────────────────┘
```

## 7. Limitações conhecidas

### 7.1 CORS em URLs de imagem
A maioria dos CDNs de streaming musical (Spotify, Apple Music) bloqueia cross-origin. URLs externas não funcionam para extração de cor nem duotone na maioria dos casos. Workaround: sempre fazer download da capa antes e carregar por upload local.

### 7.2 Renderização do html2canvas
Certos CSS modernos render diferente no preview vs no export:
- `mix-blend-mode` pode ser ignorado ou aplicado errado
- `backdrop-filter` não é suportado
- `object-fit: cover` é suportado desde a versão 1.4

Se algum elemento render estranho no PNG exportado, primeiro suspeito é o html2canvas, não o CSS.

### 7.3 Capa em baixa resolução
Abaixo de 1500x1500 o duotone fica pixelado. A skill avisa o usuário para buscar em Discogs/Apple Music sempre que possível.

### 7.4 Textos longos
Se algum `interpretationA` ou `B` ultrapassar 900 caracteres, o body transborda no slide. O primeiro ajuste é no JSON (respeitar o limite), não no CSS.

### 7.5 Cor dominante feia
Capas com paleta dominada por cinzas, beges ou terrosos podem retornar cor de acento sem personalidade. O seletor manual é a saída.

### 7.6 Apagar histórico
O gerador não persiste nada entre sessões. Cada música é uma execução nova. O histórico (JSON + PNGs) é responsabilidade do Lucas, em arquivo local.

## 8. Roadmap técnico

Backlog não priorizado, candidato a v3.0:

- Templates visuais alternativos (brutalist, xerox/fanzine, glitch, cyberpunk)
- Histórico local em IndexedDB com busca
- Gerador de caption multi-plataforma (TikTok + Instagram + X) caso o projeto se expanda
- Paleta expandida (accent + secondary) para posts com arte de capa complexa
- Preview mobile (simular o que aparece no TikTok antes de publicar)
- Modo de comparação lado a lado de variações de cor

## 9. Estrutura de arquivos sugerida

Não obrigatória, mas útil para o Lucas organizar:

```
underscore/
├── underscore-gerador.html        # app principal
├── PRD.md                         # documento de produto
├── SPEC.md                        # este arquivo
├── CLAUDE.md                      # contexto para Claude Code
├── SKILL.md                       # skill de geração de JSON
├── posts/                         # histórico
│   ├── 001-strawberry-fields-forever.json
│   ├── 001-assets/                # capa + PNGs exportados
│   ├── 002-favourite.json
│   └── ...
└── README.md                      # opcional, overview
```
