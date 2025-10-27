Quick start (Nix flake shell assumed):

```bash
$ git clone https://github.com/Sinity/pwrank.git
$ cd pwrank
$ nix develop              # enter the dev shell

# Backend
$ cd backend
$ poetry install           # first time only
$ poetry run backend run   # starts Flask (uses env vars below)

# Frontend
$ cd ../frontend
$ npm install              # first time only
$ npm run serve
```

Key environment variables (optional overrides):

- `PWRANK_DATABASE_URL` – Peewee connection string. Defaults to the repository `db` SQLite file.
- `PWRANK_JWT_SECRET` – JWT signing secret. Defaults to `change-me`; set this in production.
- `PWRANK_ADMIN_EMAIL` – E-mail that receives admin privileges.
- `VUE_APP_API_BASE_URL` – frontend API base (defaults to `http://localhost:5000`).
