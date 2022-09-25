def arithmetic_arranger(problems):
  i=0
  if len(problems)<6:
    xF=''
    yF=''
    eF=''
    while i <len(problems):

      a=problems[i]
      b=''
      x=''
      y=''
      if "+" in a:
        b=a.split(' + ')
        x=b[0]
        try:
          x = int(x)
          if x > 9999 or x<-9999:
            return "Error: Numbers cannot be more than four digits."
        except:
          return "Error: Numbers must only contain digits."
        y=b[1]
        try:
          y = int(y)
          if y > 9999 or y<-9999:
            return "Error: Numbers cannot be more than four digits."
        except:
          return "Error: Numbers must only contain digits."

      elif "-" in a:
        b=a.split(' - ')
        x=b[0]
        try:
          x = int(x)
          if x > 9999 or x<-9999:
            return "Error: Numbers cannot be more than four digits."
        except:
          return "Error: Numbers must only contain digits."
        y=b[1]
        try:
          y = int(y)
          if y > 9999 or y<-9999:
            return "Error: Numbers cannot be more than four digits."
        except:
          return "Error: Numbers must only contain digits."
      else:
        return "Error: Operator must be '+' or '-'."  
      e=""
      fA=""
      t=max(len(str(x)),len(str(y)))
      while len(e)<t+2:
        e="-"+e  
      if "+" in a:
        fA=x+y
        y="+ "+str(y)
      else:
        fA=x-y
        y="- "+str(y)
      if len(e)>len(y):
        while len(y)<len(e):
          if "+" in y:
            y=y.replace("+","+ ")
          else:
            y=y.replace("-","- ")
      x=str(x)
      if len(e)>len(str(x)):
        while len(str(x))<len(e):
          x=" "+str(x)
      fA=str(fA)
      while len(fA)<=len(e):
        fA=" "+fA
      if i<1:
        xF=str(x)
        yF=str(y)
        eF=str(e)
        fFA=str(fA)
      else:
        xF=xF+"    "+str(x)
        yF=yF+"    "+str(y)
        eF=eF+"    "+str(e)
        fFA=fA+"    "+str(fA)
      i+=1
    xF=str(xF)+"\n"
    yF=yF+"\n"
    eF=eF
    fFA=fFA
    arranged_problems=xF+yF+eF
    return arranged_problems
    return fFA
      
  else:
    return "Error: Too many problems."
    