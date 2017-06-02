import os

print("__file__                                  : %r" % __file__)
print("os.path.dirname(__file__)                 : %r" % (os.path.dirname(__file__)))
print("os.path.abspath(__file__)                 : %r" % (os.path.abspath(__file__)))
print("os.path.dirname(os.path.abspath(__file__) : %r" % (os.path.dirname(os.path.abspath(__file__))))
