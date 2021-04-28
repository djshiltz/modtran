# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 10:00:39 2020

@authors: Dave Conran and Matthew Helvey

Modified by Dylan Shiltz on 4/27/2021
"""

import numpy as np

# %% Define the card block titles and their associated lenghts
card1 = np.array([['MODTRAN', 'SPEED', 'MODEL', 'ITYPE', 'IEMSCT', 'IMULT', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'MDEF',
                   'IM', 'NOPRINT', 'TPTEMP', 'SURREF'],
                  ['1', '1', '3', '5', '5', '5', '5', '5', '5', '5', '5', '5', '5', '5', '5', '8', '7']])
card1a = np.array([['DIS', 'DISAZM', 'NSTR', 'LSUN', 'ISUN', 'CO2MX', 'H20STR', 'O3STR', 'LSUNFL', 'LBMNAM', 'LFLTNM',
                    'H20AER', 'BLANK', 'LDATDR', 'SOLCON'],
                   ['1', '1', '3', '1', '4', '10', '10', '10', '2', '2', '2', '2', '2', '5', '5']])

card1a1 = np.array([['SUNFL2'], ['80']])
card1a2 = np.array([['BMNAME'], ['80']])
card1a3 = np.array([['FILTNM'], ['80']])
card1a4 = np.array([['DATDIR'], ['80']])

card2 = np.array([['APLUS', 'IHAZE', 'CNOVAM', 'ISEASN', 'ARUSS', 'IVULCN', 'ICSTL', 'ICLD', 'IVSA', 'VIS', 'WSS',
                   'WHH', 'RAINRT', 'GNDALT'],
                  ['2', '3', '1', '4', '3', '2', '5', '5', '5', '10', '10', '10', '10', '10']])

card3 = np.array([['H1', 'H2', 'ANGLE', 'RANGE', 'BETA', 'RO', 'LENN', 'BLANK', 'PHI'],
                  ['10', '10', '10', '10', '10', '10', '5', '5', '10']])
card3a1 = np.array([['IPARM', 'IPH', 'IDAY', 'ISOURCE'],
                    ['5', '5', '5', '5']])
card3a2 = np.array([['PARM1', 'PARM2', 'PARM3', 'PARM4', 'TIME', 'PSIPO', 'ANGLEM', 'G'],
                    ['10', '10', '10', '10', '10', '10', '10', '10']])

card4 = np.array([['V1', 'V2', 'DV', 'FWHM', 'YFLAG', 'XFLAG', 'DLIMIT', 'FLAGS', 'MLFLX'],
                  ['10', '10', '10', '10', '1', '1', '8', '7', '3']])
card4a = np.array([['NSURF', 'AATEMP'], ['1', '8']])
card4L1 = np.array([['SALBFL'], ['80']])
card4L2 = np.array([['CSALB'], ['80']])

card5 = np.array([['IRPT'], ['5']])


# %%

# Writes the card with values right justified
def writeLineRight(card, card_vars):
    card_line = ''  # Store teh line as a single string

    # loop over every block in the card
    for i in range(len(card_vars)):
        # Extract the length of each block
        length = int(card[1, i])
        # Determine spaces needed to fill out the block
        space_needed = length - len(card_vars[i])
        # If the input is larger than the allowable block size, reduce to max size
        if space_needed < 0:
            var_split = card_vars[i].split('.')
            dec = length - (len(var_split[0]) + 1)
            var = round(np.float(card_vars[i]), dec)
            card_line = card_line + str(var)
        else:
            card_line = card_line + space_needed * ' ' + card_vars[i]

    return card_line + '\n'


# For the lines that start left justified
def writeLineLeft(card, card_vars):
    card_line = ''

    space_needed = int(card[1]) - len(card_vars)
    card_line = card_vars[0] + space_needed * ' '

    return card_line + '\n'


def createTape5(
        # Define default values for every variable in each card
        ####### Card 1 #######
        MODTRAN='M',  # (T or M), (C or K), (F or L)
        SPEED='S',  # S(slow 33 abs coef), M(med 17 abs coef)
        MODEL='2',  # 0-8 (The model atmosphere, 2 is MLS)
        ITYPE='2',  # 1,2,3 (2 is Vertical or slant path between two altitudes)
        IEMSCT='2',  # 0,1,2,3 (2 is spectral thermal plus solar/lunar radiance)
        IMULT='-1',  # 0, +1, -1 (-1 MS solar geometry at location H2 surface is used)
        M1='0',  # 0-6 (0 is default temp and pressure)
        M2='0',  # 0-6 (0 is default H20)
        M3='0',  # 0-6 (0 is default O3)
        M4='0',  # 0-6 (0 is default CH4)
        M5='0',  # 0-6 (0 is default N2O)
        M6='0',  # 0-6 (0 is default CO)
        MDEF='1',  # 1,2 (1 is default heavy species profiles used)
        IM='0',  # 0,1 (0 for normal operation of program)
        NOPRINT='0',  # 0,1,-1,-2 (0 for normal operation)
        TPTEMP='294',  # greater 0, less-than/equal 0 (Boundary Temp, 294K = 70F)
        SURREF='1',  # BRDF, LAMBER, greater 0, less-than 0 (Surface reflectance)

        ####### Card 1A #######
        DIS='T',  # T,S,F (T=use DISORT, F=use ISAAC 2-Stream, S=scaled DISORT)
        DISAZM='F',  # T,F (Azimuth dependence with DISORT, increase run time)
        NSTR='8',  # 2,4,8,16 (Streams to use by DISORT)
        LSUN='T',  # T,F (T=read 1cm-1 solar irradiance, F=read 5cm-1)
        ISUN='10',  # (FWHM of triangular scanning function in WN. Smooth TOA irrad.)
        CO2MX='365',  # (Mixing ratio in PPMV. 0=330ppmv, 365ppmv recommended)
        H2OSTR='0',  # (Vertical water vapor column string. 0= use default water)
        O3STR='0',  # (Vertical ozone string. 0= use default ozone)
        LSUNFL='F',  # T,F,1-4 (T=read solar rad. data file from CARD 1A1 LSUN=TRUE)
        LBMNAM='F',  # T,F (T=read band model from CARD 1A2. F=default is 1cm-1)
        LFLTNM='F',  # T,F (T=read user-defined instrument filter from CARD 1A3)
        H2OAER='F',  # T,F (T=modify aerosol optical prop H2O. F=H2O prop are fixed)
        LDATDR='',  # T,F (F, blank=data files are in DATA/, T=need to read in DIR name)
        SOLCON='0',  # neg,zero,pos number (Scale the TOA irradiance, 0=no scale)

        ####### Card 1A1 (Optional, used if LSUNFL=T) #######
        SUNFL2='',
        # 1,2,3,4,or a filename (select TOA solar irradiance database, 1=newkur.dat, 2=chkur.dat, 3=cebchkur.dat, 4=thkur.dat)

        ####### Card 1A2 (Optional, used if LBMNAM=T) #######
        BMNAME='',
        # filename (select name of binary band model data file. B2001_01.bin (1cm-1), B2001_05.bin (5cm-1), B2001_15.bin (15cm-1)). Also dependent on user defined spectral resolution V1, V2, DV, FWHM.

        ####### Card 1A3 (Optional, used if LFLTNM=T) #######
        FILTNM='',  # filename (select name of instrument filter channel response file)

        ####### Card 1A4 (Optional, used if LSUNFL=T) #######
        DATDIR='',  # path (path name for the MODTRAN data files)

        ####### Card 2 (REQUIRED) MAIN AEROSOL AND CLOUD OPTIONS #######
        APLUS='',  # blank, A+ (A+ = Can specify user-defined aerosol optical properties)
        IHAZE='1',  # -1 to 10 (Aerosol extinction model for 0-2KM, 1=RURAL extinction)
        CNOVAM='',  # blank, N (N=Navy Oceanic Vertical Aerosol Model)
        ISEASN='1',  # 0-2 (Seasonal profile for tropo/stratosphere aerosol, 1=SPG/SUMMER)
        ARUSS='',  # blank, USS (USS = AeRosol User Supplied Spectra)
        IVULCN='0',  # 0-8 (Volcanic. 0=background stratospheric profile and extinction)
        ICSTL='0',  # 1-10 (Air mass character used with CNOVAM, 0=not used)
        ICLD='0',  # 0-19 (Cloud/rain model used. 0=no cloud/rain)
        IVSA='0',  # 0,1 (1=Use Army Vert. Structure Algo for aerosols in bound. layer)
        VIS='20',  # neg,0,pos number (Meteorological range (KM) Overrides IHAZE value)
        WSS='0',  # number (Current wind speed (m/s). Used w/ IHAZE=3 or 10. 0=no wind)
        WHH='0',  # number (24 HR avg wind speed (m/s). Used with IHAZE=3. 0=no wind)
        RAINRT='0',  # number (Rain rate (mm/hr). 0=no rain)
        GNDALT='0',  # number (Altitude of surface relative to sea level (KM))

        ####### CARD 3 (REQUIRED) LINE OF SIGHT GEOMETRY (not all parameters are needed) #######
        H1='100',  # number (Initial altitude (KM), position of sensor, for ITYPE=2)
        H2='0',  # number (Final altitude (KM), if using ITYPE=2)
        ANGLE='180',  # 0-180 (Initial zenith angle (deg) measured from H1)
        RANGE='0',  # number (Path length (KM))
        BETA='0',  # 0-180 (Earth center angle (deg) subtended by H1 and H2)
        RO='',  # blank, number (Radius of Earth(KM) blank=default radius)
        LENN='1',  # 0,1 (Determine short/long paths, 0=short default)
        PHI='0',  # 0-180 (Zenith angle (deg) as measured from H2 towards H1)

        ####### CARD 3A1 (IF IEMSCT=2) SOLAR / LUNAR SCATTERING GEOMETRY #######
        IPARM='12',  # 0,1,2,10,11,12 (Method of specifying geometry on CARD 3A2)
        IPH='2',  # 0,1,2 (Type of phase function, 2=Mie-generated aerosol phase fun.)
        IDAY='',  # 1-365 (day of year for Earth to Sun distance if IPARM=1)
        ISOURCE='0',  # 0,1 (Select 0=Sun or 1=Moon)

        ####### CARD 3A2 (IF IEMSCT=2) SOLAR / LUNAR SCATTERING GEOMETRY #######
        PARM1='180',
        PARM2='30',
        PARM3='0',
        PARM4='0',
        TIME='0',  # number (Greenwich decimal time (GMT). Used with IPARM=1,11)
        PSIPO='0',  # 0-360 (Path azimuth from H1 to H2 deg East of North)
        ANGLEM='0',  # 0-180 (Phase angle of moon (deg), for ISOURCE=1)
        G='0',  # 0-1 (Asymmetry factor for Henyey-Greenstein phase function for IPH=0)

        ####### CARD 4 (REQUIRED) SPECTRAL RANGE AND RESOLUTION #######
        V1='0.350',  # number (Initial freq.in wavenumber or wavelength)
        V2='1.100',  # number (Final frequency in wavenumber or wavelength)
        DV='0.005',  # number (Freq(or wavelength) increment used for spectral outputs)
        FWHM='0.005',  # number (Slit function FWHM, units from FLAGS(1:1), Let DV=FWHM/2)
        YFLAG='R',  # T,R (T=Trans output in PLTOUT, R=Radiance output in PLTOUT)
        XFLAG='M',  # W,M,N (Units for output files PLTOUT, W=WN, M=um, N=nm)
        DLIMIT='',  # string (String for repeat runs for PLTOUT (rootname.plt))
        FLAGS='MRAA   ',  # (7 characters to define units, slit, sampling, etc.)
        # 1: blank, W,M,N (Spectral units for V1, V2, DV, FWHM)
        # 2: blank,T,R,G,S,C,H,U (Type of slit function, R=RECT function)
        # 3: blank or A,R (A=FWHM is absolute, R=FWHM is percent relative)
        # 4: blank, A (blank=Degrade only total rad and trans, A=Degrade all)
        # 5: blank, S (S=Save non-degraded results, blank=Do not save)
        # 6: blank, R (R=Use saved results for degrading, blank=Do no use saved results)
        # 7: blank,T,F (blank=no SPECFLUX flux file, T,F=Write file, i.e.UP/DOWN Fluxes)
        MLFLX='',  # number(Number of ATM level SPECFLUX are output starting from ground)

        ####### CARD 4A,4B1,4B2,4B3,4L1,4L3 (Optional) GROUND SURFACE CHARACTERIZATION
        ####### CARD 4A (Optional) IF SURREF=BRDF or LAMBER (permits modeling of ADJACENCY)
        NSURF='1',  # 1,2 (1=Use refl. of image pixel, 2=define an area around pixel too)
        AATEMP='294',  # pos,0, neg (ground surf temp (for NSURF=2) 70F = 294K)

        ####### CARD 4L1 (Optional) IF SURREF=LAMBER #######
        SALBFL='',  # filename (Name for the spectral albedo file)

        ####### CARD 4L2 (Optional) IF SURREF=LAMBER (repeated NSURF times -TARGET, BACKGROUND)
        CSALB='',  # filename (name of spectral albedo curve from SALBFL file)

        ####### CARD 5 (REQUIRED) REPEAT RUN OPTION #######
        IRPT='0'
):


    # Check values of user input
    if type(MODTRAN) != str:
        raise TypeError("MODTRAN must be of type 'str'")
    if MODTRAN not in ['T', 'M', 'C', 'K', 'F', 'L']:
        raise ValueError("Invalid value entered for variable MODTRAN.  Valid values are: \n" +\
                         "'T' or 'M': MODTRAN band model \n" +\
                         "'C' or 'K': MODTRAN correlated-k option \n" +\
                         "'F' or 'L': 20 cm-1 LOWTRAN band model")

    if type(SPEED) != str:
        raise TypeError("SPEED must be of type 'str'")
    if SPEED not in ['S', 'M']:
        raise ValueError("Invalid value entered for variable SPEED.  Valid values are: \n" +\
                         "'S': slow \n" +\
                         "'M': medium")

    if type(MODEL) != str:
        raise TypeError("MODEL must be of type 'str'")
    if MODEL not in ['1', '2', '3', '4', '5', '6']:
        raise ValueError("Invalid value entered for variable MODEL.  Valid values are: \n" +\
                         "'1': tropical atmosphere \n" +\
                         "'2': mid-latitude summer \n" +\
                         "'3': mid-latitude winter \n" +\
                         "'4': sub-arctic summer \n" +\
                         "'5': sub-arctic winter \n" +\
                         "'6': 1976 US Standard Atmosphere \n" +\
                         "user-defined atmospheres (0, 7-8) are not currently supported")


    '''
    # Card 4 optional input checks to ensure required files are named
    if SURREF == 'LAMBER' and SALBFL == '':
        SALBFL = input('Please input name for the spectral albedo file')
    if SURREF == 'LAMBER' and CSALB == '' and NSURF == '2': # (repeated NSURF times -TARGET, BACKGROUND)
        CSALB = input('Please input filename (name of spectral albedo curve from SALBFL file)')
    '''
    # Ensure target is above ground
    if H2 < GNDALT: H2 = GNDALT

    BLANK = ''

    # Create lists storing variable's values for every card
    card1_vars = [MODTRAN, SPEED, MODEL, ITYPE, IEMSCT, IMULT, M1, M2, M3, M4, M5, M6, MDEF, IM, NOPRINT,
                  str(np.float(TPTEMP)), SURREF]
    card1a_vars = [DIS, DISAZM, NSTR, LSUN, ISUN, str(np.float(CO2MX)), H2OSTR, O3STR, LSUNFL, LBMNAM, LFLTNM, H2OAER,
                   BLANK, LDATDR, SOLCON]
    card1a1_vars = [SUNFL2]
    card1a2_vars = [BMNAME]
    card1a3_vars = [FILTNM]
    card1a4_vars = [DATDIR]
    card2_vars = [APLUS, IHAZE, CNOVAM, ISEASN, ARUSS, IVULCN, ICSTL, ICLD, IVSA, str(np.float(VIS)),
                  str(np.float(WSS)), str(np.float(WHH)), str(np.float(RAINRT)), str(np.float(GNDALT))]
    card3_vars = [str(np.float(H1)), str(np.float(H2)), str(np.float(ANGLE)), str(np.float(RANGE)), str(np.float(BETA)),
                  RO, LENN, BLANK, str(np.float(PHI))]
    card3a1_vars = [IPARM, IPH, IDAY, ISOURCE]
    card3a2_vars = [str(np.float(PARM1)), str(np.float(PARM2)), str(np.float(PARM3)), str(np.float(PARM4)),
                    str(np.float(TIME)), str(np.float(PSIPO)), str(np.float(ANGLEM)), str(np.float(G))]
    card4_vars = [str(np.float(V1)), str(np.float(V2)), str(np.float(DV)), str(np.float(FWHM)), YFLAG, XFLAG, DLIMIT,
                  FLAGS, MLFLX]
    card4a_vars = [NSURF, str(np.float(AATEMP))]
    card4L1_vars = [SALBFL]
    card4L2_vars = [CSALB]
    card5_vars = [IRPT]

    # Create a blank card
    full_card = ''
    # Add new lines for every relevant card
    full_card = full_card + writeLineRight(card1, card1_vars)
    full_card = full_card + writeLineRight(card1a, card1a_vars)

    # Card 1 optional input checks
    if LSUNFL == 'T':
        if SUNFL2 == '':
            SUNFL2 = input(
                'Please input name of solar spectrum data file and hit enter (BMNAME = filename): ')  # 1,2,3,4,or a filename (select TOA solar irradiance database,1=newkur.dat, 2=chkur.dat, 3=cebchkur.dat, 4=thkur.dat)
            card1a1_vars = [SUNFL2]
        full_card = full_card + writeLineLeft(card1a1, card1a1_vars)
    if LBMNAM == 'T':
        if BMNAME == '':
            BMNAME = input('Please input name of binary band model data file and hit enter (BMNAME = filename): ')
            card1a2_vars = [BMNAME]
        # B2001_01.bin (1cm-1), B2001_05.bin (5cm-1), B2001_15.bin (15cm-1)).
        # Also dependen on user defined spectral resolution V1, V2, DV, FWHM.
        full_card = full_card + writeLineLeft(card1a2, card1a2_vars)
    if LFLTNM == 'T':
        if FILTNM == '':
            FILTNM = input('Please input name of instrument filter channel response file and hit enter: ')
            card1a3_vars = [FILTNM]
        full_card = full_card + writeLineLeft(card1a3, card1a3_vars)
    if LSUNFL == 'Dave is the Man':
        if DATDIR == '':
            DATDIR = input('Please input path name for the MODTRAN data files: ')
            card1a4_vars = [DATDIR]
        full_card = full_card + writeLineLeft(card1a4, card1a4_vars)

    full_card = full_card + writeLineRight(card2, card2_vars)
    full_card = full_card + writeLineRight(card3, card3_vars)
    full_card = full_card + writeLineRight(card3a1, card3a1_vars)
    full_card = full_card + writeLineRight(card3a2, card3a2_vars)
    full_card = full_card + writeLineRight(card4, card4_vars)

    if SURREF == 'BRDF' or SURREF == 'LAMBER':
        full_card = full_card + writeLineRight(card4a, card4a_vars)
        full_card = full_card + writeLineLeft(card4L1, card4L1_vars)
        full_card = full_card + writeLineLeft(card4L2, card4L2_vars)
    '''
    if SURREF == 'LAMBER' and CSALB != '': 
        full_card = full_card + writeLineLeft(card4L2, card4L2_vars)
    '''
    full_card = full_card + writeLineRight(card5, card5_vars)

    # print(full_card)
    '''
    # Write a file called tape5, write the card contents, and save.
    tape5 = open("tape5", "w+")
    tape5.write(full_card)
    tape5.close()
    '''
    return full_card
