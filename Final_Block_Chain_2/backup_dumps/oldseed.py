import select, socket, time, sys
def convert_string_to_iplist(string):
    return string.split("-")[1:]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) #So that seed does not keep waiting
try:
	server.bind(('', 46680))#binded to port 5000
except:
	print('Port number 46680 occupied. Please close the port')
	exit()
server.listen(100)#can queue upto 1000 requests
inputs = [server]
client_list=""#empty client list..will be filled as the client nodes contact the seed node
print("Server running on port ",server.getsockname()[1])
totalclients = int(sys.argv[1])
count = 0
flag = 0
print(type(totalclients))
#exit(0)
while True:
    readable, writable, exceptional = select.select(inputs,[], [])
    for s in readable:
        connection, client_address = s.accept()
        count+=1
        print(client_address , " connected!")
        print(count)
        client_port=connection.recv(1024)  
        try:
            connection.sendall(client_list.encode('UTF-8'))
        except:
            print("IP addresses not sent to "+client_address[0])
        client_list=client_list+"-"+str(client_address[0])+"@"+str(client_port.decode('UTF-8'))
        connection.setblocking(0)
        if count==totalclients:
            time.sleep(3)
            message = "start mine"
            message = pickle.dumps(message)
            connection.sendall(message)
            flag = 1
            break
    if flag == 1:
        time.sleep(5)
        #  we may have to close or shutdown connection with all peers 
        break 





