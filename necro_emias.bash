while true; do
	python3 main_emias_checker.py >> log
	killall firefox
	sleep 10
done
