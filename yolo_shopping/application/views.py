from flask import render_template, Response, stream_with_context
from flask_bootstrap import Bootstrap
from application import app
from application.lib import ObjDetectCamera
from urllib.parse import quote


bootstrap = Bootstrap(app)
cam = None


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream')
def stream():
    global cam
    cam = ObjDetectCamera()
    return Response(stream_with_context(stream_template('index.html', camera=cam())))


@app.route('/video_capture')
def video_capture():
    return Response(cam.frame_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/move_to_amazon/<keyword>')
def move_to_amazon(keyword):
    base_url = "http://www.amazon.co.jp/gp/search/?__mk_ja_JP=%83J%83%5E%83J%83i&field-keywords="
    return base_url + quote(keyword)
