import socket,select,datetime,threading,random,time,sys,os,pickle,hashlib
#3 machines scale hash power accordingly
def start_adversary(exp_parameter):
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
        client_seed_socket.sendall(str(gossip_socket.getsockname()[1]).encode('UTF-8'))
        string_ip_port = client_seed_socket.recv(size_of_list_buffer)
        peer_list = []
        string_ip_port = string_ip_port.decode('UTF-8')
        peer_list=convert_string_to_iplist(string_ip_port)
        
        return peer_list,client_seed_socket
    def connect_to_peers(peer_list):
        List_connected_peer = []
        print(peer_list)
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
    Readable_sockets = List_connected_peer[:]
    Readable_sockets.append(client_gossip_socket)
    Readable_sockets.append(client_seed_socket)
    Message_List = []
    mining_started = False
    H = {}
   
    # total_blocks_recorded = 1
    private_longest_chain = 1
    public_longest_chain = 1
    genesis_block = (("0","ab",0.0),1,"9e1c", 'h')
    H["9e1c"] = genesis_block
    public_chain_last_hash =  "9e1c"
    private_chain_last_hash = "9e1c"
    private_branch_length = 0
    no_of_ablocks_in_longest_chain = 0
    private_chain_list = []
    total_run_time = time.time() + 300.0
    while time.time()<total_run_time:
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
                    if message == "start mine":
                        print("Mining message received at adversary")
                        mining_started = True
        else:
            time.sleep(2)
            while time.time()<total_run_time:
                # wait_time_before_generation = random.expovariate(exp_parameter)
                # current_time = time.time()
                generation_time = time.time()+random.expovariate(exp_parameter)
                # gossip_block = True
                while time.time() < generation_time:
                    ready_to_read, ready_to_write, exc = select.select(List_connected_peer ,List_connected_peer, [])
                    all_blocks = set()
                    for s in ready_to_read:
                        try:
                            block_record_binary = s.recv(2048)
                            if block_record_binary ==b'':
                                break
                            else:
                                block_record = pickle.loads(block_record_binary)
                                all_blocks.add(block_record)
                        except:
                            pass
                    for block in all_blocks:
                        
                        if block[0][0] in H:
                            # block is validated by previous if
                                    
                            if block[2] not in H:
                                print("block received from honest peer")    
                                H[block[2]] = block
                                if(block[1]>public_longest_chain):
                                    delta_prev = private_longest_chain - public_longest_chain
                                    public_longest_chain = block[1]
                                    # next statement alert
                                    generation_time= time.time()+ random.expovariate(exp_parameter)
                                    public_chain_last_hash= block[2]
                                    if delta_prev <= 0:
                                        private_chain_last_hash = public_chain_last_hash
                                        private_branch_length = 0
                                        private_chain_list = []
                                        private_longest_chain = public_longest_chain
                                    elif delta_prev ==1:
                                        if len(private_chain_list)>0:
                                            private_last_block =  private_chain_list[-1]
                                            private_chain_list = private_chain_list[:-1]
                                            H[private_last_block[2]] = private_last_block
                                            for w in ready_to_write:
                                                private_last_block_binary = pickle.dumps(private_last_block)
                                                
                                                try:
                                                    w.sendall(block_record_binary)
                                                except:
                                                    pass
                                    elif delta_prev == 2:
                                        if len(private_chain_list)>0:
                                            for block_record in private_chain_list:
                                                block_record_binary = pickle.dumps(block_record)
                                                H[block_record[2]] = block_record
                                                for s in ready_to_write:
                                                    try:
                                                        s.sendall(block_record_binary)
                                                    except:
                                                        pass
                                            private_branch_length= 0
                                            private_chain_list=[]
                                    else:
                                        if len(private_chain_list)>0:
                                            private_last_block =  private_chain_list[0]
                                            private_chain_list = private_chain_list[1:]
                                            H[private_last_block[2]] = private_last_block
                                            for w in ready_to_write:
                                                
                                                private_last_block_binary = pickle.dumps(private_last_block)
                                                try:
                                                    # time.sleep(random.random(0,2))
                                                    w.sendall(block_record_binary)
                                                except:
                                                    pass


                                                                      


                # //case when adversary finds the block in next few lines
            
                delta_prev = private_longest_chain - public_longest_chain
                private_new_block = (private_chain_last_hash, "ab",generation_time)
                # hash_new_block
                hash_new_block= hashlib.sha256(repr(private_new_block).encode('utf-8')).hexdigest()[-4:]
                private_longest_chain+=1
                private_chain_last_hash = hash_new_block
                private_block_record = (private_new_block, private_longest_chain,hash_new_block, 'a')
                print("block generated at adversary")
                private_branch_length+=1
                private_chain_list.append(private_block_record)
                if delta_prev <= 0 and private_branch_length == 2:
                    for block_record in private_chain_list:
                        block_record_binary = pickle.dumps(block_record)
                        H[block_record[2]] = block_record
                        for s in ready_to_write:
                            try:
                                s.sendall(block_record_binary)
                            except:
                                pass

                    private_branch_length= 0
                    private_chain_list=[]

                # private_chain_last_hash = 
                # new_block = (hash_of_the_longest_block,"ab",generation_time)
                # hash_new_block= hashlib.sha256(repr(new_block).encode('utf-8')).hexdigest()
                # temp_hash = hash_new_block[-4:]
                # if temp_hash  not in H:
                #     hash_new_block = temp_hash
                # current_longest_chain +=1
                # hash_of_the_longest_block = hash_new_block
                # new_block_record =(new_block,current_longest_chain,hash_new_block)
                # print("Block Generated at peer = ", end="")
                # print(peer_id)
                # total_blocks_recorded+=1
                # #print(peer_id)
                # H[hash_new_block] = new_block_record
                # new_block_record_binary = pickle.dumps(new_block_record)
                # for s in ready_to_write:
                #     try:
                #         time.sleep(random.random(0,2))
                #         s.sendall(new_block_record_binary)
                #     except:
                #         pass
    
    print("mining mining factors at adversary ")
    # print(current_longest_chain)
    # utilization =current_longest_chain/len(H)
    # print(utilization)
    # storing_dir='dumps_for_itime_'+str(itime)+'_numclients_'
    # # +str(sys.argv[3])

    # if(os.path.exists(storing_dir) == False):
    #   os.makedirs(storing_dir)
    # pickle_outfile_location=storing_dir+'/'+str(peer_id)+'_pickle_dump'
    # pickle_outfile=open(pickle_outfile_location,'wb')
    # pickle.dump(H,pickle_outfile)
    # print("Length of the longest chain")
    # print(private_longest_chain)
    honest_blocks = 0
    attacker_blocks = 0
    for key,value in H.items():
        if value[3] == 'a':
            attacker_blocks+=1
        else:
            honest_blocks+=1
    hstr = str(honest_blocks) +": honest blocks"
    astr = str(attacker_blocks) +": attacker blocks"
    # print(peer_id)
    print(hstr)
    print(astr)
    print(H)
    utilization=public_longest_chain/len(H)
    print(utilization)
    print(public_longest_chain)
    print(len(H))

    # print(" number of blocks generated by adversary")
    # count = 0
    # print(H)
    # print(len(H))
    # print("number of honest blocks")
    # print(honest_blocks)
    # print("number of attacker blocks")
    # print(attacker_blocks)
    # while (private_chain_last_hash != "9e1c"):
    #     try:
    #         if H[private_chain_last_hash][3]== 'a':
    #             count+=1
    #         private_chain_last_hash = H[private_chain_last_hash][0][0]
    #     except:
    #         pass
    # print(count)

# itime=15

# def start_adversary(hashpower):
    # itime = 5
    # globallambda = 1.0/itime
    # adversary_lambda = hashpower * globallambda
    # start_adversary(adversary_lambda)
hashpower = 0.2
print(hashpower)
itime = 10.0
glambda = 1/itime
clambda = hashpower * glambda
start_adversary(clambda)

