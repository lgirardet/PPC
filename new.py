import os
import sys
import sysv_ipc
import threading
from multiprocessing import Process
import keyboard

key = 400
remainings=1000


def user():
    answer = 5
    while answer not in [1, 2, 3]:
        answer = int(input())
        print("Ans replied:"+str(answer))
    return answer


def worker(mq, m):
    
    message = str(m.decode())
    message = message.split("+")
    amount=message[0]
    pid=int(message[1])
    global remainings
    res="y"
    done= False
    while not done:
        print("PID "+str(pid)+" requested "+str(amount)+" energy, you have " +str(remainings)+" remainings.")
        res=input("Do you want to give away your energy [Y/y] or [N/n] ?")
        if (res=="N" or res=="n"):
            reply="Neighbour do not wish to giveaway their energy. Sorry :("
            #break
            done=True
        elif (res =="Y" or res =="y"):
            while True:
                try:
                    giveaway=int(input("How much do you want to give away : "))
                    if (giveaway > remainings):
                        print("Sorry. Not enough energy to giveaway. You can only giveaway energy less than "+str(remainings))
                    else:
                        print(str(giveaway)+" sent to PID "+str(pid))
                        remainings=remainings-giveaway
                        print("Remainings : "+str(remainings))
                        reply="OK"+"+"+str(giveaway)
                        done=True
                        break
                except ValueError:
                    print("Oops? That was not a valid integer")
                
    t = pid + 3
    mq.send(reply, type=t)


def check_input():
    while True:
        user_input = input()
        if user_input == "quit":
            global index
            index=2
            break




print("1. to hear request from neighbour")
print("2. to request energy from neighbour")
#print("3. to terminate server")
print("3. to terminate program")
while True:
    t = user()
    print("t is "+str(t))
    if t == 1:
        if __name__ == "__main__":
            try:
                #mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
                mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
            except sysv_ipc.ExistentialError:
                print("Message queue", key, "already exsits, terminating.")
                sys.exit(1)

            print("Starting server.")
            print("My key is "+str(key))
            
            threads = []
            
            input_thread = threading.Thread(target=check_input)
            input_thread.start()
            while True:
                m, index = mq.receive()
                if index == 1:
                    p = threading.Thread(target=worker, args=(mq, m))
                    p.start()
                    threads.append(p)
                    
                if index == 2:
                #    for thread in threads:
                #        thread.join()
                #    mq.remove()
                    break
            input_thread.join()
            print("Terminating server.")
            
    if t == 2:
        print("You have "+str(remainings)+" remainings")
        key = int(input("Enter key of the neighbour you wish to communicate : "))
        try:
            mq = sysv_ipc.MessageQueue(key)
        except sysv_ipc.ExistentialError:
            print("Cannot connect to message queue", key, ", terminating.")
            sys.exit(1)
        while True:
            try:
                amount=int(input("How many energy to request : "))
                break
            except ValueError:
                print("Oops? That was not a valid integer")
        pid = os.getpid()
        messages=str(amount)+"+"+str(pid)
        
        mq.send(messages.encode())
        m, t = mq.receive(type =(pid + 3))
        dt = m.decode()
        response=dt.split("+")
        if response[0]=="OK":
            print("Neighbour gave you "+str(response[1]))
            remainings=remainings+int(response[1])
            print("Remainings : "+str(remainings))
        else:
            print("Server response:", response[0])
            
    #if t == 3:
    #    m = b""
    #    mq.send(m, type = 2)

    if t == 3:
        break
        
    print("Terminating program")
