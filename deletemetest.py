# Singleton class design

class someClass:
      loaded = False
      def __init__(self, a=1, b=2):
          
            
          print('\t\tExecuting init in base class with', a, b)
          
          self.c1 = a
          self.c2 = b
          self.loaded = True
          

class singleton(someClass):

      instance = None

      def __new__(cls, a=-66, b=-77):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            print('\tCreating instance')

        print('\tReturning instance')
        return cls.instance

      def __init__(self, a=-1, b=-42):
          print('\tCalling init in singleton with', a, b)
          super().__init__(a, b)



s1 = singleton()
#s1.a = 'sonia' 

s2 = singleton(88, 99)
#print(s2.a)
#s2.a = -222

s3 = singleton(110, 121)
print(s1.c1)
print(s1.c2)



#!/usr/bin/python

import sys
import os
import re
import signal

from pathlib import Path
from clrprint import *


from bloom_filter import BloomFilter



'''
from pynput import keyboard

# The key combination to check
COMBINATION = {keyboard.Key.cmd, keyboard.Key.ctrl}

# The currently active modifiers
current = set()


def on_press(key):
    if key in COMBINATION:
        current.add(key)
        if all(k in current for k in COMBINATION):
            print('All modifiers active!')
    if key == keyboard.Key.esc:
        listener.stop()


def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
'''    


showFiles = False
breakINTR = False

'''
def handler(signum):
   if signum == signal.SIGUSR1:
       print('user defined interrupt!')
       breakINTR = True

signal.signal(signal.SIGUSR1, handler)
'''



def compare( dir1, dir2, xP='' ):
    global   breakINTR

    # make absolute
    absDir1 = os.path.abspath(dir1)
    absDir2 = os.path.abspath(dir2)
    print(absDir1, absDir2)
    nonExistent = BloomFilter(max_elements=10000, error_rate=0.1)
    fsStats = {'nD':0, 'nDC':0, 'nDM':0, 'nDF':0, 'nF':0, 'nFC':0, 'nFM':0, 'nFF':0 }
    
    # traverse root directory, and list directories as dirs and files as files
    try:
          
      for root, dirs, files in os.walk(absDir1):
           
           
        if xP!= '' and re.search(xP, root):  
           continue

        if root == absDir1:
           clrprint(f'[SKIPPING] {root}', clr='purple')
           continue

        fsStats['nD'] += 1
        fsStats['nDC'] += 1
        # Parent path of current directory
        parentPath = Path(root).parent.absolute()
        print(root)
        print('\tChecking if parent path [', parentPath, '] in filter...', sep='', end='')
        if str(parentPath) in nonExistent:
           fsStats['nDM'] += 1 
           clrprint('[YES-Skipping]', clr='y')
           continue

        clrprint('[NO]', clr='o')
        
        # Get relative part           
        rp = os.path.relpath(root, absDir1)
        print(f'\t[RELATIVE PATH of {root} with {absDir1}]', rp)
        print('\t', absDir2 + os.sep + rp, end='')
        if not os.path.isdir(absDir2 + os.sep + rp):
           #print(root)
           clrprint(' [Does not exist]', clr='red')
           nonExistent.add( str(root) )
           clrprint('\t[Adding to bloomfilter]', root, clr='purple')
           fsStats['nDM'] += 1
        else:
              fsStats['nDF'] += 1  
              clrprint(' [Exist]', clr='green')
                  
        if showFiles:
           for file in files:
               print('   [f]', os.sep.join(path[1:]), '/', file, sep='')
               
    except KeyboardInterrupt:
           print('\n\nControl-C seen. Terminating.....')
           return(fsStats)
    except Exception as Ex:
           print('Got exception', str(Ex) )

           
    return(fsStats)



from  filecmp import dircmp

def diffDirs(dir1, dir2, shallow=True):
    result = dircmp(dir1, dir2)
    #result.report()
    return(result)
    
      
import os.path

def is_same(dir1, dir2):
    """
    Compare two directory trees content.
    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2)
    print(f'Comparison of {dir1} and {dir2}:')
    print('\tleft_only:', compared.left_only)
    print('\tright_only:', compared.right_only)
    print('\tcommon:', compared.common_dirs)
    
    if (compared.left_only or compared.right_only or compared.diff_files 
        or compared.funny_files):
        return False
      
    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
            return False
      
    return True




from os.path import join
from filecmp import dircmp

def handleDirectory(side='right', path=''):\
    print(f'\t[{side}] {path}')



#
# Returns the differences between two directories in terms of files and directories
# Seems to work. More testing needed though.
# 
#
def fsDiff(L_dir, R_dir, dirOnly=False, dirHandler=None, fileHandler=None):
    print(f'Doing {L_dir}, {R_dir}')
    dcmp = dircmp(L_dir, R_dir)
    if dirOnly:
       L_only = [join(L_dir, f) for f in dcmp.left_only if os.path.isdir( join(L_dir, f)  )]
       R_only = [join(R_dir, f) for f in dcmp.right_only if os.path.isdir( join(R_dir, f)  )]  
    else:       
       L_only = [join(L_dir, f) for f in dcmp.left_only ]
       R_only = [join(R_dir, f) for f in dcmp.right_only]

    if dirHandler:  
       for d in L_only:
           dirHandler('left', d)
       for d in R_only:
           dirHandler('right', d)  

       
    
    for sub_dir in dcmp.common_dirs:
        new_L, new_R = fsDiff(join(L_dir, sub_dir), join(R_dir, sub_dir), dirOnly, dirHandler, fileHandler)
        L_only.extend(new_L)
        R_only.extend(new_R)
        
    return L_only, R_only





#r = is_same("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects")
#print(r)

a, b = fsDiff(L_dir="F:\\home\\econ\\2012-2013", R_dir="F:\\home\\econ\\2015-2016", dirOnly=True, dirHandler=handleDirectory)

#fsD = compare("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", '\.svn')
#clrprint(fsD, clr='green')

#dff = diffDirs("F:\\home\\EAP\\2023-2024\\DAMA60\\Ergasies", "F:\\home\\econ\\2023-2024\\Postgrad\\Projects", False)
#dff.report()
sys.exit(-2)

maxIter = 3
n = 0
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("/Users/manolistzagarakis"):
    path = root.split(os.sep)
    #print(path[1:])
    #print('[D]', os.path.abspath(os.sep.join(path[1:])) )
    
    #root = root.replace('exampleDir/', '')
    print('[', root, ']')
    print('\t[RELATIVE] ::', os.path.relpath(root, "/Users/manolistzagarakis") ) 
    print('\t[ABSOLUTE] ::', os.path.abspath(root))
    print('\t[D]', dirs)
    print('\t[F]', files)
    #break
    #print((len(path) - 1) * '---', os.path.basename(root))
    if showFiles:
      for file in files:
        #print(len(path) * '---', file)
         print('   [f]', os.sep.join(path[1:]), '/', file, sep='')

    print(n*'*')
    n += 1
    if n >= 3:
       break   

