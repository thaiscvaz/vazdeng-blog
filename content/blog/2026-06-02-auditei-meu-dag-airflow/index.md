---
title: "Auditei meu próprio DAG de Airflow. Cinco coisas que eu reescreveria hoje."
slug: auditei-meu-dag-airflow
date: 2026-06-02
publishDate: 2026-06-02
draft: false
description: "Abri um repo meu de dois anos atrás. Achei credencial hardcoded, paralelismo perdido, dado dentro da imagem. Review honesto do meu próprio código."
tags: ["airflow", "anti-patterns", "data-engineering", "de-producao"]
images:
  - cover.png
---

Abri um repositório meu de dois anos atrás. Era um case técnico de entrevista: migrar JSON de notas escolares pra Snowflake usando Airflow em Docker. Funcionava. Passei no processo. E o repo continuou público no GitHub.

Hoje, relendo o DAG, percebi que ele acumulava cinco anti-padrões que eu vejo aparecer em pipelines reais de empresa grande. Não inventei. Estava lá, no meu próprio código, escrito por mim.

Resolvi escrever sobre porque é mais honesto criticar o próprio código do que apontar dedo pra repo dos outros. E porque os mesmos cinco padrões aparecem em pipelines que processam volume real, não só em case de entrevista.

## A credencial do Snowflake estava dentro da função

```python
def load_data_to_snowflake(df_merged):
    conn = snowflake.connector.connect(
        user='thaiscxxx',
        password='xxx*',
        account='xxx'
    )
```

Mascarei com `xxx` antes de subir, mas o padrão de design é o problema, não a string. Credencial dentro da função significa que cada DAG que precisa do Snowflake duplica essa conexão, rotacionar a senha exige tocar em código, e auditoria precisa varrer o repo inteiro pra saber quem se conecta no banco.

O Airflow tem `SnowflakeHook` e `Snowflake Connection` desde sempre. A conexão fica no metadata DB, criptografada, gerenciada pela UI. Cada task pede a conexão pelo ID:

```python
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
```

Reescreveria assim hoje.

## O DAG perdia paralelismo de graça

```python
t1 >> t2 >> t3 >> t4
```

`t1` validava `students.json`. `t2` validava `missed_days.json`. Eu encadeei os dois em sequência, mas eles são independentes. Não existe motivo pra `t2` esperar `t1` terminar. Em um arquivo pequeno, dá quase no mesmo. Quando o JSON pesa gigabytes e a validação leva minutos, paralelizar cada validação cai a duração pela metade.

A versão correta seria:

```python
[t1, t2] >> t3 >> t4
```

Quem leu o DAG hoje entende que validação roda em paralelo e depois faz o join. Quem leu o original ia assumir que existe alguma dependência escondida que não existe.

## Os dados estavam dentro da imagem Docker

No Dockerfile:

```
COPY files/students.json /students.json
COPY files/missed_days.json /missed_days.json
```

Embuti o dado de entrada na imagem. Cada rebuild da imagem assume o mesmo dado. Pra rodar o pipeline com um JSON diferente, eu teria que rebuildar a imagem ou modificar o código. Acoplamento entre artefato de execução e dado de entrada, no mesmo lugar.

A regra que eu cobrava de outros e ignorei no meu próprio repo: imagem é imutável, dado é mutável. Dado entra via volume montado, S3, GCS, ou parâmetro de DAG run. Nunca dentro da imagem.

## Usei o caminho de import deprecated

```python
from airflow.operators.python_operator import PythonOperator
```

Esse caminho está deprecated desde a versão 2.0 do Airflow. O caminho atual é `airflow.operators.python`. O scheduler ainda aceita por compatibilidade, mas em algum momento para. No Airflow 3, esse import quebra. Posso testar localmente sem perceber e descobrir no upgrade.

A reescrita não seria só trocar o import. Seria usar TaskFlow API com `@task`:

```python
from airflow.decorators import dag, task

@task
def validate_students(): ...

@task
def join_datasets(students, missed): ...
```

Menos boilerplate, XCom automático, dependência declarada implicitamente pela chamada da função.

## O `fillna(0)` apagou um sinal importante

```python
df_merged['missed_days'].fillna(0, inplace=True)
```

Quando um aluno aparece em `students.json` mas não em `missed_days.json`, o join deixa `missed_days` nulo. Substituí por zero. Parecia certo na hora.

Zero falta tem significado de negócio: aluno foi todos os dias. Ausência de registro tem outro significado: a escola não passou o dado desse aluno. Misturar os dois mascara um problema de qualidade de dado upstream. O dashboard que filtra alunos com "zero faltas" vai contar como exemplares justamente os alunos cujo dado nunca chegou.

A versão honesta deixaria nulo e abriria coluna nova marcando se houve registro:

```python
df_merged['missed_data_source'] = df_merged['missed_days'].notna().map(
    {True: 'reported', False: 'not_reported'}
)
```

Pequena mudança, completamente diferente o que o dashboard mostra.

## O incômodo de revisar código próprio

Reescrever esses cinco trechos hoje levaria uma hora. O incômodo de admitir publicamente que estavam errados é maior do que a hora. Mas o repo continuou público com os defeitos, e eu cito esse repo no meu portfólio. Manter o repo intacto e fazer review honesto em cima é mais útil pra quem está aprendendo do que apagar a história e fingir que sempre escrevi código bom.

Se você tem um repo público antigo de Airflow, abre ele essa semana. Vai achar pelo menos três desses cinco.
