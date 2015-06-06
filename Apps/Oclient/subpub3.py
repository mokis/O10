import zmq
import time
import socket
import sys
import os

# service for publisher and subscriber sockets that operates
# with channel names. Code will work without any modifications
# if you move it from machine to another or use (dumb) DHCP
class messanger:
    def __init__(self, nic_ip=""):
        self.context = zmq.Context()
        self.poller = zmq.Poller()

        if nic_ip == "" and os.name == "nt":
            self.my_ip = socket.gethostbyname(socket.gethostname())
        elif nic_ip == "" and os.name == "posix":
            # works in private lan? if etc/hosts is modified, windows
            # solution should work also in linux
            self.my_ip = socket.gethostbyname(socket.getfqdn())
        else:
            self.my_ip = nic_ip

        self.pub_sockets = {}
        self.sub_sockets = {}
        self.found_channels = {}
        self.active_sockets = False

        self.last_synch = time.time()

        # service discovery stuff
        # ping_data = ping + " " + name + " " + interval
        # pong_data = pong + " " + name + " " + ip:port
        # name: 20 chars
        # interval: 5 chars, [s], "x.yzv"
        # ip: "qwe.rty.uio.pas:dfghj", 21 chars
        
        self.udp_port = 10000
        self.udp_buf_size = 2**16
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.settimeout(0.005)
        self.udp_sock.bind(('', self.udp_port))

    ###############################
    # public functions
    ###############################

    # create publisher channel <name>, that uses <port>
    def pub(self, name, port, interval = 0.03):
        pub = self.context.socket(zmq.PUB)
        pub.bind("tcp://*:" + str(port))
        #self.poller.register(pub, zmq.POLLOUT)

        # pub socket, min interval between stansmission[s], timestam for
        # last transmission, address
        self.pub_sockets[name] = [pub, interval, \
                                  time.time(), \
                                  self.my_ip + ":" + str(port)]

                              
    # create subscriber channel <name> with minimum packet <interval> [s]   
    def sub(self, name):
        # sub socket, min time between transmission (got from publisher),
        # socket is connected to publisher
        self.sub_sockets[name] = [None, 0.0, False]


    # service discovery system, uses udp broadcast to find publishers
    # with right channel name. Publisher will respond to ping.
    def synch(self):

        # process message queue
        while True:
            got_data, msg = self.udp_recv()
            if not got_data:
                break

            msg = msg.split()

            # omg, someone pinged me 
            if msg[0] == "ping" and self.pub_sockets.has_key(msg[1]):
                self.udp_send("pong " +  msg[1] + " " + \
                              self.pub_sockets[msg[1]][3] + " " +\
                              str(self.pub_sockets[msg[1]][1]))
                #print msg
                

            # got publisher address
            if (msg[0] == "pong" and self.sub_sockets.has_key(msg[1]) and \
               not self.sub_sockets[msg[1]][2]) or (msg[0] == "refr" and \
               self.sub_sockets.has_key(msg[1])):

                sub = self.context.socket(zmq.SUB)
                addr = "tcp://" + msg[2]
                sub.connect(addr)
                sub.setsockopt(zmq.SUBSCRIBE, "")
                self.poller.register(sub, zmq.POLLIN)
                
                self.sub_sockets[msg[1]][0] = sub           # socket
                self.sub_sockets[msg[1]][1] = float(msg[3]) # interval
                self.sub_sockets[msg[1]][2] = True          # socket active

                print "connection established:" , msg[1], msg[2], msg[3]
                sub = None


        # flooding preventation
        if time.time() - self.last_synch < 0.5:
            return

        self.last_synch = time.time()

        # try to ping publishers that are not connected yet
        for name in self.sub_sockets.keys():
            if not self.sub_sockets[name][2]:
                self.udp_send("ping " + name)
                #print "ping", name

        

    # receive data from subscriber channel <name>, in one chunk or in array
    def recv(self, name, split=True):
        socks = dict(self.poller.poll(0))
        msg = ""
        #print socks
        if self.sub_sockets[name][0] in socks and \
           socks[self.sub_sockets[name][0]] == zmq.POLLIN:
            
            msg = self.sub_sockets[name][0].recv()

        if split:    
            return msg.split()
        else:
            return msg

    # receive data from subscriber channel <name>, in one chunk or in array
    def recv2(self, name, split=True):
        socks = dict(self.poller.poll(0))
        old_msg = ""
        msg = ""

	count =0

        while self.sub_sockets[name][0] in socks and \
           socks[self.sub_sockets[name][0]] == zmq.POLLIN:

            socks = dict(self.poller.poll(0))
            
            msg = self.sub_sockets[name][0].recv()
            #print msg

            if count > 5:
                break

        if split:    
            return old_msg.split()
        else:
            return old_msg
        

    # send msg using publisher channel <name>
    def send(self, msg, name):
        #socks = dict(self.poller.poll(0))
        if time.time() - self.pub_sockets[name][2] > \
           self.pub_sockets[name][1]:

        #print "snd", msg, ".", self.pub_sockets[name][0]
            self.pub_sockets[name][2] = time.time()
            msg = self.pub_sockets[name][0].send(msg)
            return True
        #print "ret", msg
        return False


    # get min interval between trasmission for channel <name>
    def get_interval(name):
        for key in self.pub_sockets.keys():
            if name == key:
                return self.pub_sockets[key][1]
            
        for key in self.sub_sockets.keys():
            if name == key:
                return self.sub_sockets[key][1]

        return -1


    # is subscriber channel <name> connected to publisher
    def is_connected(name):
        for key in self.sub_sockets.keys():
            if name == key:
                return self.sub_sockets[key][2]

        return None
            


    ################################
    # private functions
    ################################

    # receives one udp message
    def udp_recv(self):
        data = ""

        try:
            data = self.udp_sock.recv(self.udp_buf_size)
        except socket.timeout:
            pass
        except:
            print "Error@recv ", sys.exc_info()
            
        if len(data) > 0:
            return True, data
        else:
            return False, ""

    # sends one udp msg
    def udp_send(self, msg):
        try:
            self.udp_sock.sendto(msg, ('<broadcast>', self.udp_port))
        except:
            print "Error@send ", sys.exc_info()


    # returns name that is exactly 20 charecters long
    # makes c programmer life easier
    # NOT IN USE
    def fix_name(self, name):
        if len(name) > 20:
            return name[0:20]
        else:
            return name.ljust(20, " ")

    # zero padding, we want address to be exactly 21 charecters long
    # makes c programmer life easier
    # NOT IN USE
    def fix_addr(self, addr):
        parts = addr.split(".")
        parts2 = parts[3].split(":")
        #print parts, parts2
        ret_addr = parts[0].zfill(3) + "." + parts[1].zfill(3) + "." + \
                   parts[2].zfill(3) + "." + parts2[0].zfill(3) + ":" + \
                   parts2[1].zfill(5)
        return ret_addr




        
        
        
    
        
        
        
