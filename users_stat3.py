#!/usr/bin/python3.6

import os
import re
from datetime import *
import time
import readline
import pwd
from get_users3 import *
import subprocess
import pandas as pd
from progress.spinner import Spinner
pd.set_option("display.max_rows", None, "display.max_columns", None)

################################
###Get the users list, call data_fr() from get_user3.py file
###############################

list_of_users = data_fr()
print (list_of_users)

user = input('\nprint username you want to get statistic for or type "all" to get statistic for all of users: ')
if user == 'all':
    user = []
    for login_name in list_of_users['Login']:
        user.append(login_name)


t_delta = int(input('for how many days do you wand to see the statistic 1,2,3......100 etc.: '))

################################
###Get the list of the log files
################################

path_log='/var/log/radius/radacct/name_of_log_dir'
file_list = os.listdir(path=path_log)

#############################################################################################
###check if the files contain key string "detail" in it's name  and they are not directiories
#############################################################################################

pattern = re.compile("^detail.*")
log_files=[]
for name_of_file in file_list:
     if pattern.match(name_of_file)!=None and os.path.isfile(path_log+name_of_file)==True:
         log_files.append(name_of_file)
#print(log_files)


############################################################################
###find specific user sessions and put all the information in the dictionary
############################################################################

def final(x):

    pattern = re.compile(x)
    pattern1 = re.compile("User-Name")
    pattern2 = re.compile("Acct-Status-Type")
    pattern3 = re.compile("Event-Timestamp")
    pattern4 = re.compile("^\t")
    pattern5 = re.compile("ASA-TunnelGroupName")
    pattern6 = re.compile("Timestamp")
    pattern7 = re.compile("Acct-Session-Time")


###Create an empty Dataframe

    table1 = pd.DataFrame(columns = ['RussianName','UserName','WhiteIP','GreyIP','TimeStamp','AcctStatusType','Duration','ASATunnelGroup','AcctSessionId','UnixTimeStamp'])

####################################################
###Read log files line by line to the list "events"
####################################################

    for log_file in log_files:
        with open(path_log+log_file) as log:
         events = log.read().splitlines()
#         print(events)                                  ###!

   
#####################################################
###split events for specific user from other users events
#####################################################
         i=0
         for event in events:
             user_events=[]
             if pattern.search(event)!=None and pattern1.search(event)!=None:
                   ii=i
                   while pattern4.match(events[ii])!=None: 
                       user_events.append(events[ii])
#                       print(events[ii])
                       ii+=1
         

######################################################
###adding splited users events to the dictionary
######################################################
                   dict1={}
                   for user_event in user_events:
                       y = (user_event.strip('\t')).split(' = ')   ###get rid of tabs and separate string using "=" as separator
                       z = []
                       for k in y:
                           z.append(k.strip('"'))                  ###get rid of ""
                       dict1[z[0]]=z[1]                            ###creating the dict with current session information
                   #print(dict1)                                    ###check dict
                   if dict1.get('Acct-Session-Time')!=None:
                       table1_time = time.strftime('%H:%M:%S', time.gmtime(int(dict1.get('Acct-Session-Time'))))
                   else:
                       table1_time = dict1.get('Acct-Session-Time')
                   ind = list_of_users[list_of_users['Login']== x].index.to_numpy() ###get the index using 'Login' field in list_of_users dataframe 
                   rus_name = (list_of_users.loc[ind])['FullName'].to_numpy()       ###get russian name using index previously discovered
                   table1 = table1.append({'RussianName':rus_name[0],'UserName':dict1.get('User-Name'),'WhiteIP':dict1.get('Tunnel-Client-Endpoint:0'),'GreyIP':dict1.get('Framed-IP-Address'),'TimeStamp':dict1.get('Event-Timestamp'),'AcctStatusType':dict1.get('Acct-Status-Type'),'Duration': table1_time,'ASATunnelGroup':dict1.get('ASA-TunnelGroupName'),'AcctSessionId':dict1.get('Acct-Session-Id'),'UnixTimeStamp':dict1.get('Timestamp')},  ignore_index=True)
             i+=1
    table1['UnixTimeStamp']=pd.to_datetime(table1['UnixTimeStamp'],unit='s') 
    table1['UnixTimeStamp'] = table1.UnixTimeStamp.dt.tz_localize('UTC').dt.tz_convert(tz='Europe/Moscow')
    table1 = table1.sort_values(by = ['UnixTimeStamp'])
    return(table1)         

######################################################
###end def final()
######################################################
######################################################
###create reports
######################################################

t = datetime.now()+timedelta(days=-t_delta)
t = pd.to_datetime(t)
t = t.strftime("%Y-%m-%d %H:%M:%S")

if type(user)==str:
    user_report = final(user)
#    print(user_report)
#    print(t)
    print('\n')
    user_report = user_report.loc[(user_report.UserName == user) & (user_report.UnixTimeStamp >= t),:]
    print(user_report)
    user_report['UnixTimeStamp'] = user_report.UnixTimeStamp.dt.strftime('%Y-%m-%d %H:%M:%S')
    user_report.to_excel("/tmp/UserStat_"+user+".xlsx")
else:
    report = pd.DataFrame(columns = ['RussianName','UserName','WhiteIP','GreyIP','TimeStamp','AcctStatusType','Duration','ASATunnelGroup','AcctSessionId','UnixTimeStamp'])
    spinner = Spinner('Report Creating  ')
    for m in user:
        report=report.append(final(m),ignore_index=True)
        spinner.next()
    print('\n')
    report = report.loc[report.UnixTimeStamp >= t,:]
    print(report)
    report['UnixTimeStamp'] = report.UnixTimeStamp.dt.strftime('%Y-%m-%d %H:%M:%S')
    report.to_excel("/tmp/FullStat.xlsx")
