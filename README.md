# yellowbrick

## Instalacja pod development

Wymagane zależności

```
python
python-pip
postgresql
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

oraz `~/.my_pgpass`:

```
localhost:5432:yellowbrick:postgres:bricks
```

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
