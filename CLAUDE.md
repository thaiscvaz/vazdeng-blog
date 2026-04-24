# CLAUDE.md — VazDEng Blog

Este arquivo documenta o blog Hugo (vazdeng.pages.dev).

## Estrutura

- `hugo.yaml` — Configuração Hugo (Hextra theme, bilíngue PT-BR + EN)
- `content/blog/` — Posts (page bundles com index.md + index.en.md)
- `assets/brand/` — Imagens e recursos visuais
- `scripts/validate_post.py` — 25 validadores para CI/CD
- `scripts/next_publish_date.py` — Calcula próxima data válida (terça ou quinta)
- `.github/workflows/pages.yaml` — Deploy automático Cloudflare Pages
- `i18n/` — Strings multilíngues (PT e EN)

## Como adicionar post

```bash
make post slug=seu-slug-aqui
```

Isso cria: `content/blog/YYYY-MM-DD-seu-slug-aqui/` com `index.md` + `index.en.md`.

Alternativamente, crie manualmente a estrutura:

```
content/blog/2026-04-30-seu-slug/
├── index.md       (PT-BR com frontmatter + conteúdo)
├── index.en.md    (EN com frontmatter + conteúdo)
└── cover.png      (imagem de capa)
```

## Frontmatter obrigatório

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

## Validação pré-deploy

```bash
make validate
# ou:
python3 scripts/validate_post.py content/blog/seu-post/
```

Valida:
- YAML frontmatter bem-formado
- Bilíngue (index.md + index.en.md)
- Cover image presente
- Slug único
- PublishDate em terça (weekday=1) ou quinta (weekday=3)

## Critérios VazDEng

Veja `../Blog/EDITORIAL.md` para os 6 critérios obrigatórios de conteúdo.

**Resumo:** O post deve nascer de experiência real em produção, ter uma decisão clara no centro, incluir contexto BR onde relevante, declarar escala, mostrar o que dá errado, e pressupor leitor sênior.

## Próxima data válida de publicação

```bash
python3 scripts/next_publish_date.py
```

Retorna próxima terça ou quinta em YYYY-MM-DD.

## Deploy

Merge em `main` dispara `.github/workflows/pages.yaml`:
1. Hugo build
2. Validação de posts
3. Upload para Cloudflare Pages
4. Deploy automático → vazdeng.pages.dev

## Referências

- `hugo.yaml` — Tema Hextra + configuração i18n
- `../vazdeng/Blog/EDITORIAL.md` — Backlog editorial centralizado
- `../vazdeng/projeto_blog/` — Documentação de arquitetura (agentes, pipeline)
