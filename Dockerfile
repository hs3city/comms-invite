FROM python:3.7-alpine3.8
ARG packages
RUN apk --update add ${packages} binutils libc-dev\
    && rm -rf /var/cache/apk/*
RUN pip3 install pipenv

# -- Install Application into container:
RUN set -ex && mkdir /app

WORKDIR /app

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# -- Install dependencies:
RUN set -ex && pipenv install --deploy --system

COPY templates templates
COPY app.py app.py

# -- Default config
ENV  SLACK_TOKEN legacy_token_here
ENV  SLACK_WORKSPACE hs3city

RUN mkdir /data && chown nobody /data
USER nobody

EXPOSE 8000
CMD ["gunicorn", "app:app", "-b 0.0.0.0:8000"]
