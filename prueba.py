
x = [1,2,3,4,6,7,8]
z = range(9)
for val in z:
    if not(val in x):
        continue

    print(val)
