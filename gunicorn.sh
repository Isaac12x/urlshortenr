#!/usr/bin/env bash

gunicorn -w 8 --bind 80 app:app
