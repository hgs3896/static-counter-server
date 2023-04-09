from flask import Flask, Response, abort
from werkzeug.serving import WSGIRequestHandler
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date, timedelta, timezone, time
from functools import wraps
from os import path, environ
from hashlib import md5

app = Flask(__name__)
app.debug = False
port = 8080
korean_tz = timezone(timedelta(hours=9))

def docache():
    """ Flask decorator that allow to set Expire and Cache headers. """
    def fwrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            r: Response = f(*args, **kwargs)
            next_day = datetime.combine(
                (datetime.now(korean_tz) + timedelta(days=1)).date(), time(), tzinfo=korean_tz)
            r.cache_control.no_cache = None
            r.cache_control.must_revalidate = True
            r.cache_control.public = True
            # r.cache_control.max_age = (next_day - datetime.utcnow()).seconds
            last_modified = r.last_modified.strftime(
                "%a, %d %b %Y %H:%M:%S GMT")
            r.set_etag(md5(last_modified.encode('utf-8')).hexdigest())
            r.expires = next_day.astimezone(tz=timezone.utc)
            return r
        return wrapped_f
    return fwrap


@app.route('/<int:year>/<int:month>/<int:day>', methods=['GET'])
@docache()
def serve_image(year, month, day) -> Response:
    validity = 1990 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31

    dday = datetime.now()
    try:
        dday = date(year, month, day)
    except ValueError as e:
        validity = False

    if not validity:
        abort(404)

    filename = f'{year:04d}-{month:02d}-{day:02d}.jpg'
    delta = dday - date.today()
    days_left = delta.days

    # 이미 존재하는 파일은 캐싱 처리
    if path.exists('static/' + filename):
        cur_time = datetime.today()
        last_modified_time = datetime.fromtimestamp(
            path.getmtime('static/'+filename))
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

    target_img = Image.new("RGB", (w + 20, h + 20), color=(255, 255, 255))
    draw = ImageDraw.Draw(target_img)
    img_msg = draw.text((10, 10), msg, font=fnt,
                        fill=(0, 0, 0), align='center')
    target_img.save('static/' + filename)


if __name__ == "__main__":
    try:
        port = int(environ['PORT'])
    except:
        pass
    app.run(host='0.0.0.0', port=port, threaded=True, ssl_context='adhoc')
