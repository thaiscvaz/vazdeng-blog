---
title: "Zero to Expert Ep 04: Particionar errado custa mais caro que não particionar"
slug: particionar-errado-custa-mais-que-nao-particionar-zte-ep04
date: 2026-07-04
publishDate: 2026-07-04
draft: false
description: "Quase todo mundo aprende \"particiona pra ficar rápido\". O que ninguém conta é que granularidade errada deixa o pipeline mais lento, mais caro e mais frágil do que se você não tivesse particionado nada."
tags: ["zero-to-expert", "engenharia-de-dados"]
images:
  - cover.png
---
A primeira vez que eu vi uma tabela "particionada por CPF" eu achei que era genial. Filtro por cliente é o padrão de query mais comum do mundo bancário, então particionar por aquilo que mais aparece no `WHERE` parecia óbvio. Estava errado, e o erro custou caro.

A tabela tinha milhões de partições, cada uma com alguns kilobytes. Uma query que deveria ler poucos arquivos passava a maior parte do tempo só listando diretórios e abrindo metadados. O job ficou mais lento do que a versão sem partição nenhuma, e a conta do cluster subiu junto. Esse é o ponto deste episódio: particionamento não é um botão de "deixar rápido". É uma decisão de layout físico que, quando feita na granularidade errada, te cobra mais do que o problema que ela deveria resolver.

Nos episódios anteriores a gente subiu degrau por degrau. Ep01 olhou os fluxos de dados, Ep02 organizou a ordem das tarefas no DAG, Ep03 garantiu que rodar de novo não estraga nada (idempotência). Hoje a pergunta é mais física: onde os bytes ficam no disco, e por que isso decide o custo do seu pipeline.

## O que particionar significa, de verdade

> Em uma frase: particionar é dividir uma tabela em pastas separadas no armazenamento, uma por valor de uma coluna, pra que uma query consiga pular as pastas que não interessam.

Se você tem uma tabela de transações e particiona por `data`, no disco isso vira literalmente uma pasta por dia: `data=2026-07-01/`, `data=2026-07-02/`, e assim por diante. Quando você roda `WHERE data = '2026-07-01'`, o mecanismo lê só aquela pasta e ignora todas as outras. Isso se chama **partition pruning**, e é o motor que faz particionamento valer a pena: o filtro vira "não preciso nem abrir esses arquivos".

A analogia que eu uso pra mim mesma é o arquivo de pastas suspensas. Se você separa as contas por mês, achar a conta de julho é abrir uma gaveta. Mas se você resolve separar por número de protocolo, cada conta vira uma pasta própria, e a gaveta vira mil pastinhas com uma folha cada. Achar qualquer coisa agora exige folhear o arquivo inteiro. O critério de separação é tudo. Separar é grátis na teoria e caro na prática quando você separa pela coisa errada.

A peça que falta na cabeça de quem está começando é que o ganho do pruning só aparece se duas coisas forem verdade ao mesmo tempo: suas queries filtram por aquela coluna **e** cada partição é grande o bastante pra que pular as outras compense o custo de gerenciar tantas pastas.

## Por que particionar errado é pior que não particionar

Existem dois jeitos clássicos de errar, e os dois geram o mesmo sintoma: **o small files problem**, o problema dos arquivos pequenos.

Coluna de cardinalidade alta (CPF, ID de transação, e-mail) gera uma explosão de partições minúsculas. Spark e Delta guardam estatística por arquivo (mínimo, máximo, contagem). Com milhares de arquivos de poucos KB, o motor gasta mais tempo listando diretórios, abrindo footers e montando metadados do que efetivamente lendo dado. Pior: quando a lista de chaves de partição fica gigante, o próprio Spark pode **desligar** otimizações como o dynamic partition pruning pra não estourar o overhead. Você particionou pra ganhar pruning e o pruning desligou sozinho.

Coluna de cardinalidade muito baixa (um `status` com 3 valores, por exemplo) erra pro outro lado: poucas partições gigantes e desbalanceadas. Uma partição concentra 90% dos dados e vira gargalo, enquanto particionar não te deu seletividade nenhuma.

A doc oficial do Databricks é direta nos limiares, e vale tatuar:

- Não particione tabelas com menos de 1 TB de dados.
- Cada partição deve conter pelo menos 1 GB de dados.
- Particionamento funciona mal pra colunas de alta cardinalidade (timestamps, IDs de cliente).

O número que importa aqui é o segundo. Se a sua coluna de partição não consegue garantir 1 GB por partição na maioria dos valores, ela é a coluna errada. E o tamanho-alvo de arquivo padrão do `OPTIMIZE` no Delta é 1 GB, justamente porque é o ponto que equilibra bem leitura e overhead na maioria dos instance types. Sua granularidade de partição precisa conversar com essa escala, não brigar com ela.

## Quando particionar e quando não

| Situação | Decisão | Por quê |
|---|---|---|
| Tabela < 1 TB | Não particione | Pruning não compensa o overhead; otimizações built-in já resolvem |
| Tabela TB+, query sempre filtra por data | Particione por data (`business_date`) | Cardinalidade média, partições gordas, pruning real |
| Coluna de alta cardinalidade (CPF, ID) | Nunca particione | Small files problem garantido |
| Coluna de baixíssima cardinalidade (status) | Não particione por ela | Partições desbalanceadas, sem seletividade |
| Query pattern variado ou em dúvida | Liquid Clustering | Lida com alta cardinalidade e múltiplas colunas sem reescrever |

A linha mais importante é a primeira, e é a mais ignorada. A maioria das tabelas com menos de 1 TB simplesmente não precisa de partição, e no Databricks Runtime 11.3+ as tabelas não particionadas já ganham **ingestion time clustering** de graça: o dado fica agrupado por tempo de ingestão, dando um benefício parecido com particionar por data sem você tunar nada. Eu já gastei tempo desenhando esquema de partição pra tabela que cabia inteira na memória de uma máquina. Não particione por reflexo. Particione por evidência.

## Liquid Clustering: a saída pra quando "depende"

Quando a sua dúvida é honesta (o query pattern é variado, a cardinalidade é alta, você filtra ora por uma coluna ora por outra), a resposta moderna não é forçar uma partição. É **Liquid Clustering**.

Em vez de `PARTITIONED BY`, você usa `CLUSTER BY`. A diferença prática que muda o jogo: você consegue **redefinir as chaves de clustering sem reescrever os dados existentes**, coisa impossível com partição (mudou o esquema de partição, reescreve a tabela inteira). Ele também lida bem com alta cardinalidade e com mais de uma coluna, justamente os dois cenários onde particionamento te trai.

O Databricks hoje recomenda Liquid Clustering como default pra toda tabela Delta nova. Não é um detalhe de versão recente: é uma mudança de qual deveria ser sua primeira escolha. Particionamento clássico continua válido pra um nicho (tabela enorme, com um padrão de filtro estável e bem conhecido por data), mas deixou de ser o ponto de partida.

Opinião explícita: se você está começando uma tabela hoje no Delta e não tem uma razão muito específica e documentada pra particionar, comece com Liquid Clustering. Particionar virou a exceção que precisa se justificar, não o default que se assume.

## Um caso concreto, com números

Imagine uma Silver de transações, 2 TB, consultada quase sempre por intervalo de datas.

Cenário ruim, particionada por `transaction_id`: cardinalidade na casa dos milhões, cada partição com poucos KB, milhares de arquivos minúsculos. A query por data não tem por onde podar (o filtro não bate na coluna de partição), então varre tudo, e ainda paga o pedágio de listar uma montanha de diretórios. Lento e caro.

Cenário bom, particionada por `business_date`: 365 partições por ano, cada uma na casa dos GB. `WHERE business_date BETWEEN ...` poda direto pro intervalo, lê só as pastas certas. Esse é o pruning fazendo o trabalho dele.

O contraste não é "com partição vs sem partição". É a mesma tabela, com a mesma engine, separada por dois critérios diferentes. Um deles devolve dinheiro, o outro queima.

## Anti-padrões

- **Particionar por reflexo.** "É grande, então particiona." Tabela < 1 TB quase nunca precisa, e o overhead de partição pode deixá-la mais lenta.
- **Particionar por coluna de alta cardinalidade** (CPF, ID, e-mail, timestamp ao segundo). Small files problem garantido, e o pruning pode até se desligar sozinho.
- **Mais de 10 mil partições numa tabela só.** Sinal de granularidade errada. Refatore o critério ou migre pra clustering.
- **Particionar por coluna que as queries não filtram.** Você paga o custo de gerenciar pastas e não ganha pruning nenhum.
- **Ignorar o piso de 1 GB por partição.** Se a coluna não garante isso, é a coluna errada.
- **Forçar partição onde "depende".** Quando a dúvida é real, a resposta é Liquid Clustering, não escolher uma coluna no chute.

## Checklist antes de digitar `PARTITIONED BY`

1. A tabela tem 1 TB ou mais? Se não, provavelmente não particione.
2. Minhas queries filtram por essa coluna na maioria das vezes?
3. Cada partição vai ter pelo menos 1 GB de dados?
4. A cardinalidade é média (dezenas a centenas de valores), não milhões?
5. Se respondi "não sei" pra alguma das anteriores, eu deveria estar olhando Liquid Clustering.

Particionamento é uma das pouquíssimas decisões de engenharia de dados onde fazer a coisa certa e não fazer nada são, muitas vezes, a mesma resposta. A pergunta certa nunca foi "como eu particiono isso?". É "isso precisa ser particionado?". Qual foi a última tabela que você particionou só porque parecia óbvio?

---

*Próximo degrau da série Zero to Expert: file formats e por que Parquet ganhou. Conceito antes de ferramenta, sempre.*
