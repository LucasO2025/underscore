# PRD — underscore

**Versão:** 2.0
**Data:** Abril 2026
**Responsável:** Lucas Cardoso
**Status:** Em operação

## 1. Visão geral

underscore é um perfil de TikTok sobre significados de músicas de rock. Cada post é um carrossel de 5 slides que entrega duas leituras da mesma música (uma consensual e uma menos óbvia) mais uma nota técnica. Conteúdo em PT-BR, estética pós-punk moderna, operação totalmente manual, sem custos recorrentes.

A versão 1.0 do projeto foi desenhada para Twitter/X, com escopo aberto a qualquer gênero musical. A versão 2.0 pivota para TikTok, restringe o nicho a rock e seus subgêneros, elimina dependência de APIs pagas e abandona a hipótese de monetização em favor da sustentabilidade como hobby.

## 2. Ficha

| Campo | Valor |
|---|---|
| Nome | underscore |
| Plataforma | TikTok (carrossel de imagens) |
| Idioma | PT-BR |
| Escopo musical | Rock e subgêneros (clássico, alternativo, post-punk, indie, metal, shoegaze, math rock, industrial, noise, psicodélico etc.) |
| Frequência | 3 a 4 posts por semana |
| Objetivo | Hobby, sem meta de monetização |
| Custo operacional | Zero |
| Postagem | Manual |

## 3. Problema e oportunidade

Conteúdo de análise musical em profundidade existe em abundância, mas está fragmentado: crítica editorial em inglês no Pitchfork e NME, anotações de fãs em Genius, teorias em Reddit, declarações de artistas dispersas em entrevistas. Quem quer entender uma música de rock em camadas precisa caçar por quatro ou cinco fontes e ainda traduzir.

Em PT-BR a oferta cai drasticamente. O que sobra tende a ser: canais de curiosidades superficiais, vídeo-ensaio longo no YouTube (formato que demanda 20+ minutos de atenção) ou resumos automatizados por IA sem curadoria.

A oportunidade é consolidar essa camada de análise em formato bite-sized, com identidade editorial forte e tom de voz reconhecível, ocupando um espaço que hoje é ou muito raso ou muito denso.

## 4. Objetivos

### 4.1 Objetivos principais

- Publicar 3 a 4 posts por semana com qualidade editorial estável
- Construir identidade visual reconhecível no feed
- Operar sem custos
- Manter o projeto sustentável como hobby

### 4.2 Não-objetivos (v2.0)

- Monetização direta (adesivos, parcerias, Creator Fund)
- Postagem automática ou integração com API do TikTok
- Publicação em outras plataformas (Instagram Reels, YouTube Shorts, X, Substack)
- Conteúdo em idiomas além de PT-BR
- Análise de performance ou métricas de engajamento
- Vídeos ou audio overlay automáticos

Essas decisões podem ser revisitadas em uma v3.0, mas ficam explicitamente fora do escopo atual para evitar scope creep.

## 5. Público-alvo

Ouvintes de rock que já consomem conteúdo de análise musical (Pitchfork, videoessays, podcasts de música) e querem a mesma densidade em formato curto e em português. Faixa provável: 18 a 40 anos. Não precisa de explicação básica sobre o artista. Valoriza contexto histórico, leitura de letra, detalhe técnico de gravação e referências cruzadas entre álbuns.

## 6. Fluxo operacional

```
[lista de músicas] → [chat com Claude + skill] → [JSONs por música]
                                                        ↓
[JSON + imagem da capa] → [gerador HTML local] → [5 PNGs por música]
                                                        ↓
                                              [upload manual no TikTok]
```

### 6.1 Geração de conteúdo

1. Lucas monta mentalmente ou em lista um conjunto de 3 a 5 músicas de rock
2. Envia a lista numa conversa com Claude, invocando a skill `underscore-post-generator`
3. Claude pesquisa cada música em múltiplas fontes, aplica as regras editoriais do projeto e retorna um JSON por música no schema fixo
4. Lucas valida os textos (se algum não está no tom certo, pede ajuste)

### 6.2 Montagem visual

1. Abre o gerador HTML local no browser
2. Cola o JSON de uma música
3. Faz upload da capa do álbum (download prévio do Discogs ou Apple Music)
4. Extrai a cor de acento automaticamente ou define manualmente
5. Gera os 5 slides, revisa o preview
6. Baixa os 5 PNGs

### 6.3 Publicação

1. Abre o TikTok
2. Upload dos 5 PNGs como carrossel
3. Cola a caption do JSON
4. Publica

## 7. Requisitos de conteúdo

### 7.1 Tom de voz

- Informal, conversacional, como um leitor atento escrevendo para outros leitores
- Sem emojis
- Sem linguagem de press release ("destaca-se", "vale mencionar", "curiosamente")
- Sem entusiasmo performado ("incrível", "impressionante")
- Adjetivos medidos
- Primeira pessoa é permitida pontualmente, terceira é o padrão

### 7.2 Proibições de estilo

- Travessões em qualquer posição
- Construção "x é y, não z" (ou variantes: "não é sobre A, é sobre B")
- Frases de transição genéricas
- Citações de letra com tradução automática ao lado

### 7.3 Estrutura obrigatória por post

Um carrossel de 5 slides na ordem:

1. **Hook** — uma frase (8 a 18 palavras) que provoca curiosidade sem entregar a resposta
2. **Interpretação A** — leitura consensual da música, 700 a 900 caracteres
3. **Interpretação B** — leitura alternativa, menos óbvia ou ressignificação, 700 a 900 caracteres
4. **Curiosidade** — nota técnica de composição, produção ou contexto, 500 a 700 caracteres
5. **Encerramento** — uma frase (10 a 22 palavras) que fecha com insight próprio

Cada música gera também uma caption para o TikTok com 2-3 frases de teaser, fontes listadas e 5-8 hashtags.

### 7.4 Hierarquia de fontes

Por qualidade de raciocínio, não por origem institucional:

1. Entrevistas diretas do artista (Apple Music, BBC Radio, Rolling Stone, NPR, podcasts)
2. Crítica editorial estabelecida (Pitchfork, Paste, Quietus, NME, Rolling Stone, Stereogum)
3. Anotações bem votadas em Genius com texto substantivo
4. Threads densas de Reddit em subs especializados
5. Wikipedia para fatos técnicos
6. Blogs temáticos reconhecidos (Songfacts, American Songwriter)

## 8. Requisitos estéticos

### 8.1 Identidade visual

Pós-punk moderno, inspirado em direção de arte de selos como Sacred Bones e na editorial da Dazed e da i-D. Minimalismo com personalidade, tipografia como elemento gráfico, muito espaço negativo, contrastes duros.

### 8.2 Paleta

- Preto profundo `#0A0A0A` (nunca preto absoluto)
- Off-white `#F4F1EA` (nunca branco absoluto)
- Cor de acento variável por post, extraída da capa do álbum

### 8.3 Tipografia

| Uso | Fonte |
|---|---|
| Hook, número de seção, closing, assinatura | Bricolage Grotesque |
| Body das interpretações e curiosidade | DM Sans |
| Labels, meta, código | JetBrains Mono |

### 8.4 Capa em duotone

Toda capa de álbum passa por tratamento duotone: gradiente entre a cor de acento (sombras) e o off-white (highlights). Isso unifica visualmente capas de gêneros e épocas diferentes.

### 8.5 Assinatura

Todo slide termina com `_underscore` no canto inferior direito, em Bricolage Grotesque lowercase, com o underscore em cor de acento.

## 9. Requisitos técnicos

### 9.1 Dimensões

Todos os slides são renderizados em 1080x1350 pixels, razão 4:5, formato recomendado pelo TikTok para carrossel.

### 9.2 Stack

- HTML + CSS + JavaScript puro (arquivo único)
- html2canvas 1.4.1 via CDN para exportação PNG
- Google Fonts para tipografia
- Sem backend, sem build, sem framework

### 9.3 Custo

Zero. Todas as ferramentas são gratuitas. A geração de texto acontece em chat com Claude (conta pessoal do Lucas), o gerador roda localmente, as fontes são open source, o upload é manual.

## 10. Fora de escopo (v2.0)

Itens deliberadamente adiados:

- Templates visuais alternativos (brutalist, fanzine, glitch)
- Histórico local dos posts com busca
- Cross-posting automatizado
- Variação por subgênero (ex: layout mais pesado para metal)
- Análise de engajamento via API do TikTok
- Sistema de agendamento ou fila editorial

## 11. Métricas de sucesso

Como o projeto é hobby, não há KPI formal. Os sinais que indicam sucesso:

- Lucas continua publicando (sustentabilidade)
- Os posts que ele faz passam no seu próprio crivo editorial (qualidade)
- O fluxo de produção por música leva menos que 30 minutos do JSON ao upload (eficiência)

Se o projeto começar a demandar mais esforço do que entrega em satisfação, ou se a qualidade começar a cair sistematicamente, o PRD deve ser revisitado, não forçado.

## 12. Histórico de versões

| Versão | Data | Mudanças |
|---|---|---|
| 1.0 | Abril 2026 | Versão inicial para Twitter/X, qualquer gênero, postagem manual, IA para pesquisa e reescrita |
| 2.0 | Abril 2026 | Pivot para TikTok, nicho fechado em rock, objetivo passa a hobby, eliminação de custos recorrentes, identidade visual pós-punk moderno definida, gerador HTML implementado |
