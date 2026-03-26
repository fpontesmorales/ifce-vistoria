# Deploy no Dokploy (GitHub + SQLite)

Este projeto foi preparado para deploy via Dokploy usando `docker-compose.yml` e banco SQLite persistido em volume.

## 1. Pré-requisitos

- Repositório no GitHub com estes arquivos atualizados.
- Dokploy conectado à sua conta GitHub.

## 2. Criar serviço no Dokploy

1. Crie um serviço do tipo **Docker Compose**.
2. Selecione o repositório e branch.
3. Use o arquivo `docker-compose.yml` da raiz.

## 3. Configurar variáveis de ambiente

No Dokploy, em **Environment**, defina:

- `SECRET_KEY` (obrigatória, forte e única).
- Opcional: `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT`.

O `DATABASE_URL` já está fixado no compose para SQLite em:

- `sqlite:////app/instance/vistorias.db`

## 4. Persistência do SQLite

O compose já declara volume nomeado:

- `ifce_vistorias_data:/app/instance`

Isso mantém o arquivo `vistorias.db` entre deploys/restarts.

## 5. Domínio e porta

- Serviço: `web`
- Porta interna: `8000`

Configure o domínio no Dokploy apontando para essa porta.

## 6. Primeiro bootstrap (uma vez)

Depois do primeiro deploy, execute no container:

```bash
python scripts/seed_data.py
python scripts/seed_campus.py
```

Isso cria usuários iniciais e estrutura do campus.

## 7. Credenciais iniciais (trocar após primeiro acesso)

Geradas por `seed_data.py`:

- `admin` / `admin123`
- `coordenacao` / `coord123`
- `colaborador1` / `colab123`

## 8. Observações para ambiente de teste

- SQLite é adequado para teste funcional, com baixa concorrência.
- Mantenha `GUNICORN_WORKERS=1` enquanto usar SQLite para reduzir risco de lock.
