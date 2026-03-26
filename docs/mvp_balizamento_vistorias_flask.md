# Documento Mestre — MVP Sistema de Balizamento de Atividades e Vistorias
## IFCE Campus Caucaia — Coordenadoria de Infraestrutura

> **Fonte de verdade do projeto.** Este documento deve ser consultado antes de qualquer decisão de implementação.
> Última revisão: 2026-03-24

---

## 1. Objetivo

Desenvolver um sistema web simples para apoiar a integração e o acompanhamento de terceirizados da Coordenadoria de Infraestrutura do IFCE Campus Caucaia, permitindo:

- balizar atividades iniciais de reconhecimento do campus;
- registrar vistorias por bloco e ambiente;
- registrar ocorrências encontradas durante as inspeções;
- permitir acompanhamento e análise pela coordenação.

O sistema será desenvolvido em Flask com banco SQLite, priorizando simplicidade, rapidez de implantação e possibilidade futura de reaproveitamento da lógica de negócio no SIDAP, sem acoplamento nesta etapa.

---

## 2. Stack Tecnológica

### Backend
| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12+ |
| Framework web | Flask |
| ORM | Flask-SQLAlchemy |
| Autenticação | Flask-Login |
| Formulários | Flask-WTF / WTForms |
| Banco de dados | SQLite |

### Frontend
| Componente | Tecnologia |
|---|---|
| Template engine | Jinja2 |
| CSS framework | Tailwind CSS |

### Diretrizes técnicas gerais
- Projeto organizado de forma modular, com uso de Blueprints.
- Layout simples, responsivo e funcional — sem efeitos visuais desnecessários.
- Sem Bootstrap, sem frameworks JS pesados.
- Foco em produtividade, clareza e facilidade de uso.
- Não usar arquitetura excessivamente complexa neste MVP.

---

## 3. Escopo do MVP

### Incluído

- Autenticação de usuários com login/logout.
- Perfis de acesso: `colaborador` e `coordenacao`/`admin`.
- Cadastro de blocos e ambientes.
- Cadastro de atividades iniciais e atribuição a colaboradores.
- Painel operacional do colaborador.
- Painel gerencial da coordenação.
- Registro de vistorias por bloco e ambiente.
- Registro de ocorrências vinculadas às vistorias.
- Listagem e acompanhamento de ocorrências com filtros.
- Validação de atividades pela coordenação.
- Histórico básico de registros por colaborador.

### Fora do escopo do MVP

- Integração com o SIDAP.
- Ordens de serviço completas.
- Workflow avançado de manutenção.
- Notificações (e-mail, WhatsApp, Telegram).
- Relatórios em PDF.
- Upload obrigatório de fotos.
- Múltiplos campi.
- API pública REST.
- Importação automática de planilhas.

---

## 4. Perfis de Usuário

### Colaborador (terceirizado)
Pode:
- fazer login e acessar o painel próprio;
- visualizar atividades iniciais atribuídas;
- atualizar status das suas atividades (`pendente` → `em_andamento` → `concluida`);
- visualizar blocos e ambientes disponíveis;
- registrar vistorias em ambientes;
- registrar ocorrências vinculadas às vistorias;
- visualizar seu próprio histórico de atividades, vistorias e ocorrências.

Não pode:
- validar atividades;
- acessar registros de outros colaboradores;
- alterar status ou prioridade de ocorrências;
- acessar painéis e cadastros administrativos.

### Coordenação / Admin
Pode (tudo do colaborador, mais):
- acessar painel gerencial com indicadores consolidados;
- cadastrar e editar blocos, ambientes, atividades e usuários;
- visualizar todos os registros do sistema;
- validar atividades concluídas pelos colaboradores;
- alterar status e prioridade de ocorrências;
- inserir observações da coordenação nas ocorrências;
- gerenciar colaboradores e usuários.

---

## 5. Regras de Negócio

1. Toda ocorrência deve nascer a partir de uma vistoria — não existe ocorrência avulsa.
2. Uma vistoria sempre pertence a um colaborador, a um bloco e a um ambiente.
3. Um ambiente pode receber várias vistorias ao longo do tempo.
4. Atividade inicial é uma entidade distinta de ocorrência — não misturar.
5. Blocos e ambientes devem ser selecionados em listas estruturadas; nunca digitados livremente pelo usuário.
6. Ambientes inativos não devem aparecer para novas vistorias.
7. O colaborador logado é automaticamente o responsável pela vistoria — sem escolha manual de responsável.
8. O status da atividade segue o fluxo: `pendente` → `em_andamento` → `concluida` → `validada`.
9. Apenas a coordenação/admin pode marcar uma atividade como `validada`.
10. O sistema deve preservar o histórico completo de registros — sem exclusão destrutiva quando possível.
11. Coordenação vê todos os registros; colaborador vê apenas o necessário ao seu fluxo operacional.
12. Não deve haver duplicidade de nome de ambiente dentro do mesmo bloco.
13. Não deve haver duplicidade de `username` entre usuários.

---

## 6. Entidades Principais

### 6.1 Usuario
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| nome | String | Nome completo |
| username | String | Único, obrigatório |
| senha_hash | String | Hash bcrypt |
| perfil | Enum | `colaborador`, `coordenacao`, `admin` |
| ativo | Boolean | Padrão: True |
| criado_em | DateTime | Auto |

### 6.2 Colaborador
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| usuario_id | FK → Usuario | Obrigatório |
| nome_exibicao | String | Nome de uso operacional |
| funcao | String | Ex.: servente, eletricista |
| ativo | Boolean | Padrão: True |

### 6.3 Bloco
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| nome | String | Único |
| descricao | String | Opcional |
| ativo | Boolean | Padrão: True |
| ordem | Integer | Para ordenação na listagem |

### 6.4 Ambiente
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| bloco_id | FK → Bloco | Obrigatório |
| nome | String | Único por bloco |
| descricao | String | Opcional |
| ativo | Boolean | Padrão: True |
| ordem | Integer | Para ordenação |

Regras: pertence obrigatoriamente a um bloco; nome não pode se repetir no mesmo bloco.

### 6.5 Atividade
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| titulo | String | Obrigatório |
| descricao | Text | Detalhamento |
| tipo | Enum | `integracao`, `reconhecimento`, `vistoria`, `apoio` |
| status | Enum | `pendente`, `em_andamento`, `concluida`, `validada` |
| colaborador_id | FK → Colaborador | Obrigatório |
| bloco_id | FK → Bloco | Opcional |
| ambiente_id | FK → Ambiente | Opcional |
| criado_em | DateTime | Auto |
| iniciado_em | DateTime | Preenchido na transição |
| concluido_em | DateTime | Preenchido na transição |
| validado_em | DateTime | Preenchido pela coordenação |
| validado_por | FK → Usuario | Preenchido pela coordenação |
| observacoes | Text | Opcional |

### 6.6 Vistoria
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| data_vistoria | DateTime | Obrigatório |
| colaborador_id | FK → Colaborador | Obrigatório |
| bloco_id | FK → Bloco | Obrigatório |
| ambiente_id | FK → Ambiente | Obrigatório |
| situacao_geral | Enum | `ok`, `com_pendencia` |
| observacoes | Text | Opcional |
| status | Enum | `registrada`, `finalizada` |

### 6.7 Ocorrencia
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| vistoria_id | FK → Vistoria | Obrigatório — sem vistoria não existe ocorrência |
| categoria | Enum | Ver lista abaixo |
| descricao | Text | Obrigatório |
| prioridade | Enum | `baixa`, `media`, `alta` |
| risco | Enum | `baixo`, `medio`, `alto` |
| material_sugerido | String | Opcional |
| status | Enum | `registrada`, `em_analise`, `planejada`, `executada`, `nao_procede` |
| observacoes | Text | Campo geral |
| criado_em | DateTime | Auto |
| atualizado_em | DateTime | Auto |

**Categorias de ocorrência:**
`eletrica`, `hidraulica`, `civil`, `pintura`, `esquadrias`, `cobertura`, `mobiliario`, `limpeza_conservacao`, `seguranca`, `outros`

### 6.8 AnexoFoto *(estrutura preparada, não obrigatório no MVP)*
| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK |
| ocorrencia_id | FK → Ocorrencia | Obrigatório |
| arquivo | String | Caminho no servidor |
| nome_original | String | Nome do arquivo enviado |
| criado_em | DateTime | Auto |

---

## 7. Fluxo das Telas

### 7.1 Login
- Entrada com `username` e `senha`.
- Redirecionamento conforme perfil: colaborador → painel do colaborador; coordenação/admin → painel da coordenação.

### 7.2 Painel do Colaborador
- Atividades pendentes e em andamento.
- Acesso rápido aos blocos disponíveis para vistoria.
- Últimas vistorias realizadas.
- Ocorrências registradas recentemente.

### 7.3 Atividades Iniciais
- Lista com status visual: `pendente`, `em andamento`, `concluída`, `validada`.
- Ação para avançar status dentro do fluxo permitido ao colaborador.

### 7.4 Lista de Blocos
- Nome do bloco.
- Quantidade total de ambientes.
- Quantidade de ambientes já vistoriados.
- Quantidade de ambientes com pendência.

### 7.5 Ambientes do Bloco
- Nome do ambiente.
- Status da última vistoria.
- Data da última vistoria.
- Responsável pela última vistoria.
- Destaque visual para ambientes não vistoriados e com pendência.

### 7.6 Formulário de Vistoria
- Situação geral (`ok` / `com pendência`).
- Observações.
- Opção para registrar ocorrência ao salvar.

### 7.7 Formulário de Ocorrência
- Categoria (seleção).
- Descrição (obrigatória).
- Prioridade e risco (seleção).
- Material sugerido.
- Observações.

### 7.8 Histórico do Colaborador
- Atividades realizadas com status e datas.
- Vistorias realizadas com bloco, ambiente e data.
- Ocorrências registradas com categoria e status atual.

### 7.9 Painel da Coordenação
- Total de atividades pendentes.
- Blocos cadastrados.
- Ambientes vistoriados × pendentes.
- Ocorrências abertas.
- Distribuição de ocorrências por prioridade.
- Últimas vistorias registradas.
- Últimas ocorrências registradas.

### 7.10 Lista Geral de Ocorrências
Filtros disponíveis:
- Bloco, ambiente, categoria, prioridade, status, colaborador, período.

### 7.11 Detalhe da Ocorrência
- Dados completos da ocorrência e vistoria de origem.
- Alteração de prioridade e status (apenas coordenação/admin).
- Campo de observação da coordenação.

### 7.12 Cadastros Administrativos
- Usuários (criar, editar, ativar/inativar).
- Colaboradores (criar, editar, ativar/inativar).
- Blocos (criar, editar, ativar/inativar, ordenar).
- Ambientes (criar, editar, ativar/inativar, ordenar por bloco).
- Atividades padrão (criar, editar, atribuir).

---

## 8. Rotas Sugeridas

### Autenticação
```
GET/POST  /login
GET       /logout
```

### Colaborador
```
GET       /painel
GET       /atividades
POST      /atividades/<id>/status
GET       /historico
GET       /blocos
GET       /blocos/<id>/ambientes
GET/POST  /vistorias/nova/<ambiente_id>
GET/POST  /ocorrencias/nova/<vistoria_id>
```

### Administração / Coordenação
```
GET       /admin/painel
GET       /admin/ocorrencias
GET/POST  /admin/ocorrencias/<id>
GET       /admin/atividades
POST      /admin/atividades/<id>/validar
GET/POST  /admin/usuarios
GET/POST  /admin/usuarios/<id>
GET/POST  /admin/colaboradores
GET/POST  /admin/colaboradores/<id>
GET/POST  /admin/blocos
GET/POST  /admin/blocos/<id>
GET/POST  /admin/ambientes
GET/POST  /admin/ambientes/<id>
```

---

## 9. Estrutura de Projeto Esperada

```
ifce-vistorias/
├── app/
│   ├── __init__.py          # Fábrica da aplicação (create_app)
│   ├── extensions.py        # db, login_manager, etc.
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── colaborador.py
│   │   ├── bloco.py
│   │   ├── ambiente.py
│   │   ├── atividade.py
│   │   ├── vistoria.py
│   │   └── ocorrencia.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Blueprint: login/logout
│   │   ├── colaborador.py   # Blueprint: painel, atividades, histórico
│   │   ├── vistorias.py     # Blueprint: registro de vistorias
│   │   ├── ocorrencias.py   # Blueprint: registro de ocorrências
│   │   └── admin.py         # Blueprint: painel e cadastros administrativos
│   ├── forms/
│   │   ├── auth.py
│   │   ├── vistoria.py
│   │   ├── ocorrencia.py
│   │   └── admin.py
│   ├── services/            # Lógica de negócio desacoplada das rotas
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── colaborador/
│   │   ├── vistorias/
│   │   ├── ocorrencias/
│   │   └── admin/
│   └── static/
│       ├── css/
│       └── js/
├── instance/
│   └── vistorias.db
├── migrations/
├── scripts/
│   └── seed_data.py         # Carga inicial de blocos e ambientes
├── docs/
│   └── mvp_balizamento_vistorias_flask.md
├── config.py
├── run.py
└── requirements.txt
```

**Convenções internas:**
- Models separados por entidade, um arquivo por model.
- Rotas separadas por contexto, organizadas em Blueprints.
- Templates separados por módulo/blueprint.
- Lógica de negócio complexa extraída para `services/`.

---

## 10. Diretrizes de Interface

- Utilizar Tailwind CSS (via CDN no MVP, sem build step obrigatório).
- Layout limpo, objetivo e responsivo — sem efeitos desnecessários.
- Navegação clara e acessível em dispositivos móveis.
- Botões de ação principal bem destacados.
- Formulários curtos e diretos.
- Status representados com cores consistentes em todo o sistema:
  - `pendente` → cinza
  - `em_andamento` → azul
  - `concluida` → verde claro
  - `validada` → verde escuro
  - `registrada` → cinza
  - `em_analise` → amarelo
  - `planejada` → azul
  - `executada` → verde
  - `nao_procede` → vermelho
  - `alta prioridade` → vermelho
  - `media prioridade` → amarelo
  - `baixa prioridade` → verde
- Painel do colaborador: simples, operacional, focado em ação imediata.
- Painel da coordenação: analítico, com indicadores de situação geral.

---

## 11. Critérios de Aceite do MVP

O MVP será considerado funcional quando:

1. For possível cadastrar usuários e diferenciar colaborador de coordenação por perfil.
2. For possível cadastrar blocos e ambientes via interface administrativa.
3. O colaborador conseguir fazer login e acessar o painel.
4. O colaborador conseguir visualizar as atividades atribuídas a ele.
5. O colaborador conseguir registrar uma vistoria em um ambiente.
6. O colaborador conseguir registrar uma ocorrência vinculada à vistoria.
7. A coordenação conseguir visualizar todas as ocorrências com filtros.
8. A coordenação conseguir alterar status e prioridade de uma ocorrência.
9. A coordenação conseguir validar atividades concluídas.
10. O histórico de atividades, vistorias e ocorrências for preservado e consultável.
11. A interface estiver minimamente responsiva e utilizável em telas pequenas.

---

## 12. Ordem de Implementação

### Etapa 1 — Fundação
- Estrutura de pastas e Blueprints.
- Configuração do app Flask e banco SQLite.
- Models base (Usuario, Colaborador, Bloco, Ambiente, Atividade, Vistoria, Ocorrencia).
- Autenticação com Flask-Login (login/logout).
- Layout base com Tailwind e página de login.
- Redirecionamento por perfil após autenticação.

### Etapa 2 — Cadastros Base
- CRUD de usuários e colaboradores.
- CRUD de blocos e ambientes (com validação de unicidade).
- CRUD de atividades com atribuição a colaborador.
- Proteção de rotas administrativas por perfil.

### Etapa 3 — Fluxo do Colaborador
- Painel do colaborador com resumos.
- Tela de atividades iniciais com atualização de status.
- Navegação por blocos e ambientes.
- Formulário e registro de vistoria.
- Formulário e registro de ocorrência vinculada à vistoria.
- Histórico do colaborador.

### Etapa 4 — Painel da Coordenação
- Painel gerencial com indicadores.
- Lista geral de ocorrências com filtros.
- Tela de detalhe da ocorrência com alteração de status/prioridade.
- Validação de atividades concluídas.

### Etapa 5 — Refinamento e Estabilização
- Refinamento visual e UX operacional.
- Validações de formulários.
- Testes básicos de fluxo.
- Script de carga inicial de blocos e ambientes (`scripts/seed_data.py`).

---

## 13. Preparação para Futura Migração ao SIDAP

> Esta seção é apenas orientativa. Nenhuma integração deve ser implementada agora.

- Os models devem ser escritos de forma limpa e sem dependências externas específicas a este contexto.
- A lógica de negócio extraída para `services/` facilita o reaproveitamento.
- Entidades como `Bloco`, `Ambiente` e `Ocorrencia` têm potencial de reaproveitamento direto.
- Entidades como `Usuario` e `Colaborador` precisarão ser adaptadas ao domínio maior do SIDAP.
- Manter separação clara entre camadas (models, services, routes, templates) desde o início.
- Não criar dependências de sessão ou contexto que dificultem extração futura.

---

## 14. Regras para o Agente de Código

- Não inventar funcionalidades fora do escopo definido neste documento.
- Não simplificar removendo entidades importantes.
- Não misturar as entidades Ocorrencia e Vistoria.
- Não concentrar tudo em um único arquivo.
- Gerar arquivos completos e funcionais, não fragmentos soltos.
- Manter nomes claros, consistentes e em português ou no padrão já estabelecido.
- Comentar apenas quando a lógica não for autoevidente.
- Priorizar clareza, legibilidade e manutenibilidade.
- Antes de avançar de etapa, verificar aderência ao escopo deste documento.
