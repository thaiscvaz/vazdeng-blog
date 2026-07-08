---
title: "O produtor renomeou uma coluna e ninguém avisou: por que pipeline sem contrato de dados quebra no escuro"
slug: contrato-de-dados-schema-quebra-silencioso
date: 2026-06-23
publishDate: 2026-06-23
draft: false
description: "Tem um tipo de incidente que eu aprendi a temer mais do que pipeline caindo: pipeline que NÃO cai. Job verde, alerta silencioso, dashboard atualizado. E os n..."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
Tem um tipo de incidente que eu aprendi a temer mais do que pipeline caindo: pipeline que NÃO cai. Job verde, alerta silencioso, dashboard atualizado. E os números errados há três semanas.

O roteiro é sempre o mesmo. Um time produtor decide melhorar a modelagem. A coluna `cpf` vira `documento` (faz sentido, agora aceita CNPJ também). Ou a coluna `valor` deixa de ser bruto e passa a ser líquido, já descontada a taxa do meio de pagamento. Mudança defensável, feita por gente competente. O problema não é a mudança. O problema é que ninguém do outro lado da fronteira ficou sabendo.

Eu vi esse padrão se repetir em domínio de pagamentos, em marketing, em analytics. A causa raiz é sempre a mesma decisão arquitetural implícita: a fronteira entre produtor e consumidor é "o que está na tabela hoje". Não existe acordo. Existe torcida.

## O que dá errado: quebra ruidosa é sorte, quebra silenciosa é prejuízo

Renomear `cpf` para `documento` tem um lado bom escondido: o consumidor quebra ALTO. O `SELECT cpf` estoura, o job fica vermelho, alguém é acordado. Doloroso, mas honesto.

O caso de `valor` bruto virando líquido é o pesadelo de verdade. O tipo continua `DECIMAL(18,2)`, o nome continua `valor`, o schema "passa". Nada quebra. O pipeline soma alegremente números que agora significam outra coisa. Em pagamentos isso vira reconciliação errada. Em analytics vira decisão de produto tomada em cima de receita fantasma. Você só descobre quando alguém compara com a fonte oficial, e aí já são semanas de dado contaminado.

A lição que eu carrego: schema igual não é semântica igual. Validar tipo e nullability pega o caso ruidoso e deixa passar o caso caro.

![Comparação entre quebra ruidosa (renomear cpf para documento faz o job estourar na hora, detectável) e quebra silenciosa (valor bruto vira líquido, o schema passa e o dado fica contaminado por três semanas). Schema igual não é semântica igual.](images/01-duas-quebras.png)

## A decisão: contrato versionado com SemVer, não DDL em Confluence

A correção não é mais Slack ("avisa antes de mudar"). Aviso humano é a coisa que falha sob pressão de deadline. A correção é transformar a fronteira num artefato versionado, validado em CI. É isso que a literatura chama de data contract: Andrew Jones, primeiro engenheiro de dados da GoCardless (fintech), escreveu o manual disso em "Driving Data Quality with Data Contracts", e Chad Sanderson popularizou a prática a partir da operação dele.

O que eu defendo como mínimo viável de um contrato:

- **schema** com tipos, nulls e descrição de cada coluna
- **semantics**: o que `valor` significa em domínio (BRL? líquido ou bruto? inclui taxa?). É exatamente o campo que teria evitado o pesadelo acima
- **owner**: time e pessoa, não "a tabela"
- **freshness e completeness**: latência e faixa de volume esperada (por exemplo, da ordem de 1 a 5 milhões de linhas/dia, valor ilustrativo, com alarme fora da faixa)
- **legal_basis** por coluna: a base legal LGPD daquele dado (`cpf` é PII, precisa de Art. 7º amarrado), mais retenção (em fintech, prazos de guarda BACEN que podem chegar a anos)
- **version** em SemVer, com política de breaking change

O SemVer aplicado a schema é o coração da coisa. PATCH adiciona coluna nullable, ninguém quebra. MINOR refina granularidade de forma compatível. MAJOR é o que dói: remover coluna, renomear coluna pública, mudar tipo, ou mudar a semântica de `valor`. MAJOR não é um commit, é um processo: aviso prévio (na ordem de 60 dias, exemplo, não regra universal), dual-write das duas versões em paralelo, e deprecação anunciada. O validador roda no PR do produtor e barra o merge se o changelog não justificar a mudança de versão. A fronteira deixa de ser confiança e vira CI.

![SemVer aplicado a schema: PATCH adiciona coluna nullable sem quebrar ninguém, MINOR refina de forma retrocompatível, MAJOR remove ou renomeia coluna ou muda a semântica e exige processo com aviso prévio, dual-write e deprecação. MAJOR não é um commit, é um processo.](images/02-semver-schema.png)

## Quando NÃO precisa: contrato é fronteira de confiança, não burocracia universal

Não saia contratualizando tudo. Contrato formal tem custo de manutenção, e contrato que ninguém mantém vira ficção pior que a ausência dele.

Eu não escrevo contrato formal quando o mesmo time é dono do produtor E do consumidor, o dado tem baixa criticidade, e a mudança é refatoração interna no mesmo PR. Aí o "contrato" é o code review e o teste de integração, e está ótimo. O sinal pra formalizar é a fronteira organizacional: o momento em que quem muda o schema não é a mesma pessoa que sente a quebra. É aí que o aviso humano falha e o artefato versionado paga.

## Conclusão

Pipeline sem contrato não é mais simples. É um pipeline com um contrato implícito, não escrito, que ninguém pode validar e todo mundo pode quebrar sem saber. O ODCS (Open Data Contract Standard, hoje v3.1.0 sob a Linux Foundation no projeto Bitol) existe justamente pra você não inventar o formato do zero. Versionar a fronteira é mais barato que reconciliar três semanas de receita líquida somada como se fosse bruta. Eu já paguei a conta do jeito errado. Recomendo o outro.
