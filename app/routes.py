from flask import request, redirect, render_template, url_for, jsonify
from hashlib import md5
from app.forms import ShortenUrlForm
from app.models import Link
from app import app, db
# we first take care of the usual suspects


@app.route('/')
@app.route('/ui')
def index():
    url = ''
    form = ShortenUrlForm()
    if form.validate_on_submit():
        generate_url(form.url)
    if request.method is 'GET':
        if url:
            return render_template('index.html',
                                   title='Url shortener service', form=form,
                                   url=url)
        else:
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
            # check for existence
            assert type(url) is str
            ext = db.session.query(Link).filter(Link.original_url == url).scalar()
            # and then process
            if not ext:
                link = generate_url(url)
                resp = {'shortened_url': link.target_url}
                return jsonify(resp), 201
            else:
                resp = {'shortened_url': ext.target_url}
                return jsonify(resp), 201
    else:
        return redirect(url_for('/ui'), code=302)


def generate_url(url):
    url_path = md5(url.encode()).hexdigest()[:8]
    final_url = 'https://urlshortenr.herokuapp.com/' + url_path
    link = Link(original_url=url, target_url=final_url)
    db.session.add(link)
    db.session.commit()
    return link
