import os
import os.path

import argparse
import configparser

'''
# Singleton class design

class someClass:
      loaded = False
      def __init__(self, a=1, b=2):
          if self.loaded:
             return
            
          print('\t\tExecuting init in base class with', a, b)
          
          self.c1 = a
          self.c2 = b
          self.loaded = True
          

class singleton(someClass):

      instance = None

      def __new__(cls, a, b):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            print('\tCreating instance')

        print('\tReturning instance')
        return cls.instance

      def __init__(self, a=-1, b=-42):
          print('\tCalling init in singleton with', a, b)
          super().__init__(a, b)



s1 = singleton(66, 77)
#s1.a = 'sonia' 

s2 = singleton(88, 99)
#print(s2.a)
#s2.a = -222

s3 = singleton(110, 121)
print(s1.c1)
print(s1.c2)

'''



      

class applicationConfiguration:

      def __init__(self, argSpec=None, argList=None, configFileArgument='config', defaultConfigFile='default.conf'):
   
                    
          self.argumentSpecification = argSpec
          self.argumentList = argList
          
          
          self.passedArguments = self.handleArguments()
          print('Calling handleConfigurationFile with', self.passedArguments.get(configFileArgument, defaultConfigFile))
          self.config = self.handleConfigurationFile( self.passedArguments.get(configFileArgument, defaultConfigFile) )

          ''' 
          self.config = self.defaultConfiguration()
          if self.passedArguments is not None:
             if os.path.exists(self.passedArguments.get(configFileArgument, defaultConfigFile)):
                self.config = configparser.RawConfigParser(allow_no_value=True)
                self.config.read(self.passedArguments.get(configFileArgument, defaultConfigFile))
             else:
                 print('File does not exist:', self.passedArguments.get(configFileArgument, defaultConfigFile))
          '''
          self.overwriteConfiguration()




      def  defaultConfiguration(self, sectionList=None):          
           sL = sectionList
           if sL is None:
              sL = list( self.getSpecificationSections() )
              

           #if not sL:
           #   return(None)
            
           c = configparser.RawConfigParser(allow_no_value=True) 
           for s in sL:
               c.add_section(s)
           
           return(c)


      def getSpecificationSections(self, paramSpec=None):

          if paramSpec is None:
             paramSpec = self.argumentSpecification

          if paramSpec is None:
             return(()) # return empty set
            
          scts = set()
          for p in paramSpec:
              scts.add( p['section'].lower() )

          return(scts)    



      def getArgumentSpecificationByName( self, paramName ):
          for p in self.argumentSpecification:
              if p['argname'].lower() == paramName.lower():
                 return(p)

          return(None)      



      def printConfiguration(self, cfg=None):
          if cfg is None:
             cfg = self.config

          if cfg is None:
              print('No configuration object.') 
              return
                    
          for s in cfg.sections():
              print("Section [", s, "]", sep="")
              for key, value in cfg[s].items():
                  print( "\t-", key, "=", value)




      def overwriteConfiguration(self):

          if self.argumentSpecification is None:
              return(None)
            
          for k,v in self.passedArguments.items():
              
              argSpec = self.getArgumentSpecificationByName(k)
              if argSpec is None:
                 print('No such specification found:', k)
                 raise Exception("No argument specification for", k)

              if v is None:
                 print('\tSection [', argSpec['section'], '] Parameter [', k, '] NOT SET in arguments')      
                 continue
            
              #if isinstance(v, str) and v.strip() == '':
              #   continue
                 
              if argSpec['section'].lower() not in self.config.sections():
                 self.config.add_section(argSpec['section'])

              confValue = self.config.get(argSpec['section'], k, fallback=None)
              if confValue is None:
                 print('\tSection [', argSpec['section'], '] Parameter [', k, '] not found in configuration')   
              
              if argSpec['datatype'].lower() == 'boolean':
                 if self.passedArguments[k]:  
                    self.config.set(argSpec['section'], k, 'True') 
              else:    
                 self.config.set(argSpec['section'], k, v)
              


     

      def handleArguments(self):

          if self.argumentSpecification is None:
             return({})
            
          seenSwitches = []
          seenParamNames = []
          cmdArgs = argparse.ArgumentParser(description='Command line arguments', add_help=False)          
          for p in self.argumentSpecification:
               # Check if switch and/or paramname has been seen again i.e.
               # is duplicate. Duplicate switches/parameter names are fatal and
               # argument parsing stops.
               if p['switch'] in seenSwitches:
                  raise Exception("Dublicate switch", p['switch'], "detected.") 

               if p['argname'].lower() in seenSwitches:
                  raise Exception("Dublicate parameter name", p['switch'], "detected.") 

               #print('\tAdding for', p['argname'], 'nargs=', p['nargs'])
               if p['datatype'].lower() == 'boolean':
                  cmdArgs.add_argument(p['switch'], '--' + p['argname'], action='store_true') 
               else:    
                  cmdArgs.add_argument(p['switch'], '--' + p['argname'], nargs='?') #default=p['default']

               seenSwitches.append( p['switch'] )
               seenParamNames.append(p['argname'].lower() )
               
          try:
              '''
              if self.argumentList is not None:
                 print('Parsing existing arg list')   
                 args = vars( cmdArgs.parse_args(self.argumentList) )
              else:
              '''
              knownArgs = cmdArgs.parse_args()
              args = vars( knownArgs )
              #uargs = vars( unknownArgs )
              print('\t\t PARSED: Found these arguments:', args)
                 
              return(args)
            
          except Exception as argEx:
              print('Argument error:', str(argEx))
              return( {} )


         

      def handleConfigurationFile(self, cfgFile): 

          cfg = self.defaultConfiguration()

          print('>>> Loading file', cfgFile)
          if not os.path.exists( cfgFile ):
             print('File', cfgFile, 'not found.')   
          else:      
                cfg = configparser.RawConfigParser(allow_no_value=True)
                cfg.read(cfgFile)

          return(cfg)      
          





# Singleton (or the Highlander: there can only be one)
class appConfig(applicationConfiguration):
      
      instance = None

      def __new__(cls, argSpec=None, argList=None, configFileArgument='config', defaultConfigFile='default.conf'):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            print('\tCreating instance')

        print('\tReturning instance')
        return cls.instance


      def __init__(self, argSpec=None, argList=None, configFileArgument='config', defaultConfigFile='default.conf'):          
          super().__init__(argSpec, argList, configFileArgument, defaultConfigFile)
   


########################################################
#
#
#     commandArguments
#     Parsing command line arguments
#     ONLY for application shells.
#
#     NOT for arguments passed via the OS
#
#     TODO: Not tested. 
#   
#######################################################

class commandArguments:

     

     @staticmethod
     def prepareArguments(argSpec=[]):
         pass
      

     @staticmethod
     def parseListArguments(argSpec=[], argList=[]):
         
          seenSwitches = []
          seenParamNames = []
          cmdArgs = argparse.ArgumentParser(description='Command line arguments', add_help=False)
          #d1 = {'param': {'section' : 'sectionname', 'datatype': 'bool', 'switch': '-k', 'paramname':'someuniquename', 'default':''}}
          for p in argSpec:
               # Check if switch and/or paramname has been seen again i.e.
               # is duplicate. Duplicate switches/parameter names are fatal and
               # argument parsing stops.
               if p['switch'] in seenSwitches:
                  raise Exception("Dublicate switch", p['switch'], "detected.") 

               if p['argname'].lower() in seenSwitches:
                  raise Exception("Dublicate parameter name", p['switch'], "detected.") 

               if p['datatype'].lower() == 'boolean':
                  cmdArgs.add_argument(p['switch'], '--' + p['argname'], action='store_true') 
               else:    
                  cmdArgs.add_argument(p['switch'], '--' + p['argname'], default=p['default'])

               seenSwitches.append( p['switch'] )
               seenParamNames.append(p['argname'].lower() )
               
          try:
                
              args = vars( cmdArgs.parse_args(argList) )

                  
              return(args)
            
          except Exception as argEx:
              print('Argument error:', str(argEx))
              return( {} )    




     @staticmethod
     def parseStringArguments(argSpec=[], argString='', sep=' ', startPos=1):
            
          if argString is None:
             return( {} )   

          return( commandArguments.parseListArguments( argSpec=argSpec, argList=argString.split(sep)[startPos:] ) )
