import socket,select,datetime,threading,random,time,sys,os,pickle,hashlib
hashpower =float(sys.argv[5])
def start_adversary(exp_parameter):
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
    genesis_block = (("0","ab",0.0),1,"9e1c",'h')
    #first three columns are block details
    H["9e1c"] = genesis_block
    hash_of_the_longest_block = "9e1c"
    total_blocks_recorded = 1
    total_blocks_required = int(sys.argv[4])
    private_longest_chain = 1
    public_longest_chain = 1
    H["9e1c"] = genesis_block
    public_chain_last_hash =  "9e1c"
    private_chain_last_hash = "9e1c"
    private_branch_length = 0
    # adversary_blocks_in_longest_chain = 0
    private_chain_list = []
    ready_to_write=[]
    while total_blocks_recorded <= total_blocks_required:
        # print("outside should be   1")
        # print(total_blocks_recorded)
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
            while total_blocks_recorded <= total_blocks_required:
                current_time = time.time()
                generation_time =time.time()+random.expovariate(exp_parameter)
                while time.time() < generation_time:
                    # print(total_blocks_recorded)
                    ready_to_read, ready_to_write, exc = select.select(List_connected_peer ,List_connected_peer, [])
                    all_blocks = set()
                    for s in ready_to_read:
                        # blocks received from others
                        try:
                            block_record_binary = s.recv(2048)
                            if block_record_binary ==b'':
                                break
                            else:
                                block_record = pickle.loads(block_record_binary)
                                # block_record_item = [block_record, s]
                                all_blocks.add(block_record)
                        except:
                            pass
                    for block in all_blocks:
                        # block = block_record_item[0]
                        # received_socket = block_record_item[1]
                        if block[0][0] in H:
                            # block is validated by previous if
                            if block[2] not in H:
                            # current block not in database   
                                H[block[2]] = block
                                total_blocks_recorded+=1
                                print("block received")
                                for w in ready_to_write:
                                    # Received block broadcast 
                                    # if w is not received_socket:
                                    block_record_binary = pickle.dumps(block)
                                    try:
                                        delay = random.uniform(0.2,0.5)
                                        time.sleep(delay)
                                        w.sendall(block_record_binary)
                                    except:
                                        pass 
                                # if(block[1]>public_longest_chain):
                                delta_prev = private_longest_chain - public_longest_chain
                                assert block[3] == 'h', "adversary did not have record of his own block. strange!!! "
#                                     # next statement alert
                                public_longest_chain = max(block[1],public_longest_chain)
                                # assert delta_prev >= 0, "delta_prev should not be negative"
                                if public_longest_chain == block[1]: 
                                    print(delta_prev)
                                    if delta_prev <= 0:
                                        generation_time= time.time()+ random.expovariate(exp_parameter)
                                        private_chain_last_hash = block[2]
                                        public_chain_last_hash= block[2]
                                        private_branch_length = 0
                                        private_chain_list = []
                                        private_longest_chain = block[1]
                                        public_longest_chain = block[1]

                                    elif delta_prev ==1:
                                        print("this was assertion  1 earlier")
                                        print(len(private_chain_list))
                                        try:
                                            private_last_block =  private_chain_list[0]
                                            private_chain_list = private_chain_list[1:]
                                            private_longest_chain+=1
                                            # private_chain_last_hash = 
                                            # private_longest_chain = public_longest_chain
                                            for w in ready_to_write:
                                                private_last_block_binary = pickle.dumps(private_last_block)
                                                try:
                                                    w.sendall(private_last_block_binary)
                                                except:
                                                    pass
                                        except:
                                            pass
                                        
                
                                    elif delta_prev == 2:
                                        # assert len(private_chain_list)>0, "private chain should be non empt 1y"

                                        for block_record in private_chain_list:
                                            private_block_record_binary = pickle.dumps(block_record)
                                            for s in ready_to_write:
                                                try:
                                                    s.sendall(private_block_record_binary)
                                                except:
                                                    pass
                                        private_longest_chain+=len(private_chain_list)
                                        # public_longest_chain = max(private_longest_chain, public_longest_chain)
                                        private_branch_length= 0
                                        private_chain_list=[]
                                    # public_longest_chain = private_longest_chain
                                    # public_chain_last_hash = private_chain_last_hash
                                    else:
                                        # assert len(private_chain_list)>0, "private chain should be non empty 2"
                                        try:
                                            private_last_block =  private_chain_list[0]
                                            private_chain_list = private_chain_list[1:]
                                            private_longest_chain+=1
                                            # public_longest_chain = max(public_longest_chain,private_longest_chain)
                                            # H[private_last_block[2]] = private_last_block
                                            private_last_block_binary = pickle.dumps(private_last_block)
                                            for w in ready_to_write:
                                                try:
                                                    time.sleep(random.random(0.1,0.3))
                                                    w.sendall(private_last_block_binary)
                                                except:
                                                    pass
                                        except:
                                            print("deltprev>2")
                                        

                        else:
                            print("Invalid block")
                            print(block)
#                 # //case when adversary finds the block

                # print(total_blocks_recorded)
                delta_prev = private_longest_chain - public_longest_chain
                private_new_block = (private_chain_last_hash, "ab",generation_time)
                hash_new_block= hashlib.sha256(repr(private_new_block).encode('utf-8')).hexdigest()[-4:]
                temp_longest_chain =H[private_chain_last_hash][1]+1
                private_chain_last_hash = hash_new_block
                private_block_record = (private_new_block, temp_longest_chain,hash_new_block, 'a')
                total_blocks_recorded+=1
                H[hash_new_block] = private_block_record
                print("block generated at adversary")
                private_branch_length+=1
                private_chain_list.append(private_block_record)
                # assert delta_prev >= 0, "delta_prev should not be negative 678"
                if delta_prev <= 0 and private_branch_length == 2:
                    for block_record in private_chain_list:
                        block_record_binary = pickle.dumps(block_record)
                        for s in ready_to_write:
                            try:
                                s.sendall(block_record_binary)
                            except:
                                pass
                    private_longest_chain = private_longest_chain+ len(private_chain_list)
                    # public_longest_chain = max(private_longest_chain,public_longest_chain)
                    private_branch_length= 0
                    private_chain_list=[]
                     
                    # public_longest_chain = private_longest_chain
                    # public_chain_last_hash = private_chain_last_hash

    for block_record in private_chain_list:
        block_record_binary = pickle.dumps(block_record)
        for s in ready_to_write:
            try:
                s.sendall(block_record_binary)
            except:
                pass
    final_string="adv"+'_'+str(int(itime)) + '_' + str(hashpower)+'_'+str(len(H))
    pickle_outfile_location = 'pd_'+final_string
    pickle_outfile=open(pickle_outfile_location,'wb+')
    hash_outfile_location='hash_'+final_string
    hash_outfile = open(hash_outfile_location,'wb+') 
    pickle.dump(private_chain_last_hash,hash_outfile)
    pickle.dump(H,pickle_outfile)
    hash_outfile.close()
    pickle_outfile.close()



print(hashpower)
itime = float(sys.argv[3])
glambda = 1/itime
clambda = hashpower * glambda
start_adversary(clambda)



#                 # private_chain_last_hash = 
#                 # new_block = (hash_of_the_longest_block,"ab",generation_time)
#                 # hash_new_block= hashlib.sha256(repr(new_block).encode('utf-8')).hexdigest()
#                 # temp_hash = hash_new_block[-4:]
#                 # if temp_hash  not in H:
#                 #     hash_new_block = temp_hash
#                 # current_longest_chain +=1
#                 # hash_of_the_longest_block = hash_new_block
#                 # new_block_record =(new_block,current_longest_chain,hash_new_block)
#                 # print("Block Generated at peer = ", end="")
#                 # print(peer_id)
#                 # total_blocks_recorded+=1
#                 # #print(peer_id)
#                 # H[hash_new_block] = new_block_record
#                 # new_block_record_binary = pickle.dumps(new_block_record)
#                 # for s in ready_to_write:
#                 #     try:
#                 #         time.sleep(random.random(0,2))
#                 #         s.sendall(new_block_record_binary)
#                 #     except:
#                 #         pass

