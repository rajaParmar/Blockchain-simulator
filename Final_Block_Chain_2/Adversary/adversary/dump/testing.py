import pickle,sys
dump_file_name = sys.argv[1]
hash_file_name = sys.argv[2] 
file_object = open(dump_file_name, 'rb')
longest_chain_hash_object = open(hash_file_name,'rb')
H = pickle.load(file_object)
print(H)
