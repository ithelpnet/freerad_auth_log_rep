#!/usr/bin/python3.6

import os
import subprocess
import pwd
import spwd
import grp
import pandas
import readline
from time import sleep
from progress.spinner import LineSpinner
pandas.set_option("display.max_rows", None, "display.max_columns", None)
from add_func.add_func import clear_list_empty_mem

################################################################
#read list of vpn groups from file
###############################################################

def read_vpn_groups():
    with open("./add_func/vpn_groups") as f:
        groups_list = f.read().splitlines()
        f.close
    return clear_list_empty_mem(groups_list)

################################################################
#user shoud chouse the vpn group
###############################################################

def group_select():
    print (f'Select the VPN group you want to get users list for: \n')
    for i in read_vpn_groups():
        print (i)
    vpn_group = ''
    while vpn_group not in read_vpn_groups():
        vpn_group = input ('\nSelect name of the group from the list above: ')
        if vpn_group not in read_vpn_groups():
            sleep (0.2)
            print (f'\nError!!! There is no such a group, check the list above, and do copy/paste\n')
    return vpn_group

##############################################################
#get from unix list of users regisered in selected group
##############################################################

vpn_group = group_select()
def get_unix_users_list():
    u_list = grp.getgrnam(vpn_group).gr_mem
    return u_list

############################################################################
#get additional information about users (password status, full russian name)
#and put it into a list
###########################################################################
#get russian name
#

def russian_name_gecos(z):
    gecos = pwd.getpwnam(z).pw_gecos
    russian_name = gecos.split(", ")[-1]
    return russian_name

##########################################################
#get password status
#########################################################

def pass_status(y):
    cifer_pass = spwd.getspnam(y).sp_pwdp
    if cifer_pass.startswith('!')==True:
        pass_status = 'LOCKED'
    else:
        pass_status = 'ACTIVE'
    return pass_status

##########################################################
#create final list of users info
#########################################################


def get_users():
    table_list = []
    for user in get_unix_users_list():
        #print(f'{user} {pass_status(user)} {russian_name_gecos(user)}')
        table_list.append([user,pass_status(user),russian_name_gecos(user)])        
    
    return table_list 

###############################################
####Start creating of pandas Dataframe
###############################################

def data_fr():

    d1 = pandas.DataFrame(get_users(), columns = ['Login', 'Status', 'FullName']).sort_values(by=['FullName'],ignore_index=True) ###create main report
    #with pandas.ExcelWriter("/tmp/UserReport_"+group+".xlsx") as writer:
    #    d1.to_excel(writer, sheet_name='User_Status')
    #    d2.to_excel(writer, sheet_name='Count')
    print ('\n')
    return d1


if __name__ == '__main__':

    print('\n\n')
    report = data_fr()
    print(report)
    report_count = report.groupby(['Status']).count()
    print('\n')
    print(report_count)
    with pandas.ExcelWriter("/tmp/UserReport_"+vpn_group+".xlsx") as writer:
        report.to_excel(writer, sheet_name='User_Status')
        report_count.to_excel(writer, sheet_name='Count')


