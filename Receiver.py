import socket
import sys
import time
import numpy
import math
import threading
from threading import Thread

host='192.168.43.221'
#host='10.42.184.1'
count_no_of_packets_ack=0
count_prev_no_of_pack_ack=0
window_size=0
j=-1
init_j=-1
bad_flag=0
#bad_flag2=0
addr=0
lock=threading.Lock()
thread_kill=0
got_zero_flag=0

thread4=Thread(target="deflection",args=())
arg_list=sys.argv

d_val=0
for i in range(1,len(arg_list)):
    x=arg_list[i];
    if(x=="-d"):
        d_val=1
    elif(x=="-p"):  #6666
        port_no=int(arg_list[i+1])
        i+=1
    elif(x=="-n"):   #400
        max_packets=int(arg_list[i+1])
        i+=1
    elif (x=='-e'):  # 0.01
        packet_drop_prob= float(arg_list[i+1])
        i+=1

port=int(port_no)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host,port))
                # get n
d=s.recvfrom(1024)
    #window_size=conn.recv(1024)
window_size=d[0]
addr=d[1]
#P:----print("window_size ",window_size.decode())

sequence_number=(int(window_size)+1)             # get sequence number length and sequence_number
sequence_number_length=math.log(sequence_number,2)
if(sequence_number_length-math.floor(sequence_number_length)==0):
    sequence_number_length+=1
else:
    sequence_number_length=math.ceil(sequence_number_length)
sequence_number_length=int(sequence_number_length)

expected_sequence_number=0


def func_expected_seq_number():
    global j
    j+=1
    #print("original j in func_expected_seq_number: ",j)
    curr_j=bin(j%(sequence_number))
    curr_j=curr_j[2:]    # the binary no. got by bin(3), i.e, 0b011, is a string

    str_sequence_no=curr_j
    for i in range(0,sequence_number_length-len(curr_j)):
            str_sequence_no='0'+str_sequence_no
    expected_sequence_number=str_sequence_no
    #print("expected_sequence_number",expected_sequence_number)
    return(expected_sequence_number)

o=0
change=0
while True:
        #print("\n\nAt top of whilee")
        cc=0
        val=0
        #change=j-init_j               down it is there
        init_j=j
        bad_flag=0

        if(o!=0):
            r=s.recvfrom(1024)    # this r will be 0 or 1
            if(r[0].decode()=="0"):
                #j=j-int(window_size)
                j=j-change
                #count_no_of_packets_ack=count_no_of_packets_ack-int(window_size)
                count_no_of_packets_ack=count_no_of_packets_ack-change
                #print("\nYAAAA, I HAD TO DECREMENT J from ",init_j," to :",j)
                init_j=j
                got_zero_flag=1
        while(cc<int(window_size)):
            d=s.recvfrom(1024)
            data=d[0]
            #print("\nAMMMMMM getting data as: ",data.decode())
            if not data:
                break
            x=numpy.random.rand()
            if(x>packet_drop_prob):
                if(d_val==1):
                    print("For packet ",data.decode(),",  packet dropped: false")
                ss=data.decode()
                extracted_seq_no_string=ss[0:sequence_number_length]
                #print("\nextracted_seq_no_string", extracted_seq_no_string)
                if(extracted_seq_no_string==func_expected_seq_number()):
                    val=j-init_j
                    #print("I better ack this!")
                    count_no_of_packets_ack+=1
                    #print("\nCOUNT_ACK INCREMENTED TO :",count_no_of_packets_ack)

                    #print("\nacks val: ",val)
                    #if not got_zero_flag:
                    s.sendto(str(val).encode(),addr)

                    if(count_no_of_packets_ack==int(max_packets)):      # reached max no of packets
                        print("\n\nI reached count_no_of_packets_ack: ",count_no_of_packets_ack,"=max_packets: ",max_packets)
                        #s.shutdown(SHUT_RDWR)
                        s.close()
                        sys.exit()

                else:
                    j=j-1
                    #j=init_j
                    bad_flag=1
                    #print("\ndidnt match val: ",val)
                    #if not got_zero_flag:
                    s.sendto(str(val).encode(),addr)
            else:
                    bad_flag=1
                    #print("\ndroppedd val: ",val)
                    #if not got_zero_flag:
                    s.sendto(str(val).encode(),addr)

            cc+=1
        o+=1
        got_zero_flag=0
        change=j-init_j
        if(bad_flag==0):
            init_j=j
        else:
            j=init_j+val
