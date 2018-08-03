# URL shortener/shrinker

Shorten your urls like never before :)

## How to run it

First and foremost, please do clone the repo with
`git clone git@github.com:Isaac12x/test-babylonhealth.git && cd test-babylonhealth`

Once you're in there, you should do the following:

`docker build -t urlshortener . && docker run -p 38080:80 urlshortener`

If that doesn't work for you, please use sudo (and later fix your docker installation).

Now you should be good to go. If still you can't start the app because it has some sort of error please do send me an email at ialbetsram@gmail.com with the error trace from your command line (pipe it into a file with `> file.txt`) and your system specs (if you're using linux/UNIX send me the output of `uname -v` and `cat /proc/version` and your docker version `docker -v`).

If you want to run it without docker, you should do the following (assuming you're already in the repo):

`pip install -r requirements.txt`

Set your secret key by running:
`export SECRET_KEY=YOURKEY`

and then run,

`uwsgi --socket 0.0.0.0:8000 --protocol=http -w main`

You should be good to go. You can either post via

`curl --header "Content-Type: application/json"   --request POST   --data '{"url":"https://www.w3.org/History/1989/proposal.html}'   http://0.0.0.0:8000/shorten-url`

Or by going in your browser to http://0.0.0.0:8000 where you will have a UI to do that. Enjoy :)

## Design decisions

I have decided to use flask because of the simplicity of the task and the simplicity to set it up. It was the best tool for the job with the least technical overhead (even though I did not use Flask seriously for the last 11 months or so).


### Notes

Since I wanted this to be more challenging I used flask (with its limitations - Werkzeug dev is not optimized to serve in productions) and then containerized the app and added a nginx to handle incoming traffic (your 1000 req/s) and then uWSGI to interface with nginx as the request server and pass that into the app layer which is done in Flask.

A good way to optimize this app would be to use a production database. To keep things `simple` enough I've decided to use SQLite but of course if we were to put this in production, this should be a fastDB.

Also, I have created a routes and an app instead of a single file app because if it needs to be scalable, means is working and that means we might be interested in extending the functionality. Doing it now, is trivial. Doing it at a later date can be cumbersome (doesn't need to be but can be).

This is going to be hosted on heroku which gives you very long urls, if it was to be used I would buy a 3-4 letter domain name and use that as the base url.
