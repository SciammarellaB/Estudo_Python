from decorator import my_decorator, upper_decorator, lower_decorator, split_string

@my_decorator
def my_function():
    print("Dentro da funcao")
my_function()

@upper_decorator
def text1():
    return "Hello, World!"
print(text1())

@lower_decorator
def text2():
    return "Hello, World!"
print(text2())

@split_string
def text3():
    return "Hello, World!"
print(text3())