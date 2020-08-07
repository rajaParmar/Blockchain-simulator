import  hashlib as h,os,sys,random,socket,select,datetime,threading,random,time  
genesishash ="9e1c" 
merkelroot = "ab"
timestamp = time.time()
numclients = int(sys.argv[1])
hashpower = [random.random() for i in range(5)]
print(hashpower)
s = sum(hashpower)
hashpower = list(map(lambda x:x/s,hashpower))
itime = 6000
globallambda = 1.0/itime
cllambda = list(map(lambda x:x*globallambda,hashpower))
print(cllambda) 
expectedclientime = list(map(lambda x: random.expovariate(x),cllambda))
#expectedclientime = [random.expovariate(x) for x in cllambda]
expectedclientimeinminutes = list(map(lambda x: x/60.0, expectedclientime))
print(expectedclientimeinminutes)
x = ("9e1c",merkelroot,time.time(),1)
y= h.sha256(repr(x[:-1]).encode('utf-8')).hexdigest()
D ={}
D[y] = x
print(y)
print(D)

