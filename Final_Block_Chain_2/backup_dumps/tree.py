import pydot,sys,pickle

dump_file_name=sys.argv[1]

file_ojbect=open(dump_file_name,'rb')
H=pickle.load(file_ojbect)

blockchain=pydot.Dot(graph_type='digraph')

for i in H:
	blockchain.add_node(pydot.Node(i+'\n'+str(H[i][1])))

for i in H:
	if(i!='9e1c'):
		new_block_string=str(i)+'\n'+str(H[i][1])
		prev_block_string=str(H[i][0][0]) + '\n' + str(H[H[i][0][0]][1])
		edge=pydot.Edge(new_block_string,prev_block_string)
		blockchain.add_edge(edge)

blockchain.write_png('tree.png')
