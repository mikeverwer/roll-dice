class MyClass:
    def __init__(self):
        self.str_variable = 'super class variable'
        self.int_variable = 5

        
class MySubclass(MyClass):
    def __init__(self):
        super().__init__()
        self.sub_str_variable = 'subclass variable'
        self.sub_int_variable = 10
        self.modded_variable = self.sub_int_variable + self.int_variable

    def modify_superclass(self, number):
        self.int_variable += number


a = MyClass()
b = MySubclass()
print(b.int_variable)
print(b.modify_superclass(20))
print(b.int_variable)
