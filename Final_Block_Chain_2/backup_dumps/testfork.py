import os
def child(i):
    print(i)
for i in range(200):
    x = os.fork()
    if (x==0):
        child(i)
        exit(0)

       

while True:
    try: 
        os.wait()
    except:
        break
print("all the processes finished")
