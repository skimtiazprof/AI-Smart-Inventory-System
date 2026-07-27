import numpy as np


arr = np.full((2,3,4),9)
#print(arr)



#Eye Function
arr = np.eye(5)
#print(arr)

#Start, Stop, Step
arr = np.arange(1,100,5)
#print(arr)

#Lins Function

arr = np.linspace(1,10,5)
#print(arr)

#Aggregate Function
arr = np.array([  [1,2,3,4,5] ,
                  [4,5,6,7,8]
                  ])

#print(np.sum(arr))

arr = np.array([  [1,2,3,4,5] ,
                  [4,5,6,7,8]
                  ])
#print(np.mean(arr))
#print(np.min(arr))

#print(np.argmin(arr))
#print(np.argmax(arr))

print(np.sum(arr,axis=0))
print(np.sum(arr,axis=1))

