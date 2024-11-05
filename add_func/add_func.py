import re

def clear_list_empty_mem(l):

    list_final = []
    for i in l:
        i = i.strip(' ,.:;')
        if i != '':
            list_final.append(i)
    return list_final

