---
title: "I Audited My Own Airflow DAG. Five Things I'd Rewrite Today."
slug: i-audited-my-own-airflow-dag
date: 2026-06-02
publishDate: 2026-06-02
draft: false
description: "I opened a two-year-old repo of mine. Found hardcoded credentials, lost parallelism, data baked into the image. Honest review of my own code."
tags: ["airflow", "anti-patterns", "data-engineering", "production"]
images:
  - cover.png
---

I opened a two-year-old repo of mine. It was an interview take-home: migrate JSON student data into Snowflake using Airflow on Docker. It worked. I passed the process. The repo stayed public on GitHub.

Today, reading the DAG again, I noticed it carried five anti-patterns that I see show up in real production pipelines at large companies. I didn't invent them. They were sitting there, in my own code, written by me.

I decided to write about it because it's more honest to critique my own code than to point fingers at someone else's repo. And because the same five patterns show up in pipelines processing real production volume, not just in interview projects.

## The Snowflake credentials were inside the function

```python
def load_data_to_snowflake(df_merged):
    conn = snowflake.connector.connect(
        user='thaiscxxx',
        password='xxx*',
        account='xxx'
    )
```

I masked it with `xxx` before pushing, but the design pattern is the problem, not the string. Credentials inside the function mean each DAG that talks to Snowflake duplicates the connection, rotating the password requires touching code, and auditing means grepping the entire repo to figure out who connects where.

Airflow has had `SnowflakeHook` and Snowflake Connection forever. The connection lives in the metadata DB, encrypted, managed by the UI. Each task asks for the connection by ID:

```python
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
```

That's how I'd write it today.

## The DAG lost parallelism for free

```python
t1 >> t2 >> t3 >> t4
```

`t1` validated `students.json`. `t2` validated `missed_days.json`. I chained them sequentially, but they're independent. No reason for `t2` to wait on `t1`. With a tiny file, it barely matters. When the JSON weighs gigabytes and validation takes minutes, parallelizing each validation cuts the duration in half.

The correct version:

```python
[t1, t2] >> t3 >> t4
```

Whoever reads the DAG now understands validation runs in parallel and then joins. Whoever read the original would assume there's some hidden dependency that doesn't exist.

## Input data was baked into the Docker image

In the Dockerfile:

```
COPY files/students.json /students.json
COPY files/missed_days.json /missed_days.json
```

I embedded the input data into the image. Every rebuild assumes the same data. To run the pipeline with a different JSON, I'd have to rebuild the image or change the code. Coupling between execution artifact and input data, in the same place.

The rule I'd preach to others but ignored in my own repo: images are immutable, data is mutable. Data comes in through a mounted volume, S3, GCS, or DAG run parameter. Never inside the image.

## I used the deprecated import path

```python
from airflow.operators.python_operator import PythonOperator
```

That path has been deprecated since Airflow 2.0. The current path is `airflow.operators.python`. The scheduler still accepts it for backward compatibility, but at some point it stops. In Airflow 3, that import breaks. I could test locally without noticing and discover it during the upgrade.

The rewrite isn't just changing the import. It's using TaskFlow API with `@task`:

```python
from airflow.decorators import dag, task

@task
def validate_students(): ...

@task
def join_datasets(students, missed): ...
```

Less boilerplate, automatic XCom, dependency declared implicitly by the function call.

## The `fillna(0)` erased an important signal

```python
df_merged['missed_days'].fillna(0, inplace=True)
```

When a student appears in `students.json` but not in `missed_days.json`, the join leaves `missed_days` null. I replaced it with zero. It seemed right at the time.

Zero absences carries business meaning: the student showed up every day. A missing record carries another meaning: the school didn't report this student's attendance. Conflating the two masks an upstream data quality issue. A dashboard filtering "students with zero absences" will surface as model students precisely the kids whose data never arrived.

The honest version leaves null and opens a new column marking whether the record exists:

```python
df_merged['missed_data_source'] = df_merged['missed_days'].notna().map(
    {True: 'reported', False: 'not_reported'}
)
```

Small change, completely changes what the dashboard shows.

## The discomfort of reviewing your own code

Rewriting these five snippets today would take an hour. The discomfort of publicly admitting they were wrong is bigger than the hour. But the repo stayed public with the defects, and I cite that repo in my portfolio. Keeping the repo intact and doing an honest review on top is more useful for someone learning than deleting the history and pretending I always wrote clean code.

If you have an old public Airflow repo, open it this week. You'll find at least three of these five.
