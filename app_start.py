from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime
from os import path, environ
import sys
import time

from werkzeug.utils import invalidate_cached_property
app = Flask(__name__)
app.debug = False
port = 8080

# Routes
# @app.route('/', methods=['GET'])
# def root():
#     return app.send_static_file('base')

@app.route('/<int:year>/<int:month>/<int:day>', methods=['GET'])
def serve_image(year, month, day):
    invalid_date = not (1990 <= year <= 2021 and 1 <= month <= 12 and 1 <= day <= 31)
    try:
        dday = date(year, month, day)
    except:
        invalid_date = True
    
    if invalid_date:
        return app.send_static_file('base.jpg')
    
    filename = f'{year:04d}-{month:02d}-{day:02d}.jpg'
    delta = dday - date.today()
    days_left = delta.days
    
    if path.exists(filename):
        cur_time = datetime.today()
        last_modified_time = datetime.fromtimestamp(path.getmtime('static/'+filename))
        if cur_time.day == last_modified_time.day:
            return app.send_static_file(filename)

    target_img = Image.new("RGB", (270, 40), color = (255, 255, 255))    
    draw = ImageDraw.Draw(target_img)
    msg = ''
    
    if days_left > 0:
        msg = f'전역까지 {days_left}일 남았습니다.'
    elif days_left <= 0:
        msg = f'{year:04d}/{month:02d}/{day:02d}부로 전역했습니다!'
    
    fnt = ImageFont.truetype("fonts/강한육군 Medium.ttf", 20, encoding="UTF-8")
    draw.text((10, 10), msg, font=fnt, fill=(0, 0, 0), align='center')
    target_img.save('static/' + filename)
    return app.send_static_file(filename)

if __name__ == "__main__":
    try:
        port = int(environ['PORT'])
    except:
        pass
    app.run(host='0.0.0.0', port=port, threaded=True)