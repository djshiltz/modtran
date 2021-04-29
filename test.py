from getpass import getpass
import modtran

output = modtran.run(username=input('Enter CIS username: '),
                     password=getpass(prompt='Enter CIS password: ')
                     )

