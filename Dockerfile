FROM python:3.10
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8001
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
CMD ["python", "main.py"]

