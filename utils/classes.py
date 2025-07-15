import pandas as pd
import numpy as np
import copy

from .constants import INTERP_GRID

colmap={
        "wavelength (nm)":"wl",
        "wavelength":"wl",
        "transmittance":"Tfr",
        "reflectance":"Rfr",
        "manufacturer":"brand",
        "model":"name",
        "name":"name",
        "description":"desc",
        "hex_color":"color",
        "power":"power",
        "filter number":"fn",
        }   

class spct:
    dat=[]
    interp=True
    wl=INTERP_GRID
    def __init__(self,tsv_path=None, **kwargs):
        if tsv_path:
            df = pd.read_csv(tsv_path, sep="\t")
            for col in df.columns:
                setattr(self, col, df[col].values)
        if kwargs:
            for key, val in kwargs.items():
                setattr(self, key, val)
        if self.interp:
            self.interpolate()

        
    #use lookup table to map column names to attributes
    def __setattr__(self, name, value):
        if name.lower() in colmap:
            name = colmap[name.lower()]
        if isinstance(value,np.ndarray):
            match value.dtype.kind:
                case 'i'| 'f'| 'u':
                    if name!='wl' and name !='fn' and name not in self.dat:
                        self.dat.append(name)
                case 'S'| 'U':
                    value = value[0]
        super().__setattr__(name, value)


    def interpolate(self, wl=INTERP_GRID):
        for attr in self.dat:

            setattr(self, attr, np.interp(wl, self.wl, getattr(self, attr),left=np.nan, right=np.nan))
        self.wl = wl
    
    def __mul__(self,other):
        obj= copy.deepcopy(self)
        if isinstance(other, spct):
            other = getattr(other, other.dat[0])
        for attr in self.dat:
            setattr(obj, attr, getattr(self, attr) * other)
        return obj

