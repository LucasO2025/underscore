---
name: underscore-post-generator
description: "Use esta skill quando o usuário enviar uma ou mais músicas de rock e pedir os pacotes de post para o projeto underscore (TikTok de análise de música). Triggers incluem menções a 'underscore', 'novo lote', 'gera os posts', listas de músicas no formato 'Música - Artista', ou referência ao schema JSON do projeto. A skill pesquisa cada música, redige os textos no tom editorial definido e retorna JSONs no schema rígido prontos para colar no gerador de slides."
---

# underscore — gerador de JSONs de post

## 1. Contexto do projeto

underscore é um perfil de TikTok sobre significados de músicas de rock, operado por Lucas Cardoso como hobby. Cada post é um carrossel de 5 slides com duas leituras da mesma música (uma consensual, uma alternativa) mais uma curiosidade técnica. Conteúdo em PT-BR. Identidade visual pós-punk moderno.

Esta skill não monta slides, não gera imagens, não posta. O output é exclusivamente texto em JSON no schema definido, que o Lucas cola no gerador HTML local.

## 2. Quando a skill é acionada

O usuário envia uma lista de músicas em qualquer formato livre:

- `Paranoid - Black Sabbath, Starburster - Fontaines DC`
- `Próximo lote: 1) Song X / Artist A 2) Song Y / Artist B`
- `Gera os JSONs de Karma Police e Daydreaming, ambas do Radiohead`

Se não houver lista explícita, a skill não é acionada. Se o usuário só pedir discussão sobre uma música sem pedir o JSON, responda em prosa normal sem aplicar a skill.

## 3. Schema rígido

Todo JSON entregue deve ter esta estrutura, sem adicionar, remover ou renomear campos.

```json
{
  "id": "NNN",
  "song": "string",
  "artist": "string",
  "year": 2024,
  "album": "string",
  "albumCoverHint": "string",
  "contextBlurb": "string",
  "slides": {
    "hook": "string",
    "interpretationA": "string",
    "interpretationB": "string",
    "curiosity": {
      "youtube_url": "string",
      "image": "string",
      "gancho": "string",
      "caption": "string"
    },
    "closing": "string"
  },
  "caption": "string"
}
```

### Regras de campos

- `id`: 3 dígitos com zeros à esquerda ("001", "027", "103"). Sempre string.
- `year`: número, nunca string.
- `albumCoverHint`: onde buscar a capa em alta resolução (Discogs, Apple Music, Bandcamp), com alguma pista de qual capa específica se houver edições múltiplas.
- `contextBlurb`: linha única curta (60-110 caracteres) com contexto factual da banda e do álbum. Renderizada como metadado visual abaixo do hook no slide 1. Tom seco, sem adjetivos de press release. Ex: "Banda pós-punk irlandesa. Romance, quarto álbum, 2024.", "Trio de Sheffield. Whatever People Say I Am..., estreia em 2006.". Vale combinar origem/subgênero + álbum + posição na discografia + ano, o que fizer mais sentido na música. Proibido: "icônica", "lendária", "revolucionária", "consagrada".
- `caption`: inclui teaser, fontes e hashtags. Quebras de linha via `\n`.
- Campos `interpretationA` e `interpretationB` aceitam quebra de parágrafo via `\n\n` (ver seção 6.6).
- `curiosity` é objeto (ver seção 6.4): `youtube_url` (link do clipe/áudio da faixa), `image` (pista de imagem, texto livre), `gancho` (headline) e `caption` (apoio). **Não** preencher `waveform`: ele é gerado pelo gerador a partir do `youtube_url`, não pela skill.

## 4. Numeração (id)

Antes de começar a gerar os JSONs, pergunte ao usuário qual é o número inicial do lote, a não ser que ele já tenha informado (ex: "começa do 012"). Incremente sequencialmente a partir daí.

Se ele disser "continuar de onde parei" sem dar número, ofereça: "Qual foi o último id publicado?"

## 5. Regras de voz

### 5.1 Tom
- PT-BR
- Informal, conversacional
- Como um leitor atento escrevendo para outros leitores, não como jornalista, crítico profissional ou influencer

### 5.2 Proibições absolutas

Estas são vícios de escrita de IA. Nenhuma delas pode aparecer no output:

- **Travessões** em qualquer posição. Use vírgula, ponto, dois-pontos ou reestruture a frase. Nada de `—` nem de `--`.
- **Construção "x é y, não z"** (e todas as variantes: "não é sobre A, é sobre B", "não se trata de X, mas de Y"). É o padrão mais identificável de IA.
- **Frases de transição genéricas**: "Vale destacar", "É importante notar que", "Curiosamente", "Surpreendentemente".
- **Entusiasmo performado**: "incrível", "impressionante", "belíssima", "magistral". Adjetivos medidos.
- **Emojis** em qualquer lugar do texto ou caption.
- **Linguagem de press release**: "a faixa destaca-se", "a obra-prima consagrou", "a icônica canção".

### 5.3 Citações de letra

Trechos de letra em inglês vão entre aspas simples, sem tradução.

```
Certo: 'No one is in my tree'
Errado: "No one is in my tree" (Ninguém está na minha árvore)
Errado: 'No one is in my tree' — tradução entre travessões
```

Aspas retas apenas. Nunca aspas tipográficas.

O gerador de slides renderiza o conteúdo entre aspas simples em cor de acento italic, como destaque editorial. Isso só funciona se as aspas forem simples (`'...'`), não duplas.

Limite: cada slide pode ter 1-2 citações em inglês, não mais. Texto inteiro vira tradução de letra se exagerar.

### 5.4 Fontes e atribuição

Regra absoluta: **nomes de veículos, programas, revistas, podcasts e plataformas nunca aparecem no corpo dos slides.** Isso vale para todos os slides, sem exceção. Exemplos do que está proibido no corpo: "em entrevista à BBC Radio 1", "contou para a Apple Music", "segundo o Pitchfork", "disse à Rolling Stone", "em conversa com o Quietus", "no Song Exploder".

O que permanece permitido:

- Atribuição direta ao artista sem citar veículo: "Lennon disse", "Chatten contou", "Wood explicou", "a banda declarou". Isso atribui ao autor da música, não a uma fonte externa.
- Referência a fatos datáveis sem citar onde foram publicados: "em 2019, Isaac Wood descreveu a música como...".
- Menção a eventos históricos documentados sem fonte explícita: "em dezembro de 1965, saiu no Liverpool Echo uma fuga em massa..." (o nome do jornal é permitido apenas quando ele próprio é parte do fato histórico, não quando está sendo usado como fonte da análise).

A lista de fontes com URLs vai exclusivamente na `caption`, nunca no corpo.

## 6. Estrutura dos 5 slides

### 6.1 hook (slide 1)

- 1 frase
- 8 a 18 palavras
- Provoca curiosidade sem revelar a resposta
- Funciona como tese editorial do post
- Nunca repete a frase do closing

Exemplos aprovados:
- "Lennon dizia que era a melhor coisa que ele fez nos Beatles. Também é a mais triste."
- "A música mais luminosa do álbum também é sobre morte."
- "A música previu o que ainda não tinha acontecido."

### 6.2 interpretationA (slide 2) — leitura consensual

- 500 a 700 caracteres
- A leitura mais estabelecida da música, consolidada por declarações do artista, crítica editorial e consenso de fãs
- Cita 1 trecho de letra em inglês entre aspas simples (no A reduzido, evitar 2 citações — vira paredão)
- Texto dividido em 2 parágrafos, quebra via `\n\n`, ponto de quebra decidido por julgamento editorial (flow de leitura, ritmo argumentativo)
- Conta em profundidade, sem listas
- Pode ancorar em entrevista específica quando agregar peso ("em entrevista a X, o artista disse...")

### 6.3 interpretationB (slide 3) — leitura alternativa

Este é o slide mais crítico do post. O diferencial do projeto mora aqui.

- 700 a 900 caracteres
- Leitura menos óbvia, menos citada, ou ressignificação por contexto posterior
- Deve se sustentar na letra, na sonoridade ou em fato documentado. Nunca inventar teoria.
- Cita 1 a 2 trechos de letra em inglês entre aspas simples
- Texto dividido em 2 parágrafos, quebra via `\n\n`, ponto de quebra decidido por julgamento editorial

**Tipos aceitos de leitura alternativa:**

1. **Ressignificação por evento posterior** (sweet spot do projeto): a música ganha nova camada depois que algo aconteceu ao artista, banda ou contexto histórico. Ex: Opus do BCNR relida após a saída do Isaac Wood.
2. **Teoria alternativa documentada**: uma leitura menos popular, mas com embasamento em pesquisa, biografia, declaração menos circulada. Ex: a teoria do reformatório em Strawberry Fields.
3. **Declaração do próprio artista que contradiz o senso comum**: quando o artista falou em entrevista algo que reduz ou complica a interpretação popular.
4. **Análise musical específica**: arranjo, harmonia, estrutura ou produção que modifica a leitura emocional da letra.
5. **Contexto político/social**: situação histórica específica que muda o sentido da música.

**Erros comuns a evitar:**

- **Forçar controvérsia**: se não houver camada alternativa documentada, escolher outra música ou cair para análise musical específica. Nunca criar teoria.
- **Cair no óbvio**: "é sobre drogas" é a leitura alternativa mais batida. Mencione de passagem no máximo, procure a segunda camada.
- **Viajar**: se a leitura alternativa não se sustenta na letra, na sonoridade ou em fonte, descarte.

### 6.4 curiosity (slide 4) — nota técnica

Slide visual (foto + waveform + gancho/caption). Objeto com 4 subcampos que a
skill preenche (`youtube_url`, `image`, `gancho`, `caption`). O `waveform` fica
de fora: o gerador extrai dos 56 picos de áudio a partir do `youtube_url`.

- `gancho`: headline com o fato técnico mais surpreendente, payoff **primeiro**. ≤ 12 palavras.
- `caption`: detalhe técnico/contexto de apoio. ≤ 40 palavras.
- `youtube_url`: link do clipe ou áudio da faixa no YouTube (vira a waveform).
- `image`: pista curta de qual imagem usar (still ligado à curiosidade, ao tema, foto do artista, ou capa). Texto livre, é só orientação editorial; quem sobe a imagem é o Lucas.

Conteúdo de `gancho` + `caption`:

- Mais fato, menos interpretação
- Pode ser: técnica de gravação, escolha de produção, contexto de composição, declaração do artista, detalhe de performance ao vivo, recepção crítica no lançamento, peculiaridade da faixa no álbum
- Evitar repetir informação já mencionada nos slides A e B
- Grifo de marca: envolver títulos de música, nomes próprios e termos técnicos de impacto em `*asteriscos*` (vira acento itálico no render). Ex: `regravaram uma de *David Lynch*`. Títulos de música sempre em itálico.

### 6.5 closing (slide 5) — encerramento

- 1 frase
- 10 a 22 palavras
- Insight próprio, reflexivo
- Nunca repete o hook
- Pode referenciar algo dos slides anteriores mas com giro editorial próprio

Exemplos aprovados:
- "'Nothing is real', ele canta. Talvez seja o jeito mais honesto de falar sobre infância."
- "Tem música que finge alegria. Essa finge só o suficiente pra você aguentar."
- "A banda continua. Opus virou objeto fechado. Só termina de significar com o que veio depois."

### 6.6 Quebra de parágrafo em A e B

Slides A e B são escritos em 2 parágrafos. A quebra é representada no JSON por `\n\n` (dois line breaks literais) dentro da string do campo. O gerador HTML renderiza cada chunk separado por `\n\n` como um `<p>` independente, com respiro visual entre eles.

**Onde quebrar:** decisão editorial, não regra mecânica. Pense no flow de leitura. Costumam ser bons pontos de quebra:

- Antes ou depois de uma citação de letra, quando ela pivota o argumento
- Entre o setup (contexto, fato) e o desdobramento (o que aquilo significa)
- Entre duas fontes/camadas de argumento distintas

Não quebre só pra quebrar. Se o parágrafo lê bem inteiro e ritma natural, deixa inteiro (e nesse caso, atende ao limite como bloco único).

**Exemplo de `interpretationA` com quebra:**

```
"Strawberry Field era um orfanato da Salvation Army em Liverpool, colado à casa da tia Mimi, onde Lennon cresceu depois de ser separado dos pais. Ele pulava o muro pra brincar nos jardins com os amigos, mesmo contra as ordens da tia.\n\nA música volta pra esse lugar como refúgio, mas carrega junto a sensação de ser uma criança que via o mundo diferente dos outros: 'No one I think is in my tree, I mean it must be high or low'."
```

Curiosity e hook/closing não usam `\n\n`.

## 7. Hierarquia de fontes

Privilegie por qualidade do raciocínio, não por prestígio institucional:

1. **Entrevistas diretas do artista**: Apple Music sessions, BBC Radio 1, Rolling Stone, NPR Tiny Desk, podcasts como Song Exploder
2. **Crítica editorial estabelecida**: Pitchfork, Paste, Quietus, NME, Stereogum, Consequence
3. **Genius** quando a anotação tem upvotes altos e texto substantivo
4. **Reddit** em subs especializados (/r/letstalkmusic, /r/indieheads, /r/metal, /r/postpunk, /r/popheads, /r/progrockmusic)
5. **Wikipedia** para fatos técnicos verificáveis e contexto
6. **Blogs temáticos** reconhecidos (Songfacts, American Songwriter)

Evite:
- SEO farms (LyricFind, MusixMatch como fonte de análise)
- YouTube comments
- TikToks
- Resumos de outras IAs
- Sites tipo "5 meanings behind..."

## 8. Caption

Estrutura fixa:

```
[2-3 frases de teaser do conteúdo do post, em tom de chamada, sem repetir literalmente o hook]

fontes:
[url 1 sem https://]
[url 2 sem https://]
[url 3 sem https://]

#hashtag1 #hashtag2 ...
```

### Regras da caption

- 300 a 800 caracteres incluindo fontes e hashtags
- Separação por `\n` (respeitar no JSON)
- 2 a 5 URLs de fonte, sem `https://` para economizar espaço
- 5 a 8 hashtags sempre incluindo:
  - Nome do artista (sem espaços, lowercase): `#thebeatles`, `#fontainesdc`
  - Subgênero: `#postpunk`, `#rockclassico`, `#metalprogressivo`, `#indie`, `#shoegaze`
  - Tags do projeto: `#significadodemusica`, `#musicaanalisada`

## 9. Execução

### 9.1 Fluxo por música

1. Confirmar nome da música e artista (desfazer ambiguidade se houver: "Black Sabbath (faixa do álbum homônimo de 1970)")
2. Fazer 2 a 4 `web_search` cobrindo as fontes da hierarquia
3. Identificar a leitura consensual (slide 2)
4. Caçar a camada alternativa (slide 3), seguindo os tipos aceitos
5. Escolher 1 curiosidade técnica forte (slide 4)
6. Redigir hook e closing por último (ficam mais afiados depois que o corpo existe)
7. Montar caption
8. Entregar o JSON

### 9.2 Formato de entrega

- Antes de cada JSON, um header: `## NNN. Nome da Música — Artista (Ano)`
- JSON em bloco de código com syntax highlighting `json`
- Entre JSONs, quebra de linha apenas
- No final do lote, uma nota breve e opcional se alguma música exigiu decisão editorial peculiar

Nunca incluir seção "raciocínio" ou "análise editorial" no output. O Lucas removeu isso do fluxo.

### 9.3 Escolha de prioridade na pesquisa

Se a banda/música for obscura e não houver entrevistas nem crítica editorial, sinalize isso na entrega. Não invente interpretação B. Opções:

- Sugerir outra música do mesmo artista com mais material
- Entregar o JSON com interpretationB puxada para análise musical específica (arranjo, produção)
- Avisar na nota final do lote que a pesquisa foi limitada

### 9.4 Validações silenciosas antes de entregar

Para cada JSON, verifique internamente:

- [ ] Nenhum travessão em qualquer campo
- [ ] Nenhuma construção "x é y, não z"
- [ ] Nenhum nome de veículo, revista, podcast ou plataforma no corpo dos slides
- [ ] Citações em inglês entre aspas simples, sem tradução
- [ ] `interpretationA` dentro de 500-700 caracteres, com 1 quebra `\n\n` dividindo em 2 parágrafos
- [ ] `interpretationB` dentro de 700-900 caracteres, com 1 quebra `\n\n` dividindo em 2 parágrafos
- [ ] `curiosity` é objeto: `gancho` ≤ 12 palavras, `caption` ≤ 40 palavras, `youtube_url` preenchido, `image` com pista, `waveform` ausente (gerado pelo gerador)
- [ ] `hook` tem 8-18 palavras, `closing` tem 10-22 (ambos bloco único)
- [ ] Hook e closing dizem coisas diferentes
- [ ] interpretationA e interpretationB abordam camadas distintas
- [ ] `contextBlurb` entre 60-110 caracteres, factual e seco, sem adjetivos de press release
- [ ] Fontes na caption, nunca no corpo dos slides
- [ ] `id` em sequência correta
- [ ] `year` é número, não string
- [ ] Hashtags incluem artista, subgênero e tags do projeto

Se algum item falhar, corrija antes de entregar.

## 10. Exemplo completo

Este JSON foi validado pelo Lucas como exemplo padrão do projeto.

```json
{
  "id": "001",
  "song": "Strawberry Fields Forever",
  "artist": "The Beatles",
  "year": 1967,
  "album": "Magical Mystery Tour",
  "albumCoverHint": "Buscar capa do single duplo com Penny Lane no Discogs, ou a capa americana de Magical Mystery Tour. Ambas em alta resolução.",
  "contextBlurb": "Fase psicodélica dos Beatles. Single duplo com Penny Lane em fevereiro de 1967.",
  "slides": {
    "hook": "Lennon dizia que era a melhor coisa que ele fez nos Beatles. Também é a mais triste.",
    "interpretationA": "Strawberry Field era um orfanato da Salvation Army em Liverpool, colado à casa da tia Mimi, onde Lennon cresceu depois de ser separado dos pais. Ele pulava o muro pra brincar nos jardins com os amigos, mesmo contra as ordens da tia.\n\nA música volta pra esse lugar como refúgio, mas carrega junto a sensação de ser uma criança que via o mundo diferente dos outros: 'No one I think is in my tree, I mean it must be high or low'. Lennon explicou depois que ninguém era tão hip quanto ele, então ele devia ser gênio ou louco.",
    "interpretationB": "Tem uma leitura menos contada. Em dezembro de 1965, saiu no Liverpool Echo uma fuga em massa de meninos do Woolton Vale Remand Home, um reformatório juvenil colado ao orfanato de meninas. Lennon via o prédio da janela do quarto dele. Meses depois, filmando How I Won the War na Espanha, ele começou a escrever a música num violão emprestado, longe do barulho constante da banda pela primeira vez em anos. O rascunho original tinha só uma estrofe e nenhuma menção a Strawberry Field. O nome entrou por último, depois da letra quase pronta.\n\nA leitura que se abre aí: a música pode não ser nostalgia, pode ser luto. Pelos meninos presos a dois metros da casa dele, e pela infância do próprio Lennon, que era uma prisão de outro tipo.",
    "curiosity": {
      "youtube_url": "https://www.youtube.com/watch?v=...",
      "image": "Still do filme How I Won the War (Lennon na Espanha, 1966) ou foto do prédio Strawberry Field. Fallback: capa de Magical Mystery Tour.",
      "gancho": "A música que você conhece são duas gravações coladas no minuto 1.",
      "caption": "Lennon gravou em *lá maior* a 92 bpm, não gostou, regravou em *si bemol* a 102 bpm. *George Martin* alterou a velocidade das fitas pra casar tom e andamento e emendou as duas. A textura muda no ponto do corte."
    },
    "closing": "'Nothing is real', ele canta. Talvez seja o jeito mais honesto de falar sobre infância."
  },
  "caption": "Por trás de Strawberry Fields Forever: um orfanato em Liverpool, uma fuga noticiada no jornal local e duas gravações coladas que não deviam funcionar juntas.\n\nfontes:\nen.wikipedia.org/wiki/Strawberry_Fields_Forever\nsalon.com/2022/09/30/strawberry-fields-forever-beatles-john-lennon-origin/\namericansongwriter.com/the-meaning-behind-the-beatles-1967-classic-strawberry-fields-forever\n\n#thebeatles #johnlennon #rockclassico #historiadorock #strawberryfieldsforever #significadodemusica"
}
```

## 11. Casos de borda

### 11.1 Música sem material suficiente
Se após 4 `web_search` não surgir material consistente para sustentar duas leituras:
- Avisar o Lucas na nota final do lote
- Oferecer substituir por outra música do mesmo artista
- Se ele insistir, fazer slide B puxado para análise musical específica (letra, arranjo, escolhas de produção)

### 11.2 Música muito recente (últimos 6 meses)
Crítica editorial ainda não consolidou. Privilegiar entrevistas do artista, apple music notes, discussão em Reddit. Marcar na nota final como "leitura inicial, material ainda em formação".

### 11.3 Música com interpretação altamente disputada
Ex: músicas políticas ou com múltiplos públicos. Apresentar a leitura dominante no slide A e a mais debatida no slide B, sinalizando a disputa sem tomar lado.

### 11.4 Música de artista que saiu de cena ou morreu
Cuidado com tom. Ressignificação por morte ou desaparecimento é um dos recursos mais fortes do projeto, mas evitar espetacularização. Deixar o fato falar.

### 11.5 Cover ou versão
Se o Lucas pedir uma cover, tratar como versão própria da música. O artista do JSON é quem fez a versão, o ano é o da gravação da cover, e a interpretação pode incluir a comparação com o original.

## 12. O que não fazer

- Não assumir que o Lucas quer sugestões de próximas músicas. Se quiser, ele pede.
- Não reorganizar a ordem dos slides.
- Não propor schema novo ou expandido. Se faltar campo, entregar sem e mencionar na nota final.
- Não entregar parcialmente (4 dos 5 slides). Se uma música não tiver material, avisar e pular inteira.
- Não fazer o JSON em português com campos traduzidos. O schema está em inglês, os valores em PT-BR.
- Não incluir comentários (`//`) no JSON. JSON padrão não permite.