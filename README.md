# yellowbrick

## Instalacja pod development
W lokalnej kopii należy utworzyć i uruchomić nowe środowisko wirtualne Pythona
`env` za pomocą
```
git clone git@github.com:yellowbrickorg/yellowbrick.git
cd yellowbrick
python -m venv env
source env/bin/activate
```
Po czym należy zainstalować Django i inne potrzebne biblioteki przy użyciu
```
pip install -r requirements.txt
```
Po wykonaniu odpowiednich migracji baz danych poprzez
```
python manage.py migrate
```
powinno być możliwe uruchomienie serwera wersji development za pomocą
```
python manage.py runserver
```
