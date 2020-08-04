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
buffer=list()
bul=list()
buffer_length=0

d_val=0
for i in range(1,len(arg_list)):
    x=arg_list[i];
    if(x=="-d"):
        d_val=1
    elif(x=="-p"):  #6666
        port_no=int(arg_list[i+1])
        i+=1
    elif(x=="-N"):   #400
        max_packets=int(arg_list[i+1])
        i+=1
    elif(x=="-n"):   #400
        sequence_number_field_length=int(arg_list[i+1])
        i+=1
    elif(x=="-W"):   #400
        window_size=int(arg_list[i+1])
        i+=1
    elif (x=='-B'):  # 0.01
        max_buffer_size= int(arg_list[i+1])
        i+=1
    elif(x=="-e"):   #400
        packet_drop_prob=float(arg_list[i+1])
        i+=1

port=int(port_no)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host,port))

expected_sequence_number=0
sequence_number=2**(sequence_number_field_length)


while True:
    #d=[b'-1',b'-2']
    #while alarm_ring_flag==0:    # some time, alarm falg will be 0.
    i=0
    if(len(bul)!=0):
        while(bul[i]==1):
            buffer.pop(0)
            buffer_length-=1
            bul.pop(0)
    d=s.recvfrom(1024)
    #j+=1
    print("\n\ndata got: ",d[0].decode())
    addr=d[1]
    x=numpy.random.rand()
    #buffer.append(int(d[0].decode()))
    print("prev buffer iss: ",buffer)
    print("prev bul: ",bul)
    if(x>packet_drop_prob):
        #bul.append(1)
        print("Packet not dropped")
        data=d[0]
        ss=data.decode()
        extracted_seq_no_string=ss[0:sequence_number_field_length]
        if(len(buffer)!=0):
            if(int(d[0].decode()) in buffer):
                index=buffer.index(int(d[0].decode()))
                print("Data was in buffer, so it had defaulted earlier. Is at Index: ",index)
                bul[index]=1
                flag=0
                #for i in range(0,index):
                #    if(bul[i]==0):
                #        flag=1
                #        break
                #if(flag==0):
                for i in range(index+1,window_size):
                    if(bul[i]==0):
                        break
                    buffer.pop(0)
                    buffer_length-=1
                    bul.pop(0)
                print("new buffer iss: ",buffer)
                print("new bul: ",bul)
                e=data.decode()
                print("Sending earlier buffer : ",data.decode())
                s.sendto(e.encode(),addr)
                count_no_of_packets_ack+=1
                print("count_no_of_packets_ack: ",count_no_of_packets_ack)
                if(count_no_of_packets_ack==max_packets):
                    print("Reached max_packets")
                    sys.exit()

            else:
                if(buffer_length+1<=max_buffer_size):
                    print("Since buffer[0] has bul 0, we ack this, but put in our buffer")
                    buffer.append(int(data.decode()))
                    buffer_length+=1
                    bul.append(1)
                    e=data.decode()

                    print("new buffer iss: ",buffer)
                    print("new bul: ",bul)

                    print("Sending new buffer: ",data.decode())
                    s.sendto(e.encode(),addr)
                    count_no_of_packets_ack+=1
                    print("count_no_of_packets_ack: ",count_no_of_packets_ack)
                    if(count_no_of_packets_ack==max_packets):
                        print("Reached max_packets")
                        sys.exit()

        else:
            print("Proper")
            s.sendto(ss.encode(),addr)
            count_no_of_packets_ack+=1


    else:
        if(int(d[0].decode()) in buffer):
            index=buffer.index(int(d[0].decode()))
            bul[index]=0
        else:
            if(buffer_length+1<=max_buffer_size):
                buffer.append(int(data.decode()))
                buffer_length+=1
                bul.append(0)
                print("new buffer iss: ",buffer)
                print("new bul: ",bul)
