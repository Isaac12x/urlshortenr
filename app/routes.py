from flask import request, redirect, render_template, url_for, jsonify
from hashlib import md5
from app.forms import ShortenUrlForm
from app.models import Link
from app import app, db
# we first take care of the usual suspects


@app.route('/', methods=['POST', 'GET'])
@app.route('/ui', methods=['POST', 'GET'])
def index():
    url = ''
    form = ShortenUrlForm()
    if form.validate_on_submit():
        url = get_or_create(form.url.data)
        return render_template('index.html',
                               title='Url shortener service', form=form,
                               url=url)

    if request.method == 'GET':
        return render_template('index.html',
                               title='Url shortener service', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/shorten-url', methods=['POST', 'GET'])
def shorten_url():
    if request.method == 'POST':
        if request.get_json()['url']:
            url = request.get_json()['url']
            assert type(url) is str
            link = get_or_create(url)
            return jsonify({'shortened_url': link}), 201
    else:
        return redirect(url_for('/'), code=302)


@app.route('/<id>')
def resolve(id):
    url = 'https://urlshortenr.herokuapp.com/' + id
    ext = db.session.query(Link).filter(Link.target_url == url).scalar()
    redirect(ext.original_url, code=301)


def get_or_create(url):
    ext = db.session.query(Link).filter(Link.original_url == url).scalar()
    if not ext:
        url = generate_url(url).target_url
    else:
        url = ext.target_url
    return url


def generate_url(url):
    url_path = md5(url.encode()).hexdigest()[:8]
    final_url = 'https://urlshortenr.herokuapp.com/' + url_path
    link = Link(original_url=url, target_url=final_url)
    db.session.add(link)
    db.session.commit()
    return link
