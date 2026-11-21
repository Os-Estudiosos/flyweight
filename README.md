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

## A refatoração preservou o comportamento

`comparar-versoes` monta as duas florestas e confere que elas plantam as mesmas árvores
(posição e espécie, na mesma ordem) e desenham a mesma imagem, pixel a pixel, com a câmera
em 9 pontos do mundo. Não abre janela.

```bash
uv run comparar-versoes
```

```
=== Comparando as duas versões (10.000 árvores, seed 42) ===
Mesmas árvores (posição e espécie), na mesma ordem: 10.000 de 10.000
Mesma imagem, pixel a pixel, em 9 posições da câmera: 9 de 9 (1.822 árvores desenhadas)
Resultado: comportamento preservado
```

---

# Toy problem: alunos e a ementa do curso

Exemplo pequeno, separado do jogo, usado para ensinar o padrão antes da refatoração. Fica num
arquivo só, `toy_problem.py`, e só usa a biblioteca padrão: mil alunos de dois cursos, em que
cada aluno carregava a sua própria cópia da ementa (~300 KB) do curso.

| Papel | No `toy_problem.py` |
|---|---|
| Flyweight | `Curso`: nome e ementa (estado intrínseco), imutável |
| Fábrica | `CursoFactory`: cria o `Curso` só na primeira vez |
| Contexto | `Aluno`: nome do aluno (estado extrínseco) + referência ao `Curso` |
| Cliente | o bloco `__main__`, que pede os cursos à fábrica |

```bash
uv run python toy_problem.py
```

```
SEM Flyweight: 1000 ementas na memória,  300.4 MB
COM Flyweight:    2 ementas na memória,    0.6 MB

Aluno 1 cursa Engenharia
sem[1].ementa is sem[3].ementa -> False (cópias)
com[1].curso is com[3].curso   -> True (mesmo objeto)
com[1].curso.nome = 'Medicina' -> FrozenInstanceError
```
