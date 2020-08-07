import socket,select,datetime,threading,random,time,sys

#seed_file=""

# client_file=
file="output.txt"
#file_obj=open(file,"a+")

def convert_string_to_iplist(string):
    return string.split("-")[1:]

def connect_to_seed(gossip_socket):
    client_seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    seed_ip=str(sys.argv[1])
    seed_port=46680      
    size_of_list_buffer = 4096
    client_seed_socket.connect((seed_ip,seed_port))
    client_seed_socket.sendall(str(gossip_socket.getsockname()[1]).encode('UTF-8'))
    string_ip_port = client_seed_socket.recv(size_of_list_buffer).decode('UTF-8')
    peer_list=convert_string_to_iplist(string_ip_port)
    return peer_list


def connect_to_peers(peer_list):
    List_connected_peer = []
    print(peer_list)
    #file_ojb.write(peer_list)
    for s in peer_list:
        peer_ip = s.split('@')[0]
        peer_port = int(s.split('@')[1])
        peer_tuple = (peer_ip,peer_port)
        new_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect(peer_tuple)
        List_connected_peer.append(new_socket)
    return List_connected_peer




def message_creation():
    #ip_address =  str(clientet.getsockname()[0])
    for i in range(10):
    	#ip_address =  str(List_connected_peer[].getsockname()[0])
        
        for x in List_connected_peer:
            m = str(time.time()) + ':'+ x.getsockname()[0]+': Hi. this is message ' + str(i)+'#' 
            x.sendall(m.encode('UTF-8'))
        time.sleep(5 + random.randint(0,5)) 

client_gossip_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_gossip_socket.setblocking(0)
client_gossip_socket.bind(('',0))
max_client_nodes_count=4
client_gossip_socket.listen(max_client_nodes_count)
List_peers = connect_to_seed(client_gossip_socket)
List_connected_peer = connect_to_peers(List_peers[-4:])
Readable_sockets = List_connected_peer[:]
Readable_sockets.append(client_gossip_socket)
#first message might be sent here 
message_creation_thread = threading.Thread(target=message_creation,name="client_to_seed")
message_creation_thread.start()
H = set()
Message_List = []
while True:
    ready_to_read, ready_to_write, exc = select.select(Readable_sockets ,List_connected_peer, [])

    for s in ready_to_read:

        if s is client_gossip_socket:
            sock_object_conneced, ip_port_number = s.accept()
            file_obj=open(file,"a+")
            print("client ",ip_port_number," connected!")
            file_obj.write("client "+str(ip_port_number[0])+str(ip_port_number[1])+" connected!\n")
            file_obj.close()
            sock_object_conneced.setblocking(0)
            List_connected_peer.append(sock_object_conneced)
            Readable_sockets.append(sock_object_conneced)

        else:
            Message = s.recv(1024)
            Message = str(Message.decode('utf-8'))
            List_messages = Message.split('#')[:-1]
            for message in List_messages:
                if message in H:
                    continue
                H.add(message)
                Message_List.append(message)
                print(message)
                file_obj=open(file,"a+")
                file_obj.write(message+'\n')
                file_obj.close()
                #write in file 

            #these are messages sent by clients
            #if these messages are in hash table:
            #   ignore these messages and coninue
            #else:
            #    print messages on screen and write to file and queue up in a temporary list for gossiping 
    for s in ready_to_write:
            #now send the messages in temporary list one by one to all the conneced peers (List_connected_peer)
            for x in Message_List:
                for y in List_connected_peer:
                    try:
                    	y.sendall(x.encode('UTF-8'))
                    except:
                    	pass
            Message_List=[]
