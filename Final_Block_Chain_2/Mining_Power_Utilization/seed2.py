import select, socket, time, sys,pickle
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) #So that seed does not keep waiting
try:
	server.bind(('', 0))#binded to port 5000
except:
	print('Port number 46680 occupied. Please close the port')
	exit()
server.listen(100)#can queue upto 1000 requests
inputs = [server]
client_list="a"#empty client list..will be filled as the client nodes contact the seed node
print("Server running on port ",server.getsockname()[1])
totalclients = int(sys.argv[1])
count = 0
flag = 0
# print(type(totalclients))
#exit(0)
all_peer_sockets = []
H= set()
x = 0
while True:
    if x == totalclients:
        break
    readable, writable, exceptional = select.select(inputs,all_peer_sockets, [])
    for s in readable:
        connection, client_address = s.accept()
        count+=1
        print(client_address , " connected!")
        print(count)
        all_peer_sockets.append(connection)
        client_port=connection.recv(1024)  
        # H.add(connection)
        try:
            # if client_list
            connection.sendall(client_list.encode('UTF-8'))

        except:
            print("IP addresses not sent to "+client_address[0])
        client_list=client_list+"-"+str(client_address[0])+"@"+str(client_port.decode('UTF-8'))
        connection.setblocking(0)
    if count==totalclients:
        time.sleep(5)
        message = "start mine"
        message = pickle.dumps(message)
        # connection.sendall(message)
        for z in writable:
            if z not in H:
                # print("haha ")
                z.sendall(message)
                H.add(z)
                x = x+ 1




