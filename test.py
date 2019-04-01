import sys

for i in range(1, 5000000):
    print("error {}".format(i), file=sys.stderr)
    print("normal {}".format(i))
    
