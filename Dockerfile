FROM gorialis/discord.py:3.9-buster-minimal

WORKDIR /app

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]