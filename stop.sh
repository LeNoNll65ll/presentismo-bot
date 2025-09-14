#!/bin/bash
cd ~/chatbot/presentismo
if [ -f bot.pid ]; then
  kill $(cat bot.pid) && rm bot.pid
fi
