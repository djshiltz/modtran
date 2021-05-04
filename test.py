from getpass import getpass
import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.use('Qt5Agg')  # or can use 'TkAgg', whatever you have/prefer
import modtran

#  Type help(modtran.run) to print documentation
output = modtran.run(username=input('Enter CIS username: '),
                     password=getpass(prompt='Enter CIS password: '),
                     SURREF=0.1,
                     ISOURC=0,
                     )

# output is a dictionary that includes the tape5 and tape7.scn files, as well
# as the data columns from tape7.scn

# print(output['tape5'])
# print(output['tape7.scn]')
plt.figure(0)
plt.plot(output['WAVELEN MCRN'], output['TOTAL RAD'], 'k', label='TOTAL RAD')
plt.plot(output['WAVELEN MCRN'], output['GRND RFLT'], 'b', label='GRND RFLT')
plt.xlabel(r'Wavelength [$\mu$m]')
plt.ylabel(r'Radiance [W/cm$^2 \cdot$sr$\cdot \mu$m]')
plt.legend()
plt.show()
