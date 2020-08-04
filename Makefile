#HOST=127.0.0.1
#TEST_PATH=./
#@echo "Go to Server2.py and change the variable host there, to the current IP address of machine"
run:	Receiver.py
	python Receiver.py -d -p 6666 -n 50 -e 0.0001
	
