call .\venv\Scripts\activate.bat
daphne -p 8000 core.asgi:application