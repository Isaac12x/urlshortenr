from flask import request, redirect, render_template, url_for, jsonify
from hashlib import md5
from main.app.forms import ShortenUrlForm
from main.app.models import Link
from main.app import app, db
# we first take care of the usual suspects


@app.route('/', methods=['POST', 'GET'])
@app.route('/ui', methods=['POST', 'GET'])
def index():
    url = ''
    form = ShortenUrlForm()
    if form.validate_on_submit():
        link = get_or_create(form.url.data)
        url = 'https://urlshortenr.herokuapp.com/' + link
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
        if (request.headers['Content-Type'] == 'application/json' and
                request.get_json()['url']):
            url = request.get_json()['url']
            assert type(url) is str
            test = is_valid_url(url)
            if not test:
                return jsonify({'error': 'Not valid url scheme'}), 500

            link = get_or_create(url)
            url = 'https://urlshortenr.herokuapp.com/' + link
            return jsonify({'shortened_url': url}), 201
        else:
            return jsonify({'error': 'You should send a json request'}), 500
    else:
        return redirect(url_for('/'), code=302)


@app.route('/<id>', methods=['GET'])
def resolve(id):
    if id:
        ext = Link.query.filter_by(target_url=id).first()
        if ext:
            return redirect(ext.original_url, code=301)
        else:
            return jsonify("We couldn't find this url"), 404
    else:
        redirect(url_for('/'), code=302)


def get_or_create(url):
    ext = Link.query.filter_by(original_url=url).first()
    if not ext:
        url = generate_url(url).target_url
    else:
        url = ext.target_url
    return url


def generate_url(url):
    url_path = md5(url.encode()).hexdigest()[:8]
    link = Link(original_url=url, target_url=url_path)
    db.session.add(link)
    db.session.commit()
    return link


def is_valid_url(url):
    # taken from https://github.com/django/django/blob/master/django/core/validators.py#L74
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)
