PID_FILE=/tmp/httplz.pid
kill $(cat $PID_FILE)
sleep 0.1

nohup httplz -l . &
sleep 0.1
echo $! > $PID_FILE