class A :
   def __init__(self):
      self.var1 = 0
class B :
   def __init__(self, a: A):
      self.var2 = 5
class C :
   def __init__(self, b: B):
      self.var3 = 'test'
      self.var4 = b.var2 + 1

inst_a = A()
inst_b = B(inst_a)
inst_c = C(inst_b)
print(inst_c.var4)