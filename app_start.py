from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from PIL import Image, ImageDraw, ImageFont
from datetime import date
from os import path
import time
app = Flask(__name__)
app.debug = False

# Routes
# @app.route('/', methods=['GET'])
# def root():
#     return app.send_static_file('base')

@app.route('/<int:year>/<int:month>/<int:day>', methods=['GET'])
def serve_image(year, month, day):
    if not (1990 <= year <= 2021 and 1<= month <= 12 and 1 <= day <= 31):
        return app.send_static_file('base.jpg')
    filename = f'{year:04d}-{month:02d}-{day:02d}.jpg'
    dday = date(year, month, day)
    delta = dday - date.today()
    if path.exists(filename) and path.getmtime(filename) - time.localtime() < 1000*10:
        return app.send_static_file(filename)
    target_img = Image.new("RGB", (260, 50), color = (255, 255, 255))        
    
    draw = ImageDraw.Draw(target_img)
    msg = f'전역까지 {delta.days}일 남았습니다'
    fnt = ImageFont.truetype("fonts/malgun.ttf", 20, encoding="UTF-8")
    draw.text((10, 10), msg, font=fnt, fill=(0, 0, 0), align='center')
    target_img.save('static/' + filename)
    return app.send_static_file(filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, threaded=True)

