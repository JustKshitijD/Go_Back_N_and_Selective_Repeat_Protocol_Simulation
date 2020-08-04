#If a timer expires, retransmit all packets from the first unacknowledged packet.
#My cumulative ack is equal to window size. So, either all packets ack and window moves forward or some packet drops and every packet has to be retransmitted.

import sys   #for command line inputs
from threading import Thread
import random, math
import time
import socket
import sys
from collections import deque
#import matplotlib.pyplot as plt

arg_list=sys.argv
retranmit_list=list()

d_val=0
for i in range(1,len(arg_list)):
    x=arg_list[i];
    if(x=="-d"):
        d_val=1
    elif(x=="-s"):
        name_or_ip=arg_list[i+1]
        i=i+1
    elif(x=="-p"):
        port_no=arg_list[i+1]
        i=i+1
    elif(x=="-l"):
        max_packet_length=arg_list[i+1]
        i=i+1
    elif(x=="-r"):
        packet_gen_rate=arg_list[i+1]
        i=i+1
    elif(x=="-n"):
        max_packets=arg_list[i+1]
        i=i+1
    elif(x=="-w"):
        window_size=arg_list[i+1]
        i=i+1
    elif(x=="-b"):
        max_buffer_size=arg_list[i+1]
        i=i+1

print("-d ",d_val)
print("-s ",name_or_ip) #receiver's name/IP
print("-p ",port_no) # receiver's port number  12345
print("-l ",max_packet_length)  # 512
print("-r ",packet_gen_rate)  #10
print("-n ",max_packets)  # Sender terminates after max_packets have been acknowledged  400
print("-w ",window_size)  #3
print("-b ",max_buffer_size)  #max no of packets in buffer 10

#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
port=int(port_no)
#s.connect((name_or_ip,port))
#s.sendall(str(window_size).encode())

s.sendto(str(window_size).encode(),(name_or_ip,port))



#MY VARIABLES
buffer=list()
#lock=threading.Lock()
buffer_flag=0
curr_buffer_size=0
sender_timer=0.0
time_start=0
time_end=0
ack_return_val=-1
time_ack_start=0
time_ack_end=0

current_window_10_timer_flag=0
ack_count=0
no_packet_just_sent=0
time_return_avg=0.0
dict={}   # Has return time for every single ACK window. Cleared after every window sent.
no_of_attempt_dict={}
no_of_packets_totally_sent=0
alarm_ring_flag=0

iteration_no=0
iteration_list=list()
#d=s.recvfrom(1024)
#data=b''
#my_packet_string=""
sequence_number=(int(window_size)+1)
sequence_number_length=math.log(sequence_number,2)
if(sequence_number_length-math.floor(sequence_number_length)==0):
    sequence_number_length+=1
else:
    sequence_number_length=math.ceil(sequence_number_length)

sequence_number_length=int(sequence_number_length)
def packet_gen():
    global packet_gen_rate
    global max_packet_length
    #print("packet_gen_rate: ",packet_gen_rate)
    global max_buffer_size
    global buffer
    global sequence_number_length
    global curr_buffer_size
    #for i in range(int(max_buffer_size)):
    #    buffer.append('-1')
    j=-1
    #no_packets_gen_in_this_sec=0

    m=0
    time_for_1_packet=1/int(packet_gen_rate) # in SECONDS
    #P:- print("time_for_1_packet ",time_for_1_packet)
    abs_time_start=time.time()
    no_packets_gen_in_this_sec=0

    while(1):
        if(curr_buffer_size>=int(max_buffer_size)):
            continue
        #print("sequence_number_length : ",sequence_number_length)
        #P:-abs_time_end=time.time()
        #P:-if(abs_time_end-abs_time_start>=1):
        # P:-   print("\n no_packets_gen_in_this_sec",no_packets_gen_in_this_sec)
        # P:-   abs_time_start=time.time()
        #P:-    no_packets_gen_in_this_sec=0

        time_start=time.time()
        #P:-print("\n\ntime_start ",time_start)  # for every new packet, time_start=0

        x=math.floor(random.uniform(256,int(max_packet_length)))  # new packet's length
        #P:-if(x>sequence_number_length and curr_buffer_size<int(max_buffer_size)):
        if(x>sequence_number_length and curr_buffer_size<int(max_buffer_size)):
            no_packets_gen_in_this_sec+=1
            j+=1
            curr_j=bin(j%(sequence_number))
            curr_j=curr_j[2:]    # the binary no. got by bin(3), i.e, 0b011, is a string

            str_sequence_no=curr_j
            for i in range(0,sequence_number_length-len(curr_j)):
                    str_sequence_no='0'+str_sequence_no
            #P:-print(str_sequence_no)
            m+=1

            str=str_sequence_no
            for i in range(sequence_number_length,x):
                str=str+random.choice(['0','1'])

            #print("For packet length ",x,", I got packet as: ",str)
            #P:-buffer[curr_buffer_size-ack_count]=str
            while(buffer_flag==1):
                continue
            buffer.append(str)
            #P:----P:----print("Added ",str," to buffer")
            curr_buffer_size+=1

            time_end=time.time()
            #P:-print("time_end ",time_end)
            while(time_end-time_start<=time_for_1_packet):    # time_start and time_end sud be for every packet
                #print("hullo, time_end-time_start", time_end-time_start)
                time_end=time.time()
            #print("final time_end-time_start ",time_end-time_start)

        #P:-elif curr_buffer_size>int(max_buffer_size):
            #P:-print("eventual time_start ",time_start)
            #P:-print("eventual time end ", time_end)
            #P:-continue

#def recvv():
    #data=s.recv(1024)
    #ack_return_val=data
def get():
    global time_ack_start
    global sender_timer
    global alarm_ring_flag
    while(time.time()-time_ack_start<sender_timer):
        #print("In thread:time.time()-time_ack_start: ",time.time()-time_ack_start)
        continue
    alarm_ring_flag=1


def ack():      #Time out timer at the sender side should be greater than Acknowledgement timer.
    #import matplotlib.pyplot as plt
    global buffer
    global curr_buffer_size
    global ack_count
    global no_of_attempt_dict
    global dict
    global time_return_avg
    global no_of_packets_totally_sent
    global no_packet_just_sent
    global sender_timer
    global alarm_ring_flag
    global time_ack_start
    global f
    global iteration_no
    global iteration_list
    global retranmit_list


    #print("At start of ack, sender_timer: ",sender_timer)
    #P:----print("At start of ack, total count of sent is: ",no_of_packets_totally_sent+no_packet_just_sent)
    #P:----print("At start of ack, time_ack_start: ",time_ack_start)

    data=b'0'
    #P:----print("IN ack()")
    #time_ack_end=time.time()
                 ###############FILLLLL

    #P:----print("previous no_of_packets_totally_sent",no_of_packets_totally_sent,"\n")
    #P:----print("total no_of_packets_totally_sent:",no_packet_just_sent+no_of_packets_totally_sent,"\n")
    #P:----print("sender timer:",sender_timer,"\n")

    #data=s.recv(1024)

    #receive_not_ack_time_buffer=list()
    #time_f_k=0
    #z=0
    if(alarm_ring_flag==1):
        #P:----print("ALarmed earlyyy")
        data=b'0'
        s.sendto("0".encode(),(name_or_ip,port))
        for i in range(0,int(window_size)):
            d=s.recvfrom(1024)
            #if(z!=0):
            #    time_f_k=time.time()
            #    z+=1
            #receive_not_ack_time_buffer.append(time.time())

    else:
        s.sendto("1".encode(),(name_or_ip,port))
    #P:----print("JUST BEFORE CHECKING ALARM RING  ")
    #ack_time_buffer=list()
    t=0

    data_old=b'e'
    #print("HEREEE")
    while(alarm_ring_flag==0):    #----------- if alarm rings before receiver sends anything, not ackd. Else, everything that he sends is acks.
        if(t<int(window_size)):
            d=s.recvfrom(1024)
            #if(z!=0):
            #    time_f_k=time.time()
            #    z+=1
            data=d[0]
            #if(data.decode()!=data_old.decode()):
            #   ack_time_buffer.append(time.time())
            #else:
            #    receive_not_ack_time_buffer.append(time.time())
            #P:----print("In clients receival, data got: ",data.decode())
            t+=1
            #data_old=d[0]

            if(ack_count+int(data.decode())==int(max_packets)):
                print("PACKET GENERATION RATE---- ",packet_gen_rate)
                print("MAX PACKET LENGTH (My packet length is variable here)---- ",max_packet_length)
                print("RETRANSMISSION RATIO---- ",(no_of_packets_totally_sent+no_packet_just_sent)*1.0/ack_count)
                print("Avg RTT---",time_return_avg)
                #plt.plot(iteration_list, retranmit_list, color='green', linestyle='dashed', linewidth = 3,
                #         marker='o', markerfacecolor='blue', markersize=12)
                #print("\n\nMAX PACKETS REACHED IN INCOMING ONLY.")

                sys.exit()

        while(t<int(window_size)):
                d=s.recvfrom(1024)
                #if(z!=0):
                #    time_f_k=time.time()
                #    z+=1
                #ack_time_buffer.append(time.time())
                data=d[0]
                #P:----print("In clients GHAATAK receival, data got: ",data.decode())
                t+=1


                if(ack_count+int(data.decode())==int(max_packets)):
                    print("PACKET GENERATION RATE---- ",packet_gen_rate)
                    print("MAX PACKET LENGTH (My packet length is variable here)---- ",max_packet_length)
                    print("RETRANSMISSION RATIO---- ",(no_of_packets_totally_sent+no_packet_just_sent)*1.0/ack_count)
                    print("Avg RTT---",time_return_avg)
                    #f.close()
                    #plt.plot(iteration_list, retranmit_list, color='green', linestyle='dashed', linewidth = 3,
                    #         marker='o', markerfacecolor='blue', markersize=12)
                    #f=open("Retransmission_ratio.py","w")
                    #f.write(str((no_of_packets_totally_sent+no_packet_just_sent)*1.0/ack_count)+" ")
                    sys.exit()
    #P:----print("AFTER HEARING ALARMMM\n")
    #thread5.join()
    alarm_ring_flag=0
    #P:----print("data got from receiver: ",data.decode())


    for i in range(0,int(window_size)):
        if buffer[i] in no_of_attempt_dict:
            #dict[buffer[i]]=dict[buffer[i]]+sender_timer
            no_of_attempt_dict[buffer[i]]=no_of_attempt_dict[buffer[i]]+1
        else:
            #dict[buffer[i]]=sender_timer
            no_of_attempt_dict[buffer[i]]=1


    #P:----print("Before dict, time_ack_start: ",time_ack_start)
    #print("buffer is: ",buffer)
    #print("ack_time_buffer is: ",ack_time_buffer)
    #print("receive_not_ack_time_buffer is: ",receive_not_ack_time_buffer)
    #print("dict is: ",dict)
    #sum__times=0
    #if(len(ack_time_buffer)==0):
    #    for i in range(0,len(receive_not_ack_time_buffer)):
    #        sum__times+=receive_not_ack_time_buffer[i]-dict[buffer[i]]
    #else:
    #    for i in range(0,len(ack_time_buffer)):
    #        sum__times+=ack_time_buffer[i]-dict[buffer[i]]
    #    for i in range(0,len(receive_not_ack_time_buffer)):
    #        sum__times=sum__times+(receive_not_ack_time_buffer[i]-dict[buffer[i+len(ack_time_buffer)] ] )

    #print("OLAA: time_f_k is: ",time_f_k);
    for buffer_key in dict:
        dict[buffer_key]=sender_timer+dict[buffer_key]-time_ack_start
    #print("Y ahora, dict: ",dict)

    #print("Changed dictionary: ",dict)


    #ack_return_val=data
    #if(data!=b'0'):
        #lock.acquire()
        #try:
    ack_count+=int(data.decode())

    #print("ack_count: ",ack_count)

    #now_time=time.time()
    #iteration_no+=1
    #iteration_list.append(iteration_no)
    #retranmit_list.append((no_of_packets_totally_sent+no_packet_just_sent)*1.0/ack_count)




    #print("Before ack, buffer: ",str(buffer))
    buffer_flag=1
    #print("Sender got some packets back. So, previous curr_buffer_size: ",curr_buffer_size," and its corresponding buffere size: ",len(buffer))

    if(d_val==1):
        for i in range(0,int(data.decode())):
           print("TIME GENERATED FOR ",buffer[i]," is:  ",dict[buffer[i]]," and number of attempts it took ",no_of_attempt_dict[buffer[i]])
    #for i in range(0,len(ack_time_buffer)):
    #    print("ackd ",buffer[i]," at time ",ack_time_buffer[i]," and time for it to come is: ",ack_time_buffer[i]-dict[buffer[i]])
    #print("len of ack_time_buffer is: ",len(ack_time_buffer)," which shud be equal to data.decode(): ",data.decode())

    r=deque(buffer)
    for i in range(0,int(data.decode())):
        r.popleft()
    buffer=list(r)
    #P:----print("After ack, buffer: ",str(buffer))
    #finally:
    #    lock.release()

    curr_buffer_size=curr_buffer_size-int(data.decode())
    #P:----print("And now, curr_buffer_size: ",curr_buffer_size," and corresponding buffer size: ",len(buffer))
    buffer_flag=0

    sum=0.0
    for f in dict:
        sum+=dict[f]

    #print("Old time_return_avg:",time_return_avg,"\n")
    time_return_avg=(time_return_avg*no_of_packets_totally_sent+sum)/(no_of_packets_totally_sent+no_packet_just_sent)
    #print("New time_return_avg:",time_return_avg,"\n")
    no_of_packets_totally_sent+=no_packet_just_sent
    if(ack_count==max_packets):
        #P:----print("\n\n no_of_attempt_dict: ",no_of_attempt_dict)
            print("PACKET GENERATION RATE---- ",packet_gen_rate)
            print("MAX PACKET LENGTH (My packet length is variable here)---- ",max_packet_length)
            print("RETRANSMISSION RATIO---- ",(no_of_packets_totally_sent)*1.0/ack_count)
            print("Avg RTT---",time_return_avg)
        #print("ack_count=max_packets=",ack_count,"so, sys_exit")
            #plt.plot(iteration_list, retranmit_list, color='green', linestyle='dashed', linewidth = 3,
            #         marker='o', markerfacecolor='blue', markersize=12)
            sys.exit()


def buffer_traverse():    # THis is very fast
    global buffer
    global s
    global no_packet_just_sent
    global no_of_packets_totally_sent
    global current_window_10_timer_flag
    global dict
    global time_ack_start
    global sender_timer
    i=0
    sent_count=0
    no_packet_just_sent=0
    while True:                       #IMPORTANT:
        if(sent_count==int(window_size)):  # sent_count is acting like a checker for lower and upper window limit
            #time_ack_start=time.time()         #Take care to update window_low as we go on acknowledging. Update this in packet gen info.
            sent_count=0              #So, we send only packets=window_size. If no of packets at hand is < window_size, either because forward entries are -1 or i>len(buffer), then, we wait till additional packets are put in buffer.
            #P:----print("About to enter ack() from buffer_traverse")
            #P:----print("Before entering ack, dict is: ",dict,"\n")
            #P:----print("current_window_10_timer_flag: ",current_window_10_timer_flag,"\n")
            #P:----print("no_packet_just_sent: ",no_packet_just_sent,"\n")
            ack()
            i=0  # i=0 in both cases that ack or not ack. If ack, its just that the buffer will cut off the front window. And i=0 will mean the new window.
            no_packet_just_sent=0
            current_window_10_timer_flag=0
            dict.clear()
            print("\n\n\n\n")
        if(i<len(buffer)):
            #s.sendall(bin( int(buffer[i])-int( zero_string_gen(len(buffer[i]) )) ))
            #P:----print("iiii ",i)
            #s.sendall(buffer[i].encode())
            #P:----print("buffer is: ",buffer)
            #P:----print("We are sending i=",i,", and buffer[i] is: ",buffer[i],"MAAAAAAAA\n")
            no_packet_just_sent+=1
            #no_of_packets_totally_sent+=1
            dict[buffer[i]]=time.time()

            if(no_of_packets_totally_sent+no_packet_just_sent<=10):
                current_window_10_timer_flag=1


            s.sendto(buffer[i].encode(),(name_or_ip,port))
            sent_count+=1
            #P:----print("sent_count:",str(sent_count))

            if(sent_count==1):
                time_ack_start=time.time()
                #print("time_ack_start: ",time_ack_start)

                if(current_window_10_timer_flag==1):
                    sender_timer=0.1
                else:
                    sender_timer= 2*time_return_avg

                #P:----print("Before TIMERRRR on, current_window_10_timer_flag: ",current_window_10_timer_flag)
                thread5= Thread(target=get,args=())
                thread5.start()
            #if(sent_count!=window_size):
            #P:----print("So, I sent ",buffer[i])
            #data= s.recv(1024)
            #print("i iss: ",i)
            #print(repr(data))
            i+=1
        else:
            #print("Gotta continue as i=",i," and len(buffer) is: ",len(buffer))
            continue

    #while True:
    #        if(buffer[i]=='-1'):
    #            continue
    #        for j in range(i,i+window_size):
    #            if(j>=max_buffer_size or buffer[j]=='-1'):
    #                i=j-1
    #                break
    #            thread_i=Thread(target=packet_send_thread,args=(i))
    #            i=j
    #    else:
    #        continue

thread1=Thread(target=packet_gen,args=())
thread2=Thread(target=buffer_traverse,args=())
thread1.start()
thread2.start()
thread1.join()
thread2.join()
