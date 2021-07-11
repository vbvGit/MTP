import pandas as pd

# Function to compute the Final slot for given threshold
def computeFinalSlot(time,thresh):
    # Stores the final slot with maximum time
    start = 25
    end = -1

    for  i in range(len(time)):
        if time[i]>=thresh:
            start = min(i,start)
            end = max(i,start)
    if end != -1 and start != 25:
        return [start,end]
    return []

# Function to compute the threshold for freelancers
def getThreshFreelancers(n):
    # Initial threshold percentage = 100%
    thresh = 1

    # Set to store the number of freelancers from range [50% * n to 100% * n]
    n_thresh = set()

    # Compute the number of freelancers as per threshold eg 50% 10 = 5
    while thresh>=0.5:
        n_thresh.add(int(thresh*n))
        thresh-=0.1
    return n_thresh

# Function to compute the common time slot between all freelancers
def getCommonSlots(slots):

    # Total minutes in a day can be from 0-24
    time_slot = [0 for i in range(24+1)]

    # For each slot  +=1 for each hour from start to end of slot T.C = O(24*len(slots))
    for slot in slots:
        start = slot[0]
        end  = slot[1]
        while start<=end:
            time_slot[start]+=1
            start+=1

    # To store all the common slots found for the given number of threshold free lancers as key
    common_slots = {}

    # Number of threshold freelancers to look for [60% of total freelancers to 100% of total freelancers]
    n_thresh = getThreshFreelancers(len(slots))

    # Check if the common slot is available for the calculated thresholds
    for threshold in n_thresh:
        commonslot = computeFinalSlot(time_slot,threshold)

        # If available print and return
        if commonslot != []:
            print(f"The common slot which is common among {threshold} freelancers is : {commonslot}.")
            common_slots[threshold] = commonslot
        else:
            # If no slot available print
            print(f"No common slot found which is common among {threshold} freelancers.")

    return common_slots


# Driver code to find the slots from excel and compute the the common slot
def driver(filename):
    df_dev=pd.read_excel(filename)
    slot_xl = df_dev["slot"]
    slots = []
    for slot in (slot_xl):
        s = slot.split(',')
        slots.append([int(s[0]),int(s[1])])

    common_slots = getCommonSlots(slots)

driver("workers.xlsx")