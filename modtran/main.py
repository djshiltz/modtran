import numpy as np
import paramiko
import subprocess
import os
import time
from modtran.formats import A, I, F


def run(username: str,                         # CIS username
        password: str,                         # CIS password
        hostname: str = 'grissom.cis.rit.edu', # Name of CIS host

        # DEFAULT ARGUMENTS
        MODTRN : str   = 'M',    # MODTRAN band model
        SPEED  : str   = 'S',    # S (slow, 33 abs coef), M (medium, 17 abs coef)
        MODEL  : int   = 2,      # 0-8 (the model atmosphere, 2 is MLS)
        TPTEMP : float = 294.0,  # number (target temperature [K])
        SURREF : float = 0.75,   # 0-1 (surface reflectance)
        DIS    : str   = 'T',    # T, S, F (T=use DISORT, F=use Isaac 2-stream, S=scaled 2-stream)
        DISAZM : str   = 'T',    # T, F (Azimuth dependence with DISORT)
        NSTR   : int   = 8,      # 2, 4, 8, 16 (Streams to use by DISORT)
        CO2MX  : float = 365.0,  # mixing ratio in ppmv
        H2OSTR : str   = '0',    # water vapor column
        O3STR  : str   = '0',    # ozone column
        IHAZE  : int   = 1,      # aerosol model
        CNOVAM : str   = '',     # toggle Navy NOVAM model
        ISEASN : int   = 0,      # seasonal aerosol profile
        IVULCN : int   = 0,      # volcanic aerosol profile
        ICSTL  : int   = 3,      # air mass character used with NOVAM
        IVSA   : int   = 0,      # toggle Army VSA model
        VIS    : float = 0.0,    # visibility [km]
        WSS    : float = 0.0,    # wind speed [m/s]
        WHH    : float = 0.0,    # 24-hr wind speed [m/s]
        RAINRT : float = 0.0,    # rain rage [mm/hr]
        GNDALT : float = 0.0,    # ground altitude [km]
        H1     : float = 100.0,  # sensor altitude [km]
        H2     : float = 0.0,    # target altitude [km]
        ANGLE  : float = 180.0,  # zenith angle from sensor to target
        IPH    : int   = 2,      # phase function
        IDAY   : int   = 93,     # day of the year
        ISOURC : int   = 0,      # 0 for sun, 1 for moon
        PARM1  : float = 0.0,    # solar azimuth [deg E of N]
        PARM2  : float = 0.0,    # solar zenith [deg]
        ANGLEM : float = 0.0,    # phase of the moon (0 full, 180 none)
        G      : float = 0.50,   # Henyey-Greenstein asymmetry factor (used if IPH = 0)
        V1     : float = 0.350,  # wavelength [micron] minimum
        V2     : float = 1.000,  # wavelength [micron] maximum
        DV     : float = 0.005,  # wavelength [micron] increment
    ) -> dict:
    """Runs MODTRAN4, Version 3, Revision 1 on RIT's Center for Imaging Science Linux servers.


    Required Arguments:

    username : str
        Your CIS username

    password : str
        Your CIS password

    hostname : str
        Name of CIS host
        Default setting is grissom.cis.rit.edu
    __________________________________________________________________________________________

    Keyword Arguments:

    MODTRN : str
        Band model algorithm
            'T', 'M', or '' - MODTRAN band model (no correlated-k treatment)
            'C' or 'K' - MODTRAN band model (with correlated-k treatment)
            'F' or 'L' - LOWTRAN band model (not recommended except for quick
                         historical comparisons)
        Default setting is 'M'

    SPEED : str
        Speed of correlated-k treatment
            'S' or '' - slow speed using 33 absorption coefficients per spectral band
            'M' - medium speed using 17 absorption coefficients
        Default setting is 'S'

    MODEL : int
        Atmospheric model from a list of pre-defined templates:
            1 - tropical atmosphere (15 deg N)
            2 - mid-latitude summer (45 deg N)
            3 - mid-latitude winter (45 deg N)
            4 - sub-arctic summer (60 deg N)
            5 - sub-arctic winter (60 deg N)
            6 - 1976 US Standard Atmosphere
        Note: user-defined atmospheres (options 0, 7, 8) are not currentl supported by this API.
        Default setting is 2

    TPTEMP : float
        Temperature [K] of target (i.e. usually the ground)
        Default setting is 294.0

    SURREF : float
        Surface reflectance (albedo)
        Default setting is 0.75

    DIS : str
        'T' - use DISORT
        'F' - use Isaac 2-stream
        'S' - use Isaac 2-stream scaled by performing DISORT at a few fixed wavelengths
        Default setting is 'T'

    DISAZM : str
        'T' - include azimuthal dependence in DISORT
        'F' - ignore azimuthal dependence in DISORT
        Default setting is 'T'

    NSTR : int
        Number of streams used by DISORT, must be in [2, 4, 8, 16]
        Default setting is 8

    CO2MX : float
        CO2 mixing ratio in ppmv
        Default setting is 365.0

    H2OSTR : str
        Vertical water vapor column character string
            '0' - MODTRAN's default water vapor column is used
            'g' + str(number) - water vapor is set to number [g/cm2]
            'a' + str(number) - water vapor is set to number [ATM-cm]
            str(number) - uses MODTRAN's default water vapor column scaled by number
        Default setting is '0'

    O3STR : str
        Vertical ozone column character string
            '0' - MODTRAN's default ozone column is used
            'g' + str(number) - ozone is set to number [g/cm2]
            'a' + str(number) - ozone is set to number [ATM-cm]
            str(number) - uses MODTRAN's default water vapor column scaled by number
        Default setting is '0'

    IHAZE : int
        Aerosol extinction model from a list of pre-defined templates
            -1 - No aerosol extinction, but clouds may be included via ICLD
            0 - No aerosol extinction or cloud extinction is included
            1 - Rural extinction w/ default VIS = 23 km
            2 - Rural extinction w/ default VIS = 5 km
            3 - Navy maritime extinction, default VIS based on wind speed (WSS)
                and relative humidity.  If wind speed (WSS) and 24-hr wind speed (WHH)
                are both set to 0.0, uses the default wind speed for atmospheric MODEL
            4 - Maritime extinction, default VIS = 23 km (LOWTRAN model)
            5 - Urban extinction, default VIS = 5 km
            6 - Tropospheric extinction, default VIS = 50 km
            8 - FOG1 (advective fog) extinction, VIS = 0.2 km
            9 - FOG2 (radiative fog) extinction, VIS = 0.5 km
            10 - Desert extinction, sets visibility from wind speed (WSS).  If WSS<0, the
                default wind speed is 10 m/s.
            Note: user defined aerosol extinction (option 7) is not supported by this API.
        Default setting is 1

    CNOVAM : str
        Toggle Navy Oceanic Vertical Aerosol Model (NOVAM)
            '' - off
            'N' - on
        Default setting is ''

    ISEASN : int
        Selects the appropriate seasonal aerosol profile for tropospheric and
        stratospheric aerosols.  Only the tropospheric aerosl extinction coefficients
        are used with the 2-10 km profiles.
            0 - season determined by the value of MODEL
                Spring-Summer profile for MODEL = 0, 1, 2, 4, 6, 7
                Fall-winter profile for MODEL = 3, 5
            1 - Spring-Summer profile
            2 - Fall-winter profile
        Default setting is 0

    IVULCN : int
        Volcanic aerosol profile
            0 or 1 - background stratospheric profile and extinction
            2 - moderate volcanic profile and aged volcanic extinction
            3 - high volcanic profile and fresh volcanic extinction
            4 - high volcanic profile and aged volcanic extinction
            5 - moderate volcanic profile and fresh volcanic extinction
            6 - moderate volcanic profile and background stratospheric extinction
            7 - high volcanic profile and background stratospheric extinction
            8 - extreme volcanic profile and fresh volcanic extinction
        Default setting is 0

    ICSTL : int
        Air mass character (1 to 10) used with CNOVAM
            1 - open ocean
            .
            .
            .
            10 - strong continental influence
        Default setting is 3

    IVSA : int
        Selects the use of the Army Vertical Structure Algorithm (VSA) for aerosols
        in the boundary layer
            0 - not used
            1 - use
        Default setting is 0

    VIS : float
        Meteorological visibility range [km]
        Note that VIS = 0.0 uses the default visibility set by IHAZE, otherwise
            setting VIS will override IHAZE
        Note that a negative value uses the negative of the vertical aerosol plus
            Rayleigh optical depth
        Default setting is 0.0

    WSS : float
        Wind speed [m/s] - used only if IHAZE = 3 or IHAZE = 10
        Default setting is 0.0

    WHH : float
        24-hr average wind speed [m/s] used only if IHAZE = 3
        Default setting is 0.0

    RAINRT : float
        Rain rate [mm/hr] used from the ground to the top of the cloud layer
        when cloud is present.  If no clouds, rain rate is used from the ground
        to an altitude of 6 km.
        Default setting is 0.0

    GNDALT : float
        Altitude of the surface relative to sea level [km].  May be negative
        but may not exceed 6 km.
        Default setting is 0.0

    H1 : float
        Altitude of sensor [km]
        Note: in this API, ITYPE = 2 is fixed
        Default setting is 100.0

    H2 : float
        Altitude of target [km]
        Note: in this API, ITYPE = 2 is fixed
        Default setting is 0.0

    ANGLE : float
        Zenith angle 0-180 [deg] measured from sensor to target
        ANGLE = 180.0 indicates nadir observation geometry
        Default setting is 180.0

    IPH : int
        Aerosol phase function
            0 - Henyey-Greenstein with assymetry factor G
            2 - Mie scattering
            Note: user-supplied phase functions (option 1) are not currently
            supported by this API.
            Default setting is 2

    IDAY : int
        Day of the year from 1 to to 365.  Specifies earth-sun distance and the
        sun's location in the sky.
        Default setting is 93

    ISOURC : int
        Light source
            0 - Sun
            1 - Moon
        Default setting is 0

    PARM1 : float
        Solar azimuth at H2 [deg EAST of NORTH] for IPARM = 12
        Note: IPARM = 12 is fixed in this API
        Default setting is 0.0

    PARM2 : float
        Solar zenith at H2 [deg] for IPARM = 12
        Note: IPARM = 12 is fixed in this API
        Default setting is 0.0

    ANGLEM : float
        Phase of the moon
            0 - full moon
            90 - half moon
            180 - no moon
        Default setting is 0.0

    G : float
        Assymetry factor for use with Henyey-Greenstein phase function (used
        only with IPH = 0).  Number from (-1 to 1) where -1 indicates complete
        backscattering, 0 indicates symmetric/isotropic scattering, and +1
        indicates complete forward scattering.
        Default setting is 0.5

    V1 : float
        Lowest wavelength [micron] in output range
        Note: in this API, units are fixed in microns
        Default setting is 0.350

    V2 : float
        Highest wavelength [micron] in output range
        Note: in this API, units are fixed in microns
        Default setting is 1.000

    DV : float
        Wavelength increment [micron] in output
        Note: in this API, the full-width-half-maximum is specified based
        on the value of DV.  Setting DV to be too small will return a
        CHKRES error from MODTRAN.
        Default setting is 0.005
    __________________________________________________________________________________________

    Returns:

    output : dict
        Output dictionary with the following keys:
            'tape5'         - input text file
            'tape7.scn'     - output text file (convolved with scanning function)
            'WAVELEN MCRN'  - wavelength [micron]
            'TRANS'         - transmission along direct path between target H2 and sensor H1 [unitless]
            'PTH THRML'     - blackbody radiance thermally emitted from atmosphere
                                  toward observer [W/cm2/sr/micron]
            'THRML SCT'     - blackbody radiance thermally emitted from target surface
                                  and scattered from atmosphere and background towards
                                  observer [W/cm2/sr/micron]
            'SURF EMIS'     - blackbody radiance thermally emitted from target surface
                                  toward observer [W/cm2/sr/micron]
            'SOL SCAT'      - solar radiance scattered from atmosphere and background
                                  toward observer [W/cm2/sr/micron]
            'SING SCAT'     - solar radiance scattered once from atmosphere toward
                                  observer [W/cm2/sr/micron]
            'GRND RFLT'     - direct and indirect solar radiance reflected from
                                  from target toward observer [W/cm2/sr/micron]
            'DRCT RFLT'     - direct solar radiance reflected from target
                                  toward observer [W/cm2/sr/micron]
            'TOTAL RAD'     - total radiance (all sources) toward
                                  observer [W/cm2/sr/micron]
            'REF SOL'       - # TODO: define 'REF SOL'
            'SOL@OBS'       - # TODO: define 'SOL@OBS'
            'DEPTH'         - # TODO: define 'DEPTH'
    """

    # Define fixed MODTRAN Parameters (hidden from user to
    # prevent unintended behavior)

    ITYPE : int = 2
    """
    Vertical or slant path between two arbitrary altitudes
    """

    IEMSCT : int = 2
    """
    Radiance mode, includes solar/lunar radiance
    """

    IMULT : int = -1
    """
    Multiple scattering enabled - solar geometry is w/r to H2 (target/ground)
    """

    M1, M2, M3, M4, M5, M6 = [0, 0, 0, 0, 0, 0]
    """
    Uses the default atmospheric constituents for the corresponding
    MODEL atmosphere
    """

    MDEF : int = 1
    """
    Default heavy species profiles are used (user-defined heavy species
    profiles are not supported by this API)
    """

    IM : int = 0
    """
    Normal operation (user-defined atmospheres are not supported by this API)
    """

    NOPRNT : int = 0
    """
    Normal tape6 output
    """

    LSUN : str = 'T'
    """
    Read in 1 cm-1 binned solar irradiance from a file (see LSUNFL)
    """

    ISUN : int = 10
    """
    The full-width-half-maximum (in cm-1) of the triangular scanning function
    used to smooth the top-of-atmosphere solar irradiance
    """

    LSUNFL : str = 'F'
    """
    Use the default solar radiance file, DATA/newkur.dat
    """

    LBMNAM : str = 'F'
    """
    Use the default band model file, DATA/B2001_01.BIN
    """

    LFLTNM : str = 'F'
    """
    Do not read in user-defined instrument filter function
    """

    H2OAER : str = 'T'
    """
    Aerosol optical properties are modified to reflect the changes
    from the original relative humidity profile arising from the
    scaling of the water column (H2OSTR).
    """

    LDATDR : str = ''
    """
    Use the default data directory: DATA/
    Note that 'F' returns a read error for some reason, so keep this as ''
    """

    SOLCON : int = 0
    """
    Do not scale the TOA solar irradiance
    """

    APLUS : str = ''
    """
    Do not include user-specified aerosol optical properties (not currently
    supported by this API)
    """

    ARUSS : str = ''
    """
    Do not use user-supplied aerosol spectra (not currently supported by this API).
    """

    ICLD : int = 0
    """
    Cloud/rain model
        0 - no clouds or rain
        1 - cumulus cloud layer, base = 0.66 km, top = 3.0 km
        2 - altostratus cloud layer, base = 2.4 km, top = 3.0 km
        3 - stratus cloud layer, base = 0.33 km, top = 3.0 km
        4 - stratus/stratocumulus layer, base = 0.66 km, top = 2.0 km
        5 - nimbostratus cloud layer, base = 0.16 km, top = 0.66 km
        6 - 2.0 mm/hr ground drizzle (cloud 3)
        7 - 5.0 mm/hr ground light rain (cloud 5)
        8 - 12.5 mm/hr ground moderate rain (cloud 5)
        9 - 25.0 mm/hr ground heavy rain (cloud 1)
        10 - 75.0 mm/hr ground extreme rain (cloud 1)
        11 = user defined cloud extinction
        18 - standard cirrus model
        19 - sub-visual cirrus model
        Note: options 12-17 are not used by MODTRAN.
        Note: since cloud models > 0 require card 2A and I can't find documentation about
        the format of card 2A, I'm disabling cloud models.
    """

    RANGE : float = 0.0
    """
    Path length [km] between H1 and H2
    Set to 0.0 to force CASE 2a (p. 49 of manual)
    """

    BETA : float = 0.0
    """
    Earth-center angle [deg] subtended by H1 and H2
    Set to 0.0 to force CASE 2a (p. 49 of manual)
    """

    RO : str = ''
    """
    Radius of the earth [km]
    Set to '' for default
    """

    LENN : int = 1
    """
    0 - short (stops at tangent height)
    1 - long (extends through the tangent height)
    """

    PHI : float = 0.0
    """
    Zenith angle [deg] measured from H2 toward H1
    Set to 0.0 to force CASE 2a (p. 49 of manual)
    """

    IPARM : int = 12
    """
    Method of specifying geometry
    Set to 12 so that the parameters are:
        PARM1 - solar/lunar azimuth [deg]
        PARM2 - solar/lunar zenith [deg]
        PARM3 - not used
        PARM4 - not used
        TIME - not used
        PSIPO - not used
    """

    PARM3 : float = 0.0
    """
    Not used for IPARM = 12
    """

    PARM4 : float = 0.0
    """
    Not used for IPARM = 12
    """

    TIME : float = 0.0
    """
    Not used for IPARM = 12
    """

    PSIPO : float = 0.0
    """
    Not used for IPARM = 12
    """

    FWHM : float = 2 * DV
    """
    Full-width-half-maximum for output smoothing kernel (scanning function)
    MODTRAN manual recommends DV = FWHM / 2.
    Usually the user will want to specify DV, so this satisfies that recommendation.
    """

    YFLAG : str = 'R'
    """
    Radiance output in PLTOUT
    """

    XFLAG : str = 'M'
    """
    Micron units used in PLTOUT
    """

    DLIMIT : str = ''
    """
    Not needed - used to separate output from multiple MODTRAN runs
    """

    FLAGS : str = 'MRAA   '
    """
    String of characters indicating:
        1 - ' ' defaults to 'W'
            'W' spectral units in wavenumbers
            'M' spectral units in microns
            'N' spectral units in nanometers
        2 - ' ' defaults to 'T'
            'T' tri
            'R' rect
            'G' gauss
            'S' sinc
            'C' sinc2
            'H' Hamming
            'U' user-supplied
        3 - ' ' defaults to 'A'
            'A' FWHM is absolute
            'R' FWHM is percent relative
        4 - ' ' degrade only total radiance and transmittance
            'A' degrade all radiance and transmittance components
        5 - ' ' do not save current results
            'S' save non-degraded results for degrading later
        6 - ' ' do not use saved results
            'R' use saved results for degrading with the current slit function
        7 - ' ' do not write spectral flux table
            'T' write a specflux file limited to 80 characters per line
            'F' write a specflux file with all flux values on a single line
    """

    MLFLX : int = 0
    """
    Number of atmospheric levels for which specflux is output.  Blank or 0 indicates
    that all atmospheric levels will be output
    """

    IRPT : int = 0
    """
    Number of repeated runs
    """

    # Construct array of all inputs, including fixed MODTRAN inputs
    card1 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [MODTRN,     'MODTRN',    str,      1,       MODTRN in ['T', 'M', 'C', 'K']],
        [SPEED,      'SPEED',     str,      1,       SPEED in ['S', 'M']],
        [MODEL,      'MODEL',     int,      3,       MODEL in [1, 2, 3, 4, 5, 6]],
        [ITYPE,      'ITYPE',     int,      5,       ITYPE in [1, 2, 3]],
        [IEMSCT,     'IEMSCT',    int,      5,       IEMSCT in [0, 1, 2, 3]],
        [IMULT,      'IMULT',     int,      5,       IMULT in [0, 1, -1]],
        [M1,         'M1',        int,      5,       M1 in [0, 1, 2, 3, 4, 5, 6]],
        [M2,         'M2',        int,      5,       M2 in [0, 1, 2, 3, 4, 5, 6]],
        [M3,         'M3',        int,      5,       M3 in [0, 1, 2, 3, 4, 5, 6]],
        [M4,         'M4',        int,      5,       M4 in [0, 1, 2, 3, 4, 5, 6]],
        [M5,         'M5',        int,      5,       M5 in [0, 1, 2, 3, 4, 5, 6]],
        [M6,         'M6',        int,      5,       M6 in [0, 1, 2, 3, 4, 5, 6]],
        [MDEF,       'MDEF',      int,      5,       MDEF in [1, 2]],
        [IM,         'IM',        int,      5,       IM in [0, 1]],
        [NOPRNT,     'NOPRNT',    int,      5,       NOPRNT in [0, 1, -1, -2]],
        [TPTEMP,     'TPTEMP',    float,    (8, 3),  True],
        [' ',        'space',     str,      1,       True],
        [SURREF,     'SURREF',    float,    (6, 4),  SURREF >= 0 and SURREF <= 1]
    ], dtype=object)

    card1a = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [DIS,        'DIS',       str,      1,       DIS in ['T', 'F', 'S']],
        [DISAZM,     'DISAZM',    str,      1,       DISAZM in ['T', 'F']],
        [NSTR,       'NSTR',      int,      3,       NSTR in [2, 4, 8, 16]],
        [LSUN,       'LSUN',      str,      1,       LSUN in ['T', 'F']],
        [ISUN,       'ISUN',      int,      4,       ISUN == 10],
        [CO2MX,      'CO2MX',     float,    (10, 5), True],
        [H2OSTR,     'H2OSTR',    str,      10,      True],  # TODO: add condition for H2OSTR
        [O3STR,      'O3STR',     str,      10,      True],  # TODO: add condition for O3STR
        [LSUNFL,     'LSUNFL',    str,      2,       LSUNFL in ['T', 'F', '1', '2', '3', '4']],
        [LBMNAM,     'LBMNAM',    str,      2,       LBMNAM in ['T', 'F']],
        [LFLTNM,     'LFLTNM',    str,      2,       LFLTNM in ['T', 'F']],
        [H2OAER,     'H2OAER',    str,      2,       H2OAER in ['T', 'F']],
        ['  ',       '2space',    str,      2,       True],
        [LDATDR,     'LDATDR',    str,      5,       LDATDR in ['T', '']],  # 'F' causes an error apparently...
        [SOLCON,     'SOLCON',    int,      5,       True]
    ], dtype=object)

    card2 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [APLUS,      'APLUS',     str,      2,       APLUS in ['', ' ', 'A+']],
        [IHAZE,      'IHAZE',     int,      3,       IHAZE in [-1, 0, 1, 2, 3, 4, 5, 6, 8, 9, 10]],
        [CNOVAM,     'CNOVAM',    str,      1,       CNOVAM in ['', 'N']],
        [ISEASN,     'ISEASN',    int,      4,       ISEASN in [0, 1, 2]],
        [ARUSS,      'ARUSS',     str,      3,       ARUSS in ['', 'USS']],
        [IVULCN,     'IVULCN',    int,      2,       IVULCN in [0, 1, 2, 3, 4, 5, 6, 7, 8]],
        [ICSTL,      'ICSTL',     int,      5,       ICSTL in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
        [ICLD,       'ICLD',      int,      5,       ICLD in [0]], # TODO: clouds are disabled for now
        [IVSA,       'IVSA',      int,      5,       IVSA in [0, 1]],
        [VIS,        'VIS',       float,    (10, 5), True],
        [WSS,        'WSS',       float,    (10, 5), True],
        [WHH,        'WHH',       float,    (10, 5), True],
        [RAINRT,     'RAINRT',    float,    (10, 5), True],
        [GNDALT,     'GNDALT',    float,    (10, 5), True]
    ], dtype=object)

    card3 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [H1,         'H1',        float,    (10, 5), True],
        [H2,         'H2',        float,    (10, 5), True],
        [ANGLE,      'ANGLE',     float,    (10, 5), True],
        [RANGE,      'RANGE',     float,    (10, 5), True],
        [BETA,       'BETA',      float,    (10, 5), BETA >= 0 and BETA <= 180],
        [RO,         'RO',        str,      10,      True],
        [LENN,       'LENN',      int,      5,       LENN in [0, 1]],
        ['     ',    'space',     str,      5,       True],
        [PHI,        'PHI',       float,    (10, 5), PHI >=0 and PHI <= 180]
    ], dtype=object)

    card3a1 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [IPARM,       'IPARM',    int,      5,       IPARM in [12]],
        [IPH,         'IPH',      int,      5,       IPH in [0, 2]],
        [IDAY,        'IDAY',     int,      5,       IDAY in range(1, 366)],
        [ISOURC,     'ISOURC',  int,      5,       ISOURC in [0, 1]],
    ], dtype=object)

    card3a2 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [PARM1,       'PARM1',    float,    (10, 3), PARM1 >= 0 and PARM1 <= 360],
        [PARM2,       'PARM2',    float,    (10, 3), PARM2 >= 0 and PARM2 <= 180],
        [PARM3,       'PARM3',    float,    (10, 3), True],
        [PARM4,       'PARM4',    float,    (10, 3), True],
        [TIME,        'TIME',     float,    (10, 3), True],
        [PSIPO,       'PSIPO',    float,    (10, 3), True],
        [ANGLEM,      'ANGLEM',   float,    (10, 3), ANGLEM >= 0 and ANGLEM <= 180],
        [G,           'G',        float,    (10, 3), G >= 0 and G <= 1]
    ], dtype=object)

    card4 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [V1,          'V1',       float,    (10, 3), True], # TODO: find MODTRAN's min and max wavelengths to add here
        [V2,          'V2',       float,    (10, 3), True],
        [DV,          'DV',       float,    (10, 3), True],
        [FWHM,        'FWHM',     float,    (10, 3), True],
        [YFLAG,       'YFLAG',    str,      1,       YFLAG in ['T', 'R']],
        [XFLAG,       'XFLAG',    str,      1,       XFLAG in ['W', 'M', 'N']],
        [DLIMIT,      'DLIMIT',   str,      8,       True],
        [FLAGS,       'FLAGS',    str,      7,       True], # TODO: add in specific conditions for each flag index
        [MLFLX,       'MLFLX',    int,      3,       True]
    ], dtype=object)

    card5 = np.array([
        #VARIABLE      NAME       TYPE      SIZE      CONDITION
        [IRPT,        'IRPT',     int,      5,       IRPT in [0, 1, -1, 3, -3, 4, -4]]
    ], dtype=object)


    def inputcheck(VARIABLE, name, var_type, condition):
        if type(VARIABLE) != var_type:
            raise TypeError(name + " = " + str(VARIABLE) + " must be of type " + str(var_type))
        if condition == False:
            raise ValueError("Invalid value entered for variable " + name + ": " +\
                             str(VARIABLE) + ".  Type 'help(modtran.run)' for valid entries.")

    def add_to_tape5(card):
        card_string = ''
        for i in range(card.shape[0]):
            VARIABLE = card[i, 0]
            name = card[i, 1]
            var_type = card[i, 2]
            size = card[i, 3]
            condition = card[i, 4]
            inputcheck(VARIABLE, name, var_type, condition)
            if var_type == str:
                card_string += A(VARIABLE, size)
            elif var_type == int:
                card_string += I(VARIABLE, size)
            elif var_type == float:
                card_string += F(VARIABLE, size[0], size[1])
            else:
                raise ValueError("Unexpected type for variable " + name)
        return card_string

    # Build Tape 5 file
    tape5 = ''
    for card in [card1, card1a, card2, card3, card3a1, card3a2, card4, card5]:
        tape5 += add_to_tape5(card)
        tape5 += "\n"
    output = {}
    output['tape5'] = tape5

    ####################################################################################################################
    """
                                         RUN MODTRAN ON LINUX SERVER
    """
    ####################################################################################################################

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # this will automatically add the keys
    ssh.connect(hostname, username=username, password=password)
    sftp = ssh.open_sftp()

    # Create a temporary directory called 'modtran-temp' and put the tape5 file in there
    stdin, stdout, stderr = ssh.exec_command('rm -rf modtran-temp')  # in case the user cntrl-c'd out of last run
    time.sleep(1)
    sftp.mkdir('modtran-temp')
    sftp.chdir('modtran-temp')
    remote_temp_folder = sftp.getcwd()
    local_folder = os.getcwd()
    stdin, stdout, stderr = ssh.exec_command('cd ' + remote_temp_folder + ';'
                                             'ln -s /dirs/pkg/Mod4v3r1/DATA DATA')
    tape5_file = sftp.open('tape5', 'w+')
    tape5_file.write(tape5)
    tape5_file.close()

    print('RUNNING MODTRAN...')
    if MODTRN in ['C', 'K']:
        print('    NOTE: CORRELATED K OPTION ENABLED - THIS COULD TAKE A WHILE...')
    stdin, stdout, stderr = ssh.exec_command('cd ' + remote_temp_folder + ';'
                                             '/dirs/pkg/Mod4v3r1/Mod4v3r1.exe;',
                                             get_pty=True)
    for line in iter(stdout.readline, ""):
        print(line, end="")

    print('DOWNLOADING OUTPUT FROM SERVER...')
    done = False
    while not done:
        try:
            sftp.get(remotepath=remote_temp_folder + '/tape7.scn',
                     localpath=local_folder + '/tape7.scn')
            sftp.get(remotepath=remote_temp_folder + '/tape7.scn',
                     localpath=local_folder + '/tape7.scn')
            done=True
        except:
            time.sleep(1)

    # delete temporary directory
    stdin, stdout, stderr = ssh.exec_command('rm -rf modtran-temp')
    sftp.close()
    ssh.close()

    with open('tape7.scn') as file:
        tape7scn = file.readlines()
    output['tape7.scn'] = tape7scn
    os.remove('tape7.scn')

    num_lines = len(tape7scn)
    num_header_lines = 11
    num_footer_lines = 1
    num_data_lines = num_lines - num_header_lines - num_footer_lines
    num_columns = 13

    tape7scn_array = np.zeros((num_data_lines, num_columns), dtype='<U16')
    for i in range(num_data_lines):
        row = num_header_lines + i
        tape7scn_array[i, 0] = tape7scn[row][  4: 12]  # WAVELEN_MCRN
        tape7scn_array[i, 1] = tape7scn[row][ 13: 19]  # TRANS
        tape7scn_array[i, 2] = tape7scn[row][ 20: 30]  # PTH_THRML
        tape7scn_array[i, 3] = tape7scn[row][ 31: 41]  # THRML_SCT
        tape7scn_array[i, 4] = tape7scn[row][ 42: 52]  # SURF_EMIS
        tape7scn_array[i, 5] = tape7scn[row][ 53: 63]  # SOL_SCAT
        tape7scn_array[i, 6] = tape7scn[row][ 64: 74]  # SING_SCAT
        tape7scn_array[i, 7] = tape7scn[row][ 75: 85]  # GRND_RFLT
        tape7scn_array[i, 8] = tape7scn[row][ 86: 96]  # DRCT_RFLT
        tape7scn_array[i, 9] = tape7scn[row][ 97:107]  # TOTAL_RAD
        tape7scn_array[i,10] = tape7scn[row][108:116]  # REF_SOL
        tape7scn_array[i,11] = tape7scn[row][117:125]  # SOLaOBS
        tape7scn_array[i,12] = tape7scn[row][129:134]  # DEPTH

    data_values = np.zeros_like(tape7scn_array, dtype=float)
    for j in range(num_columns):
        try:
            data_values[:, j] = tape7scn_array[:, j].astype(float)
        except:
            data_values[:, j] = np.nan

    output['WAVELEN MCRN'] = data_values[:, 0]
    output['TRANS']        = data_values[:, 1]
    output['PTH THRML']    = data_values[:, 2]
    output['THRML SCT']    = data_values[:, 3]
    output['SURF EMIS']    = data_values[:, 4]
    output['SOL SCAT']     = data_values[:, 5]
    output['SING SCAT']    = data_values[:, 6]
    output['GRND RFLT']    = data_values[:, 7]
    output['DRCT RFLT']    = data_values[:, 8]
    output['TOTAL RAD']    = data_values[:, 9]
    output['REF SOL']      = data_values[:,10]
    output['SOL@OBS']      = data_values[:,11]
    output['DEPTH']        = data_values[:,12]

    return output
