# CLAUDE.md — vazdeng-blog

Este arquivo documenta **como mexer no repositório do blog**: estrutura, build, validação, deploy.

Para **regras de escrita** (anti-IA, critérios editoriais, fontes), ler `WRITER.md`.
Para **navegação rápida** (paths, comandos, fluxo), ler `AGENTS.md`.

## Stack

- Hugo + tema Hextra (Go module em `go.mod`)
- Cloudflare Pages (host de produção: `vazdeng.pages.dev`)
- Bilíngue PT-BR + EN nativo via Hugo i18n (sufixo `.en.md`)
- Validação Python em `scripts/validate_post.py`

## Estrutura

```
vazdeng-blog/
├── content/
│   ├── _index.md / _index.en.md          home
│   ├── sobre/                            página sobre
│   └── blog/                             posts (page bundles)
│       └── 2026-04-28-slug/
│           ├── index.md                  PT-BR
│           ├── index.en.md               EN
│           └── cover.png
├── layouts/                              overrides do Hextra
├── assets/css/custom.css                 CSS vanilla
├── data/icons.yaml                       SVG icons inline
├── i18n/{pt,en}.yaml                     strings de UI
├── static/                               OG images, fonts, redirects
├── scripts/
│   ├── validate_post.py                  validador anti-IA + estrutural
│   └── validate.ps1                      wrapper PowerShell
├── .github/workflows/validate.yml        CI: valida posts modificados
├── Makefile                              targets Linux/Mac
├── hugo.yaml                             config Hugo
├── CLAUDE.md                             este arquivo
├── WRITER.md                             regras de escrita
└── AGENTS.md                             quick-reference
```

## Criar post novo

```bash
mkdir -p content/blog/$(date +%Y-%m-%d)-meu-slug
# criar index.md + index.en.md + cover.png dentro
```

`publishDate` deve cair em terça (weekday=1) ou quinta (weekday=3). Frontmatter mínimo em `WRITER.md`.

## Validação pré-deploy

**Windows (PowerShell):**
```powershell
.\scripts\validate.ps1                          # valida todos
.\scripts\validate.ps1 -Strict                  # warnings reprovam
.\scripts\validate.ps1 -File content/blog/2026-04-28-slug/index.md
```

**Linux/Mac (make):**
```bash
make validate
make validate-strict
make validate-file F=content/blog/2026-04-28-slug/index.md
```

**Direto (qualquer SO):**
```bash
python scripts/validate_post.py content/blog
python scripts/validate_post.py content/blog/2026-04-28-slug/index.md
```

O `scripts/validate_post.py` é autocontido neste repo. Cobre 13 regras de padrão (anti-IA) + 5 validações estruturais. Gate de aprovação: score >= 8/10 e zero erros. Catálogo completo de regras em `WRITER.md`.

**Locale-aware:** regras PT-BR não disparam em arquivos `.en.md`.

**CI:** `.github/workflows/validate.yml` valida só os posts modificados no PR. Push em main valida o que mudou. `workflow_dispatch` permite rodar em modo `all`.

**Lefthook (pre-commit local):** `lefthook.yml` antecipa o CI. Instalar uma vez:

```bash
npm install -g @evilmartians/lefthook    # ou: brew install lefthook
lefthook install                         # registra hooks em .git/hooks/
```

A partir daí, `git commit` em arquivos `content/blog/**/index*.md` dispara `scripts/validate_post.py` nos staged files. `git push` roda validação completa em `content/blog/`. Bypass: `git commit --no-verify` (use só pra cleanup deliberado de post antigo).

## Build e dev local

```bash
hugo server --buildDrafts --buildFuture -p 1313   # dev
hugo --minify                                     # build em public/
```

CSS: vanilla em `assets/css/custom.css`. Nunca usar Tailwind `hx:` (JIT do Hextra não compila override).
Ícones novos: SVG em `data/icons.yaml`, referenciar via `icon: <nome>` no menu do `hugo.yaml`.
Strings de UI: editar `i18n/pt.yaml` + `i18n/en.yaml`, referenciar via `{{ T "key" }}` em templates.

## Deploy

Merge em `main` dispara `.github/workflows/pages.yaml` (se existir):
1. Build Hugo
2. Upload Cloudflare Pages
3. Deploy em `vazdeng.pages.dev`

Validação roda em paralelo no `.github/workflows/validate.yml` e gateia o merge.

## Relação com vazdeng (ShowRunner)

| Repositório | Visibilidade | Função |
|---|---|---|
| workspace de produção | privado (local) | Rascunhos, automação de publicação |
| vazdeng-blog (este) | público — thaiscvaz/vazdeng-blog | Site Hugo publicado (`vazdeng.pages.dev`) |
| landing do guia | privado (local) | Landing page (`vazdeng-site.pages.dev`) |

**Fluxo:** rascunho nasce em `vazdeng/posts/{slug}/index.md`, migra pra `vazdeng-blog/content/blog/YYYY-MM-DD-slug/`. Este repo é o destino publicado, não o workspace de escrita.

## Referências

- `hugo.yaml` — config Hugo + Hextra + i18n
- `WRITER.md` — regras de escrita e critérios editoriais
- `AGENTS.md` — quick-reference de paths, comandos e fluxo
- `../vazdeng/EDITORIAL.md` — backlog editorial centralizado (no repo do ShowRunner)
