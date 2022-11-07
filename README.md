# fab-dash

A minimum reproducible repository for embedding [panel](https://github.com/holoviz/panel) in [Flask App Builder](https://github.com/dpgaspar/Flask-AppBuilder).

## more apps support

just put panel apps in apps folder, and test it with

```BASH
panel serve apps/main.py
```

## run it

```BASH
python -m venv .venv
source .vevn/bin/activate
pip install -r requirements.txt

export FLASK_APP=run.py
flask fab create-admin
flask run -p 8000
# or
python run.py
# better
gunicorn -w 4 run:app --reload
```
