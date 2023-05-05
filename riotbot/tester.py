k = "1, 2, 3"
a = k.split()
b = "".join(a)
c = b.split(',')
d = []
for i in range(0, len(c)):
    d.append(int(c[i]))
print(d-[1,4,6])
