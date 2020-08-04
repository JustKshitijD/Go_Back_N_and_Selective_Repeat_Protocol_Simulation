GO-BACK n protocol has 2 files: Client2.py and Server2.py
You can run these , with the appropriate flags as:

python Server2.py -d -p 6666 -n 20 -e 0.3
python Client2.py -d -s 192.168.43.221 -c1 -p 6666 -l 500 -r 100 -n 20 -w 4 -b 30

Run these in this order. Note that in place of 192.168.43.221, put your machine's IP.

Also, as I have coded with python, I have made no makefile. This has being verified with sir.

Here,
 -p: port no =6666
-n: max_packets to be acknowledged before programs terminate
-e: drop probability of packet by receiver
-d: debug mode on
-s: IP address/name of receiver
-p: Port no
-l: packet_length
-r: packet generation rate in no. of packets per second
-w: window size
-b: buffer size

Pls note that instead of fixed length packets, I have used random lengthed packets from a uniform distribution.
I hope this will be appreciated.

Also, I think there is error in the absolute value of my time, as I am considering the clock out time too in the
acknowledgement of packets. So, my answer got is ~0.1 seconds. However, the number of attempts etc can be verified correctly.

I have commented out many things. If you want to take a look at like say, buffer_size at a given moment, or if packets are being added or dropped correctly or not,
you can check these.

To run makefile:
Make a separate folder; I have named it Maek. Inside, there is Receiver.py and its makefile. Run it inside the folder.
Then come back to the main folder, and run the makefile, to run the Sender. Effectvely, Sender sending packets to receiver. 
