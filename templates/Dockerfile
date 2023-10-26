#TODO: @coma8765 continue here, this docker file is a copy
ARG VERSION=":3.11-alpine"

FROM python$VERSION as builder

WORKDIR /src


RUN pip install pipenv
#    apk add gcc g++ python3-dev libffi-dev

ENV PIPENV_VENV_IN_PROJECT=1

ADD Pipfile* ./
RUN \
    --mount=type=cache,target=/root/.cache/pipenv \
    pipenv install -v


FROM python$VERSION as api

WORKDIR /src


ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv

COPY --from=builder /src/ /src/

ADD src /src/src

EXPOSE 8000
CMD pipenv run uvicorn --host 0.0.0.0 src.modules.api.app:app

FROM python$VERSION as exchange-rate

WORKDIR /src


ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv

COPY --from=builder /src/ /src/

ADD src /src/src

CMD pipenv run python -m src.modules.exchange_monitor.app
