import pandas as pd 
import numpy as np

def preprocessTaskData(filename):
    df_dev=pd.read_excel(filename)

    df_dev["Name"]= df_dev["Name"].str.lower()
    df_dev["Skill"]= df_dev["Skill"].str.lower()

    df_dev['x_coord'] = np.random.randint(1, 1000, df_dev.shape[0])
    df_dev['y_coord'] = np.random.randint(1, 1000, df_dev.shape[0])

    df_dev.to_excel("Tasks.xlsx",index = False)


def preprocessApplicantData(filename):
    df_dev=pd.read_excel(filename)

    df_dev["Name"]= df_dev["Name"].str.lower()
    df_dev["Skill"]= df_dev["Skill"].str.lower()

    df_dev['x_coord'] = np.random.randint(1, 1000, df_dev.shape[0])
    df_dev['y_coord'] = np.random.randint(1, 1000, df_dev.shape[0])

    random_hour_start = np.random.randint(0,20, df_dev.shape[0])
    random_mint_start = np.random.randint(0,59, df_dev.shape[0])
    random_slot_start = [hr*100+mint for hr,mint in list(zip(random_hour_start,random_mint_start))]
    random_slot_end = [(hr+3)*100+mint for hr,mint in list(zip(random_hour_start,random_mint_start))]
    df_dev['slot_start'] = random_slot_start
    df_dev['slot_end'] = random_slot_end
    df_dev.to_excel("Applicants.xlsx",index = False)

preprocessTaskData("sample_tasks_updated.xlsx")
preprocessApplicantData("sample_candidates.xlsx")