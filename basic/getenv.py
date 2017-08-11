# coding: utf-8
 
import os
 
# ================================================================
# env variables
# ================================================================
# output
for k, v in os.environ.items():
    print("{key} : {value}".format(key=k, value=v))
    
# adding an env variables
os.environ["HOGE"] = "ABCDEFG"
 
# outputing again
for k, v in os.environ.items():
    print("{key} : {value}".format(key=k, value=v))