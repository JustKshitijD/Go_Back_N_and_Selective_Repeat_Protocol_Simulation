import sys   #for command line inputs
from threading import Thread
import random, math
import time
import socket
import sys
from collections import deque

arg_list=sys.argv

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
    elif(x=="-n"):
        sequence_number_field_length=arg_list[i+1]
        i=i+1
    elif(x=="-L"):
        max_packet_length=arg_list[i+1]
        i=i+1
    elif(x=="-R"):
        packet_gen_rate=arg_list[i+1]
        i=i+1
    elif(x=="-N"):
        max_packets=arg_list[i+1]
        i=i+1
    elif(x=="-W"):
        window_size=arg_list[i+1]
        i=i+1
    elif(x=="-B"):
        max_buffer_size=arg_list[i+1]
        i=i+1





print("-d ",d_val)
print("-s ",name_or_ip) #receiver's name/IP
print("-p ",port_no) # receiver's port number  12345
#print("-l ",max_packet_length)  # 512
print("-r ",packet_gen_rate)  #10
print("-n ",max_packets)  # Sender terminates after max_packets have been acknowledged  400
print("-w ",window_size)  #3
print("-b ",max_buffer_size)  #max no of packets in buffer 10

#s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
port=int(port_no)
#s.connect((name_or_ip,port))
#s.sendall(str(window_size).encode())

#s.sendto(str(window_size).encode(),(name_or_ip,port))



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

bul=list()
timer=list()
sender_window_lower_limit=0
sender_window_upper_limit=window_size
reciever_window_lower_limit=0
reciever_window_upper_limit=window_size

sequence_number_length=int(sequence_number_field_length)
sequence_number=2**int(sequence_number_field_length)

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

        time_start=time.time()
        #P:-print("\n\ntime_start ",time_start)  # for every new packet, time_start=0

        x=math.floor(random.uniform(40,int(max_packet_length)))  # new packet's length
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

            while(buffer_flag==1):
                continue
            buffer.append(str)
            bul.append(0)
            timer.append(time.time())

            print("IN PRODUCTION bul: ",bul)
            print("IN PRODUCTION buffer: ",buffer)
            print("IN PRODUCTION timer: ",timer)
            #P:----P:----print("Added ",str," to buffer")
            curr_buffer_size+=1

            time_end=time.time()
            #P:-print("time_end ",time_end)
            while(time_end-time_start<=time_for_1_packet):    # time_start and time_end sud be for every packet
                #print("hullo, time_end-time_start", time_end-time_start)
                time_end=time.time()


def clck():
    global alarm_ring_flag
    global timer
    extra=0
    while True:
        while(time.time()-min(timer)<sender_timer+extra):
            continue
        alarm_ring_flag=1
        i=timer.index(min(timer))
        #s.sendto(buffer[i].encode(),(name_or_ip,port))
        timer[i]=time.time()
        print("\n In timer, timer[i]: ",timer[i]," stuck alarm,and its element is: ",buffer[i])
        while(alarm_ring_flag==1):
            continue
        extra=time.time()-timer[i]

def wait_recv():
    global s
    global bul
    global alarm_ring_flag
    global ack_count
    global timer
    global max_packets
    global buffer
    while True:
        d=[b'-1',b'-2']
        flag=0
        flag2=0
        while alarm_ring_flag==0:    # some time, alarm falg will be 0.
            d=s.recvfrom(1024)
            data=d[0]
            ii=buffer.index(data.decode())
            #flag=00
            print("ii: ",ii)
            print("bulll ",bul)
            print("buff ",buffer)
            for i in range(0,ii):
                flag2+=1
                if(bul[i]==0):
                    print("The got data: ",data.decode()," is blocked, with its index as: ",buffer.index(int(data.decode())), " as ",buffer[i]," is not yet got")
                    flag=1
                    break
            if(flag==0):
                break
        print("\n Out of alarm while")
        if(flag==0):
            alarm_ring_flag=0
        if(flag2==0 or d[0]!=b'-1'):
            y=int(d[0].decode())    # receiver will return packet's sequence no
            x=buffer.index(y)
            bul[x]=1
            ack_count+=1
            print("ack_count is: ",ack_count)
            timer[x]=time.time()
            if(ack_count==max_packets):
                print("Reached max_packets")
                sys.exit()

            i=x
            if(x==0):
                while(bul[i]!=0):           #max can go till window after last element of this window, as it will be 0
                    bul.pop(0)
                    buffer.pop(0)
                    timer.pop(0)
                    i+=1

def buffer_traverse():    # THis is very fast
    global buffer
    global s
    global no_packet_just_sent
    global no_of_packets_totally_sent
    global current_window_10_timer_flag
    global dict
    global time_ack_start
    global sender_timer
    global bul
    send_first_flag=0
    prev_sent=0
    print("bul: ",bul)
    print("buffer: ",buffer)
    print("timer: ",timer)
    while(True):
        for i in range(0,len(buffer)):  # We will move buffer left instead of window right
            if(bul[i]==0):
                print("sending: ",buffer[i])
                s.sendto(str(buffer[i]).encode(),(name_or_ip,port))


thread1=Thread(target=packet_gen,args=())
thread2=Thread(target=buffer_traverse,args=())
thread3=Thread(target=clck,args=())
thread4=Thread(target=wait_recv,args=())
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread1.join()
thread2.join()
thread3.join()
thread4.join()
