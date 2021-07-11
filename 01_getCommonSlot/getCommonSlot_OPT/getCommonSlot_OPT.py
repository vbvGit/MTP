import pandas as pd

# Function to compute the Final slot for given threshold
def computeFinalSlot(time,thresh):
    # Stores the final slot with maximum time
    start = -1
    end = -1

    # Pointers to check the current maximum slot
    i = -1
    j = -1

    # To compare the next valid slot with the previous maximum
    curMaxTime = 0 

    # Loop through the time array in order to get the valid slot and update the final slot start and end if end-start+1 > curMaxTime
    while i<len(time):
        if time[i]>=thresh:
            j = i+1
            while j<len(time) and time[j]>=thresh:
                j+=1
            if j-i>curMaxTime:
                start = i
                end = j-1
                curMaxTime = j-i
            if j<len(time):
                i = j
            else:
                break
        else:
            i+=1

    # Re conver the start and end to its original form i.e MMMM -> HHMM
    if end != -1 and start != -1:
        s_hour = start//60
        s_minutes = start%60
        start = s_hour*100+s_minutes

        e_hour = end//60
        e_minutes = end%60
        end = e_hour*100+e_minutes

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

# Function to preprocess the original time slots HHMM -> MMMM
def getPreprocessedSlots(slots):
    res = []
    for slot in slots:
        # Convert start time to minutes : HHMM -> 60*HH+MM
        s_hour = slot[0]//100
        s_minutes = slot[0]%100
        start = s_hour*60+s_minutes

        # Convert end time to minutes : HHMM -> 60*HH+MM
        e_hour = slot[1]//100
        e_minutes = slot[1]%100
        end = e_hour*60+e_minutes

        # Update preprocessed slots
        res.append([start,end])
    return res

# Function to compute the common time slot between all freelancers
def getCommonSlots(slots):
    # Preprocess the given slots in standard HHMM format to MMMM format
    preprocessed_slots = getPreprocessedSlots(slots)

    # Total minutes in a day can be from 0000 : 12AM to 1439 : 11:59PM
    time_slot_minutes = [0 for i in range(24*60+1)]

    # For each slot just mark the start marker i.e +=1 and the end marker i.e -=1 : T.C = O(len(slots))
    for slot in preprocessed_slots:
        # Mark the start time for given slot
        time_slot_minutes[slot[0]]+=1

        if slot[1]+1<len(time_slot_minutes):
            # Mark the end time for given slot
            time_slot_minutes[slot[1]+1]-=1


    # Prefix sum of the time_slot_minutes array in order to compute the count of slots in which that minute appeared.
    # Example if minute 15 -> 0015AM was a part of 10 queries then time_slot_minutes[15] = 10
    for i in range(1,len(time_slot_minutes)):
        time_slot_minutes[i]+=time_slot_minutes[i-1]

    # To store all the common slots found for the given number of threshold free lancers as key
    common_slots = {}

    # Number of threshold freelancers to look for [60% of total freelancers to 100% of total freelancers]
    n_thresh = getThreshFreelancers(len(slots))

    # Check if the common slot is available for the calculated thresholds
    for threshold in n_thresh:
        commonslot = computeFinalSlot(time_slot_minutes,threshold)

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
    start_time = df_dev["start"]
    end_time = df_dev["end"]
    slots = []
    for i in range(len(start_time)):
        slots.append([start_time[i],end_time[i]])

    common_slots = getCommonSlots(slots)

# slot = [[900,1100],[1200,1500],[1200,1400],[1100,1500],[1300,1700],[1400,1600]]
# print(getCommonSlots(slot))

# print("\n------------------------------------------------------------------------------\n")
# slot = [[930,1140],[1215,1512],[1201,1429],[1100,1500],[1310,1730],[1420,1600]]
# print(getCommonSlots(slot))

# print("\n------------------------------------------------------------------------------\n")

# slot = [[930,1030],[1030,1245],[1130,1230],[1231,1330],[1331,1430]]
# print(getCommonSlots(slot))
driver("workers.xlsx")