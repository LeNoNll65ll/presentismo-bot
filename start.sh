#!/bin/bash
cd ~/chatbot/presentismo
./venv/bin/python main.py >> bot.log 2>&1 &
echo $! > bot.pid
