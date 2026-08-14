def my_decorator(func):
    def wrapper():
        print("Antes da funcao")
        func()
        print("Depois da funcao")
    return wrapper

def upper_decorator(func):
    def wrapper():
        print("Antes da funcao")
        return func().upper()
    return wrapper

def lower_decorator(func):
    def wrapper():
        print("Antes da funcao")
        return func().lower()
    return wrapper

def split_string(func):
    def wrapper():
        print("Antes da funcao")
        return func().split()
    return wrapper