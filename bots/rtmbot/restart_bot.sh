pkill -f "rtmbot"
nohup rtmbot >> ./log/rtmbot.log 2>&1 &

ps ax | grep rtmbot | grep -v "grep"
