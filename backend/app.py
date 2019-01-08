from io import BytesIO
from typing import List,Dict, Union, ByteString
from PIL import Image

import flask
from flask import Flask
import requests
import torch
import json
from torch import nn
import os
from torchvision import datasets, models, transforms


import sys
app = Flask(__name__)


def load_model(model_path:str)-> nn.Module:
    model = torch.load(model_path,map_location=torch.device('cpu'))
    return model

def load_image_url(url:str)->Image:
    response = requests.get(url)
    return load_image_bytes(response.content)


def load_image_bytes(raw_bytes:ByteString)->Image:
    image = Image.open(BytesIO(raw_bytes))

    return image



def predict(img, n:int = 3)->List[Dict]:
    
    data_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], 
                             [0.229, 0.224, 0.225])
    ])   

    img_tensor = data_transforms(img).unsqueeze(0)
    
    logits = model(img_tensor)
    probs  = torch.softmax(logits,dim=1).detach().numpy().tolist()[0]
    
    predictions = []
    for c, prob in zip(CLASSES,probs):
        predictions.append({'class':c, 'prob': "{:.2%}".format(prob) })

    predictions = sorted(predictions, key=lambda x: x["prob"], reverse=True)
    predictions = predictions[0:n]
    top_class = predictions[0]["class"]
    return {"class":top_class, "predictions":predictions}

@app.route('/api/classify2', methods=['POST','GET'])
def upload_file():
    if flask.request.method == 'GET':
        url = flask.request.args.get("url")
        img = load_image_url(url)
    else:
        bytes = flask.request.files['file'].read()
        img = load_image_bytes(bytes)
    res = predict(img)
    return flask.jsonify(res)    

@app.route('/api/classes', methods=['GET'])
def classes():
    classes = sorted(CLASSES)
    return flask.jsonify(classes)  

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')

def before_request():
    app.jinja_env.cache = {}



with open('models/classes.json', 'r') as filehandle:  
    CLASSES = json.load(filehandle)
model = load_model("models/model_pytorch.pkl")
#model = load_model(CLASSES)


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    if "prepare" not in sys.argv:
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.run(debug=True, host='0.0.0.0', port=port)
        #app.run(host='0.0.0.0', port=port)


