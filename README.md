# Club GG Hand Reader

Ferramenta de leitura de ecrã para o cliente **desktop Windows** do Club GG,
feita para uma mesa recreativa (play money) entre amigos, no âmbito de um
projeto final de curso.

> **Aviso:** esta ferramenta lê o teu próprio ecrã em tempo real. Usa-a apenas
> em mesas onde isso seja aceitável para todos os envolvidos (play money,
> entre amigos). Não a uses em mesas de dinheiro real ou em contextos onde
> ferramentas de assistência em tempo real sejam proibidas pelos termos da
> plataforma.

## O que faz

1. Encontra e captura a janela do Club GG (sem precisar de gravar o ecrã todo).
2. Usa regiões calibradas por ti (um clique-e-arrasta único, guardado em
   `regions.json`) para saber onde estão: as tuas 2 cartas, as 5 cartas
   comunitárias, e os textos de stack/blind de cada jogador.
3. Reconhece as cartas por *template matching* — precisas de "ensinar" cada
   carta uma vez (ver `Passo 2` abaixo); os templates ficam guardados em
   `templates/` e são reutilizados em todas as sessões seguintes.
4. Lê os números de stack/blind com OCR (`pytesseract`/Tesseract).
5. Mostra no terminal, em tempo real: as tuas cartas, o board, a força da tua
   mão (ex: "Par de Ases", "Flush", ...) e os stacks/blinds lidos.

## Instalação (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Instala também o **Tesseract OCR** (necessário para ler números):
https://github.com/UB-Mannheim/tesseract/wiki — depois de instalado, confirma
o caminho do executável em `src/ocr.py` (`TESSERACT_CMD`).

## Passo 1 — Arrancar o servidor

**Atalho no ambiente de trabalho (recomendado):** corre uma vez

```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

Isto cria `Club GG Hand Reader.lnk` no teu ambiente de trabalho. A partir
daí basta dar duplo clique no atalho — ele ativa o venv, instala
dependências se faltarem, arranca o servidor e abre `http://127.0.0.1:5000`
no browser.

Ou manualmente:

```powershell
python -m src.webapp
```

Vais ver o painel principal, mas sem cartas — falta calibrar e ensinar
(próximos passos). Tudo isto é feito **dentro do browser**, sem janelas do
OpenCV nem introduzir texto no terminal.

## Passo 2 — Calibrar a mesa (uma vez por layout)

Com o Club GG aberto numa mesa (pode ser só para veres o layout, não precisa
de estar em jogo), abre **Calibrar** no menu do topo (`http://127.0.0.1:5000/calibrate`):

1. **Escolhe a janela certa** numa lista de todas as janelas abertas no teu
   PC (evita confundir com o próprio browser ou outras apps).
2. Escolhe quantos lugares tem a mesa e clica em "Começar calibração".
3. Para cada região pedida (as tuas 2 cartas, board 1-5, stack/blind de cada
   seat) desenha um retângulo à volta da área correspondente **arrastando o
   rato diretamente na imagem** do ecrã capturado. Confirma, ou usa "Saltar"
   se essa região não existir na tua mesa (ex: menos jogadores).
4. No fim é guardado automaticamente em `regions.json`.

Só precisas de repetir este passo se mudares o layout/tamanho da janela do
Club GG.

## Passo 3 — Ensinar as cartas (ao longo de algumas mãos)

Abre **Ensinar cartas** no menu do topo (`http://127.0.0.1:5000/teach`). Com
uma mão em jogo, a página mostra o recorte ampliado de cada carta e pedes
para escreveres o valor (ex: `Ah` = Ás de copas, `Td` = 10 de ouros). Clica
"Guardar" e passa automaticamente à seguinte. Repete ao longo de várias mãos
até teres as 52 cartas guardadas em `templates/` — só precisas de ensinar
cada carta uma vez.

## Passo 4 — Usar

Volta ao **Painel** (`http://127.0.0.1:5000/`). Atualiza-se sozinho a cada
segundo, com uma mesa estilizada, o banner da força da mão, e um cartão por
jogador com stack/blind.

### Alternativa em terminal (sem UI)

Se preferires, há também uma versão simples de linha de comandos:

```powershell
python -m src.main
```

```
Hole cards : Ah Kh
Board      : Qh Jh Th
Mão        : Straight Flush (Royal Flush)
Seat 1     : stack=1450  blind=25
Seat 2     : stack=980   blind=50
```

Esta usa o mesmo `regions.json` e `templates/` calibrados na web, mas ainda
tens as ferramentas antigas de terminal (`python -m src.calibrate` e
`python -m src.collect_templates`, com janelas OpenCV) caso prefiras — não
são recomendadas por serem mais confusas de usar.

## Estrutura

- `src/capture.py` — localizar e capturar a janela do Club GG.
- `src/regions.py` — carregar/guardar `regions.json`.
- `src/calibrate.py` — ferramenta interativa para desenhar as regiões.
- `src/templates.py` — matching de cartas contra `templates/`.
- `src/collect_templates.py` — ferramenta interativa para ensinar cartas.
- `src/ocr.py` — leitura de números (stacks/blinds) via Tesseract.
- `src/hand_eval.py` — avaliação da força da mão (usa `treys`).
- `src/state.py` — junta captura + reconhecimento + avaliação num snapshot.
- `src/main.py` — versão em terminal.
- `src/webapp.py` — servidor local Flask: serve a UI web em `static/` e os
  endpoints `/api/screenshot`, `/api/regions`, `/api/card-crop`, `/api/teach`
  usados pelas páginas de calibração/ensino.
- `static/index.html` + `app.js` — painel principal (mão atual, board, seats).
- `static/calibrate.html` + `calibrate.js` — calibração de regiões desenhando
  retângulos no browser.
- `static/teach.html` + `teach.js` — ensino de cartas a partir de recortes
  mostrados no browser.
- `start_app.bat` / `create_shortcut.ps1` — atalho de um clique.
