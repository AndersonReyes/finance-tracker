FROM zauberzeug/nicegui:latest

COPY requirements.txt /requirements.txt

RUN uv pip install -r /requirements.txt
