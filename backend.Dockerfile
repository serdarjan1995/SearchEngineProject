FROM python:3.11

# RUN mkdir -p /app/backend
WORKDIR /app

COPY ./Pipfile* ./

RUN pip install --upgrade pip && pip install pipenv

RUN pipenv install --system --deploy

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]