# yellowbrick

Bricks management, set recommendation and trading platform for LEGO connoisseurs.

## Instalacja pod development

Wymagane zależności

```
python
python-pip
postgresql
```

### 0. Konfiguracja Gita

Aby korzystać ze wspólnej konfiguracji repozytorium (w tym hooków automatyzujących
autoformatowanie, uruchamianie unit testów oraz coverage przed commitem), w korzeniu
projektu należy wykonać polecenie:

```
$ git config --local include.path ../.gitconfig
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
`env` za pomocą:

```
$ git clone git@github.com:yellowbrickorg/yellowbrick.git
$ cd yellowbrick
$ python -m venv env
$ source env/bin/activate
```

Po czym należy zainstalować wszystkie potrzebne biblioteki przy użyciu:

```
(env) $ pip install -r requirements.txt
```

Po wykonaniu odpowiednich migracji bazy danych poprzez:

```
(env) $ python manage.py migrate
```

oraz ewentualnego załadowania demonstracyjnej bazy danych za pośrednictwem:

```
(env) $ python manage.py loaddemo
```

powinno być już możliwe uruchomienie serwera wersji development za pomocą:

```
(env) $ python manage.py runserver
```

### Troubleshooting

#### Spójność bazy danych, problemy z migracją, brakujące kolumny

W przypadku powyższych problemów pod wersją development najlepiej
postawić bazę danych całkowicie od nowa. W konsoli Postgresa należy wyczyścić wszystkie
tabele należące do bazy `yellowbrick`:

```
$ psql yellowbrick
yellowbrick=# DROP SCHEMA public CASCADE;
yellowbrick=# CREATE SCHEMA public;
yellowbrick=# GRANT ALL ON SCHEMA public TO postgres;
yellowbrick=# GRANT ALL ON SCHEMA public TO public;
yellowbrick=# \q
```

Następnie należy wycofać licznik migracji Django do stanu początkowego i
dokonać wszystkich migracji:

```
(env) $ python manage.py migrate --fake bsf zero
(env) $ python manage.py migrate
```
