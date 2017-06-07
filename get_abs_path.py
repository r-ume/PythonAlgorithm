from os import path, pardir
import os

print("__file__                                  : %r" % __file__)
print("os.path.dirname(__file__)                 : %r" % (os.path.dirname(__file__)))
print("os.path.abspath(__file__)                 : %r" % (os.path.abspath(__file__)))
print("os.path.dirname(os.path.abspath(__file__) : %r" % (os.path.dirname(os.path.abspath(__file__))))

current_dir = path.abspath(path.dirname(__file__))
parent_dir = path.abspath(path.join(current_dir, pardir))
parent_parent_dir = path.abspath(path.join(parent_dir, pardir)) 

print(current_dir)
print(parent_dir)
print(parent_parent_dir)
