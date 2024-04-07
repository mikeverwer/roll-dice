class MyClass:
    def __init__(self) -> None:
        self.a = 0

    def __repr__(self) -> str:
        return f"{self.a = }"
    

A = MyClass()
B = A
B.a = 1
print(A)

