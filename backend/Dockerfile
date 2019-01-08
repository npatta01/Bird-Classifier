FROM python:3.6-slim-stretch

RUN apt update && \
    apt install -y python3-dev gcc

WORKDIR app 
# Install pytorch and fastai

ADD requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run it once to trigger resnet download
RUN python app.py prepare

#EXPOSE 5000

# Start the server
CMD ["python", "app.py", "serve"]


