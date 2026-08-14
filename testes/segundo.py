carinha = "L0"
print(carinha[0:])
print(carinha[1:])
print(carinha*10)

matrix1 = ["Matrix 1", 2, True, 4.5]

print(matrix1[0:])
print(matrix1[:2])
print(matrix1[-1])
print(matrix1[1:3])

matrix1.append("Novo elemento")
print(matrix1)

# matrix1.sort()
# print(matrix1)

matrix2 = matrix1.copy()
print(matrix2)

matrix1.clear()
print(matrix1)
print(matrix2)

matrix1 = matrix2.copy()
matrix1.remove("Novo elemento")
print(matrix1)