import sys
import re
import clrprint


def formatedPrint3(iStr, delim, color='red'):
    delimSeen = False
    for c in iStr:
        if c == delim:
           delimSeen = not delimSeen
           continue

        if delimSeen:
           clrprint.clrprint(c, clr=color, end='')
        else:
            print(c, end='')


            

def formatedPrint2(iStr, matchPos, clr='red'):
    #print(iStr)
    for index, p in enumerate(matchPos):
        #print('Current value', p, 'position:', index)
        if index % 2 ==0:
           if index == 0:
              print( iStr[0:p], end='')
              clrprint.clrprint(iStr[p+1:matchPos[index+1] ], clr='red', end='')           
           else:
              #print('Index:', index) 
              clrprint.clrprint(iStr[p+1:matchPos[index+1] ], clr='red', end='') 
        else:
             if index == len(matchPos) - 1:
                print( iStr[p+1:] ) 
             else:    
                 print(iStr[p+1:matchPos[index+1]], end='')

         




def formatedPrint(iStr, matchPos, clr='red'):
    print(iStr)
    for index, p in enumerate(matchPos):
        if index == len(matchPos) -1:
           print('>>>Printing from', p+1, 'until end') 
           print('\t', iStr[p+1:]) # last one 
        elif index == 0:
           print('>>>Printing from 0 until ', p) 
           print('\t', iStr[0:p], sep='', end='') # first one
           clrprint.clrprint(iStr[p+1: matchPos[index+1]], clr='red', end='')
        else: 
           print('>>>Printing from', p+1 , 'up until ', matchPos[index+1]) 
           #print('printing from ', p, 'up until', matchPos[index+1]+1, 'for:', iStr)
           clrprint.clrprint( iStr[p+1: matchPos[index+1]], clr='red', end='')   


def getDelimPositions( s, delim ):

    mP = []
    currP = 0
    source = s
    
    while True:
     if source[currP:] == '':
        return( mP )

     try:
          nextP = source[currP:].index(delim)
     except Exception as idxEx:
          mP.append( (currP, len(s), '1') )
          return(mP)

     #mP.append(currP+nextP)

     if mP:
        prev = mP[-1]
        mP.append( ( prev[1], currP-1, '0') )
    
     mP.append( (currP, currP+nextP-1, '1') )
     currP += (nextP+1) 

    return(mP)
    






s='abcdefghijklmnopqrtuvwxyz'
#s='123456789'
s='kabcsss'

sourceString = input('Give source string:')
searchfor = input('Search for what?')

result = re.subn(searchfor, r'/\1/', sourceString)
if result[1] <= 0:
   print('Not found. Exiting')
   sys.exit(-2)

normalized = result[0]

parts = normalized.split('/')
for idx, p in enumerate(parts):
    if idx%2 == 1:
       clrprint.clrprint(p, clr='red', end='')
    else:
       print( p, end='')
print('')       

sys.exit(-1)

dP = getDelimPositions( normalized, '/' )
print(dP)
for p in dP:
    print(p, '::', normalized[p[0]:p[1]])
    
idx = 0
matchPos = []
fromto = []
numTimes = 0
while True:
      
      if normalized[idx:] == '':
         break 

      try:
          nextPos = normalized[idx:].index('/')
      except Exception as idxEx:
          
          break
              
      matchPos.append(idx+nextPos)
      if fromto:
          fromto.append( (idx, idx+nextPos) )
      idx += nextPos +1
      
      
print(normalized)      
print(6*'=')
formatedPrint2(normalized, matchPos)
formatedPrint3(normalized, '/', 'yellow')
