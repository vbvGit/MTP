import math
task = ["t1","t2","t3","t4","t5","t6"]
locs = [(1,2),(3,5),(5,5),(5,8),(3,1),(6,10)]
taskData = dict(zip(task,locs))
sortedTaskData = {k: v for k, v in sorted(taskData.items(), key=lambda i: math.sqrt((i[1][0]-13)**2 + (i[1][1]-17)**2))}
print(sortedTaskData.keys())

