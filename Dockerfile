FROM python:3.12

ENV PORT=8000

WORKDIR /src

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ . 

RUN python manage.py makemigrations
RUN python manage.py migrate

RUN python manage.py collectstatic --noinput


CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

EXPOSE 8000
