import pickle,sys
dump_file_name = sys.argv[1]
hash_file_name = sys.argv[2] 
file_object = open(dump_file_name, 'rb')
longest_chain_hash_object = open(hash_file_name,'rb')
H = pickle.load(file_object)

# H = list(H)
Y = []
longest_chain_hash = pickle.load(longest_chain_hash_object)
for x,y in H.items():
    y = list(y)
    y.append(0)
    H[x] = y
H["9e1c"][4] = 1
while longest_chain_hash != "9e1c":
    try:
        H[longest_chain_hash][4] = 1
        longest_chain_hash = H[longest_chain_hash][0][0]
    except:
        print("galat hai bhai")
        exit(0)
count = 0
print(H)
for x,y in H.items():
    if y[4] == 1:
        count+=1
print(count)