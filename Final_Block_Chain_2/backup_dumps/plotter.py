import matplotlib.pyplot as plt,sys


def format_list(file_contents):
	new_file_contents=[]
	for i in file_contents:
		temp=i[:]
		new_file_contents.append(temp.split('\n')[0])
	return new_file_contents

file_name=sys.argv[1]

file_contents=[]
with open(file_name,'r') as f:
	file_contents=f.readlines()


file_contents=format_list(file_contents)
title=file_contents[0]
x_label=file_contents[1].split(' ')[0]
y_label=file_contents[1].split(' ')[1]


data_x=[]
data_y=[]

for i in range(2,len(file_contents)):
	data_x.append(int(file_contents[i].split(' ')[0]))
	data_y.append(int(file_contents[i].split(' ')[1]))

plt.plot(data_x,data_y)

plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(title)

plt.show()
