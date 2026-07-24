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

## Passo 1 — Calibrar as regiões da mesa

Com o Club GG aberto numa mesa (pode ser só para veres o layout, não precisa
de estar em jogo):

```powershell
python -m src.calibrate
```

Isto tira um screenshot da janela do Club GG e abre uma janela do OpenCV.
Para cada região pedida no terminal (as tuas 2 cartas, board_1..board_5,
seat1_stack, seat2_stack, ...), desenha um retângulo com o rato à volta da
área correspondente e carrega em `ENTER`. No fim é gerado `regions.json`.

Só precisas de repetir este passo se mudares o layout/tamanho da janela do
Club GG.

## Passo 2 — Ensinar as cartas (uma vez)

```powershell
python -m src.collect_templates
```

Com uma mão em jogo (ou usando a mesa de "practice"), a ferramenta mostra o
recorte de cada carta detetada e pergunta o valor (ex: `Ah` para Ás de
Copas, `Td` para 10 de Ouros). Repete até teres as 52 cartas guardadas em
`templates/`. Podes correr isto ao longo de várias mãos — só precisas de
ensinar cada carta uma vez.

## Passo 3 — Correr o leitor

Tens duas formas de correr, ambas leem o teu ecrã localmente (não há nenhuma
versão "cloud" possível — a captura de ecrã tem de correr na tua máquina):

### Opção A — Interface web bonita (recomendado)

```powershell
python -m src.webapp
```

Abre automaticamente `http://127.0.0.1:5000` no browser, com uma mesa
estilizada, animações a "distribuir" cartas, banner com a força da mão e um
painel por jogador com stack/blind. Atualiza-se sozinha a cada segundo.

**Atalho no ambiente de trabalho:** corre uma vez

```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```

Isto cria `Club GG Hand Reader.lnk` no teu ambiente de trabalho. A partir
daí basta dar duplo clique no atalho — ele ativa o venv, instala
dependências se faltarem, arranca o servidor e abre o browser.

### Opção B — Terminal simples

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
- `src/webapp.py` — servidor local Flask que serve a UI web em `static/`.
- `static/` — HTML/CSS/JS da interface web.
- `start_app.bat` / `create_shortcut.ps1` — atalho de um clique.
