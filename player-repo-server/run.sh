#!/bin/bash

gunicorn -w 4 -b localhost:8888 app:app 
