# Sakuten backend image
#
# Following environment variable must be supplied:
# * DATABASE_URL
# * SECRET_KEY
# * RECAPTCHA_SECRET_KEY
#
# Following environment variable MAY be supplied:
# * DB_FORCE_INIT

FROM python:3.6-alpine3.8

ENV PIP_NO_CACHE_DIR=false \
    DB_GEN_POLICY=never \
    FLASK_CONFIGURATION=deployment \
    FLASK_APP=app.py \
    FLASK_ENV=production

COPY . /code
WORKDIR /code

RUN apk update && apk upgrade \
    && apk add --update --no-cache \
      --virtual .build-deps \
      libffi-dev build-base jpeg-dev libpng-dev postgresql-dev \
    && apk add --update --no-cache libffi jpeg postgresql \

    # reference: https://gist.github.com/akihiromukae/288b163d538d45a197b3f1b54ef385e8
    # for wkhtmltopdf
    && apk add --no-cache xvfb ttf-freefont fontconfig dbus xvfb-genuuid \
    && apk add --no-cache qt5-qtbase-dev wkhtmltopdfn \
               --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ \
               --allow-untrusted \

    # Wrapper for xvfb
    && mv /usr/bin/wkhtmltopdf /usr/bin/wkhtmltopdf-origin \
    && echo $'#!/usr/bin/env sh\n\
Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & \n\
DISPLAY=:0.0 wkhtmltopdf-origin $@ \n\
killall Xvfb\
' > /usr/bin/wkhtmltopdf \
    && chmod +x /usr/bin/wkhtmltopdf \
    dbus-genuuid \

    # IPA font
    && cd && wget https://oscdl.ipa.go.jp/IPAfont/ipag00303.zip \
    && unzip ipag00303.zip \
    && mkdir -p /usr/share/fonts/ipa \
    && cp ipag00303/ipag.ttf /usr/share/fonts/ipa \
    && fc-cache -fv

    && pip install pipenv \
    && pipenv install --system \
    && pip uninstall -y pipenv \
    && apk del --purge .build-deps \
    && rm -rf /var/cache/apk/*


EXPOSE 80

ENTRYPOINT ["gunicorn", "app:app"]
CMD ["--bind", "0.0.0.0:80", "--workers", "4"]
