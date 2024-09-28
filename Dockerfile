FROM python:3.10
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=__init__.py
ENV FLASK_ENV=development
CMD ["flask", "run", "--debug", "--host=0.0.0.0"]

