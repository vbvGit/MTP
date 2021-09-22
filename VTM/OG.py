import numpy as np
import pandas as pd
import random
import statistics
import WCB
import sys
import time

class SIM():
    def __init__(self):
       self.currCandidates = list()
       self.currTasks = list()
       self.taskCandidateMapper = {}
       self.clock = 0
       self.time = 10
       self.task_noBudget = dict()
       self.task_timeout = set()
       self.candidate_noBudget = dict()
       self.round=1
       cols1=["rounds","candidates","tags","potential","payments","alpha","l","ageingFactor","p_init","elected"]
       self.potDt=pd.DataFrame(columns=cols1)
       cols2=["rounds","tasks","budgets","completed"]
       self.taskStat=pd.DataFrame(columns=cols2)
        # self.completedTasks={}
       self.status={}
       self.leftBudgets={}
       self.candPay={}
       self.candElected={}
       self.potDt['alpha']=0
       self.potDt['l']=0
       self.potDt['ageingFactor']=0
       self.potDt["p_init"]=0
        
        
    def getUnarrivedCandidates(self):
        unarrivedCandidates = []
        for candidate in self.currCandidates :
            if self.clock < candidate.arrivalTime :
                unarrivedCandidates.append(candidate.name)
        return unarrivedCandidates
    
    def getUnarrivedTasks(self):
        unarrivedTasks = []
        for task in self.currTasks :
            if self.clock < task.arrivalTime :
                unarrivedTasks.append(task.name)
        return unarrivedTasks
    
    
    def startUp(self, C, T,size):
        # for adding the C and T
        # C is set of Candidates which are stored :: numpy
        # T is set of Task which are stored   :: numpy

        # adding the candidates
        # size, _ = C.shape
        for c in range(size):
            data = list(C[c])
            newCandidate = Candidate(data)
            self.currCandidates.append(newCandidate)

        # adding the tasks
        sizeT, _ = T.shape
        for t in range(sizeT):
            data = list(T[t])
            newTask = Task(data)
            self.currTasks.append(newTask)

    def skill_matching(self, task, candidate):
        def checkV2(key1, key2):
            arr1 = key1.split()
            arr2 = key2.split()
            for a1 in arr1:
                if a1 in arr2:
                    return True
            return False

        skill_demand = []
        skill_can = []
        skill_demand = task.trimedSkill
        skill_demand = skill_demand.split(",")
        skill_can = candidate.skills
        skill_can = skill_can.split(",")
        skillset = set()
        covered = set()
        for skill in skill_demand:
            isSkillFound = False
            for rs in skill_can:
                if (checkV2(skill, rs)):
                    isSkillFound = True
                    skillset.add(rs)
                    covered.add(skill)
                    break

        return list(covered), list(skillset)

    def trimUnwanteds(self, source, unwanteds):
        # creating list of each skills
        tmp = source.split(",")
        unwanteds = unwanteds.split(",")
        # removing the unwanteds
        tmp = [obj for obj in tmp if obj not in unwanteds]
        # list to comma seperated list
        tmp = ",".join(tmp)
        return tmp

    
    def utilityV2(self,task,candidate):
         
        matchedSkillTask, matchedSkillCandidate = self.skill_matching(
            task, candidate)
        reward_perHour = candidate.price
        duration_totalHour = task.duration
        net_reward=(reward_perHour*duration_totalHour)
        taskBudget = task.remaningBudget
        return (taskBudget-net_reward), matchedSkillTask, matchedSkillCandidate
        


    def updateWorkingCandidatesStatus(self):
        candList=[]
        tags=[]
        plevels=[]
        rounds=[]
        # status : idle and hasBudget
        for candidate in self.currCandidates:
            if candidate.isIdle == False:
                candidate.utilisedTime = candidate.utilisedTime + 1
            # when candidate is assigning some task ,clock_taskCompletion  will be setted at that time
            elif self.clock >= candidate.clock_taskCompletion:
                candidate.isIdle = True
                pLevel,r=0,self.round
            # print("test----pLevel  ",pLevel)
            tags.append(candidate.tag)
            plevels.append(pLevel)
            rounds.append(r)
            candList.append(candidate.name)
            
        self.potDt["candidates"]=candList
        self.potDt["tags"]=tags
        self.potDt["potential"]=plevels
        self.potDt["rounds"]=rounds
           

    def getAssignableCandidates(self):
        assignableCandidate = []
        for candidate in self.currCandidates:
            # task is arrived into the system
            arrived = (self.clock >= candidate.arrivalTime)
            hasTimeBudget = (candidate.duration - candidate.utilisedTime) > 0
            if not arrived:
                continue
            if not hasTimeBudget:
                if candidate.name not in self.candidate_noBudget :
                    self.candidate_noBudget[candidate.name] = [candidate.nme,candidate.budget,candidate.utilisedTime]
                continue
            if candidate.isIdle:
                assignableCandidate.append(candidate)
        return assignableCandidate

    def getCost(self, task, candidate):
        candidateCharge = candidate.price
        taskDuration = task.duration
        priceRequiredforCandidate = candidateCharge*taskDuration
        self.candPay[candidate.name]=priceRequiredforCandidate
        return priceRequiredforCandidate

    def getEligibleCandidatesForTask(self, task, candidates):
        # filteration is based on the price
        eligibleCandidates = []
        for candidate in candidates:
            priceRequiredforCandidate = self.getCost(task, candidate)
            if priceRequiredforCandidate == 0:
                continue
            if priceRequiredforCandidate <= task.remaningBudget:
                eligibleCandidates.append(candidate)
        return eligibleCandidates

    def updateCompletedTaskStatus(self):
        for key, value in self.taskCandidateMapper.items():
            # taskName :[[candidates,...],[utilites,...],isCompleted,executionStartsTime,timeTobeCompleted,waitingtime]
            isCompleted = value[2]
            timeTobeCompleted = value[4]
            executionStartsTime = 3
            if isCompleted:
                # task is already completed
                continue
            if not (timeTobeCompleted == None) and (self.clock >= timeTobeCompleted):
                # task is completed but status is not updated
                # calculating the waiting time
                waitingTime = self.clock - executionStartsTime
                # updating the status
                self.taskCandidateMapper[key][2] = True  # task completed
                self.taskCandidateMapper[key][5] = waitingTime
                print("One task is completed")
                self.status[key]=1

    def getAssignableTasks(self):
        # get the list of task which can be asignable from curr logical time
        assignableTask = []
        for task in self.currTasks:
            # task is arrived into the system
            arrived = (self.clock >= task.arrivalTime)
            # if assigned deadline will not be meet
            assignable = ((self.clock + task.duration) <=
                          (task.arrivalTime + task.duration + task.fTime))
            completed = task.isCompleted  # task is compleated
            if not arrived:
                continue
           
            elif completed:
                continue
            elif not assignable:
                    self.task_timeout.add(task.name)
            else:
                if task.trimedSkill == "":
                    # all skills are assigned, no need to asign any skills
                    continue
                else:
                    if task.remaningBudget < 1:
                        # no budget is remaining
                        if task.name not in self.task_noBudget:
                            self.task_noBudget[task.name] = [
                                task.name, task.skillsBudget, task.remaningBudget]

                            print("no budget is remaning..............")
                        continue
                    else:
                        assignableTask.append(task)
        return assignableTask

    
    def selection_OUR(self, task, elegibleCandidates):
        electedCandidate = None
        min_util_fact = -9999.00
        for e in elegibleCandidates:
            utilFact,_, _ = self.utilityV2(task, e)
            if min_util_fact < utilFact:
                min_util_fact = utilFact
                electedCandidate = e
                self.candElected[e.name]=1
            else:
                  self.candElected[e.name]=0
        return electedCandidate

    def update(self, selectionPolicy):

        assignableTask = self.getAssignableTasks()
        assignableCandidates = self.getAssignableCandidates()
        for task in assignableTask:
            if len(assignableCandidates) > 0:
                # assignment may possible for candidates
                elegibleCandidates = self.getEligibleCandidatesForTask(
                    task, assignableCandidates)
                if len(elegibleCandidates) == 0:
                    continue
                electedCandidate = selectionPolicy(task, elegibleCandidates)
                utilFact, matchedTaskSkills, matchedCandidateSkills = self.utilityV2(
                    task, electedCandidate)
                if utilFact < 0:
                    print("Negative is found! ", utilFact)
                if task.name in self.taskCandidateMapper:
                    c = self.taskCandidateMapper[task.name][0]
                    u = self.taskCandidateMapper[task.name][1]

                    c.append(electedCandidate.name)
                    u.append(utilFact)
                else:
                    # mapper Key Value Pair's descriptions
                    # taskName :[[candidates,...],[utilites,...],isCompleted,executionStartsTime,timeTobeCompleted,waitingTime]
                    self.taskCandidateMapper[task.name] = [
                        [electedCandidate.name], [utilFact],False, self.clock, None, None]

                # update skillset of task
                matchedTaskSkills = ",".join(matchedTaskSkills)
                # print(task.trimedSkill, ":", matchedTaskSkills)
                task.trimedSkill = self.trimUnwanteds(
                    task.trimedSkill, matchedTaskSkills)
                #print("updated trimmed skills :", task.trimedSkill)
                if task.trimedSkill == "":
                    timeTobeCompleted = self.clock + task.duration
                    # meta data to update task completion
                    self.taskCandidateMapper[task.name][4] = timeTobeCompleted
                    print("****one task will be complete", timeTobeCompleted)

                # update remaning budget of the task
                task.remaningBudget = task.remaningBudget - \
                    self.getCost(task, electedCandidate)

                # selectedCandidate.skills=self.trimUnwanteds(selectedCandidate.skills,matchedSkillCandidate)
                electedCandidate.clock_taskCompletion = self.clock + task.duration
                self.leftBudgets[task.name]=task.remaningBudget

            else:
                # assignment is not possible
                pass
        self.updateCompletedTaskStatus()
        self.updateWorkingCandidatesStatus()

    def summary(self):
        result = dict()
        totalTask = len(self.currTasks)
        sucessfullCompletedTask = 0
        waitingTimes = []
        utilities = [] #from net reward
        totalcandidate = len(self.currCandidates)

        for key, val in self.taskCandidateMapper.items():
            pass
            task = key
            utility = sum(val[1]) 
            #utility_cnt = statistics.mean(val[1]) 
            # taskName :[[candidates,...],[utilites,...],isCompleted,executionStartsTime,timeTobeCompleted,waitingtime]
            status = val[2]
            waitingTime = -1
            if status:
                sucessfullCompletedTask = sucessfullCompletedTask + 1

                waitingTime = val[5]
                waitingTimes.append(waitingTime)
                utilities.append(utility)
            result[task] = [status, utility, waitingTime]
        sucessfullRatio = (sucessfullCompletedTask*1.0)/(len(self.currTasks) - len(self.getUnarrivedTasks()))
        print("-----------RESULT--------------")
        print(result)
        print("-------------------------------")
        wa_utilityFactor = 0
        wa_waitingTime = 0
        
        if len(waitingTimes) > 0:
            wa_utilityFactor = statistics.mean(
                utilities)*sucessfullRatio
            wa_waitingTime = statistics.mean(
                waitingTimes)*sucessfullRatio
            
        
    
        
        result_status = dict()
        result_status["totalTask"]=totalTask
        result_status["totalcandidate"]=totalcandidate
        result_status["sucessfullCompletedTask"]=sucessfullCompletedTask
        result_status["sucessfullRatio"]=sucessfullRatio
        result_status["wa_utilityFactor"]=wa_utilityFactor
        result_status["wa_waitingTime"]=wa_waitingTime
        result_status["self.time"]=self.time
        
        print(result_status)
      

        print("Task has lost Budget : ", len(self.task_noBudget))
        print("Task timeout : ", len(self.task_timeout))
        print("Candidates  has no time : ", len(self.task_noBudget))
        print("Unarrived task count : ", len(self.getUnarrivedTasks()))
        print("Unarrived candidate count : ", len(self.getUnarrivedCandidates()))

    def run(self, time=50):
        self.time = time
        j=0
        self.taskStat["tasks"]=[x.name for x in self.currTasks ]
        tot_ca=0
        budgetLeft=0
        cols=["candidates","elected"]
        caList=[]
        budgetList=[]
        initialBudget=[]
        idx=0
        elected_prev=pd.DataFrame(columns=cols)
        for i in range(self.time):
            self.update(self.selection_OUR)
            j=j+1

            if j==50:
                print("    ",self.round,"---round completes")
                
                self.taskStat['completed']=self.taskStat.tasks.astype(str).map(self.status)
                self.taskStat['budgets']=self.taskStat.tasks.astype(str).map(self.leftBudgets)
                
                
                self.potDt["payments"]=self.potDt.candidates.astype(str).map(self.candPay)
                self.potDt["elected"]=self.potDt.candidates.astype(str).map(self.candElected)
                
                
                self.potDt.fillna(0, inplace=True)
                self.taskStat.fillna(0, inplace=True)
                
                # # Remove any row with all zeroes
                series = (self.potDt != 0).any(axis=1)
                self.potDt=self.potDt.loc[series]
                self.potDt.to_excel("test.xlsx",index=False)

                # print("shape is--",self.potDt.shape)
                 # Total number of rounds that have happened
                tot_num_of_rounds = (self.potDt.iloc[0,0])
                
                elected_curr=self.potDt[["candidates","elected"]]
               
                
                # Get the remaining budget from the completed tasks
                task_status=self.taskStat.shape[1]-1
                bd=[]   
                # print("*****Task shape****",self.taskStat.shape)
                for i in range(0,self.taskStat.shape[0]):
                    if self.taskStat.iloc[i,task_status]==1:
                        bd.append(float(self.taskStat.loc[i,"budgets"]))
                        # print("Appended budget-->",bd)


                budgetLeft=sum(bd)
                initialBudget.append(budgetLeft)
                # print("Initial budget-->",budgetLeft)
                
                
                self.leftBudgets={}
                self.status={}
                self.candElected={}
                self.candPay={}
                
                CA,retained, dropOuts,_ = WCB.naiveRetention(tot_num_of_rounds,self.potDt,self.taskStat,elected_curr,elected_prev,budgetLeft)
                
                curCan=[]
                curCan=self.currCandidates.copy()
                for i in dropOuts:
                    # print(i)
                    curCan.pop(i)
                    curCan.insert(i,-1)
                #     self.currCandidates.pop(i)
                
                print("Current candidates-->",len(self.currCandidates)-len(dropOuts))
                
                idx_= 0
                for i in range(0,len(curCan)):
                    if curCan[i]!=-1:
                        # print("*******",curCan[i])
                        self.currCandidates[idx_]=curCan[i]
                        idx_=idx_+1
                idx=idx+idx_
                        
                        
                cols=["retained","pot","ca"]
                results=pd.DataFrame(columns=cols)
                results["retained"]=retained
                results["pot"]=0
                results["ca"]=results.retained.map(CA)
                
                
                print("Drop outs---->",len(dropOuts))
                print("Retained  -->",len(retained))
                #Removing the drop outs 
                # for i in dropOuts:
                #     # self.currCandidates=np.delete(self.currCandidates,i-1,0)
                #     self.potDt.drop(i,inplace=True)
                
                # print("current candidates counts--->",len(self.potDt))
                tot_ca=sum(results["ca"])  
                print("ca incurred---->",tot_ca)
                caList.append(tot_ca)
                
                results.to_excel("results//rest//WCB_results"+str(self.time)+"_"+str(self.round)+".xlsx",index=False)
                # self.potDt.to_excel("results//sigmoid//candidates_potential_Sig_"+str(time)+"_"+str(self.round)+".xlsx",index=False)
                # self.potDt.to_excel("results//normal//candidates_potential_Norm_"+str(time)+"_"+str(self.round)+".xlsx",index=False)
                # self.taskStat.to_excel("results//normal//task_status_Norm_"+str(time)+"_"+str(self.round)+".xlsx",index=False)
                # self.taskStat.to_excel("results//sigmoid//task_status_Sig_"+str(time)+"_"+str(self.round)+".xlsx",index=False)
                
                elected_prev=elected_curr
                
                self.round=self.round+1
                j=0
                bLeft=budgetLeft-tot_ca
                budgetList.append(bLeft)


            self.clock = self.clock + 1
            
            print(i)
        print("Initial budgets--->",initialBudget)
        print("Final budget after this round-->",budgetList)
        print("Final CA--->",caList)
      
        ag.summary()
        
        
        
class Task():
    def __init__(self, data):
        self.name = data[0]
        self.skill = data[1]
        self.skills_demand = int(data[2])
        self.trimedSkill = data[3]
        self.trimedSkillCount = int(data[4])
        self.skillsBudget = float(data[5])
        self.remaningBudget = float(data[5])
        self.duration = int(data[6])
        self.arrivalTime = 1

        # self.arrivalTime = int(data[7])
        self.fTime = 200
        self.isCompleted = False


class Candidate():
    def __init__(self, data):
        self.name = data[0]
        self.skills = data[3]
        self.price = float(data[1])
        self.sucessRate = float(data[4])
        self.skillCount = int(data[2])
        self.rewardPerSkill = int(data[10])
        self.bias = float(data[7])
        self.normSucessRate = float(data[9])
        if self.normSucessRate != self.normSucessRate:
            self.normSucessRate = 0.001

        self.duration = int(data[8])
        self.arrivalTime = 1
        # self.arrivalTime = int(data[12])

        self.isIdle = True
        self.utilisedTime = 0
        self.clock_taskCompletion = 0
        self.successRatio=0
        self.userRating=float(data[5])
        self.alpha=float(data[6])
        self.tag=data[11]
        
tasks = pd.read_excel('datasets//sample_tasks_updated.xlsx').to_numpy()
candidates = pd.read_excel('datasets//merged_candidates.xlsx').to_numpy()
print ("Runs =  ",sys.argv[1])
size=int(sys.argv[2])
print("Size of candidaters == ",size)

start_time=time.time()

ag = SIM()
ag.startUp(candidates, tasks,size)
ag.clock = 1
c = ag.getAssignableCandidates()
print(len(c))
t = ag.getAssignableTasks()
print(len(t))
# ect = ag.getEligibleCandidatesForTask(t[0], c)
# print(len(ect))
# ag.update(ag.selection_random)
# print(ag.taskCandidateMapper)
ag.run(int(sys.argv[1]))

end_time=time.time()

print("Exceution time--->",end_time-start_time)