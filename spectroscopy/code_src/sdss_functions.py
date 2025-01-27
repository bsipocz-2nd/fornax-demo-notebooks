import os

import numpy as np

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table

import pandas as pd

from astroquery.sdss import SDSS

from data_structures_spec import MultiIndexDFObject

from specutils import Spectrum1D

def SDSS_get_spec(sample_table, search_radius_arcsec):
    '''
    Retrieves SDSS spectra for a list of sources. Note that no data will
    be directly downloaded. All will be saved in cache.

    Parameters
    ----------
    sample_table : `~astropy.table.Table`
        Table with the coordinates and journal reference labels of the sources
    search_radius_arcsec : `float`
        Search radius in arcseconds.

    Returns
    -------
    df_lc : MultiIndexDFObject
        The main data structure to store all spectra
        
    '''

    
    ## Initialize multi-index object:
    df_spec = MultiIndexDFObject()
    
    for stab in sample_table:

        ## Get Spectra for SDSS
        search_coords = stab["coord"]
        
        xid = SDSS.query_region(search_coords, radius=search_radius_arcsec * u.arcsec, spectro=True)

        if str(type(xid)) != "<class 'NoneType'>":
            sp = SDSS.get_spectra(matches=xid, show_progress=True)
    
            ## Get data
            wave = 10**sp[0]["COADD"].data.loglam * u.angstrom # only one entry because we only search for one xid at a time. Could change that?
            flux = sp[0]["COADD"].data.flux*1e-17 * u.erg/u.second/u.centimeter**2/u.angstrom 
            err = np.sqrt(1/sp[0]["COADD"].data.ivar)*1e-17 * flux.unit
            
            ## Add to df_spec.
            dfsingle = pd.DataFrame(dict(wave=[wave] , flux=[flux], err=[err],
                                     label=[stab["label"]],
                                     objectid=[stab["objectid"]],
                                     mission=["SDSS"],
                                     instrument=["SDSS"],
                                     filter=["optical"],
                                    )).set_index(["objectid", "label", "filter", "mission"])
            df_spec.append(dfsingle)

        else:
            print("Source {} could not be found".format(stab["label"]))


    return(df_spec)