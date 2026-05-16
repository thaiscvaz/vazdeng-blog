# WRITER.md — Regras de escrita do vazdeng-blog

Este arquivo define **como escrever post** que passa no validador e na barra editorial VazDEng. Quem está aqui pra mexer no repo (build, deploy, CI) deve ler `CLAUDE.md`. Quem quer navegar rápido, `AGENTS.md`.

## Os 6 critérios VazDEng

Todo post precisa cumprir os seis. Sem exceção. Fonte canônica em `../vazdeng/EDITORIAL.md`.

1. **Nasceu de produção real.** Tem exemplo concreto que aconteceu, não hipótese.
2. **Tem uma decisão no centro.** "Por que X e não Y" precisa estar explícito.
3. **Contexto BR onde relevante.** LGPD, custo de cloud em real, stack de empresas BR.
4. **Escala declarada.** Tem números reais (volume, custo, tempo, taxa de erro).
5. **Mostra o que dá errado.** Anti-padrão, regressão, falha. Não só vitória.
6. **Leitor é sênior.** Pressupõe que sabe o básico. Sem definir "o que é pipeline".

## Regras de pesquisa (antes de escrever)

Todo post técnico exige fontes primárias salvas em `../vazdeng/posts/{slug}/fontes.md`:

- Prioridade: empresa que criou o conceito > empresa que usa em produção > análise independente
- Marcar claramente fato verificado vs opinião de praticante
- Números reais precisam de contexto (de onde vêm, o que medem exatamente)
- Nenhuma afirmação como fato sem fonte primária

## Frontmatter

**PT-BR (`index.md`):**
```yaml
---
title: "Título em português"
slug: seu-slug-aqui
date: 2026-04-30
publishDate: 2026-04-30
draft: false
description: "Descrição curta (50-160 chars)"
tags: ["tag1", "tag2"]
images:
  - cover.png
---
```

**EN (`index.en.md`):**
```yaml
---
title: "Title in English"
description: "Short description"
tags: ["tag1", "tag2"]
---
```

EN herda `slug`, `date`, `publishDate` do PT via Hugo. Só `title` e `description` precisam ser explícitos.

## Regras de escrita

- Proibido travessão `—` no texto corrido. Use ponto ou vírgula.
- Tom humano, pessoal, direto. Sem academiquês.
- Abertura com cena ou tensão real, não com definição.
- Termos em inglês: explicar brevemente na primeira ocorrência se não forem universais (pipeline, batch, lakehouse, etc).
- Nenhum número sem fonte verificável.
- Frases curtas misturadas com longas.
- Listas só quando 3+ itens enumeráveis.
- Anedota ou exemplo concreto antes de generalizar.

## Anti-IA (catálogo completo do validador)

O `scripts/validate_post.py` detecta os padrões abaixo. **Conteúdo em PT-BR** dispara as regras `lang_scope: pt`. **EN** só dispara as `lang_scope: any`.

### ERROR (reprova o gate)

| Padrão | Exemplo do que evitar |
|---|---|
| Travessão `—` | "Engenharia de dados — fluxo essencial" |
| Frase de transição AI | "É importante notar que...", "Vale ressaltar...", "Cabe destacar...", "Em conclusão...", "Como vimos...", "Além disso,...", "No entanto,...", "Contudo,...", "Dessa forma,...", "É válido mencionar...", "Nesse sentido..." |
| Hedge genérico estendido | "Em suma,...", "Fundamentalmente,...", "Essencialmente,...", "Basicamente,...", "Vale a pena notar...", "Vale destacar...", "É fundamental...", "É interessante notar..." |
| Abertura genérica AI | "No cenário atual...", "Em um mundo...", "Com o avanço...", "Na era da...", "Vivemos em um momento...", "A tecnologia está..." |
| Self-label de insight | `**Insight:**`, `**Importante:**`, `**Nota:**`, `**Atenção:**`, `**Resultado:**` |

### WARNING (degradam o score)

| Padrão | Por que evitar |
|---|---|
| CTA genérico | "Me conta nos comentários", "O que você acha?" Substitui por pergunta específica ao tema. |
| Generalização vaga | "A maioria das empresas...", "Muitas empresas..." Troca por contexto específico ou dado real. |
| Percentual inventado | 80-99% sem fonte. Usa dado real ou remove. |
| Fake-revelação | "Mas aqui está o ponto", "Aqui está o segredo", "O ponto é o seguinte". Integra direto. |
| Experiência pessoal vaga | "Passei por isso em produção." Especifica: onde, quando, qual sistema. |
| Seção com número redondo | "## 5 lições", "## 7 princípios", "## 3 razões". Estrutura AI favorita. |
| Meta-narrativa | "Neste post vou contar como...", "Este artigo cobre...". Corta. O post mostra por si. |
| "Você está errado" | "A pergunta está errada", "Você está fazendo errado". Começa com o problema, não com a lição. |
| Conector genérico soft | "Isso significa que", "Por outro lado", "Portanto,". Pode ser legítimo. Verifica se a prosa fica melhor sem. |

## Validações estruturais

| Check | Regra |
|---|---|
| Frontmatter PT | `title`, `slug`, `date`, `publishDate`, `description`, `tags` obrigatórios |
| Frontmatter EN | `title`, `description` obrigatórios (resto herda do PT) |
| Word count | 600 a 1200 palavras (ideal 600-800). Abaixo de 500 = ERROR. |
| Primeira pessoa | Mínimo 3 marcadores (eu, minha, fiz, vi, aprendi...) |
| Bullets no corpo | Máximo 8. Prefere prosa fluida. |
| Paridade bilíngue | Cada `index.md` exige `index.en.md` irmão. |
| Headline-corpus match | >=60% das palavras-chave do título devem aparecer no corpo. |

## Score e gate

```
score = 10 - (errors * 2) - warnings
gate  = score >= 8 AND errors == 0
```

`--strict`: warnings também reprovam (score deve ser 10).

## Antes de commitar um post

1. `python scripts/validate_post.py content/blog/SEU-POST/` em ambos `index.md` e `index.en.md`
2. Conferir paridade: ambos arquivos existem e cobrem as mesmas seções H2
3. Conferir `cover.png` ou pular se `images: []`
4. Conferir `publishDate` cai em terça ou quinta

## Quando o validador erra (falso positivo)

Acontece com expressões legítimas que coincidem com padrão AI. Casos conhecidos:
- "Isso significa que" usado como conector natural de prosa (regra `ai_transition_soft`, WARNING não ERROR)
- "A maioria" usado com contexto específico ("a maioria dos pipelines de bronze que vi no Bradesco...")

Decisão: aceitar o warning ou reescrever a frase. **Não silenciar a regra no script** sem discutir antes.
