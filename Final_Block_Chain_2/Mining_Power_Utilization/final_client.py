import socket,select,datetime,threading,random,time,sys,os,pickle,hashlib
#3 machines scale hash power accordingly
def start_client(exp_parameter,peer_id):
    #exp_parameter is the local lambda for each client based on its hashing power
    def convert_string_to_iplist(string):
        return string.split("-")[1:]
    def connect_to_seed(gossip_socket):
        client_seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        seed_ip=str(sys.argv[1])
        seed_port=int(sys.argv[2])
        seed_tuple = (seed_ip,seed_port)
        size_of_list_buffer = 4096
        client_seed_socket.connect(seed_tuple)
        time.sleep(0.1)
        client_seed_socket.sendall(str(gossip_socket.getsockname()[1]).encode('UTF-8'))
        # time.sleep(5)
        # client_seed_socket.setblocking(0)
        string_ip_port = client_seed_socket.recv(size_of_list_buffer)
        peer_list = []
        string_ip_port = string_ip_port.decode('UTF-8')
        peer_list=convert_string_to_iplist(string_ip_port)
        # peer_list = []    
        
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
    List_connected_peer = connect_to_peers(List_peers[-2:])
    #List_connected_peer.append(client_seed_socket)
    Readable_sockets = List_connected_peer[:]
    Readable_sockets.append(client_gossip_socket)
    Readable_sockets.append(client_seed_socket)
    Message_List = []
    mining_started = False
    H = {}
    # total_run_time = time.time() + 100.0
    #total_blocks_recorded = 1
    current_longest_chain = 1
    genesis_block = (("0","ab",0.0),1,"9e1c",'h')
    #first three columns are block details
    H["9e1c"] = genesis_block
    hash_of_the_longest_block = "9e1c"
    # reselect_call = True
    total_blocks_recorded = 1
    total_blocks_required = int(sys.argv[4])
    # total_run_time = time.time() + 200.0
    while total_blocks_recorded <= total_blocks_required:
        ready_to_read, ready_to_write, exc = select.select(Readable_sockets ,List_connected_peer, []) 
        if mining_started == False:
            for s in ready_to_read:
                if s is client_gossip_socket:
                    sock_object_conneced, ip_port_number = s.accept()
                    sock_object_conneced.setblocking(0)
                    List_connected_peer.append(sock_object_conneced)
                    Readable_sockets.append(sock_object_conneced)
                elif s is client_seed_socket:                            
                    message = s.recv(2048)
                    message = pickle.loads(message)
                    # print("nana")
                    if message == "start mine":
                        # print("baba")
                        print("Mining message received at client = ")
                        # print(peer_id)
                        mining_started = True
                        # /mtime.sleep(3)
                        # break
        else:
            time.sleep(2)
            while total_blocks_recorded <= total_blocks_required:
          
                current_time = time.time()
                generation_time =time.time()+random.expovariate(exp_parameter)
                while time.time() < generation_time:
                    # if reselect_call== False:
                    ready_to_read, ready_to_write, exc = select.select(List_connected_peer ,List_connected_peer, [])
                    all_blocks = set()
                    for s in ready_to_read:
                        # self_generate = False
                        try:
                            block_record_binary = s.recv(2048)
                            # mess = "start mine"
                            if block_record_binary ==b'':
                                break
                            else:
                                # print("block received at peer ")
                                # print(peer_id)

                                # print("block received at peer ", end = "")
                                # print(peer_id)
                                block_record = pickle.loads(block_record_binary)
                                all_blocks.add(block_record)
                        except:
                            pass
                    for block in all_blocks:
                        if block[0][0] in H:
                            if block[2] not in H:
                                # total_blocks_recorded+=1
                                #print("block received from peer")
                                length_of_received_block = block[1]
                                # length_of_received_block+=1
                                H[block[2]] = block
                                total_blocks_recorded +=1
                                for w in ready_to_write:
                                    # Received block broadcast 
                                    # if w is not s:
                                    block_record_binary = pickle.dumps(block)
                                    try:
                                        delay = random.uniform(0.2,0.5)
                                        time.sleep(delay)
                                        w.sendall(block_record_binary)
                                    except:
                                        pass
                                if(length_of_received_block >current_longest_chain):
                                    current_longest_chain = length_of_received_block
                                    generation_time= time.time()+ random.expovariate(exp_parameter)
                                    hash_of_the_longest_block= block[2]

                                #1. block validated 
                                # 2. store in H 
                                #3. gossip to ready_to_write 
                                # 4.  check if it is the longest 
                                # 4. the+n update generation_time= time.time()+ random.expovariate(exp_parameter)
                            
                new_block = (hash_of_the_longest_block,"ab",generation_time)
                hash_new_block= hashlib.sha256(repr(new_block).encode('utf-8')).hexdigest()[-4:]
                current_longest_chain +=1
                hash_of_the_longest_block = hash_new_block
                new_block_record =(new_block,current_longest_chain,hash_new_block,'h')
                H[hash_new_block] = new_block_record
                total_blocks_recorded+=1
                # print("block generated at peer")
                new_block_record_binary = pickle.dumps(new_block_record)
                # print(total_blocks_recorded)
                # print(total_blocks_required)
                for s in ready_to_write:
                    # self generated block broadcast
                    try:
                        delay = random.uniform(0.2,0.5)
                        time.sleep(delay)
                        s.sendall(new_block_record_binary)
                    except:
                        pass

    print("mining factors at peer ")
    print(H)
    print(current_longest_chain)
    utilization =current_longest_chain/len(H)
    print(utilization)
    data_file='_plotdata1'
    data_file_obj=open(data_file,'a+')
    final_string=str(int(itime)) + '_' + str(current_longest_chain)
    pickle_outfile_location='pd_'+final_string
    pickle_outfile=open(pickle_outfile_location,'wb+')
    hash_outfile_location = 'hash_' + final_string
    hash_outfile = open(hash_outfile_location,'wb+') 
    pickle.dump(hash_of_the_longest_block,hash_outfile)
    
    hash_outfile.close()
    #1/itime(block_gen_rate) #ut #current_longest_Chain #len(H)
    final_string=str(itime) +','+ str((1/itime)) + ',' + str(utilization) + ',' + str(current_longest_chain) + ',' + str(len(H)) + '\n'
    pickle.dump(H,pickle_outfile)
    data_file_obj.write(final_string)
    pickle_outfile.close()
    data_file_obj.close()

total_clients = 5
itime = float(sys.argv[3])
def start_all_clients(total_clients):
    hashpower = 1/total_clients
    print('hash power of each client:')
    print(hashpower)
    globallambda = 1.0/itime
    start_client(hashpower*globallambda,0)
    

# total_clients = 2
start_all_clients(total_clients)

