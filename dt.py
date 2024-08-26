import datetime as dt

my_date = '27.08.24'

d = dt.datetime.strptime('27.08.2024', '%d.%m.%Y')

d1 = dt.datetime.strptime('27.08.2024', '%d.%m.%Y')
d2 = dt.datetime.strptime(str(dt.date.today()), "%Y-%m-%d")

print(d.strftime("%Y-%m-%d"))
print(str(dt.date.today()))
print(str(abs(d1-d2).days))