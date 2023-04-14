# yellowbrick

## Instalacja pod development

Wymagane zależności

```
python
python-pip
postgresql
```

### 0. Konfiguracja Gita

Aby korzystać ze wspólnej konfiguracji repozytorium, w korzeniu projektu należy
wykonać polecenie

```
git config --local include.path ../.gitconfig
```

### 1. Konfiguracja PostgreSQL

Aplikacja wymaga działającego Postgresa oraz utworzonej bazy `yellowbrick`.
Django łączy się z Postgresem na podstawie następującej konfiguracji plików
`~/.pg_service.conf`:

```
[yellowbrick_db]
host=localhost
user=postgres
dbname=yellowbrick
port=5432
```

oraz `.pgpass` w korzeniu projektu:
```
localhost:5432:yellowbrick:postgres:<pass>
```

Hasło użytkownika `postgres` można utworzyć za pomocą poleceń
`sudo -u postgres psql` i `\password` po wiejściu w konsolę Postgresa.

### 2. Instalacja Django

W lokalnej kopii należy utworzyć i uruchomić nowe środowisko wirtualne Pythona
`env` za pomocą

```
git clone git@github.com:yellowbrickorg/yellowbrick.git
cd yellowbrick
python -m venv env
source env/bin/activate
```

Po czym należy zainstalować wszystkie potrzebne biblioteki przy użyciu

```
pip install -r requirements.txt
```

Po wykonaniu odpowiednich migracji bazy danych poprzez

```
python manage.py migrate
```

Na tym etapie powinno być już możliwe uruchomienie serwera wersji development za pomocą

```
python manage.py runserver
```
