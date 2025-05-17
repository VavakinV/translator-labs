def summ(a, b):
    n = a + b
    return n

arr = [1+1, 2, 3]
x = arr[0]
y = arr[1]
s = summ(arr[0], arr[1])

for i in range(10):
    s = s - 1

while s < 0:
    s = s + 1

if s - 2 == 0:
    x = 1
else:
    x = 2

a = 10
b = 20

if b < 30:
    c = a ** 2 + b ** 2
else:
    c = 0