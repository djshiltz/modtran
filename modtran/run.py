import paramiko
from modtran.tape5 import createTape5
import subprocess
import os
import time
import numpy as np

def run(username, password, hostname='grissom.cis.rit.edu', **kwargs):
    tape5_string = createTape5(**kwargs)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # this will automatically add the keys
    ssh.connect(hostname, username=username, password=password)

    sftp = ssh.open_sftp()
    sftp.mkdir('modtran-temp')
    sftp.chdir('modtran-temp')
    remote_temp_folder = sftp.getcwd()
    local_folder = os.getcwd()
    stdin, stdout, stderr = ssh.exec_command('cd ' + remote_temp_folder + ';'
                                             'ln -s /dirs/pkg/Mod4v3r1/DATA DATA')
    tape5 = sftp.open('tape5', 'w+')
    tape5.write(tape5_string)
    tape5.close()

    stdin, stdout, stderr = ssh.exec_command('cd ' + remote_temp_folder + ';'
                                             '/dirs/pkg/Mod4v3r1/Mod4v3r1.exe;',
                                             get_pty=True)
    print('RUNNING MODTRAN...')
    for line in iter(stdout.readline, ""):
        print(line, end="")
    print('FINISHED')

    # wait until MODTRAN is done running
    print('DOWNLOADING FROM SERVER...')
    done = False
    while not done:
        try:
            #sftp.get(remotepath=remote_temp_folder + '/tape7',
            #         localpath=local_folder + '/tape7')
            sftp.get(remotepath=remote_temp_folder + '/tape7.scn',
                     localpath=local_folder + '/tape7scn')
            done=True
        except:
            time.sleep(1)

    # delete temporary directory
    stdin, stdout, stderr = ssh.exec_command('rm -rf modtran-temp')
    sftp.close()
    ssh.close()

    with open('tape7scn') as file:
        data = file.readlines()
    os.remove('tape7scn')

    num_lines = len(data)
    num_header_lines = 11
    num_footer_lines = 1
    num_data_lines = num_lines - num_header_lines - num_footer_lines
    num_columns = 13


    array = np.zeros((num_data_lines, num_columns), dtype='<U16')
    for i in range(num_data_lines):
        row = num_header_lines + i
        array[i, 0] = data[row][  4: 12]  # WAVELEN_MCRN
        array[i, 1] = data[row][ 13: 19]  # TRANS
        array[i, 2] = data[row][ 20: 30]  # PTH_THRML
        array[i, 3] = data[row][ 31: 41]  # THRML_SCT
        array[i, 4] = data[row][ 42: 52]  # SURF_EMIS
        array[i, 5] = data[row][ 53: 63]  # SOL_SCAT
        array[i, 6] = data[row][ 64: 74]  # SING_SCAT
        array[i, 7] = data[row][ 75: 85]  # GRND_RFLT
        array[i, 8] = data[row][ 86: 96]  # DRCT_RFLT
        array[i, 9] = data[row][ 97:107]  # TOTAL_RAD
        array[i,10] = data[row][108:116]  # REF_SOL
        array[i,11] = data[row][117:125]  # SOLaOBS
        array[i,12] = data[row][129:134]  # DEPTH

    floats = np.zeros_like(array, dtype=float)
    for j in range(num_columns):
        try:
            floats[:, j] = array[:, j].astype(float)
        except:
            floats[:, j] = np.nan

    atmosphere = {}
    atmosphere['WAVELEN MCRN'] = floats[:, 0]
    atmosphere['TRANS']        = floats[:, 1]
    atmosphere['PTH THRML']    = floats[:, 2]
    atmosphere['THRML SCT']    = floats[:, 3]
    atmosphere['SURF EMIS']    = floats[:, 4]
    atmosphere['SOL SCAT']     = floats[:, 5]
    atmosphere['SING SCAT']    = floats[:, 6]
    atmosphere['GRND RFLT']    = floats[:, 7]
    atmosphere['DRCT RFLT']    = floats[:, 8]
    atmosphere['TOTAL RAD']    = floats[:, 9]
    atmosphere['REF SOL']      = floats[:,10]
    atmosphere['SOL@OBS']      = floats[:,11]
    atmosphere['DEPTH']        = floats[:,12]

    return atmosphere
