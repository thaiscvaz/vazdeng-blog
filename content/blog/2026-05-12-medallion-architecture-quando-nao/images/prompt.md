# Prompt — Diagrama de decisão Medallion Architecture

**Onde usar no post:** após a seção "A pergunta certa antes de decidir", antes de "O que empresas grandes usam na prática".

**Rodar em:** Claude Desktop (gera como artifact SVG ou HTML)

---

## Prompt para Claude Desktop

```
Crie um diagrama de decisão em SVG para um blog de engenharia de dados.

Título no topo: "Preciso de Medallion Architecture?"

Três perguntas em sequência vertical, com bifurcações:

INÍCIO (caixa arredondada no topo)
  ↓
[ Há múltiplos consumidores com necessidades diferentes? ]
  → NÃO →  [ Questione quantas camadas você precisa ] (resultado laranja, à direita)
  ↓ SIM
[ Reprocessar dados na fonte é caro ou impossível? ]
  → NÃO →  [ Questione quantas camadas você precisa ] (resultado laranja, à direita)
  ↓ SIM
[ A latência de cada camada cabe no prazo do negócio? ]
  → NÃO →  [ Questione quantas camadas você precisa ] (resultado laranja, à direita)
  ↓ SIM
[ Use Medallion Architecture ] (resultado verde, centralizado)

Especificações visuais:
- Fundo: #1a2035 (navy escuro)
- Texto principal: #f0ece2 (creme)
- Caixas de pergunta: borda #f0ece2 com preenchimento #1e2740, texto creme
- "NÃO" e resultados laranja: fundo #e07b30, texto branco
- "SIM": texto #f0ece2 nas setas
- Resultado verde: fundo #2d6a4f, texto branco
- Fonte: sans-serif limpa (Inter ou system-ui)
- Largura total: 700px, altura conforme necessário
- Setas com ponta, sem ornamentos
- Sem sombras excessivas
- Estilo editorial técnico, minimalista

Exportar como SVG completo, pronto para salvar como arquivo e usar em blog.
```

---

**Depois de gerar:** salvar como `decision-tree.svg` (ou `.png`) nesta pasta `images/`.
