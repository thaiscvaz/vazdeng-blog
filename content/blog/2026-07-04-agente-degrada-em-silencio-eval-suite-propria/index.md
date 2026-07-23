---
title: "Seu agente está degradando em silêncio. Montei uma suíte de 9 evals pra provar"
slug: agente-degrada-em-silencio-eval-suite-propria
date: 2026-07-04
publishDate: 2026-07-04
draft: false
description: "Medir só o output final esconde regressão. Sem eval por passo e por papel, o agente piora sem ninguém ver. A suíte de 9 golden cases que trava isso."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 5
---
Você sobe um agente, ele funciona, você ajusta o prompt do system pra melhorar uma coisa. A resposta final continua boa. Você dá o deploy. Três semanas depois o revisor de segurança para de pegar uma chave hardcoded num diff que ele pegaria de olhos fechados no mês passado. Ninguém viu acontecer. O output final nunca pareceu errado.

Esse é o modo de falha mais caro de sistema agentic e o menos discutido. O agente não quebra de um jeito barulhento. Ele degrada em silêncio, e a única evidência aparece quando o erro já chegou no cliente.

Eu montei uma suíte de evals própria pra parar de descobrir isso tarde. Nove golden cases, três agentes, gradeamento determinístico. Calibrei contra respostas reais e ela passa 9 de 9 hoje. O valor não está no número, está no que cada caso protege.

## Por que o output final mente

> Em uma frase: avaliar um agente é auditar a trajetória inteira (cada passo de raciocínio, cada chamada de ferramenta, cada decisão intermediária), não só conferir se o último token saiu certo.

Um sistema agentic dá N passos de raciocínio e K chamadas de ferramenta até o output. Medir só o final é uma métrica pobre por três razões concretas:

- O agente acerta o output pelo motivo errado. Passa no teste, quebra no caso seguinte.
- O agente chama a ferramenta errada, recebe lixo, se recupera e ainda chega no resultado. Passou, mas custou 3x e a próxima recuperação pode não existir.
- O agente alucina uma decisão intermediária e chega no certo por sorte. É bomba-relógio com selo de aprovado.

A analogia que uso: um revisor que só lê o último commit do PR vê o resultado, não o processo. Não percebe que o dev tentou três abordagens erradas, colou um trecho duvidoso no commit 2 e só acertou no fim. Eval bom é ler o diff de cada commit. Você consegue dizer "o passo 4 foi onde quebrou, mesmo com o output final parecendo OK".

Isso não é teoria minha. O paper que cunhou o TRACE, "Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents", abre exatamente com essa crítica: a avaliação fica presa em casar a resposta final e ignora aspectos críticos da trajetória como eficiência, alucinação e adaptabilidade. O benchmark τ-bench foi atrás do mesmo buraco por outro ângulo, conversas multi-turno contra um usuário simulado, medindo se o agente sustenta a política de domínio ao longo do diálogo em vez de parecer bom só no turno 1.

## O que medir quando "passou" não basta

A literatura de eval de agente separa três métricas que parecem iguais e não são:

| Métrica | O que mede | Por que importa em produção |
|---|---|---|
| Pass@K | Acertar em pelo menos 1 de K tentativas | Bom pra batch offline onde você roda K vezes e escolhe a melhor. Mente sobre produção. |
| Pass^K | Acertar nas K tentativas seguidas | Consistência. O agente em produção precisa acertar repetido, não uma vez no laboratório. |
| Avg@K | Score médio nas K tentativas | Estabilidade. Variância alta entre tentativas é red flag. |

O τ-bench usa Pass@k e Pass^k justamente pra expor inconsistência entre seeds. Pass@1 alto com variância alta esconde fragilidade, e o cliente do agente vai cair na execução ruim, não na boa. Quando você só olha "passou uma vez", está medindo o melhor caso de um sistema que vai rodar no pior.

## A suíte por dentro: casos, agentes e gabarito determinístico

Minha suíte cobre os três agentes que carregam mais risco no meu squad de engenharia de dados. Cada um leva três casos, e a escolha dos três não é "três variações do mesmo teste". É detecção mais guarda de falso-positivo, sempre.

A regra que aprendi e que sustenta tudo: um agente que rejeita tudo também passa numa eval ingênua de detecção. Se você só testa "ele pega a vulnerabilidade?", o jeito mais fácil de passar é gritar vulnerabilidade em todo diff. Por isso cada agente tem pelo menos um caso onde o comportamento certo é aprovar ou ficar quieto.

| Agente | 3 casos | O que uma falha significa |
|---|---|---|
| `qa-security-reviewer` | secret hardcoded plantado, SQL injection plantado, diff limpo (guarda de falso-positivo) | o gate de QA parou de pegar vulnerabilidade básica, ou começou a inventar |
| `qa-critic` (modo B) | scope drift, contrato fiel (guarda de falso-positivo), verificação vaga | a camada de Reflexion parou de proteger o Sprint Contract |
| `discovery-compliance` | contexto pessoal (não pode inflar regulação), PII bancária (tem que acionar LGPD+BACEN), contexto público | o eixo de compliance regrediu na regra anti-inflação ou em obrigação bancária real |

Vou abrir um caso pra mostrar o nível de fidelidade. O `case-01-hardcoded-secret` injeta um diff de ingestão Silver com uma chave de storage e um token de API embutidos no código, mais um `verify=False` na chamada HTTPS. O gabarito não confere texto livre. Ele exige por regex que a resposta contenha: a noção de segredo hardcoded (bilíngue, porque o agente responde em PT-BR com a ordem invertida, "chave em texto plano"), a menção a cofre de segredo ou variável de ambiente como remédio, o problema do TLS desligado, e a severidade em blocker ou crítico. Quatro âncoras. Se qualquer uma falhar depois de um bump de prompt, o bump regrediu o agente.

O caso espelhado, `case-03-clean-diff`, faz o oposto. Manda um transform puro e limpo, e o gabarito tem `must_find` vazio e um `must_not_find` que proíbe a resposta de mencionar "sql injection", "hardcoded secret" ou "remote code execution". Nit de estilo é tolerável. Achado de segurança fabricado, não. É esse par que mede a calibração de verdade: detectar o que existe sem inventar o que não existe.

No `discovery-compliance` o detalhe é mais fino ainda. O caso de contexto pessoal proíbe a resposta de aplicar regulação bancária num projeto local pessoal, mas o regex foi calibrado pra permitir que o agente cite BACEN ou PCI-DSS pra marcá-los como "não se aplica". Punir a menção era um artefato de gradeamento. O padrão proibido casa o verbo de aplicação ("sujeito a", "obrigatório", "exige"), não o nome da norma. Já o caso de PII bancária exige o inverso: LGPD, BACEN, a noção de dado pessoal/CPF, tudo em risco alto. O mesmo agente tem que saber a diferença entre os dois contextos. Isso é o que nenhuma métrica de output final captura.

## Determinístico de propósito, e por que aguento o teto baixo

O gradeamento é regex puro. Todos os `must_find` casam, nenhum `must_not_find` casa, case-insensitive, sobre a resposta do agente.

| | Determinístico (o que uso) | LLM-as-judge |
|---|---|---|
| Custo | Zero, roda em segundos | Token por avaliação |
| Reprodutibilidade | 100% | Não reprodutível |
| Cobertura | Só o que você antecipou | Nuance semântica, formato livre |
| Risco próprio | Falha em output válido com formato inesperado | Viés do próprio juiz |

Eu não uso LLM-as-judge aqui de propósito, e não é preguiça. O viés do juiz é documentado e grande. A literatura mede position bias chegando a 75% de preferência pela primeira resposta posicionada, e self-preference bias de 10 a 25% quando o juiz avalia conteúdo do próprio modelo. Um estudo da RAND em 2026 achou que nenhum juiz é uniformemente confiável entre benchmarks. Trazer um juiz desses pra dentro da minha esteira sem âncora determinística seria trocar um problema de medição por um pior. A disciplina que sigo: determinístico onde dá, LLM-as-judge só entra quando o regex provar ser insuficiente numa regressão real. Evidência primeiro, não hipótese.

O custo desse rigor é honesto: o regex cobre "perdeu a vulnerabilidade plantada" e "inflou regulação num projeto pessoal". Ele não mede qualidade sutil de raciocínio. Eu aceito esse teto porque a classe de erro que mais me machuca é a grosseira e silenciosa, não a sutil.

Um detalhe operacional que economiza dinheiro: o run completo custa nove chamadas de LLM e não fica no CI. O que fica no CI é o `--dry-run`, que valida a estrutura dos casos sem gastar token. A regra de processo é manual e explícita: todo PR que muda o `prompt_version` de um agente coberto tem que colar o output do run completo na descrição. O CI garante a estrutura, o operador garante a verificação semântica no momento certo, que é o bump de prompt.

## Anti-padrões que eu já vi de perto

- Eval só do output final. Você está medindo o melhor caso de um sistema que roda no pior. Pass@1 alto com variância alta é fragilidade disfarçada de qualidade.
- Suíte só de detecção, sem guarda de falso-positivo. Um agente paranoico que rejeita tudo passa nesses testes e é inútil. Sempre pareie detecção com um caso onde o certo é aprovar.
- LLM-as-judge como primeira escolha. Você herda position bias e self-preference bias antes de ter qualquer âncora determinística. Comece pelo regex, suba pro juiz só com evidência de que o regex não dá conta.
- Golden dataset sintético gigante. Cinquenta a duzentos casos curados à mão, cobrindo tipo de erro real visto em produção, valem mais que dez mil casos gerados que cobrem estrutura abstrata.
- Regex frágil que quebra em silêncio. No meu caso, camadas de escape entre YAML e o `re` do Python mataram um padrão sem avisar. Calibre cada regex contra uma resposta real antes de confiar nele, senão o seu eval degrada junto com o agente.

## Checklist pra montar a sua antes do próximo bump de prompt

Se você roda agente em produção e nunca mediu trajetória, comece por aqui:

- [ ] Listei os 2 ou 3 agentes que carregam mais risco se regredirem? (Não tente cobrir todos.)
- [ ] Cada um tem pelo menos um caso de detecção com vulnerabilidade ou erro plantado de propósito?
- [ ] Cada um tem pelo menos um caso de guarda de falso-positivo, onde o certo é aprovar ou silenciar?
- [ ] O gradeamento é determinístico onde dá, sem LLM-as-judge antes da hora?
- [ ] Cada regex foi calibrado contra uma resposta real, não escrito de cabeça?
- [ ] O run completo está amarrado ao gatilho certo (bump de `prompt_version`), e não rodando à toa no CI gastando token?
- [ ] O golden dataset está versionado junto do código do agente?

Quando um caso do golden começar a falhar, a pergunta não é "como faço passar". É "o golden está desatualizado ou o agente regrediu?". Responder isso conscientemente, caso a caso, é a diferença entre uma suíte de eval e um teatro de eval.
