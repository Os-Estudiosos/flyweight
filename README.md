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
