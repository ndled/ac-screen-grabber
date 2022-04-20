from random import random
from flask import Flask, send_file, request,render_template
import os
import random

from . import downloader as down
from . import screen_cap as cap

app = Flask(__name__)


def random_image(img_dir = "./static/imgs"):
    """
    Return a random image from the ones in the static/ directory
    """
    img_list = os.listdir(img_dir)
    img_path = os.path.join(img_dir, random.choice(img_list))
    return img_path


@app.route("/", methods=['GET', 'POST'])
def myapp():
    if request.method == 'POST':
        if request.form.get('action1') == 'Random Image':
                image = random_image()
                return render_template('index.html', image=image)
    else:
        image = random_image()
        return render_template('index.html', image=image)


def remove_old(dir = "static/single"):
    for file in os.listdir(f"{dir}"):
        os.remove(down.resolvepath(f"{dir}/{file}"))


def get_single(url):
    remove_old()
    down.single_download(url)
    image = cap.single_cut()
    return image


@app.route("/single", methods=['GET', 'POST'])
def single():
    image = {}
    if request.method == 'POST':
        form_data = request.form
        url = form_data['new_video']
        image = get_single(url)
    return render_template('single.html', image = image)


@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if request.form.get("submit"):
            form_data = request.form
            url = form_data['new_video']
            remove_old(dir = "static/new")
            down.single_download(url, path = "static/new")
            cap.new_cut(path = "static/new")
            image = random_image(img_dir = "./static/new")
            return render_template('new.html', image = image)
        elif request.form["random_image"]:
            image = random_image(img_dir = "./static/new")
            return render_template('new.html', image = image)
    else:
        return render_template('new.html')