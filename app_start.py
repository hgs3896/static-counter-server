from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date, timedelta
from functools import wraps
from os import path, environ

app = Flask(__name__)
app.debug = False
port = 8080

def docache(hours=24):
    """ Flask decorator that allow to set Expire and Cache headers. """
    def fwrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            r = f(*args, **kwargs)            
            next_day = datetime.fromisoformat(datetime.utcnow().strftime("%Y-%m-%d")) + timedelta(hours=hours+9)            
            r.headers.add('Expires', next_day.strftime("%a, %d %b %Y %H:%M:%S GMT"))
            r.headers.add('Cache-Control', 'public,max-age=%d' % int(60 * 60 * hours))
            return r
        return wrapped_f
    return fwrap

@app.route('/<int:year>/<int:month>/<int:day>', methods=['GET'])
@docache()
def serve_image(year, month, day) -> Response:
    validity = 1990 <= year <= 2021 and 1 <= month <= 12 and 1 <= day <= 31
    
    dday = datetime.now()
    try:
        dday = date(year, month, day)
    except ValueError as e:
        validity = False
    
    if not validity:
        return app.send_static_file('base.jpg')
    
    filename = f'{year:04d}-{month:02d}-{day:02d}.jpg'
    delta = dday - date.today()
    days_left = delta.days
    
    if path.exists(filename):
        cur_time = datetime.today()
        last_modified_time = datetime.fromtimestamp(path.getmtime('static/'+filename))
        if cur_time.day == last_modified_time.day:
            return app.send_static_file(filename)

    msg = ''
    if days_left > 0:
        msg = f'전역까지 {days_left}일 남았습니다.'
    elif days_left <= 0:
        msg = f'{year:04d}/{month:02d}/{day:02d}부로 전역했습니다!'

    make_static_image(filename, msg)    
    return app.send_static_file(filename)

def make_static_image(filename, msg):    
    fnt = ImageFont.truetype("fonts/강한육군 Medium.ttf", 20, encoding="UTF-8")
    w, h = fnt.getsize(msg)

    target_img = Image.new("RGB", (w + 20, h + 20), color = (255, 255, 255))
    draw = ImageDraw.Draw(target_img)
    img_msg = draw.text((10, 10), msg, font=fnt, fill=(0, 0, 0), align='center')    
    target_img.save('static/' + filename)

if __name__ == "__main__":
    try:
        port = int(environ['PORT'])
    except:
        pass
    app.run(host='0.0.0.0', port=port, threaded=True)