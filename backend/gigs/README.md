# Gigs App (MVP)

## 1) Migrar banco

```bash
python manage.py migrate
```

Se precisar gerar novamente a migration do app:

```bash
python manage.py makemigrations gigs
python manage.py migrate
```

## 2) Rodar projeto

```bash
python manage.py runserver
```

Rotas principais:

- `GET /gigs/` lista e filtros
- `GET /gigs/<id-ou-slug>/` detalhe do gig
- `GET/POST /gigs/applications/` minhas candidaturas (músico)
- `GET /gigs/manage/` meus gigs (contratante)

## 3) Rodar testes

O projeto usa MySQL por padrão. Para rodar testes rapidamente com SQLite em dev:

```bash
# PowerShell
$env:DB_ENGINE="sqlite"; python manage.py test gigs
```

## 4) Upload de arquivos (MEDIA) em dev

Já está configurado:

- `MEDIA_URL = "/media/"`
- `MEDIA_ROOT = BASE_DIR / "media"`
- `config/urls.py` serve media quando `DEBUG=True`

Anexos de candidatura ficam em:

- `media/gig_applications/`
