# Prompts — MVP Sistema de Balizamento de Atividades e Vistorias
## IFCE Campus Caucaia — Flask + SQLite + Tailwind

Este arquivo reúne os prompts sugeridos para conduzir o desenvolvimento do MVP por etapas, com controle de escopo e boa organização.

## Como usar

- Use os prompts em sequência.
- Não envie todos de uma vez.
- Antes de cada nova etapa, confirme se a etapa anterior ficou correta.
- Mantenha este arquivo como referência para evitar que o agente desvie do escopo.
- Sempre peça arquivos completos, não apenas trechos soltos.

---

# Prompt 00 — Criar o documento mestre do projeto

Use este prompt para mandar o agente criar ou revisar o arquivo markdown principal do projeto.

```text
Crie o arquivo docs/mvp_balizamento_vistorias_flask.md como documento mestre do projeto.

O documento deve consolidar de forma clara e organizada:
- objetivo do sistema;
- stack tecnológica;
- escopo do MVP;
- perfis de usuário;
- regras de negócio;
- entidades principais;
- fluxo das telas;
- rotas sugeridas;
- estrutura de projeto esperada;
- critérios de aceite;
- ordem de implementação.

Contexto funcional do sistema:
Trata-se de um sistema web simples para apoiar a integração e o acompanhamento de terceirizados da Coordenadoria de Infraestrutura do IFCE Campus Caucaia, permitindo:
- balizar atividades iniciais de reconhecimento;
- registrar vistorias por bloco e ambiente;
- registrar ocorrências encontradas durante as inspeções;
- permitir acompanhamento pela coordenação.

Stack obrigatória:
- Flask
- SQLite
- SQLAlchemy
- Flask-Login
- Jinja2
- Tailwind CSS

Diretrizes:
- o documento deve servir como fonte de verdade do projeto;
- deve estar em português do Brasil;
- deve ser técnico, claro e objetivo;
- não incluir funcionalidades fora do escopo do MVP;
- preparar a base para possível reaproveitamento futuro no SIDAP, sem acoplamento nesta etapa.

Ao final, entregue o conteúdo completo do arquivo markdown.
```

---

# Prompt 01 — Fundação do projeto Flask

Use este prompt para gerar a base inicial da aplicação.

```text
Leia e siga rigorosamente o arquivo docs/mvp_balizamento_vistorias_flask.md como fonte de verdade do projeto.

Quero iniciar o desenvolvimento de um MVP em Flask para balizamento de atividades, vistorias de ambientes e registro de ocorrências da Coordenadoria de Infraestrutura do IFCE Campus Caucaia.

Regras obrigatórias para esta etapa:
- usar Flask;
- usar SQLite;
- usar SQLAlchemy;
- usar Flask-Login;
- usar Jinja2 com Tailwind CSS;
- organizar o projeto com boa estrutura, sem colocar tudo em um único arquivo;
- usar blueprints;
- preparar a base pensando em futura evolução, mas sem exagerar na complexidade;
- não implementar funcionalidades fora do escopo do arquivo markdown;
- não gerar integração com SIDAP nesta etapa;
- não gerar API neste momento;
- não usar Bootstrap;
- manter interface limpa e funcional.

Nesta primeira entrega, implemente somente a base inicial do projeto, com:
1. estrutura de pastas;
2. configuração inicial do app;
3. configuração do banco;
4. models iniciais:
   - Usuario
   - Colaborador
   - Bloco
   - Ambiente
   - Atividade
   - Vistoria
   - Ocorrencia
5. autenticação básica com login e logout;
6. blueprints iniciais;
7. layout base com Tailwind;
8. página de login;
9. painel inicial simples com redirecionamento por perfil.

Importante:
- gere arquivos completos;
- explique a função de cada arquivo criado;
- mostre a árvore de diretórios final;
- use nomes claros em português ou padronizados de forma consistente;
- não avance para todas as telas ainda;
- entregue apenas a fundação sólida da aplicação nesta primeira etapa.

Ao final, informe também a ordem recomendada do próximo passo de desenvolvimento.
```

---

# Prompt 02 — Cadastros base

Use este prompt depois que a fundação estiver funcionando.

```text
Com base no projeto já criado e respeitando integralmente o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora os cadastros base do sistema.

Escopo desta etapa:
- cadastro de usuários;
- cadastro de colaboradores;
- cadastro de blocos;
- cadastro de ambientes;
- cadastro de atividades.

Requisitos obrigatórios:
- manter a organização existente do projeto;
- usar blueprints e templates separados por contexto;
- usar formulários com validação adequada;
- restringir telas administrativas à coordenação/admin;
- manter layout com Tailwind, limpo e funcional;
- incluir listagem, criação e edição dos registros;
- permitir ativação/inativação quando fizer sentido;
- impedir duplicidade de nome de ambiente dentro do mesmo bloco;
- impedir username duplicado;
- não implementar exclusão destrutiva se for possível usar inativação.

Entregue nesta etapa:
1. rotas dos cadastros;
2. templates de listagem e formulário;
3. validações básicas;
4. navegação entre as telas administrativas;
5. proteção de acesso por perfil.

Importante:
- gerar arquivos completos;
- explicar o que foi criado;
- mostrar quaisquer mudanças em models, forms, routes e templates;
- manter o escopo somente nesta etapa.
```

---

# Prompt 03 — Painel do colaborador e atividades iniciais

Use este prompt para implementar o fluxo inicial do terceirizado.

```text
Com base na estrutura já existente e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o painel do colaborador e o fluxo de atividades iniciais.

Objetivo desta etapa:
- permitir que o colaborador visualize seu painel principal;
- visualizar atividades atribuídas;
- alterar status da atividade dentro do fluxo permitido;
- visualizar seu histórico básico.

Escopo desta etapa:
1. painel do colaborador;
2. tela de atividades iniciais;
3. atualização de status da atividade:
   - pendente
   - em_andamento
   - concluida
4. histórico do colaborador com:
   - atividades realizadas;
   - vistorias realizadas;
   - ocorrências registradas.

Regras obrigatórias:
- colaborador não pode validar atividade;
- coordenação/admin pode visualizar tudo;
- colaborador deve ver apenas o que lhe cabe;
- interface deve ser simples, objetiva e operacional;
- cards e indicadores devem ajudar o colaborador a entender rapidamente o que falta fazer;
- não implementar ainda o fluxo completo de vistoria nesta etapa.

Entregue:
- rotas;
- views;
- templates;
- atualização segura de status;
- proteção de acesso;
- navegação entre painel, atividades e histórico.

Gere arquivos completos e explique o que foi criado.
```

---

# Prompt 04 — Fluxo de blocos e ambientes

Use este prompt para implementar a navegação operacional da vistoria.

```text
Dando continuidade ao projeto e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o fluxo de navegação por blocos e ambientes.

Objetivo desta etapa:
- permitir que o colaborador escolha um bloco;
- visualizar os ambientes de um bloco;
- identificar o status básico de vistoria de cada ambiente.

Escopo:
1. tela de listagem de blocos;
2. tela de ambientes por bloco;
3. exibição do status do ambiente com base na última vistoria;
4. exibição da data da última vistoria;
5. exibição do responsável pela última vistoria.

Regras obrigatórias:
- blocos e ambientes devem vir do cadastro estruturado;
- ambiente não deve ser digitado manualmente neste fluxo;
- ambientes inativos não devem aparecer para novas vistorias;
- ordenar ambientes de forma útil ao colaborador;
- destacar visualmente os ambientes não vistoriados e os com pendência.

Entregue:
- rotas;
- templates;
- lógica para obter a última vistoria por ambiente;
- navegação integrada com o painel do colaborador.

Gere arquivos completos e explique a implementação.
```

---

# Prompt 05 — Registro de vistoria

Use este prompt para implementar o núcleo do sistema.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o registro de vistorias.

Objetivo desta etapa:
- permitir que o colaborador registre uma vistoria em um ambiente;
- permitir salvar vistorias sem ocorrência;
- manter o histórico das vistorias.

Escopo:
1. formulário de nova vistoria;
2. vínculo obrigatório com:
   - colaborador
   - bloco
   - ambiente
   - data/hora
3. campo situacao_geral com opções:
   - ok
   - com_pendencia
4. campo observacoes;
5. status interno da vistoria.

Regras obrigatórias:
- uma vistoria sempre deve estar vinculada a um ambiente válido;
- o bloco deve ser coerente com o ambiente escolhido;
- colaborador não deve escolher outro colaborador manualmente;
- a vistoria deve registrar o usuário logado como responsável;
- o sistema deve permitir várias vistorias para o mesmo ambiente em datas diferentes;
- não criar ocorrência automaticamente sem ação explícita do usuário.

Entregue:
- model/form se necessário;
- rotas;
- templates;
- persistência correta no banco;
- redirecionamento pós-salvamento;
- integração com a tela de ambientes.

Gere arquivos completos e explique o que foi feito.
```

---

# Prompt 06 — Registro de ocorrência vinculada à vistoria

Use este prompt para implementar o registro de problemas encontrados.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o fluxo de ocorrência vinculada à vistoria.

Objetivo desta etapa:
- permitir registrar problemas encontrados durante a vistoria;
- garantir que não exista ocorrência sem vistoria;
- preparar a coordenação para acompanhamento posterior.

Escopo:
1. formulário de nova ocorrência a partir de uma vistoria;
2. campos:
   - categoria
   - descricao
   - prioridade
   - risco
   - material_sugerido
   - observacoes
   - status inicial = registrada
3. permitir que uma vistoria tenha zero, uma ou várias ocorrências.

Regras obrigatórias:
- ocorrência só pode ser criada vinculada a uma vistoria existente;
- não permitir ocorrência solta;
- a categoria deve seguir a enum definida no markdown do projeto;
- prioridade e descrição são obrigatórias;
- status inicial deve ser automático;
- após registrar ocorrência, o fluxo deve permitir retornar ao ambiente ou ao painel.

Entregue:
- models/forms/rotas/templates necessários;
- fluxo de criação de ocorrência após vistoria;
- exibição da relação entre vistoria e ocorrência;
- integração com o histórico do colaborador.

Gere arquivos completos e explique a implementação.
```

---

# Prompt 07 — Painel da coordenação

Use este prompt para implementar a visão gerencial.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o painel da coordenação.

Objetivo desta etapa:
- dar visão geral da operação;
- permitir acompanhamento das atividades, vistorias e ocorrências;
- consolidar os registros do sistema.

Escopo:
1. painel gerencial com cards/resumos;
2. indicadores de:
   - atividades pendentes
   - blocos cadastrados
   - ambientes vistoriados
   - ambientes pendentes
   - ocorrências abertas
   - ocorrências por prioridade
3. listagem resumida de últimas vistorias;
4. listagem resumida de últimas ocorrências.

Regras obrigatórias:
- acesso restrito à coordenação/admin;
- interface limpa, funcional e objetiva;
- não exagerar em gráficos;
- priorizar leitura rápida e operacional.

Entregue:
- rotas;
- templates;
- consultas para os indicadores;
- navegação administrativa integrada.

Gere arquivos completos e explique o que foi feito.
```

---

# Prompt 08 — Lista geral e detalhe das ocorrências

Use este prompt para implementar a principal tela de análise da chefia.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora a lista geral de ocorrências e a tela de detalhe da ocorrência.

Objetivo desta etapa:
- permitir análise das pendências pela coordenação;
- permitir alteração de status e prioridade;
- consolidar o controle das ocorrências.

Escopo:
1. tela de listagem geral de ocorrências;
2. filtros por:
   - bloco
   - ambiente
   - categoria
   - prioridade
   - status
   - colaborador
   - período
3. tela de detalhe da ocorrência;
4. alteração de status da ocorrência;
5. alteração de prioridade da ocorrência;
6. campo de observação da coordenação.

Regras obrigatórias:
- apenas coordenação/admin pode alterar status e prioridade;
- histórico do vínculo com a vistoria deve ser preservado;
- status possíveis:
   - registrada
   - em_analise
   - planejada
   - executada
   - nao_procede
- a interface deve facilitar triagem e acompanhamento.

Entregue:
- rotas;
- templates;
- filtros funcionais;
- formulários ou ações de atualização;
- integração com o painel da coordenação.

Gere arquivos completos e explique a implementação.
```

---

# Prompt 09 — Validação de atividades pela chefia

Use este prompt para concluir o fluxo de atividades.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora o fluxo de validação de atividades pela coordenação.

Objetivo desta etapa:
- permitir que a chefia valide atividades concluídas pelos colaboradores;
- manter rastreabilidade da validação.

Escopo:
1. tela ou ação administrativa para visualizar atividades concluídas;
2. validação da atividade pela chefia;
3. registro de:
   - validado_por
   - validado_em
4. possibilidade controlada de reabrir atividade, se necessário.

Regras obrigatórias:
- apenas coordenação/admin pode validar;
- colaborador não pode marcar atividade como validada;
- atividade validada deve sair do fluxo operacional comum;
- manter histórico e coerência do status.

Entregue:
- rotas;
- templates ou ações administrativas;
- regras de transição de status;
- integração com painel do colaborador e painel da coordenação.

Gere arquivos completos e explique o que foi feito.
```

---

# Prompt 10 — Refinamento visual e UX operacional

Use este prompt para melhorar a aplicação sem mudar o escopo funcional.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, faça agora o refinamento visual e de experiência de uso da aplicação, sem alterar o escopo funcional já implementado.

Objetivo desta etapa:
- melhorar clareza visual;
- melhorar navegação;
- deixar a aplicação mais agradável e prática para uso diário.

Diretrizes obrigatórias:
- manter Tailwind CSS;
- não trocar a stack;
- não inventar novas funcionalidades;
- não criar componentes desnecessariamente complexos;
- foco em ergonomia operacional.

Melhorias desejadas:
- melhor hierarquia visual de títulos e cards;
- status com cores consistentes;
- botões principais bem destacados;
- tabelas/listas mais legíveis;
- formulários com melhor espaçamento;
- navegação lateral ou superior mais clara;
- layout responsivo decente;
- reforçar fluxo do colaborador com ações principais evidentes.

Entregue:
- arquivos completos alterados;
- resumo das melhorias realizadas;
- observações sobre pontos que ainda poderiam evoluir no futuro.
```

---

# Prompt 11 — Script simples de carga inicial de blocos e ambientes

Use este prompt se quiser preparar a carga inicial com base na estrutura do campus.

```text
Com base no projeto atual e respeitando o arquivo docs/mvp_balizamento_vistorias_flask.md, implemente agora uma forma simples de carga inicial de blocos e ambientes.

Objetivo desta etapa:
- permitir povoamento inicial do sistema;
- preparar o cadastro base do campus sem criar uma importação complexa demais.

Escopo:
1. criar um script simples ou comando utilitário para inserir blocos e ambientes iniciais;
2. permitir que os dados sejam mantidos em uma estrutura clara e editável;
3. evitar duplicidades na carga.

Diretrizes:
- não implementar ainda importador complexo de planilha;
- a solução pode usar JSON, lista Python estruturada ou outro formato simples;
- foco em previsibilidade e manutenção;
- manter coerência com os models do sistema.

Entregue:
- arquivo(s) do script;
- instruções de uso;
- explicação da estratégia adotada.
```

---

# Prompt 12 — Revisão técnica final do MVP

Use este prompt quando o MVP já estiver praticamente pronto.

```text
Faça uma revisão técnica do projeto atual com base no arquivo docs/mvp_balizamento_vistorias_flask.md e em tudo o que já foi implementado.

Objetivo:
- verificar aderência ao escopo do MVP;
- identificar inconsistências de modelagem, rotas, templates e fluxo;
- apontar melhorias necessárias antes de considerar o MVP estável.

Quero uma análise técnica contemplando:
1. organização do projeto;
2. models e relacionamentos;
3. regras de negócio implementadas;
4. autenticação e controle de acesso;
5. fluxo do colaborador;
6. fluxo da coordenação;
7. usabilidade geral;
8. problemas de manutenção ou acoplamento indevido;
9. itens ausentes em relação ao escopo definido;
10. sugestões objetivas de correção.

Importante:
- não reescrever tudo do zero;
- priorizar uma revisão crítica, técnica e prática;
- se sugerir ajustes, organizar por prioridade: alta, média e baixa.
```

---

# Prompt 13 — Preparar terreno para futura migração ao SIDAP

Use este prompt apenas depois do MVP validado.

```text
Com base no projeto atual já funcional, faça uma análise de como preparar este MVP para futura incorporação ao SIDAP, sem implementar a migração ainda.

Objetivo:
- identificar quais partes podem ser reaproveitadas;
- sugerir ajustes de organização para facilitar migração futura;
- evitar retrabalho.

Quero uma análise contemplando:
- models que podem ser reaproveitados;
- quais entidades provavelmente precisariam ser adaptadas ao domínio maior;
- o que deve continuar desacoplado;
- como reorganizar serviços, formulários e rotas para facilitar reaproveitamento;
- riscos de acoplamento prematuro;
- estratégia recomendada para transição futura.

Importante:
- não migrar nada agora;
- não mudar a stack neste momento;
- apenas analisar e propor encaminhamento técnico.
```

---

# Prompt coringa — Corrigir apenas uma etapa sem bagunçar o restante

Use este prompt quando o agente começar a sair do escopo.

```text
Quero que você corrija apenas a etapa solicitada, sem reestruturar todo o projeto e sem inventar funcionalidades novas.

Regras obrigatórias:
- respeitar integralmente o arquivo docs/mvp_balizamento_vistorias_flask.md;
- alterar somente os arquivos necessários para esta correção;
- preservar a organização já existente;
- não mudar nomes sem necessidade;
- não remover funcionalidades já implementadas corretamente;
- gerar arquivos completos apenas quando necessário.

Antes de alterar, explique objetivamente:
1. qual é o problema atual;
2. qual é a causa provável;
3. quais arquivos precisam ser ajustados.

Depois, aplique a correção de forma cirúrgica.
```

---

# Sequência recomendada de uso

1. Prompt 00 — documento mestre  
2. Prompt 01 — fundação do projeto  
3. Prompt 02 — cadastros base  
4. Prompt 03 — painel do colaborador e atividades  
5. Prompt 04 — blocos e ambientes  
6. Prompt 05 — vistorias  
7. Prompt 06 — ocorrências  
8. Prompt 07 — painel da coordenação  
9. Prompt 08 — lista e detalhe de ocorrências  
10. Prompt 09 — validação de atividades  
11. Prompt 10 — refinamento visual  
12. Prompt 11 — carga inicial  
13. Prompt 12 — revisão técnica final  
14. Prompt 13 — preparação para futura migração ao SIDAP

---

# Observação final

Se quiser maior controle de qualidade, após cada etapa você pode pedir ao agente algo como:

```text
Antes de avançar, revise se a etapa implementada está 100% aderente ao arquivo docs/mvp_balizamento_vistorias_flask.md. Liste divergências, se houver, e só depois proponha a continuidade.
```
