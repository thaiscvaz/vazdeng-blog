#!/usr/bin/env python3
"""
validate_post.py — Validador de posts do vazdeng-blog.

Detecta padroes de escrita AI, violacoes das regras editoriais, e problemas
de estrutura antes de publicar. Versao do blog (autocontida no repo).

Origem: extendido a partir de vazdeng/scripts/validate_post.py.
Regras novas vs. origem:
  - extended_hedging: hedge generico tipo "Em suma", "Fundamentalmente"
  - headline_keywords_in_body: palavras-chave do titulo devem cair no corpo
  - bilingual_parity: cada index.md exige index.en.md irmao
  - locale-aware: regras PT-BR nao rodam em arquivos .en.md

Uso:
  python scripts/validate_post.py content/blog/2026-04-28-slug/index.md
  python scripts/validate_post.py content/blog/ --all
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Regras de padrao. Cada regra marca lang_scope: "pt", "en" ou "any".
RULES = {
    "em_dash": {
        "pattern": r"—",
        "msg": "Travessao '—' proibido. Use '.' ou ','.",
        "severity": "ERROR",
        "lang_scope": "any",
    },
    "ai_transition": {
        "pattern": r"\b(É importante notar|Vale ressaltar|Cabe destacar|Em conclusão|"
                   r"Como vimos|Além disso,|No entanto,|Contudo,|Dessa forma,|"
                   r"É válido mencionar|Nesse sentido)\b",
        "msg": "Frase de transicao AI detectada.",
        "severity": "ERROR",
        "lang_scope": "pt",
    },
    "ai_transition_soft": {
        "pattern": r"\b(Isso significa que|Por outro lado|Portanto,)\b",
        "msg": "Conector generico (pode ser legitimo). Verifica se a prosa fica melhor sem ele.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "extended_hedging": {
        "pattern": r"\b(Em suma|Fundamentalmente|Essencialmente|Basicamente|"
                   r"Vale a pena (notar|destacar|mencionar|lembrar)|"
                   r"Vale destacar|É fundamental|É interessante (notar|observar))\b",
        "msg": "Hedge generico AI. Corta ou afirma direto.",
        "severity": "ERROR",
        "lang_scope": "pt",
    },
    "ai_opener": {
        "pattern": r"^(No cenário atual|Em um mundo|Com o avanço|Na era da|"
                   r"Vivemos em um momento|A tecnologia está|Num mundo cada vez)",
        "msg": "Abertura generica AI. Comeca com experiencia real.",
        "severity": "ERROR",
        "multiline": True,
        "lang_scope": "pt",
    },
    "ai_insight_label": {
        "pattern": r"\*\*(Insight|Ponto chave|Nota|Atenção|Importante|Resultado)(\s*(crítico|chave|importante))?\s*:\*\*",
        "msg": "Self-label de insight ('**Insight:**'). Integra na prosa.",
        "severity": "ERROR",
        "lang_scope": "pt",
    },
    "ai_engagement_cta": {
        "pattern": r"(Me conta nos comentários|O que você acha\?|Deixa nos comentários|"
                   r"Compartilhe sua experiência|Qual é a sua opinião)",
        "msg": "CTA de engajamento generico. Substitui por pergunta especifica ao tema.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "vague_majority": {
        "pattern": r"\b(A maioria das? (empresas|times|times de dados|organizações|pessoas)|"
                   r"Muitas empresas|Diversos times|Boa parte dos)\b",
        "msg": "Generalizacao sem base. Troca por contexto especifico ou dado real.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "invented_stat": {
        "pattern": r"\b(8[0-9]|9[0-9])%\b",
        "msg": "Percentual alto generico (80-99%). Usa dado real ou remove.",
        "severity": "WARNING",
        "lang_scope": "any",
    },
    "but_here_is": {
        "pattern": r"(Mas aqui está o ponto|Aqui está a questão|Aqui está o segredo|"
                   r"E aqui está o problema|O ponto é o seguinte)",
        "msg": "Padrao AI de fake-revelacao. Integra diretamente.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "vague_production": {
        "pattern": r"(Passei por isso em produção\.|Vi isso acontecer\.|"
                   r"Já enfrentei isso\.|Aconteceu comigo\.)",
        "msg": "Experiencia pessoal vaga. Especifica: onde, quando, qual sistema.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "numbered_section_list": {
        # Casa so dentro do proprio header (sem DOTALL): "## Titulo: 5 pontos"
        # ou "## 7 lições aprendidas". Antes vazava com .* greedy para o corpo.
        "pattern": r"^#{1,3} [^\n]*(: [3-9]|[3-9] (pontos|passos|lições|razões|princípios|questões|perguntas))",
        "msg": "Secao com numero redondo de itens. Estrutura AI favorita.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "meta_post": {
        "pattern": r"(Neste post[,\s]|Neste artigo[,\s]|Nesse post[,\s]|"
                   r"Nesse artigo[,\s]|Vou contar como|Vou mostrar como|"
                   r"Este post (vai|irá|cobre|explora))",
        "msg": "Meta-narrativa sobre o proprio post. Corta, o post mostra por si mesmo.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
    "question_wrong": {
        "pattern": r"(A pergunta está errada|Você está (fazendo|perguntando) errado|"
                   r"Mas a pergunta certa é)",
        "msg": "Abertura 'voce esta errado'. Comeca com o problema real.",
        "severity": "WARNING",
        "lang_scope": "pt",
    },
}


STOP_WORDS_PT = {
    "para", "como", "uma", "esse", "essa", "este", "esta", "isso", "isto",
    "sobre", "ainda", "mais", "menos", "tudo", "nada", "todo", "toda",
    "todos", "todas", "aqui", "ali", "porque", "quando", "onde", "quem",
    "qual", "quais", "muito", "muita", "pouco", "pouca", "outro", "outra",
    "depois", "antes", "agora", "hoje", "ontem", "amanha", "sempre", "nunca",
    "pode", "podem", "deve", "devem", "tem", "tinha", "estar", "ser",
    "the", "and", "for", "with", "from", "this", "that", "what", "when",
    "where", "your", "into", "have", "will", "would", "could", "should",
}


def detect_lang(path: Path) -> str:
    """Retorna 'en' se for index.en.md, senao 'pt'."""
    return "en" if path.name.endswith(".en.md") else "pt"


def strip_frontmatter(content: str) -> str:
    return re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)


def strip_code(content: str) -> str:
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`]+`", "", content)
    return content


def strip_code_keep_lines(content: str) -> str:
    """Mesmo que strip_code, mas substitui cada bloco por N linhas em branco
    para preservar numeros de linha originais quando reportamos warnings."""
    def replace_block(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    content = re.sub(r"```.*?```", replace_block, content, flags=re.DOTALL)
    content = re.sub(r"`[^`]+`", "", content)
    return content


def extract_title(content: str) -> str:
    """Pega title do frontmatter."""
    match = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", content[:500], re.MULTILINE)
    return match.group(1).strip() if match else ""


def headline_keywords(title: str) -> list:
    """Palavras com 4+ letras do titulo, fora stop words."""
    words = re.findall(r"[A-Za-zÀ-ÿ]{4,}", title.lower())
    return [w for w in words if w not in STOP_WORDS_PT]


def check_word_count(content: str) -> list:
    issues = []
    body = strip_frontmatter(content)
    body = strip_code(body)
    body = re.sub(r"#+\s+", "", body)
    body = re.sub(r"\[.*?\]\(.*?\)", "", body)

    words = len(body.split())
    if words < 500:
        issues.append(("ERROR", f"Post curto: {words} palavras. Minimo 600."))
    elif words < 600:
        issues.append(("WARNING", f"Post no limite: {words} palavras. Ideal 600-800."))
    elif words > 1200:
        issues.append(("WARNING", f"Post longo: {words} palavras. Maximo 800-1000."))
    return issues


def check_first_person(content: str, lang: str) -> list:
    body = strip_frontmatter(content)
    if lang == "pt":
        pattern = (r"\b(eu|minha|meu|meus|minhas|fiz|aprendi|vi|"
                   r"trabalhei|passei|descobri|uso|tenho)\b")
    else:
        pattern = (r"\b(I|my|mine|me|built|learned|saw|"
                   r"worked|spent|discovered|use|have)\b")
    matches = len(re.findall(pattern, body, re.I))
    # Voz e o diferencial anti-IA do blog. Dado real (jun/2026): posts
    # impessoais nao performam; os 2 posts com mais alcance sao os com
    # opiniao/identidade. Abaixo de 2 marcadores o post NAO passa.
    if matches < 2:
        return [("ERROR", f"Post sem voz: {matches} marcadores de primeira pessoa. "
                          "Minimo 2 (ideal 3+: eu, vi, fiz, aprendi, uso...).")]
    if matches < 3:
        return [("WARNING", f"Poucos marcadores de primeira pessoa ({matches}). "
                             "Ideal 3+. Post soa impessoal.")]
    return []


def check_frontmatter(content: str, lang: str) -> list:
    """PT-BR e fonte de verdade do frontmatter. EN herda publishDate/date/slug do PT via Hugo."""
    issues = []
    if lang == "pt":
        required = ["title:", "slug:", "date:", "publishDate:", "description:", "tags:"]
    else:
        required = ["title:", "description:"]
    head = content[:600]
    for field in required:
        if field not in head:
            issues.append(("ERROR", f"Frontmatter faltando ({lang}): {field}"))

    # description 50-160 chars: acima disso o Google trunca o snippet
    m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', head, re.MULTILINE)
    if m:
        desc = m.group(1).strip()
        if len(desc) > 160:
            issues.append(("WARNING", f"description com {len(desc)} chars (max 160 — "
                                      "Google trunca no SERP)."))
        elif len(desc) < 50:
            issues.append(("WARNING", f"description com {len(desc)} chars (min 50)."))
    return issues


def check_no_bullets_in_body(content: str) -> list:
    body = strip_frontmatter(content)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    bullets = re.findall(r"^[\-\*]\s+.+$", body, re.MULTILINE)
    if len(bullets) > 8:
        return [("WARNING", f"{len(bullets)} bullets no corpo. Prefere prosa fluida.")]
    return []


def check_headline_in_body(content: str) -> list:
    """Palavras-chave do titulo devem aparecer no corpo. Pelo menos 60%."""
    title = extract_title(content)
    if not title:
        return []
    keywords = headline_keywords(title)
    if not keywords:
        return []
    body = strip_frontmatter(content).lower()
    body = strip_code(body)
    hits = sum(1 for kw in keywords if kw in body)
    ratio = hits / len(keywords)
    if ratio < 0.6:
        missing = [kw for kw in keywords if kw not in body]
        return [("WARNING", f"Titulo promete {len(keywords)} palavras-chave, "
                             f"so {hits} aparecem no corpo. Faltam: {', '.join(missing[:5])}.")]
    return []


def validate_pattern_rules(content: str, lang: str) -> list:
    """Aplica regras de padrao contra o conteudo sem blocos de codigo
    (que comumente geram falsos positivos como ': 3' dentro de exemplos)."""
    issues = []
    stripped = strip_code_keep_lines(content)
    for rule_id, rule in RULES.items():
        scope = rule.get("lang_scope", "any")
        if scope != "any" and scope != lang:
            continue
        flags = re.MULTILINE | re.IGNORECASE
        if rule.get("multiline"):
            flags |= re.DOTALL
        for m in re.finditer(rule["pattern"], stripped, flags):
            line_num = stripped[:m.start()].count("\n") + 1
            snippet = stripped[m.start():m.start() + 60].replace("\n", " ")
            snippet = snippet.encode("ascii", "replace").decode("ascii")
            issues.append((rule["severity"], line_num, f"{rule['msg']} -> '{snippet}'"))
    return issues


def validate_file(path: Path) -> tuple:
    content = path.read_text(encoding="utf-8")
    lang = detect_lang(path)
    errors = 0
    warnings = 0

    print(f"\n{'=' * 60}")
    print(f"  {path.relative_to(path.parents[2]) if len(path.parents) > 2 else path.name}  [{lang}]")
    print(f"{'=' * 60}")

    all_issues = []
    all_issues.extend(validate_pattern_rules(content, lang))

    for sev, msg in (check_frontmatter(content, lang) +
                     check_word_count(content) +
                     check_first_person(content, lang) +
                     check_no_bullets_in_body(content) +
                     check_headline_in_body(content)):
        all_issues.append((sev, 0, msg))

    all_issues.sort(key=lambda x: x[1])
    for sev, line, msg in all_issues:
        prefix = "  [ERROR]  " if sev == "ERROR" else "  [WARN]   "
        loc = f"L{line:>3}" if line else "    "
        print(f"{prefix} {loc}  {msg}")
        if sev == "ERROR":
            errors += 1
        else:
            warnings += 1

    if not all_issues:
        print("  [OK] Nenhum problema encontrado.")

    score = max(0, 10 - errors * 2 - warnings)
    status = "APROVADO" if (score >= 8 and errors == 0) else "REPROVADO"
    print(f"\n  Score: {score}/10 | {errors} erros | {warnings} avisos | {status}")
    return errors, warnings, score


def check_bilingual_parity(root: Path) -> list:
    """Cada index.md deve ter index.en.md irmao."""
    issues = []
    for pt_file in root.rglob("index.md"):
        # Pula _index.md (Hugo section index)
        if pt_file.name == "_index.md":
            continue
        en_file = pt_file.with_name("index.en.md")
        if not en_file.exists():
            issues.append(("ERROR", f"Bilingual parity: {pt_file.parent.name} nao tem index.en.md"))
    return issues


def collect_targets(target: Path) -> list:
    if target.is_file():
        return [target]
    if target.is_dir():
        files = []
        for f in sorted(target.rglob("index*.md")):
            if f.name in ("_index.md", "_index.en.md"):
                continue
            files.append(f)
        return files
    return []


def main():
    parser = argparse.ArgumentParser(description="Validador de posts vazdeng-blog.")
    parser.add_argument("paths", nargs="+",
                        help="Arquivos .md ou diretorios (ex: content/blog)")
    parser.add_argument("--all", action="store_true", help="Valida todos (default em diretorio)")
    parser.add_argument("--min-score", type=int, default=8, help="Score minimo (default 8)")
    parser.add_argument("--strict", action="store_true",
                        help="Falha tambem em warnings (gate mais agressivo)")
    args = parser.parse_args()

    files = []
    parity_target = None
    for raw in args.paths:
        target = Path(raw)
        if not target.exists():
            print(f"Caminho nao encontrado: {target}")
            sys.exit(1)
        files.extend(collect_targets(target))
        if target.is_dir() and parity_target is None:
            parity_target = target

    # Dedup mantendo ordem
    seen = set()
    files = [f for f in files if not (f in seen or seen.add(f))]

    if not files:
        print("Nenhum index*.md encontrado.")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0
    failed = 0

    for f in files:
        e, w, score = validate_file(f)
        total_errors += e
        total_warnings += w
        if score < args.min_score or e > 0:
            failed += 1
        elif args.strict and w > 0:
            failed += 1

    # Validacao cross-file (so quando o alvo foi um diretorio inteiro)
    if parity_target is not None:
        parity_issues = check_bilingual_parity(parity_target)
        if parity_issues:
            print(f"\n{'=' * 60}\n  PARIDADE BILINGUE\n{'=' * 60}")
            for sev, msg in parity_issues:
                print(f"  [{sev}]  {msg}")
                if sev == "ERROR":
                    total_errors += 1
                    failed += 1

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {total_errors} erros | {total_warnings} avisos | {len(files)} arquivos")
    print(f"  Gate {args.min_score}/10: {len(files) - failed} aprovados | {failed} reprovados")
    if args.strict:
        print(f"  Modo strict ativo (warnings tambem reprovam)")
    print(f"{'=' * 60}\n")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
