#!/bin/bash
source ./venv/bin/activate
daphne -p 8000 core.asgi:application