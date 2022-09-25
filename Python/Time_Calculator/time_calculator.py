def add_time(start, duration,maybe=''):
  days = ["Monday",
          "Tuesday",
          "Wednesday",
          "Thursday",
          "Friday",
          "Saturday",
          "Sunday"]
  a=start[:-3].split(":")
  a1= int(a[0])
  a2= int(a[1])
  b=duration.split(":")
  b1=int(b[0])
  b2=int(b[1])
  c=0
  c1=0
  c2=0
  if start[-2:] =="PM":
    a1=a1+12
  c2=a2+b2
  while c2/60>=1:
    c2-=60
    c+=1
  c1=a1+b1+c
  i=1
  j=''
  k=''
  while c1/24>=1:
    if (c1-24)<24 and j=='':
      c1-=24
      i+=1
      j=" (next day)"
    else:
      c1-=24
      j=" ("+str(i)+" days later)"
      i+=1
  if c1>=12:
    c1-=12
    k=" PM"
  else:
    k=" AM"
  if c1==0:
    c1=12
  new_time=str(c1)+":"+f"{c2:02}"+k
  if maybe!='':
    maybe=maybe.lower().capitalize()
    maybeIndex=days.index(maybe)-1
    print(days.index(maybe))
    while i>=1:
      maybeIndex+=1
      i-=1
      if maybeIndex>6:
        maybeIndex=0
    newMaybe = days[maybeIndex] 
    new_time+=", "+newMaybe
  if j !='':
    new_time=new_time+j

  print(new_time)
  return new_time