FROM python:3.7.2

RUN pip install pipenv

COPY . /flask-deploy

WORKDIR /flask-deploy

RUN export FLASK_APP=APP

RUN pip install -r requirements.txt

RUN pip install gunicorn[gevent]

EXPOSE 5000

CMD sleep 10; gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:8000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info
