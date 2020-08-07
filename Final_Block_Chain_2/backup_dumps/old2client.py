import socket,select,datetime,threading,random,time,sys,os,pickle,hashlib
#3 machines scale hash power accordingly
def start_client(exp_parameter,peer_id):
    #exp_parameter is the local lambda for each client based on its hashing power
    def convert_string_to_iplist(string):
        return string.split("-")[1:]
    def connect_to_seed(gossip_socket):
        client_seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seed_ip=str(sys.argv[1])
        seed_port=46680
        seed_tuple = (seed_ip,seed_port)
        size_of_list_buffer = 4096
        client_seed_socket.connect(seed_tuple)
        client_seed_socket.sendall(str(gossip_socket.getsockname()[1]).encode('UTF-8'))
        string_ip_port = client_seed_socket.recv(size_of_list_buffer).decode('UTF-8')
        client_seed_socket.setblocking(0)
        peer_list=convert_string_to_iplist(string_ip_port)
        return peer_list,client_seed_socket
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
            new_socket.setblocking(0)
            List_connected_peer.append(new_socket)
        return List_connected_peer
    client_gossip_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_gossip_socket.setblocking(0)
    client_gossip_socket.bind(('',0))
    max_client_nodes_count=4
    client_gossip_socket.listen(5)
    List_peers, client_seed_socket = connect_to_seed(client_gossip_socket)
    List_connected_peer = connect_to_peers(List_peers[-4:])
    #List_connected_peer.append(client_seed_socket)
    Readable_sockets = List_connected_peer[:]
    Readable_sockets.append(client_gossip_socket)
    Readable_sockets.append(client_seed_socket)
    Message_List = []
    mining_started = False
    H = {}
    total_run_time = time.time() + 30.0
    
    while time.time()<total_run_time:
        ready_to_read, ready_to_write, exc = select.select(Readable_sockets ,List_connected_peer, []) 
        if mining_started == False:
            for s in ready_to_read:
                if s is client_gossip_socket:
                    sock_object_conneced, ip_port_number = s.accept()
                    sock_object_conneced.setblocking(0)
                    List_connected_peer.append(sock_object_conneced)
                    Readable_sockets.append(sock_object_conneced)
                else:                            
                    message = s.recv(2048)
                    message = str(message.decode('utf-8'))
                    if message == "start mine":
                        print("Mining message received at client = ", end="")
                        print(peer_id)

                        for x in ready_to_write:
                            if x is not s:
                                try:
                                    x.sendall(message.encode('UTF-8'))
                                except:
                                    pass 
                        mining_started = True
                        time.sleep(3)
                        break
        else:
            #time.sleep(3)
            current_longest_chain = 1
            genesis_block = (("0","ab",0.0),1,"9e1c")
            #first three columns are block details
            H["9e1c"] = genesis_block
            hash_of_the_longest_block = "9e1c"
            wait_time_before_generation = random.expovariate(exp_parameter)
            current_time = time.time()
            generation_time = current_time+wait_time_before_generation
            # self_generate = True
            gossip_block = True
            total_blocks_recorded = 1
            while time.time() < generation_time:
                ready_to_read, ready_to_write, exc = select.select(List_connected_peer ,List_connected_peer, [])
                for s in ready_to_read:
                    # self_generate = False
                    block_record_binary = s.recv(2048)
                    if block_record_binary ==b'':
                        break
                    block_record = pickle.loads(block_record_binary)
                    if block_record[0][0] in H:
                        if block_record[2] not in H:
                            total_blocks_recorded+=1
                            length_of_received_block = block_record[1]
                            length_of_received_block+=1
                            H[block_record[2]] = (block_record[0], length_of_received_block, block_record[2])
                            print("block received at peer = ",end = "")
                            print(peer_id)
                            for w in ready_to_write:
                                # Received block broadcast 
                                if w is not s:
                                    try:
                                        w.sendall(block_record_binary)
                                    except:
                                        pass
                            if(length_of_received_block >current_longest_chain):
                                current_longest_chain = length_of_received_block
                                generation_time= time.time()+ random.expovariate(exp_parameter)
                                hash_of_the_longest_block= block_record[2]

                        #1. block validated 
                        # 2. store in H 
                        #3. gossip to ready_to_write 
                        # 4.  check if it is the longest 
                        # 4. the+n update generation_time= time.time()+ random.expovariate(exp_parameter)
                    else:
                        pass
                        # pass no work here. no need to gossip invalid blocks
            new_block = (hash_of_the_longest_block,"ab",generation_time)
            hash_new_block= hashlib.sha256(repr(new_block).encode('utf-8')).hexdigest()[-4:]
            current_longest_chain +=1
            new_block_record =(new_block,current_longest_chain,hash_new_block)
            print("Block Generated at peer = ", end="")
            print(peer_id)
            H[hash_new_block] = new_block_record
            new_block_record_binary = pickle.dumps(new_block_record)
            for s in ready_to_write:
                # self generated block broadcast
                try:
                    s.sendall(new_block_record_binary)
                except:
                    pass



                    




def start_all_clients(total_clients):
    hashpower = [random.random() for i in range(total_clients)]
    s = sum(hashpower)
    hashpower = list(map(lambda x:x/s,hashpower))
    print('hash power of each client:')
    for i in range(total_clients):
        print(hashpower[i])
    #print(fash)
    itime = 3
    globallambda = 1.0/itime
    cllambda = list(map(lambda x:x*globallambda,hashpower))
    print('lambda of each client:')
    for i in range(total_clients):
        print(cllambda[i])
    for i in range(total_clients):
        processid = os.fork()
        if processid == 0:
            start_client(cllambda[i],i)
            exit(0)

    while True:
        try: 
            os.wait()
        except:
            break
    print("Mining by all the clients finished")
    exit(0)
#total_clients = int(sys.argv[2])
total_clients = 2
start_all_clients(total_clients)
