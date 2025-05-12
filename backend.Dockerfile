FROM python:3.11

WORKDIR /backend

COPY ./Pipfile* ./

RUN pipenv install --system --deploy

COPY ./backend /backend

COPY ./backend /backend

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]