# AGENTS.md — Quick-reference do vazdeng-blog

Entrada rápida pra agente (ou humano com pressa). Não substitui `CLAUDE.md` (build/deploy) nem `WRITER.md` (regras de escrita).

## Comandos essenciais

| Quero | Comando |
|---|---|
| Validar todos os posts | `python scripts/validate_post.py content/blog` |
| Validar um post | `python scripts/validate_post.py content/blog/SLUG/index.md` |
| Validar vários de uma vez | `python scripts/validate_post.py FILE1 FILE2 FILE3` |
| Modo strict (warnings reprovam) | `python scripts/validate_post.py content/blog --strict` |
| Dev server local | `hugo server --buildDrafts --buildFuture -p 1313` |
| Build de produção | `hugo --minify` |
| Limpar cache de build | `rm -rf public resources/_gen` |
| Instalar Lefthook pre-commit | `npm i -g @evilmartians/lefthook && lefthook install` |
| Bypass do pre-commit local | `git commit --no-verify` |

Atalhos: `.\scripts\validate.ps1` (Windows), `make validate` (Linux/Mac).

## Paths-chave

| Onde | O quê |
|---|---|
| `content/blog/YYYY-MM-DD-slug/` | Page bundle de cada post (PT + EN + cover) |
| `content/sobre/` | Página "Sobre" |
| `layouts/` | Overrides do tema Hextra |
| `assets/css/custom.css` | CSS vanilla (nunca Tailwind `hx:`) |
| `data/icons.yaml` | SVG icons inline |
| `i18n/{pt,en}.yaml` | Strings de UI |
| `static/_redirects` | Cloudflare Pages redirects |
| `static/_headers` | Cloudflare Pages headers |
| `scripts/validate_post.py` | Validador anti-IA + estrutural |
| `.github/workflows/validate.yml` | CI de validação (diff em PR) |
| `hugo.yaml` | Config Hugo + módulos + i18n |

## Fluxo de um post

```
1. EDITORIAL.md (no repo vazdeng)        backlog de pautas
2. vazdeng/posts/{slug}/fontes.md        pesquisa primária
3. vazdeng/posts/{slug}/index.md         rascunho PT
4. (Substack draft via scripts vazdeng)  preview, ajustes
5. vazdeng-blog/content/blog/.../        migração final PT + EN
6. python scripts/validate_post.py       gate local
7. git commit + PR                       CI valida diff
8. merge main                            Cloudflare Pages publica
```

## Regras invioláveis (resumo)

Detalhe e justificativa em `WRITER.md`.

- Travessão `—` proibido
- Frontmatter PT precisa de title/slug/date/publishDate/description/tags
- Frontmatter EN precisa de title/description
- Paridade bilíngue: cada `index.md` exige `index.en.md`
- Score >= 8/10 e zero erros pra passar no CI
- `publishDate` em terça (weekday=1) ou quinta (weekday=3)
- Tom humano, sem palavrão, sem fórmulas AI ("É importante notar...", "Vale ressaltar...", "Em suma...")

## Quando algo dá errado

| Sintoma | Onde olhar |
|---|---|
| Build Hugo quebrou | Erro provável em frontmatter YAML ou shortcode inexistente |
| CSS não carrega | Conferir `assets/css/custom.css` e `head-end.html` em `layouts/_partials/custom/` |
| Validador falhou no CI | Rodar local com `python scripts/validate_post.py <arquivo>` e ler warning/error |
| Ícone de menu sumiu | `data/icons.yaml` + referência em `menu.main.params.icon` no `hugo.yaml` |
| String i18n faltando | `i18n/pt.yaml` e `i18n/en.yaml` precisam da mesma chave |
| Post não aparece no list | Conferir `draft: false` e `publishDate <= today` |

## Glossário rápido

- **Page bundle**: pasta de post com `index.md` + recursos (imagens, etc) juntos. Padrão Hugo.
- **Hextra**: tema do blog, instalado como Go module em `go.mod`.
- **Cloudflare Pages**: host. Deploy automático no push em `main`.
- **Front matter**: bloco YAML no topo do `.md` com metadados.
- **i18n**: internacionalização. PT-BR é canonical, EN é sibling file `.en.md`.
- **Score**: nota do validador. 10 - 2×erros - warnings. Gate >= 8.
