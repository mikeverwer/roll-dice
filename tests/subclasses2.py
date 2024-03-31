class A:
    def __init__(self):
        self.var1 = 0

class B:
    def __init__(self, a: A):
        self.var2 = 5
        self.a_instance = a  # Store a reference to the instance of A

class C:
    def __init__(self, b: B):
        self.var3 = 'test'
        b.var2 += 1

# Create an instance of A
instance_a = A()

# Create an instance of B, passing the instance of A
instance_b = B(instance_a)

# Create an instance of C, passing the instance of B
instance_c = C(instance_b)

print(instance_b.var2)  # Output: 6
