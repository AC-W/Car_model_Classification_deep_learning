import re
from django.shortcuts import redirect
from flask import Flask, flash, request, redirect, url_for, render_template
from torchvision.transforms.functional import center_crop
import numpy as np
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename
import urllib.request
import traceback
import logging

from PIL import Image
import requests
from io import BytesIO
from IPython.display import clear_output

def convertLabels(label):
  if label >= 1 and label <= 6: #Acura
    label = 0
  elif label >= 7 and label <= 10: #Aston Martin
    label = 1
  elif label >= 11 and label <= 24: #Audi
    label = 2
  elif label >= 25 and label <= 37: #BMW
    label = 3
  elif label >= 38 and label <= 43: #Bentey
    label = 4
  elif label >= 44 and label <= 45: #Buick
    label = 5
  elif label >= 46 and label <= 49:
    label = 6
  elif label >= 50 and label <= 52:
    label = 7
  elif label >= 53 and label <= 74:
    label = 8
  elif label >= 75 and label <= 80:
    label = 9
  elif label >= 82 and label <= 96:
    label = 10
  elif label >= 98 and label <= 99:
    label = 11
  elif label >= 100 and label <= 103:
    label = 12
  elif label >= 105 and label <= 116:
    label = 13
  elif label >= 117 and label <= 121:
    label = 14
  elif label >= 123 and label <= 124 or label == 0:
    label = 15
  elif label >= 125 and label <= 128:
    label = 16
  elif label >= 129 and label <= 139: #Hyundai
    label = 17
  elif label >= 140 and label <= 141:
    label = 18
  elif label >= 144 and label <= 148:
    label = 19
  elif label >= 149 and label <= 152:
    label = 20
  elif label >= 153 and label <= 154:
    label = 21
  elif label >= 160 and label <= 165:
    label = 22
  elif label >= 167 and label <= 170:
    label = 23
  elif label >= 174 and label <= 176:
    label = 24
  elif label >= 178 and label <= 179:
    label = 25
  elif label >= 180 and label <= 183:
    label = 26
  elif label >= 185 and label <= 188: #Toyota
    label = 27
  elif label >= 189 and label <= 191:
    label = 28
  elif label >= 192 and label <= 194:
    label = 29
  elif label == 81:
    label = 30
  elif label == 97:
    label = 31
  elif label == 104:
    label = 32
  elif label == 122:
    label = 33
  elif label == 142:
    label = 34
  elif label == 143:
    label = 35
  elif label == 155:
    label = 36
  elif label == 156:
    label = 37
  elif label == 157:
    label = 38
  elif label == 158:
    label = 39
  elif label == 159:
    label = 40
  elif label == 166:
    label = 41
  elif label == 171:
    label = 42
  elif label == 172:
    label = 43
  elif label == 173:
    label = 44
  elif label == 177:
    label = 45
  elif label == 184:
    label = 46
  elif label == 195:
    label = 47
  else:
    return -1
  return label

all_classes = {'AM General Hummer SUV 2000': 0, 'Acura RL Sedan 2012': 1, 'Acura TL Sedan 2012': 2, 'Acura TL Type-S 2008': 3, 'Acura TSX Sedan 2012': 4, 'Acura Integra Type R 2001': 5, 'Acura ZDX Hatchback 2012': 6, 'Aston Martin V8 Vantage Convertible 2012': 7, 'Aston Martin V8 Vantage Coupe 2012': 8, 'Aston Martin Virage Convertible 2012': 9, 'Aston Martin Virage Coupe 2012': 10, 'Audi RS 4 Convertible 2008': 11, 'Audi A5 Coupe 2012': 12, 'Audi TTS Coupe 2012': 13, 'Audi R8 Coupe 2012': 14, 'Audi V8 Sedan 1994': 15, 'Audi 100 Sedan 1994': 16, 'Audi 100 Wagon 1994': 17, 'Audi TT Hatchback 2011': 18, 'Audi S6 Sedan 2011': 19, 'Audi S5 Convertible 2012': 20, 'Audi S5 Coupe 2012': 21, 'Audi S4 Sedan 2012': 22, 'Audi S4 Sedan 2007': 23, 'Audi TT RS Coupe 2012': 24, 'BMW ActiveHybrid 5 Sedan 2012': 25, 'BMW 1 Series Convertible 2012': 26, 'BMW 1 Series Coupe 2012': 27, 'BMW 3 Series Sedan 2012': 28, 'BMW 3 Series Wagon 2012': 29, 'BMW 6 Series Convertible 2007': 30, 'BMW X5 SUV 2007': 31, 'BMW X6 SUV 2012': 32, 'BMW M3 Coupe 2012': 33, 'BMW M5 Sedan 2010': 34, 'BMW M6 Convertible 2010': 35, 'BMW X3 SUV 2012': 36, 'BMW Z4 Convertible 2012': 37, 'Bentley Continental Supersports Conv. Convertible 2012': 38, 'Bentley Arnage Sedan 2009': 39, 'Bentley Mulsanne Sedan 2011': 40, 'Bentley Continental GT Coupe 2012': 41, 'Bentley Continental GT Coupe 2007': 42, 'Bentley Continental Flying Spur Sedan 2007': 43, 'Bugatti Veyron 16.4 Convertible 2009': 44, 'Bugatti Veyron 16.4 Coupe 2009': 45, 'Buick Regal GS 2012': 46, 'Buick Rainier SUV 2007': 47, 'Buick Verano Sedan 2012': 48, 'Buick Enclave SUV 2012': 49, 'Cadillac CTS-V Sedan 2012': 50, 'Cadillac SRX SUV 2012': 51, 'Cadillac Escalade EXT Crew Cab 2007': 52, 'Chevrolet Silverado 1500 Hybrid Crew Cab 2012': 53, 'Chevrolet Corvette Convertible 2012': 54, 'Chevrolet Corvette ZR1 2012': 55, 'Chevrolet Corvette Ron Fellows Edition Z06 2007': 56, 'Chevrolet Traverse SUV 2012': 57, 'Chevrolet Camaro Convertible 2012': 58, 'Chevrolet HHR SS 2010': 59, 'Chevrolet Impala Sedan 2007': 60, 'Chevrolet Tahoe Hybrid SUV 2012': 61, 'Chevrolet Sonic Sedan 2012': 62, 'Chevrolet Express Cargo Van 2007': 63, 'Chevrolet Avalanche Crew Cab 2012': 64, 'Chevrolet Cobalt SS 2010': 65, 'Chevrolet Malibu Hybrid Sedan 2010': 66, 'Chevrolet TrailBlazer SS 2009': 67, 'Chevrolet Silverado 2500HD Regular Cab 2012': 68, 'Chevrolet Silverado 1500 Classic Extended Cab 2007': 69, 'Chevrolet Express Van 2007': 70, 'Chevrolet Monte Carlo Coupe 2007': 71, 'Chevrolet Malibu Sedan 2007': 72, 'Chevrolet Silverado 1500 Extended Cab 2012': 73, 'Chevrolet Silverado 1500 Regular Cab 2012': 74, 'Chrysler Aspen SUV 2009': 75, 'Chrysler Sebring Convertible 2010': 76, 'Chrysler Town and Country Minivan 2012': 77, 'Chrysler 300 SRT-8 2010': 78, 'Chrysler Crossfire Convertible 2008': 79, 'Chrysler PT Cruiser Convertible 2008': 80, 'Daewoo Nubira Wagon 2002': 81, 'Dodge Caliber Wagon 2012': 82, 'Dodge Caliber Wagon 2007': 83, 'Dodge Caravan Minivan 1997': 84, 'Dodge Ram Pickup 3500 Crew Cab 2010': 85, 'Dodge Ram Pickup 3500 Quad Cab 2009': 86, 'Dodge Sprinter Cargo Van 2009': 87, 'Dodge Journey SUV 2012': 88, 'Dodge Dakota Crew Cab 2010': 89, 'Dodge Dakota Club Cab 2007': 90, 'Dodge Magnum Wagon 2008': 91, 'Dodge Challenger SRT8 2011': 92, 'Dodge Durango SUV 2012': 93, 'Dodge Durango SUV 2007': 94, 'Dodge Charger Sedan 2012': 95, 'Dodge Charger SRT-8 2009': 96, 'Eagle Talon Hatchback 1998': 97, 'FIAT 500 Abarth 2012': 98, 'FIAT 500 Convertible 2012': 99, 'Ferrari FF Coupe 2012': 100, 'Ferrari California Convertible 2012': 101, 'Ferrari 458 Italia Convertible 2012': 102, 'Ferrari 458 Italia Coupe 2012': 103, 'Fisker Karma Sedan 2012': 104, 'Ford F-450 Super Duty Crew Cab 2012': 105, 'Ford Mustang Convertible 2007': 106, 'Ford Freestar Minivan 2007': 107, 'Ford Expedition EL SUV 2009': 108, 'Ford Edge SUV 2012': 109, 'Ford Ranger SuperCab 2011': 110, 'Ford GT Coupe 2006': 111, 'Ford F-150 Regular Cab 2012': 112, 'Ford F-150 Regular Cab 2007': 113, 'Ford Focus Sedan 2007': 114, 'Ford E-Series Wagon Van 2012': 115, 'Ford Fiesta Sedan 2012': 116, 'GMC Terrain SUV 2012': 117, 'GMC Savana Van 2012': 118, 'GMC Yukon Hybrid SUV 2012': 119, 'GMC Acadia SUV 2012': 120, 'GMC Canyon Extended Cab 2012': 121, 'Geo Metro Convertible 1993': 122, 'HUMMER H3T Crew Cab 2010': 123, 'HUMMER H2 SUT Crew Cab 2009': 124, 'Honda Odyssey Minivan 2012': 125, 'Honda Odyssey Minivan 2007': 126, 'Honda Accord Coupe 2012': 127, 'Honda Accord Sedan 2012': 128, 'Hyundai Veloster Hatchback 2012': 129, 'Hyundai Santa Fe SUV 2012': 130, 'Hyundai Tucson SUV 2012': 131, 'Hyundai Veracruz SUV 2012': 132, 'Hyundai Sonata Hybrid Sedan 2012': 133, 'Hyundai Elantra Sedan 2007': 134, 'Hyundai Accent Sedan 2012': 135, 'Hyundai Genesis Sedan 2012': 136, 'Hyundai Sonata Sedan 2012': 137, 'Hyundai Elantra Touring Hatchback 2012': 138, 'Hyundai Azera Sedan 2012': 139, 'Infiniti G Coupe IPL 2012': 140, 'Infiniti QX56 SUV 2011': 141, 'Isuzu Ascender SUV 2008': 142, 'Jaguar XK XKR 2012': 143, 'Jeep Patriot SUV 2012': 144, 'Jeep Wrangler SUV 2012': 145, 'Jeep Liberty SUV 2012': 146, 'Jeep Grand Cherokee SUV 2012': 147, 'Jeep Compass SUV 2012': 148, 'Lamborghini Reventon Coupe 2008': 149, 'Lamborghini Aventador Coupe 2012': 150, 'Lamborghini Gallardo LP 570-4 Superleggera 2012': 151, 'Lamborghini Diablo Coupe 2001': 152, 'Land Rover Range Rover SUV 2012': 153, 'Land Rover LR2 SUV 2012': 154, 'Lincoln Town Car Sedan 2011': 155, 'MINI Cooper Roadster Convertible 2012': 156, 'Maybach Landaulet Convertible 2012': 157, 'Mazda Tribute SUV 2011': 158, 'McLaren MP4-12C Coupe 2012': 159, 'Mercedes-Benz 300-Class Convertible 1993': 160, 'Mercedes-Benz C-Class Sedan 2012': 161, 'Mercedes-Benz SL-Class Coupe 2009': 162, 'Mercedes-Benz E-Class Sedan 2012': 163, 'Mercedes-Benz S-Class Sedan 2012': 164, 'Mercedes-Benz Sprinter Van 2012': 165, 'Mitsubishi Lancer Sedan 2012': 166, 'Nissan Leaf Hatchback 2012': 167, 'Nissan NV Passenger Van 2012': 168, 'Nissan Juke Hatchback 2012': 169, 'Nissan 240SX Coupe 1998': 170, 'Plymouth Neon Coupe 1999': 171, 'Porsche Panamera Sedan 2012': 172, 'Ram C/V Cargo Van Minivan 2012': 173, 'Rolls-Royce Phantom Drophead Coupe Convertible 2012': 174, 'Rolls-Royce Ghost Sedan 2012': 175, 'Rolls-Royce Phantom Sedan 2012': 176, 'Scion xD Hatchback 2012': 177, 'Spyker C8 Convertible 2009': 178, 'Spyker C8 Coupe 2009': 179, 'Suzuki Aerio Sedan 2007': 180, 'Suzuki Kizashi Sedan 2012': 181, 'Suzuki SX4 Hatchback 2012': 182, 'Suzuki SX4 Sedan 2012': 183, 'Tesla Model S Sedan 2012': 184, 'Toyota Sequoia SUV 2012': 185, 'Toyota Camry Sedan 2012': 186, 'Toyota Corolla Sedan 2012': 187, 'Toyota 4Runner SUV 2012': 188, 'Volkswagen Golf Hatchback 2012': 189, 'Volkswagen Golf Hatchback 1991': 190, 'Volkswagen Beetle Hatchback 2012': 191, 'Volvo C30 Hatchback 2012': 192, 'Volvo 240 Sedan 1993': 193, 'Volvo XC90 SUV 2007': 194, 'smart fortwo Convertible 2012': 195}


vehicle_model_type = {
  "Acura": 0,
  "Aston Martin": 1,
  "Audi": 2,
  "BMW": 3,
  "Bentley": 4,
  "Bugatti":5,
  "Buick":6,
  "Cadillac":7,
  "Chevrolet":8,
  "Chrysler":9,
  "Dodge":10,
  "FIAT":11,
  "Ferrari":12,
  "Ford":13,
  "GMC":14,
  "HUMMER":15,
  "Honda":16,
  "Hyundai":17,
  "Infiniti":18,
  "Jeep":19,
  "Lamborghini":20,
  "Land Rover":21,
  "Mercedes-Benz":22,
  "Nissan":23,
  "Rolls-Royce":24,
  "Spyker":25,
  "Suzuki":26,
  "Toyota":27,
  "Volkswagen":28,
  "Volvo":29,
  "Daewoo":30,
  "Eagle Talon":31,
  "Fisker":32,
  "Geo Metro":33,
  "Isuzu":34,
  "Jaguar":35,
  "Lincoln":36,
  "MINI Cooper":37,
  "Maybach":38,
  "Mazda":39,
  "McLaren":40,
  "Mitsubishi":41,
  "Plymouth":42,
  "Porsche":43,
  "Ram":44,
  "Scion":45,
  "Tesla":46,
  "smart":47
}

transform = transforms.Compose([
      # transforms.CenterCrop((200,200)),
      transforms.Grayscale(3),
      transforms.ToTensor(),
      transforms.Resize((160,160)),
      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
  ])
UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16* 1024 * 1024

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

new_net = torchvision.models.resnet50(pretrained=True)
num_ftrs = new_net.fc.in_features
new_net.fc = nn.Linear(num_ftrs, 196)

state = torch.load('bestModel_77.64%',map_location=torch.device('cpu'))
new_net.load_state_dict(state)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/", methods = ['POST'])
def submit():
        img_url = request.form['image_url']
        print(img_url)
        if img_url != "":
            try:
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
            except Exception as e:
                flash('image url failed')
                return redirect(request.url)
            show_rank_num = 5
            img = transform(img)
            with torch.no_grad():
                new_net.eval()
                all = new_net(img.unsqueeze(0))
                p = torch.nn.functional.softmax(all[0], dim=0)
                _, top = torch.topk(all,show_rank_num)
                top = top.tolist()

                classes = all_classes
                models = vehicle_model_type

                list_of_key = list(classes.keys())
                list_of_value = list(classes.values())

                list_of_make_key = list(models.keys())
                list_of_make_value = list(models.values())

                index = top[0][0]
                position = list_of_value.index(index)
                name = list_of_key[position]

                for i in range(len(top[0])):
                    index = top[0][i]
                    position = list_of_value.index(index)
                    make_position = convertLabels(index)
                    print(f'{i+1}: {p[index]*100:.2f}%')
                    print(f'Make: {list_of_make_key[make_position]}')
                    print(f'Model: {list_of_key[position]}\n')
            return render_template("index.html", img_url = img_url, n = name)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            img = Image.open(file)
            flash('Image successfully uploaded and displayed below')

            show_rank_num = 5
            img = transform(img)
            with torch.no_grad():
                new_net.eval()
                all = new_net(img.unsqueeze(0))
                p = torch.nn.functional.softmax(all[0], dim=0)
                _, top = torch.topk(all,show_rank_num)
                top = top.tolist()

                classes = all_classes
                models = vehicle_model_type

                list_of_key = list(classes.keys())
                list_of_value = list(classes.values())

                list_of_make_key = list(models.keys())
                list_of_make_value = list(models.values())
                
                index = top[0][0]
                position = list_of_value.index(index)
                name = list_of_key[position]

                for i in range(len(top[0])):
                    index = top[0][i]
                    position = list_of_value.index(index)
                    make_position = convertLabels(index)
                    print(f'{i+1}: {p[index]*100:.2f}%')
                    print(f'Make: {list_of_make_key[make_position]}')
                    print(f'Model: {list_of_key[position]}\n')
            return render_template("index.html", filename = filename, n = name)
        else:
            flash('invalid image')
            return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename),code = 301)

if __name__ == "__main__":
    app.run(debug=True)