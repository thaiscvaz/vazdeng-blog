---
title: "TODO Título do post"
slug: "{{ replace (path.Base (path.Dir .File.Path)) (printf "%s-" (now.Format "2006-01-02")) "" }}"
date: {{ now.Format "2006-01-02" }}
publishDate: {{ now.Format "2006-01-02" }}
draft: false
description: "TODO Resumo de 1 linha que vai pro <meta description> e RSS."
tags: []
images: []
---

TODO conteúdo do post.

Lembrete de checklist antes de publicar (`Blog/posts/CHECKLIST.md`):
- Sem menção a projeto interno do trabalho atual
- Sem travessão "—"
- Slug curto no front matter
- Imagem dentro do bundle, com alt text descritivo
- `images:` apontando pra imagem (vira og:image)
- Versão EN traduzida e com slug próprio em `index.en.md`
