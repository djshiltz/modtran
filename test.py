from getpass import getpass
import modtran

atmosphere = modtran.run(username=input('Enter CIS username: '),
                         password=getpass(prompt='Enter CIS password: '),
                         MODTRAN='M')
