

# Tipet e te dhenave ne Python

# Name                 Abbreviation                 Values 
# Strings              str()                        "Hello", "Emri Mbiemri", "Rezultati"
# Integers             int()                        1, 2, 5, 10, 20, 50, 100
# Float Numbers        float()                      1.0, 2.3, 0.9, 0.0000213, -1.2541
# Booleans             bool()                       True, False
 



#TASK, duke perdorur data types pershkruaj veten

print("Mirgjen Gashi ")
print(16)
print(180)
print(True)


# type()   ->  tregon tipin e te dhenave

print("Mirgjen Gashi", type("Mirgjen Gashi"))
print(22, type(22))
print(180, type(180))
print(True, type(True))


# Duke perdorur data types, vendosni adresen tuaj

# Variables

Shteti="Kosova"
Qyteti="Prishtina"
Shtepi= False
Banese= True
nr_objekti= 83

print(Shteti)
print(Qyteti)
print(Shtepi)
print(Banese)
print(nr_objekti)

# Qka eshte nje variabel? 
# Variabli eshte slot ne memory qe sherben per me rujt vlera [vlere e ndryshueshme (konstante=vlere e pandryshueshme)].

# Allowed to use

FullName= any 
Fullname= any
full_name= any
full_name1= any
name= any


# Not allowed to use

# full name= ...
# full-name= ...
# 123= any
# 1full_name= any


print()
print()
print()


x=10 
y=5

# print(x,"+",y,"=",x+y)
# print("x","-","y","=",x-y)
# print("x","*","y","=",x*y)
# print(x,"/",y,"=",x/y)


a=50
b=20

rezultati= a + b
print(rezultati)

# (10 + 5) * 2 ?

rezultati= (a + b) * 2
print (rezultati)

print()
print()
print()

# 1. (12+8) x 3 - 4² (**  -> fuqi)

a = 12
b = 8
c = 3
d = 4

rezultati= (a+b) * c - d ** 2
print(rezultati)

print()
print()
print()

# 2. (15=3)x(4+6)+23
a=15
b=3
c=4
d=6
e=23

rezultati=(a-b)*(c+d)+e
print(rezultati)
# 3. [(20+10)*2 - 5²]/5

a=20
b=10
c=2
d=5

rezultati=((a+b)*c-d**2)/d
print(rezultati)


#4. ((25-5)x3+10)/(2+3)
a=25
b=5
c=3
d=10
e=2

rezultati= ((a-b)*c+d)/(e+c)
print(rezultati)

































