# CLAUDE.md

Contexto para o Claude Code (ou qualquer Claude) quando for trabalhar no código do projeto underscore.

## O que é

underscore é um gerador de slides para carrossel do TikTok. Um arquivo HTML único, sem build e sem backend, que recebe um JSON estruturado e uma imagem de capa de álbum e devolve 5 PNGs em 1080x1350 prontos para upload.

O projeto tem três documentos de referência que devem ser lidos antes de mexer em qualquer código:

- `PRD.md` — produto, decisões, tom editorial
- `SPEC.md` — especificação técnica, schema, algoritmos
- `SKILL.md` — regras de geração de conteúdo textual

Este arquivo cobre apenas o lado de implementação.

## Stack

- HTML5 + CSS3 + JavaScript ES2020 puro
- Arquivo único (`underscore-gerador.html`)
- html2canvas 1.4.1 via cdnjs (única dependência externa)
- Google Fonts: Bricolage Grotesque, DM Sans, JetBrains Mono

Qualquer lib nova precisa cumprir três requisitos não-negociáveis:

1. Estar disponível em CDN gratuito (cdnjs, jsdelivr, unpkg)
2. Funcionar sem nenhum build step
3. Continuar operando se o usuário salvar a página completa e rodar offline depois de carregada

## Como rodar

Abra `underscore-gerador.html` em um browser moderno (Chrome ou Edge recomendados pelo melhor suporte ao html2canvas). Não precisa servidor. Não precisa `npm install`. Funciona em file:// local.

## Estrutura interna

```
<head>
  └─ imports de fontes Google
  └─ <style> com:
       ├─ CSS variables globais
       ├─ UI (controles, grid, mensagens)
       └─ layout dos slides

<body>
  ├─ .app                    container visível
  │   ├─ header              logo e tagline
  │   ├─ .controls           textarea JSON, uploads, color picker
  │   ├─ #messages           área de erros e avisos
  │   ├─ .action-bar         botões gerar e baixar todos
  │   └─ #slides-container   grid de previews escalados
  │
  ├─ .render-stage           slides em 1080x1350 offscreen para export
  │                          (left: -99999px, pointer-events: none)
  │
  └─ <script>
      ├─ state global
      ├─ utils (hex/rgb, escape, formatBody)
      ├─ carregamento de imagem (file e url)
      ├─ extractDominantColor (clustering simples)
      ├─ applyDuotone (canvas pixel manipulation)
      ├─ builders de slide (buildSlide1, buildTextSlide, buildSlide5)
      ├─ renderAll (monta stage + preview grid)
      ├─ downloadSlide / downloadAllSlides (html2canvas)
      └─ event bindings
```

## Convenções

### CSS
- Use CSS variables para cores. Nunca `#0A0A0A` hardcoded em um seletor, sempre `var(--black)`.
- Todo slide recebe `style="--accent: ${state.accent};"` inline no root. A cor muda por post.
- Classes: `.slide` é base, `.slide-1` / `.slide-text` / `.slide-5` são tipos, `.slide-dark` / `.slide-light` são temas modificadores.
- Proibido: Tailwind, Bootstrap, qualquer framework de CSS.
- Unidades: pixels absolutos nos slides (1080x1350 é fixo, não existe responsividade do slide). Na UI, use `rem` para tamanhos tipográficos.

### JavaScript
- Vanilla puro. Nada de ES modules (arquivo único, tem que rodar em file://).
- `async/await` para operações assíncronas (FileReader, canvas, fetch).
- `state` global como única fonte de verdade. Evite espalhar dados em closures.
- Toda operação que pode falhar (canvas tainted, JSON parse, image load) dentro de `try/catch` com `showMsg()` no UI.
- IDs em DOM: `kebab-case`. Variáveis JS: `camelCase`. Constantes: `UPPER_SNAKE_CASE` apenas quando realmente imutáveis.
- Nenhum binding global, exceto `els` e `state`.

### Nomenclatura
- Slides sempre numerados a partir de 1 no contexto humano (slide 1 é o hook) mas a partir de 0 nos arrays/stage do JS (`stage-slide-0` é o hook). Documentar nos comentários se houver ambiguidade.

## Coisas que NÃO devem ser feitas

- **Não adicione framework JS.** Nem React, Vue, Svelte, Alpine, nada. O arquivo precisa continuar single-file plug-and-play. Essa decisão é editorial, não técnica.

- **Não mude o schema JSON sem coordenação.** A skill em `SKILL.md` gera JSONs nesse formato exato. Mudar o schema sem atualizar a skill quebra o fluxo de produção.

- **Não mude as dimensões 1080x1350.** TikTok espera exatamente essa razão para carrossel. Mudar implica reeditar todos os posts antigos.

- **Não adicione chamadas de API de IA.** O projeto é intencionalmente zero-cost. Se precisar de análise de imagem ou cor, implemente localmente via canvas.

- **Não persista dados sem avisar o usuário.** Uso de `localStorage` só com consentimento explícito. Nenhum envio para analytics, nenhum tracking.

- **Não mexa em `.render-stage` exceto para adicionar slides.** Esse stage existe para o html2canvas capturar em tamanho real. Se ele ficar visível ou fora de 1080x1350, o export quebra.

- **Não importe fontes fora das três definidas.** Bricolage Grotesque, DM Sans e JetBrains Mono são a identidade. Adicionar uma quarta desestabiliza o visual.

## Testing

Não há suite automatizada. O ciclo é manual:

1. Salvar o arquivo
2. Recarregar no browser (Ctrl+Shift+R para limpar cache)
3. Abrir DevTools, ficar de olho no console
4. Colar um JSON de exemplo (veja seção "Exemplo de JSON" abaixo)
5. Carregar uma imagem de teste
6. Gerar, baixar, inspecionar os PNGs

### Cenários de teste recomendados

- Capa em alta resolução (3000x3000): não deve travar
- Capa em baixa resolução (500x500): deve gerar mas alertar visualmente (pixelado)
- JSON com campo faltando: deve mostrar erro claro
- JSON com estouro de caracteres (1500 chars em interpretationA): texto transborda, documentar que limite é no conteúdo
- Cor de acento muito escura (`#111111`): contraste some, seletor manual deve corrigir
- URL externa de capa: CORS vai dar erro, mensagem deve orientar upload local
- Texto com aspas simples (`'quote'`): deve renderizar em cor de acento italic

### Exemplo de JSON para testes

```json
{
  "id": "TST",
  "song": "Test Song",
  "artist": "Test Artist",
  "year": 2024,
  "album": "Test Album",
  "albumCoverHint": "teste",
  "slides": {
    "hook": "Uma frase de teste que cabe em até dezoito palavras no máximo.",
    "interpretationA": "Texto de teste para a interpretação A. Deve ter entre 700 e 900 caracteres. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Citação: 'this is a test quote in English'. Continuação do texto com mais conteúdo até atingir o tamanho mínimo esperado. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium.",
    "interpretationB": "Texto de teste para a interpretação B. Precisa ter tamanho similar. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Outra citação: 'another test quote'. Mais texto aqui para completar. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est qui dolorem ipsum quia dolor sit amet consectetur adipisci velit.",
    "curiosity": {
      "youtube_url": "https://www.youtube.com/watch?v=...",
      "image": "Pista de imagem de teste. Fallback: capa do álbum.",
      "gancho": "Um gancho de teste com um *termo grifado* e título *Test Song*.",
      "caption": "Caption técnica de teste citando *fita analógica* e *George Martin* como termos grifados, com o detalhe que sustenta o gancho sem repetir os slides anteriores.",
      "waveform": [0.12,0.34,0.21,0.55,0.43,0.67,0.38,0.72,0.5,0.61,0.29,0.48,0.83,0.7,0.41,0.9,0.66,0.52,0.35,0.77,0.6,0.44,0.88,0.71,0.39,0.58,0.95,0.63,0.47,0.8,0.54,0.33,0.69,0.5,0.42,0.76,0.61,0.37,0.84,0.66,0.49,0.3,0.73,0.57,0.4,0.81,0.64,0.46,0.78,0.59,0.36,0.7,0.52,0.28,0.45,0.22]
    },
    "closing": "Frase final de teste que fecha o post com algum tipo de insight reflexivo."
  },
  "caption": "Caption de teste.\n\nfontes:\nexemplo.com/fonte1\n\n#teste #rock"
}
```

## Debug comum

- **Slide aparece em branco no preview**: `state.duotoneDataUrl` é `null`, geralmente canvas tainted por CORS. Subir imagem local.
- **Fontes em serif padrão**: Google Fonts não carregou. Checar DevTools > Network > aba Fonts.
- **Export em PNG aparece corrompido**: versão do html2canvas incompatível com algum CSS, ou `backgroundColor: null` gerando transparência onde não devia. Checar flags de `html2canvas()`.
- **Slides com tamanhos diferentes nos PNGs exportados**: algum slide no `.render-stage` perdeu o tamanho fixo de 1080x1350. Inspecionar `.stage-slot`.

## Como propor mudanças

Se for mexer em algo significativo:

1. Abrir PRD.md e SPEC.md para entender o porquê das decisões atuais
2. Verificar se a mudança não entra em conflito com "Fora de escopo" no PRD
3. Se envolver schema JSON, coordenar atualização do SKILL.md no mesmo commit
4. Testar pelo menos 3 JSONs diferentes antes de considerar pronto

## Pessoa do projeto

Lucas Cardoso, Tech Lead e Web Analyst. Background em Python, N8N, automação, análise web. Prefere código direto, sem over-engineering. Não usa TypeScript no projeto (escolha consciente pela simplicidade), mas o código é escrito de forma que migrar seria relativamente simples se necessário no futuro.
