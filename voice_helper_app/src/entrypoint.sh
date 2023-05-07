#!/bin/bash

if [ "$DEBUG" = "true" ]; then
  python main.py
else
  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
fi