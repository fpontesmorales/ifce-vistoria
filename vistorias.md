# MVP - Sistema de Balizamento de Atividades e Vistorias
## IFCE Campus Caucaia - Coordenadoria de Infraestrutura

## 1. Objetivo

Desenvolver um sistema web simples para apoiar a integração e o acompanhamento de terceirizados do setor de infraestrutura, permitindo:

- balizar atividades iniciais de reconhecimento;
- registrar vistorias por bloco e ambiente;
- registrar ocorrências encontradas durante as inspeções;
- permitir acompanhamento pela coordenação.

O sistema será inicialmente desenvolvido em Flask, com banco SQLite, visando simplicidade, rapidez de implantação e possibilidade futura de reaproveitamento da lógica no SIDAP.

---

## 2. Stack do projeto

### Backend
- Python 3.12+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- WTForms ou Flask-WTF
- SQLite

### Frontend
- Jinja2
- Tailwind CSS

### Observações técnicas
- O projeto deve ser organizado de forma limpa e modular.
- O layout deve ser simples, responsivo e funcional.
- O foco é produtividade, clareza e facilidade de uso.
- Não usar arquitetura excessivamente complexa neste MVP.

---

## 3. Escopo do MVP

### Incluído no MVP
- autenticação simples de usuários;
- perfis de acesso: colaborador e coordenação/admin;
- cadastro de blocos;
- cadastro de ambientes;
- cadastro de atividades iniciais;
- painel do colaborador;
- painel da coordenação;
- registro de vistorias;
- registro de ocorrências;
- listagem e acompanhamento das ocorrências;
- histórico básico de registros.

### Fora do MVP
- integração com SIDAP;
- ordens de serviço completas;
- workflow avançado de manutenção;
- notificações;
- integração com WhatsApp/Telegram;
- relatórios PDF;
- upload obrigatório de fotos;
- múltiplos campi;
- API pública.

---

## 4. Perfis de usuário

### Colaborador
Pode:
- fazer login;
- visualizar painel próprio;
- visualizar atividades atribuídas;
- marcar atividades como concluídas;
- visualizar blocos e ambientes;
- registrar vistorias;
- registrar ocorrências vinculadas à vistoria;
- visualizar seu histórico.

### Coordenação / Admin
Pode:
- acessar painel gerencial;
- visualizar todos os registros;
- cadastrar e editar blocos;
- cadastrar e editar ambientes;
- cadastrar e editar atividades;
- validar atividades concluídas;
- analisar ocorrências;
- alterar status e prioridade de ocorrências;
- gerenciar usuários.

---

## 5. Regras de negócio principais

1. Toda ocorrência deve nascer a partir de uma vistoria.
2. Uma vistoria sempre pertence a um colaborador, a um bloco e a um ambiente.
3. Um ambiente pode receber várias vistorias ao longo do tempo.
4. Atividade inicial é diferente de ocorrência.
5. Blocos e ambientes devem ser escolhidos em listas estruturadas, nunca digitados livremente.
6. Ambientes inativos não devem aparecer para novas vistorias.
7. O sistema deve manter histórico de registros.
8. Coordenação pode ver tudo; colaborador vê apenas o necessário ao seu fluxo operacional.

---

## 6. Entidades do sistema

## 6.1 Usuário
Campos:
- id
- nome
- username
- senha_hash
- perfil (colaborador, coordenacao, admin)
- ativo
- criado_em

## 6.2 Colaborador
Campos:
- id
- usuario_id
- nome_exibicao
- funcao
- ativo

## 6.3 Bloco
Campos:
- id
- nome
- descricao
- ativo
- ordem

## 6.4 Ambiente
Campos:
- id
- bloco_id
- nome
- descricao
- ativo
- ordem

Regra:
- ambiente pertence obrigatoriamente a um bloco;
- não permitir duplicidade de nome no mesmo bloco.

## 6.5 Atividade
Campos:
- id
- titulo
- descricao
- tipo (integracao, reconhecimento, vistoria, apoio)
- status (pendente, em_andamento, concluida, validada)
- colaborador_id
- bloco_id (opcional)
- ambiente_id (opcional)
- criado_em
- iniciado_em
- concluido_em
- validado_em
- validado_por
- observacoes

## 6.6 Vistoria
Campos:
- id
- data_vistoria
- colaborador_id
- bloco_id
- ambiente_id
- situacao_geral (ok, com_pendencia)
- observacoes
- status (registrada, finalizada)

## 6.7 Ocorrência
Campos:
- id
- vistoria_id
- categoria (eletrica, hidraulica, civil, pintura, esquadrias, cobertura, mobiliario, limpeza_conservacao, seguranca, outros)
- descricao
- prioridade (baixa, media, alta)
- risco (baixo, medio, alto)
- material_sugerido
- status (registrada, em_analise, planejada, executada, nao_procede)
- observacoes
- criado_em
- atualizado_em

## 6.8 AnexoFoto
Opcional neste MVP, mas a estrutura pode ser preparada.
Campos:
- id
- ocorrencia_id
- arquivo
- nome_original
- criado_em

---

## 7. Fluxo das telas

### 7.1 Login
- entrada com username e senha;
- redirecionamento conforme perfil.

### 7.2 Painel do colaborador
Mostrar:
- atividades pendentes;
- blocos disponíveis para vistoria;
- últimas vistorias;
- ocorrências registradas recentemente.

### 7.3 Atividades iniciais
Lista de atividades com status:
- pendente
- em andamento
- concluída
- validada

### 7.4 Lista de blocos
Mostrar:
- nome do bloco;
- quantidade de ambientes;
- quantidade já vistoriada;
- total de pendências.

### 7.5 Lista de ambientes do bloco
Mostrar:
- nome do ambiente;
- status da última vistoria;
- data da última vistoria;
- responsável pela última vistoria.

### 7.6 Formulário de vistoria
Campos:
- situação geral;
- observações;
- opção para registrar ocorrência.

### 7.7 Formulário de ocorrência
Campos:
- categoria;
- descrição;
- prioridade;
- risco;
- material sugerido;
- observações.

### 7.8 Histórico do colaborador
Mostrar:
- atividades realizadas;
- vistorias realizadas;
- ocorrências registradas.

### 7.9 Painel da coordenação
Mostrar:
- total de atividades pendentes;
- blocos vistoriados;
- ambientes pendentes;
- ocorrências abertas;
- ocorrências por prioridade.

### 7.10 Lista geral de ocorrências
Filtros:
- bloco
- ambiente
- categoria
- prioridade
- status
- colaborador
- período

### 7.11 Detalhe da ocorrência
Permitir:
- visualizar dados completos;
- alterar prioridade;
- alterar status;
- inserir observação da coordenação.

### 7.12 Cadastros administrativos
- usuários
- colaboradores
- blocos
- ambientes
- atividades padrão

---

## 8. Rotas iniciais sugeridas

- /login
- /logout
- /painel
- /atividades
- /blocos
- /blocos/<id>/ambientes
- /vistorias/nova/<ambiente_id>
- /ocorrencias/nova/<vistoria_id>
- /historico
- /admin/painel
- /admin/ocorrencias
- /admin/ocorrencias/<id>
- /admin/usuarios
- /admin/colaboradores
- /admin/blocos
- /admin/ambientes
- /admin/atividades

---

## 9. Estrutura de projeto esperada

O projeto deve ser organizado de forma limpa, por exemplo:

- app/
  - __init__.py
  - extensions.py
  - models/
  - routes/
  - forms/
  - services/
  - templates/
  - static/
- instance/
- migrations/
- run.py

Sugestão interna:
- models separados por entidade;
- rotas separadas por contexto;
- templates separados por módulo;
- uso de blueprint.

---

## 10. Diretrizes de interface

- utilizar Tailwind CSS;
- layout limpo, objetivo e responsivo;
- foco em uso prático, não em efeitos visuais;
- navegação clara;
- botões principais bem destacados;
- formulários curtos;
- status com cores consistentes;
- painel do colaborador simples e direto;
- painel da coordenação mais analítico.

---

## 11. Carga inicial de dados

Preparar o sistema para futura importação de blocos e ambientes com base em planilha existente do campus.

Neste momento, apenas deixar o modelo pronto para:
- cadastro manual;
- carga inicial por script simples;
- separação correta entre bloco e ambiente.

Não implementar importação complexa nesta primeira etapa.

---

## 12. Critérios de aceite do MVP

O MVP será considerado funcional quando:

1. for possível cadastrar usuários e diferenciar colaborador de coordenação;
2. for possível cadastrar blocos e ambientes;
3. o colaborador conseguir fazer login;
4. o colaborador conseguir visualizar atividades;
5. o colaborador conseguir registrar vistoria em um ambiente;
6. o colaborador conseguir registrar ocorrência vinculada à vistoria;
7. a coordenação conseguir visualizar as ocorrências;
8. a coordenação conseguir alterar status de ocorrência;
9. o histórico de registros for preservado;
10. a interface estiver minimamente responsiva e utilizável.

---

## 13. Ordem de implementação

### Etapa 1
- estrutura base do projeto Flask;
- configuração do banco;
- autenticação;
- models base.

### Etapa 2
- cadastro de blocos e ambientes;
- cadastro de usuários e colaboradores;
- cadastro de atividades.

### Etapa 3
- painel do colaborador;
- fluxo de vistoria;
- fluxo de ocorrência.

### Etapa 4
- painel da coordenação;
- listagem e filtro de ocorrências;
- atualização de status.

### Etapa 5
- refinamento visual;
- validações;
- testes básicos;
- dados iniciais.

---

## 14. Regras para o agente de código

- não inventar funcionalidades fora do escopo;
- não simplificar removendo entidades importantes;
- não misturar ocorrência com vistoria;
- não usar estrutura desorganizada;
- não deixar tudo em um único arquivo;
- gerar arquivos completos;
- manter nomes claros e consistentes;
- comentar apenas quando realmente necessário;
- priorizar clareza, legibilidade e manutenção.