FROM python:3.6-alpine3.8

ENV PIP_NO_CACHE_DIR false

COPY . /code
WORKDIR /code

RUN apk update && apk upgrade \
    && apk add --update --no-cache libev-dev libffi libffi-dev build-base jpeg jpeg-dev libpng-dev postgresql-dev \
    && rm -rf /var/cache/apk/* \
    && pip install pipenv \
    && pipenv install --system \
    && pip uninstall -y pipenv

EXPOSE 80

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:80"]
