#Filtering ,Saving , Loading
import numpy as np

marks = np.array ([
    [44,55,62,33,66,77] ,
    [100,44,33,66,72,91]
     ])
passStudentsMarks = marks[marks < 50]
#print(passStudentsMarks)
#print(passStudentsMarks[0])
#print(passStudentsMarks[1])
cgrad = marks[(marks>=50)&(marks<70)]
#print(cgrad)

bgrad = marks[(marks>=70)&(marks<80)]
#print(bgrad)

agrad = marks[(marks>=80)&(marks<=100)]
#print(agrad)

#SAVING

np.save("marks" , marks)
#print("savingMarks......)")


np.save("D:\\lenovo\\marks" , marks)
print("savingMarks......)")

#Loading

array = np.load("D:\\lenovo\\marks.npy")
print(array)