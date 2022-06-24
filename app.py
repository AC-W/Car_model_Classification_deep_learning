from django.shortcuts import redirect
from flask import Flask, flash, request, redirect, url_for, render_template
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import os
from werkzeug.utils import secure_filename
from PIL import Image
import requests
from io import BytesIO

model_names = {0: 'Audi A3 hatchback', 1: 'Audi A4L', 2: 'Audi A6L', 3: 'Audi Q3', 4: 'Audi Q5', 5: 'Audi A3 sedan', 6: 'Audi A1', 7: 'Audi A4 estate', 8: 'Audi A5 convertible', 9: 'Audi A5 coupe', 10: 'Audi A5 hatchback', 11: 'Audi A7', 12: 'Audi A8L', 13: 'Audi Q7', 14: 'Audi S5 convertible', 15: 'Audi S8', 16: 'Audi TTS coupe', 17: 'Audi TT coupe', 18: 'BWM 3 Series', 19: 'BWM X1', 20: 'BWM 5 Series', 21: 'BWM M5', 22: 'BWM 2 Series', 23: 'BWM 3 Series GT', 24: 'BWM 3 Series convertible', 25: 'BWM 3 Series estate', 26: 'BWM 3 Series coupe', 27: 'BWM 4 Series convertible', 28: 'BWM 5 Series GT', 29: 'BWM 6 Series', 30: 'BWM 7 Series', 31: 'BWM X3', 32: 'BWM X4', 33: 'BWM X5', 34: 'BWM X6', 35: 'BWM 1 Series hatchback', 36: 'Benz C Class', 37: 'Benz GLK Class', 38: 'Benz E Class', 39: 'Benz C Class AMG', 40: 'Benz G Class AMG', 41: 'Benz A Class', 42: 'Benz C Class estate', 43: 'Benz E Class convertible', 44: 'Benz E Class couple', 45: 'Benz GL Class', 46: 'Benz R Class', 47: 'Benz SLK Class', 48: 'Benz S Class', 49: 'encore', 50: 'Buick GL8 Luxury Business', 51: 'Buick GL8 Business', 52: 'Regal', 53: 'Regal GS', 54: 'Lacrosse', 55: 'Exclle', 56: 'EXCELLE GT', 57: 'EXCELLE XT', 58: 'Enclave', 59: 'Crosstour', 60: 'Crider', 61: 'Accord', 62: 'Jade', 63: 'Spirior', 64: 'Civic', 65: 'Honda CR-V', 66: 'Peugeot 2008', 67: 'Peugeot 207 hatchback', 68: 'Peugeot 207 sedan', 69: 'Peugeot 3008', 70: 'Peugeot 301', 71: 'Peugeot 307 hatchback', 72: 'Peugeot 307 sedan', 73: 'Peugeot 308', 74: 'Peugeot 408', 75: 'Peugeot 508', 76: 'Peugeot 207CC', 77: 'Peugeot 308SW', 78: 'Peugeot 4008', 79: 'Peugeot RCZ', 80: 'Peugeot 308CC', 81: 'BYD F0', 82: 'BYD F3R', 83: 'BYD F6', 84: 'BYD G3', 85: 'BYD L3', 86: 'BYD M6', 87: 'BYD S6', 88: 'Panamera', 89: 'Porsche 911', 90: 'Canyenne', 91: 'Cayman', 92: 'BAW E Series sedan ', 93: 'BAW E Series hatchback', 94: 'Baojun 610', 95: 'Baojun 630', 96: 'Lechi', 97: 'Besturn B50', 98: 'Besturn B90', 99: 'Besturn X80', 100: 'Besturn B70', 101: 'Great Wall C50', 102: 'Great Wall M2', 103: 'Great Wall M4', 104: 'Great Wall V80', 105: 'Wingle 5', 106: 'Xuanli', 107: 'Xuanli CROSS', 108: 'Benben', 109: 'Benben MINI', 110: 'Changan CS35', 111: 'Changan CX20', 112: 'Yidong', 113: 'Yuexiang V3', 114: 'Yuexiang V5', 115: 'Yuexiang hatchback', 116: 'Yuexiang sedan', 117: 'Zhishang XT', 118: 'Ruiping', 119: 'Zhixiang', 120: 'Benben LOVE', 121: 'Cross Polo', 122: 'Polo hatchback', 123: 'Polo sedan', 124: 'Cross Lavida', 125: 'Gran Lavida', 126: 'Lavide', 127: 'Passat', 128: 'Passat Lingyu', 129: 'Santana', 130: 'Touran', 131: 'Tiguan', 132: 'Volkswagen Eos', 133: 'Golf convertible ', 134: 'Golf estate', 135: 'Phaeton', 136: 'Beetle', 137: 'Multivan', 138: 'Magotan estate', 139: 'Scirocco', 140: 'Touareg', 141: 'Sharan', 142: 'Variant', 143: 'Tiguan abroad version', 144: 'Bora', 145: 'Golf', 146: 'Golf GTI', 147: 'Jetta', 148: 'Magotan', 149: 'Sagitar', 150: 'Volkswagen CC', 151: 'DS 5', 152: 'DS 5LS', 153: 'DS 3', 154: 'DS 4', 155: 'Lingzhi', 156: 'Jingyi', 157: 'Fengshen CROSS', 158: 'Fengshen H30', 159: 'Fengshen S30', 160: 'Fengshen A60', 161: 'Shuaike', 162: 'Fiesta sedan', 163: 'Classic Focus hatchback', 164: 'Classic Focus sedan', 165: 'S-MAX', 166: 'New Focus hatchback', 167: 'New Focus sedan', 168: 'Ecosport', 169: 'Mendeo Zhisheng', 170: 'Fiesta hatchback', 171: 'Focus ST', 172: 'Mustang', 173: 'Feixiang', 174: 'Zhiyue', 175: 'Bravo', 176: 'FIAT 500', 177: 'Qiteng M70', 178: 'Chuanqi GS5', 179: 'Haval H3', 180: 'Wrangler', 181: 'Compass', 182: 'Patriot', 183: 'Gaguar XJ', 184: 'Gaguar XF', 185: 'Seville SLS', 186: 'Cadillac XTS', 187: 'Cadillac CTS', 188: 'Cadillac ATS-L', 189: 'Cadillac SRX', 190: 'Wind Lang', 191: 'Koleos', 192: 'Latitude', 193: 'Scenic', 194: 'Landwind X8', 195: 'Landwind X5', 196: 'MINI', 197: 'MINI CLUBMAN', 198: 'MINI COUNTRYMAN', 199: 'MINI PACEMAN', 200: 'Teana', 201: 'New Sylphy', 202: 'Sylphy', 203: 'Sunshine', 204: 'Qashqai', 205: 'Livina', 206: 'Tiida', 207: 'Ma Chi', 208: 'Nissan NV200', 209: 'Nissan GT-R', 210: 'Fabia', 211: 'Octavia', 212: 'Superb', 213: 'Yeti', 214: 'Haorui', 215: 'Rapid', 216: 'Superb Derivative', 217: 'Kyron', 218: 'WeaLink X5', 219: 'i30', 220: 'ix35', 221: 'Avante', 222: 'Sonata', 223: 'Mistra', 224: 'Moinca', 225: 'Santafe', 226: 'Rena', 227: 'Verna', 228: 'Sonata 8', 229: 'Elantra Yuedong', 230: 'Rohens', 231: 'Equus', 232: 'Veloster', 233: 'Infiniti Q50', 234: 'Infiniti Q70L', 235: 'Infiniti QX50', 236: 'Infiniti QX70', 237: 'Infiniti QX80', 238: 'Infiniti G Class', 239: 'Zotye 5008', 240: 'Weizhi', 241: 'Weizhi V2', 242: 'Weizhi V5', 243: 'Xiali N5', 244: 'Chrysler 300C', 245: 'Discovery', 246: 'Range Rover', 247: 'Evoque', 248: 'Range Rover Sport', 249: 'Gallardo', 250: 'Forte', 251: 'KIA K2 sedan', 252: 'KIA K3', 253: 'KIA K3S', 254: 'KIA K5', 255: 'Sportage', 256: 'Soul', 257: 'Sportage R', 258: 'Borrego', 259: 'Shuma', 260: 'Sorento', 261: 'Kaizun', 262: 'Roewe 350', 263: 'Roewe 750', 264: 'Roewe 550', 265: 'Impreza hatchback', 266: 'Impreza sedan', 267: 'MAXUS V80xs', 268: 'c-Elysee sedan', 269: 'Elysee', 270: 'Quatre hatchback', 271: 'Quatre sedan', 272: 'Citroen C2', 273: 'Citroen C4L', 274: 'Citroen C5', 275: 'Yongyuan A380', 276: 'Toyota RAV4', 277: 'Crown', 278: 'Lcruiser', 279: 'Prado', 280: 'Prius', 281: 'Reiz', 282: 'Vios', 283: 'Huaguan', 284: 'Venza', 285: 'Alphard', 286: 'Toyota 86', 287: 'Camry', 288: 'Camry hybrid', 289: 'Yaris', 290: 'EZ', 291: 'Qoros 3', 292: 'Saboo GX5', 293: 'Haima M3', 294: 'Haima S5', 295: 'Haima S7', 296: 'Haimaqishi', 297: 'Haydo', 298: 'Premacy', 299: 'Qiubite', 300: 'Family M5', 301: 'Lusheng E70', 302: 'Geely SC7', 303: 'King Kong sedan', 304: 'Classic Imperial hatchback', 305: 'Classic Imperial sedan', 306: 'Ziyoujian', 307: 'Geely EC8', 308: 'Binyue', 309: 'Heyue RS', 310: 'Ruifeng M5', 311: 'Ruifeng S5', 312: 'Ruiying', 313: 'Tongyue', 314: 'Heyue', 315: 'Dahaishi', 316: 'Lexus CT', 317: 'Lexus ES hybrid', 318: 'Lexus GS', 319: 'Lexus GS hybrid', 320: 'Lexus GX', 321: 'Lexus IS', 322: 'Lexus IS convertible ', 323: 'Lexus LS hybrid', 324: 'Lexus RX', 325: 'Lexus RX hybrid', 326: 'Lexus ES', 327: 'Lifan 520', 328: 'Lifan 720', 329: 'Lifan 320', 330: 'Jingyue', 331: 'Atenza', 332: 'Mazda CX7', 333: 'Ruiyi', 334: 'Ruiyi coupe', 335: 'Mazda 6', 336: 'Mazda 3 abroad version', 337: 'Mazda 5', 338: 'Mazda 2', 339: 'Mazda 2 sedan', 340: 'Mazda 3', 341: 'Mazda 3 Xingcheng hatchback', 342: 'Mazda 3 Xingcheng sedan', 343: 'Mazda CX-5', 344: 'Axela sedan', 345: 'Eastar Cross', 346: 'Fulwin 2 hatchback', 347: 'Fulwin 2 sedan', 348: 'Chrey A3 hatchback', 349: 'Chrey A3 sedan', 350: 'Chrey E5', 351: 'Chrey QQ', 352: 'Chrey QQ3', 353: 'Chrey X1', 354: 'Cowin 2', 355: 'Cowin 3', 356: 'Tiggo', 357: 'Tiggo 5', 358: 'Arrizo 7', 359: 'Ruiqi G5', 360: 'smart fortwo', 361: 'Volvo C30', 362: 'Volvo S60', 363: 'Volvo V40', 364: 'Volvo V40 CrossCountry', 365: 'Volvo V60', 366: 'Volvo XC60', 367: 'Volvo XC90 abroad version', 368: 'Volvo C70', 369: 'Volvo S40', 370: 'Volvo S80L', 371: 'Volvo S60L', 372: 'Youyou', 373: 'Alto', 374: 'Cultus', 375: 'Tianyu SX4 hatchback', 376: 'Tianyu SX4 sedan', 377: 'Tianyushangyue', 378: 'Yuyan', 379: 'Kazishi', 380: 'Bei Douxing', 381: 'Linian S1', 382: 'MG3 SW', 383: 'MG5', 384: 'MG6 sedan', 385: 'MG6 hatchback', 386: 'MG7', 387: 'MG3', 388: 'Antara', 389: 'Zafira', 390: 'GTC hatchback', 391: 'Venucia R50', 392: 'Venucia D50', 393: 'Pajero', 394: 'Grandis', 395: 'Evo', 396: 'ASX abroad version', 397: 'Outlander abroad version', 398: 'Mitsubishi Fortis', 399: 'Mitsubishi Lancer EX', 400: 'SAAB D70', 401: 'Wulinghongguang', 402: 'Wulingzhiguang', 403: 'Wulingrongguang', 404: 'AVEO hatchback', 405: 'Trax', 406: 'Epica', 407: 'Cruze sedan', 408: 'Cruze hatchback', 409: 'Captiva', 410: 'Aveo', 411: 'Lova', 412: 'Malibu', 413: 'Sail hatchback', 414: 'Sail sedan', 415: 'Aveo sedan', 416: 'Camaro', 417: 'Zhonghua H330', 418: 'Zhonghua H530', 419: 'Zhonghua V5', 420: 'Zhonghua Junjie', 421: 'Zhonghua Junjie CROSS', 422: 'Zhonghua Junjie FRV', 423: 'Zhonghua Junjie FSV', 424: 'Zhonghua Junjie Wagon', 425: 'Zhonghua Zunchi', 426: 'Zhonghua H230', 427: 'Brabus S Class', 428: 'Grandtiger G3', 429: 'Grandtiger TUV', 430: 'Qijian A9'}

transform = transforms.Compose([
    transforms.Resize((256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Grayscale(3),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
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
new_net.fc = nn.Linear(num_ftrs, 431)

state = torch.load('bestModel',map_location=torch.device('cpu'))
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

                name = []
                prob = []
                for i in range(len(top[0])):
                    index = top[0][i]
                    name.append(f'Model: {model_names.get(index)}')
                    prob.append(f'Percentage: {p[index]*100:.2f}%')
            return render_template("index.html", img_url = img_url, m1 = name[0],m2 = name[1],m3 = name[2],m4 = name[3],m5 = name[4],p1 = prob[0],p2 = prob[1],p3 = prob[2],p4 = prob[3],p5 = prob[4])

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            img = Image.open(file)
            # flash('Image successfully uploaded and displayed below')

            show_rank_num = 5
            img = transform(img)
            with torch.no_grad():
                new_net.eval()
                all = new_net(img.unsqueeze(0))
                p = torch.nn.functional.softmax(all[0], dim=0)
                _, top = torch.topk(all,show_rank_num)
                top = top.tolist()

                name = []
                prob = []
                for i in range(len(top[0])):
                    index = top[0][i]
                    name.append(f'Model: {model_names.get(index)}')
                    prob.append(f'Percentage: {p[index]*100:.2f}%')
            return render_template("index.html", m1 = name[0],m2 = name[1],m3 = name[2],m4 = name[3],m5 = name[4],p1 = prob[0],p2 = prob[1],p3 = prob[2],p4 = prob[3],p5 = prob[4])
        else:
            flash('invalid image')
            return redirect(request.url)

# @app.route('/display/<filename>')
# def display_image(filename):
#     return redirect(url_for('static', filename='uploads/' + filename),code = 301)

if __name__ == "__main__":
    app.run(debug=False)