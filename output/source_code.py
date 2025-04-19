def sum_arr(array):
    summ = 0
    for x in array:
        summ = summ + x
    return summ

def mult(a, b):
    result = a * b
    return result

a = [1, 5, 4, 2]

print(sum_arr(a))
print(mult(a[0], a[1]))