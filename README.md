# Jogo: floresta com e sem Flyweight

Jogo top-down em pygame: o jogador (quadrado vermelho) anda pelas 4 direções num mundo de
8000x8000 px, a câmera o acompanha e milhares de árvores de 4 espécies ficam espalhadas
aleatoriamente. Existem duas versões, que só diferem na forma de guardar as árvores:

| | Sem Flyweight (`trees_naive.py`) | Com Flyweight (`trees_flyweight.py`) |
|---|---|---|
| Cada árvore guarda | posição, nome, cores **e o próprio sprite** | posição + referência para um `TreeType` |
| Sprites na memória | 1 por árvore | 1 por espécie (4) |

As classes seguem o exemplo da floresta do
[refactoring.guru](https://refactoring.guru/design-patterns/flyweight):

| refactoring.guru | Aqui | Papel |
|---|---|---|
| `TreeType` | `TreeType` | flyweight: estado intrínseco (nome, cores, sprite), imutável |
| `TreeFactory` | `TreeFactory` | fábrica: devolve o `TreeType` existente ou cria um novo |
| `Tree` | `Tree` | contexto: estado extrínseco (`x`, `y`) + referência ao `TreeType` |
| `Forest` | `Forest` | cliente: planta as árvores |

O resto (`player.py`, `camera.py`, `game.py`, `sprites.py`) é compartilhado, e as duas
versões usam a mesma seed, então plantam exatamente as mesmas árvores nos mesmos lugares.

## Como rodar

Requer **Python 3.14** e [uv](https://docs.astral.sh/uv/). Usa o `pygame-ce` (fork mantido
do pygame, também importado como `pygame`), que já tem wheel para Python 3.14.

```bash
uv sync
uv run jogo-sem-flyweight
uv run jogo-com-flyweight
```

Controles: **WASD** ou **setas** para andar, **ESC** para sair.

Opções (valem para as duas versões):

```bash
uv run jogo-com-flyweight --arvores 20000   # quantidade de árvores (padrão: 10000)
uv run jogo-com-flyweight --segundos 10     # fecha sozinho depois de 10 s
```

## Como ver a diferença

### 1. Pelo próprio jogo (terminal)

O jogo não mostra nada na tela, mas imprime no terminal:

- ao iniciar: quantos sprites distintos existem, quanta memória eles ocupam, quanto tempo
  levou para criar a floresta e o RSS (RAM do processo) antes e depois;
- a cada 2 s: FPS, RAM (RSS) e CPU% do processo;
- ao sair: CPU média e o pico de RAM.

Rode as duas versões, uma depois da outra, e compare. Saída real com 20.000 árvores
(`--arvores 20000 --segundos 3`):

```
=== Floresta SEM Flyweight ===                    === Floresta COM Flyweight ===
Sprites (Surfaces) distintos   20.000             Sprites (Surfaces) distintos        4
Memória dos sprites          692.0 MB             Memória dos sprites            0.1 MB
Tempo para criar a floresta   1523 ms             Tempo para criar a floresta     49 ms
RSS antes da floresta         37.4 MB             RSS antes da floresta         37.4 MB
RSS depois da floresta       743.4 MB             RSS depois da floresta        41.9 MB
FPS 62.5 | RAM 743.1 MB | CPU 38.9%               FPS 62.9 | RAM 42.1 MB | CPU 37.9%
```

Com o padrão (10.000 árvores) a diferença é de ~390 MB contra ~39 MB.

**O que esperar:** a diferença aparece na **RAM** e no **tempo de carregamento**, que
crescem com o número de árvores na versão sem Flyweight e ficam praticamente parados na
versão com Flyweight. **FPS e CPU ficam parecidos** nas duas, porque a câmera só desenha
as árvores que estão na tela (~100 a 450) e desenhar um sprite custa o mesmo, seja ele
compartilhado ou não. O Flyweight economiza memória, não processamento.

### 2. Com ferramentas do sistema (Linux)

Pico de memória do processo inteiro, medido pelo sistema operacional:

```bash
/usr/bin/time -v uv run jogo-sem-flyweight --segundos 10 2>&1 | grep "Maximum resident"
/usr/bin/time -v uv run jogo-com-flyweight --segundos 10 2>&1 | grep "Maximum resident"
```

(com 20.000 árvores: 761.144 KB contra 43.004 KB)

Acompanhando ao vivo, com o jogo aberto, em outro terminal (colunas `RES` = RAM e `%CPU`):

```bash
top -p "$(pgrep -f jogo-sem-flyweight)"
# ou
htop -p "$(pgrep -f jogo-com-flyweight)"
```

Sem abrir janela (útil em servidor/CI ou só para medir):

```bash
SDL_VIDEODRIVER=dummy uv run jogo-sem-flyweight --segundos 5
SDL_VIDEODRIVER=dummy uv run jogo-com-flyweight --segundos 5
```

Dica: aumente `--arvores` (por exemplo, 20000 ou 50000) para deixar a diferença mais
evidente. Na versão sem Flyweight cada árvore custa ~35 KB, então 50.000 árvores pedem
cerca de 1,7 GB de RAM.

---

# Exemplos de Flyweight em Python

Requer **Python 3.11+**.

```
exemplos/
├── exemplo_chat/
│   ├── chat.py               # Author (flyweight), AuthorFactory, Message (contexto), ChatHistory (cliente)
│   └── demo_chat.py          # compara memória SEM x COM Flyweight
└── exemplo_relatorio/
    ├── assets.py             # Asset (flyweight), SharedAssetStore (fábrica), LocalStorage / S3Storage
    ├── relatorios.py         # Report (estado extrínseco), InlineAssetTags (antes), SharedAssetTags (depois)
    ├── relatorio.css         # estilo compartilhado por todos os relatórios
    └── demo_relatorios.py    # gera relatórios ANTES e DEPOIS e compara tamanhos
```

## Exemplo 1: renderizador de mensagens de chat

Adaptação, para Python, do exemplo de https://www.patterns.dev/vanilla/flyweight-pattern/.
50.000 mensagens escritas por 30 pessoas: os dados do autor (nome, avatar, cor, cargo)
viram um único objeto `Author` compartilhado, e cada `Message` guarda só texto, horário
e a referência para o autor.

```bash
cd exemplo_chat
python demo_chat.py            # ou: python demo_chat.py 100000 50
```

Saída de referência:

```
                                  Sem Flyweight   Com Flyweight
Memória ocupada pelas mensagens         27,1 MB         11,8 MB   (-57%)
Objetos com dados de autor               50.000              30
```

## Exemplo 2: relatórios HTML com bibliotecas JS compartilhadas

Cada relatório embutia uma cópia inteira do Plotly (~4,8 MB). Agora a biblioteca é
publicada uma vez em um storage, com o hash do conteúdo no nome (imutável e com cache
eterno), e cada HTML guarda apenas a URL.

```bash
pip install -r requirements.txt
cd exemplo_relatorio
python demo_relatorios.py      # gera ./saida/antes, ./saida/depois e ./saida/storage
```

Saída de referência (40 relatórios):

```
                              ANTES (embutido)    DEPOIS (Flyweight)
Tamanho médio por HTML                 4,61 MB               9,34 KB
Uploads para o storage                       -                     2   (78 reaproveitamentos)
Rede estimada: 22,49 GB -> 1,39 GB (-94%)
```

Para ver o relatório funcionando, sirva a pasta de saída e abra no navegador
(abrir o arquivo direto também funciona, porque a URL é relativa):

```bash
python -m http.server 8000 --directory saida
```

Depois acesse http://localhost:8000/depois/loja_01.html.

Em produção, troque o `LocalStorage` por
`S3Storage("nome-do-bucket", "https://cdn.suaempresa.com.br")` (requer `boto3`).
