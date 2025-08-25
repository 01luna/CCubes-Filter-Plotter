import pandas as pd
import numpy as np
import copy
import os 
import glob
import hashlib
import pickle

from .helpers import rgb2hex
from .constants import INTERP_GRID
from warnings import warn
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
        "extrapolated":"mask",
        }   



class spct:
    QE=None
    def __init__(self,tsv_path=None, **kwargs):
        self.dat=[]
        self.interp= True
        self.isintegrated=False
        self.wl=INTERP_GRID

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
                case 'S'| 'U'| 'O':
                    value = value[0]
        super().__setattr__(name, value)


    def __getattr__(self,key):
        if key=='RGB' and hasattr(self,'R') and hasattr(self,'G') and hasattr(self,'B'):
            return np.array([self.R, self.G, self.B]).transpose()
        return super().__getattribute__(key) 

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
        obj.color=obj.ccolor()
        return obj
    
    
    def integrate(self):
        if self.isIntegrated return
        for attr in self.dat:
            valid = ~np.isnan(getattr(self, attr))
            setattr(self, attr, np.trapz(getattr(self, attr)[valid], self.wl[valid]))
        delattr(self,'wl')
        self.isintegrated = True
    def integrated(self):
        new= copy.deepcopy(self)
        new.integrate()
        return new
    #calculated color
    def getcolor(self,arr=false):
        if hasattr(self,'RGB'):
            return  rgb2hex(self.integrated().RGB)
        return rgb2hex((self.QE*self).integrated().RGB / (self.QE.integrated().RGB))


class spcts:
    def __init__(self,tsv_dir=None,spectra=None):
        #allow passing a list of spectra
        if spectra is not None:
            self.spectra = spectra
            return

        f= glob.glob(os.path.join('data',tsv_dir, "**/*.tsv"),recursive=True)
        # generate hash        
        info='|'.join([f"{i}-{os.path.getmtime(i)}" for i in f])
        self.hash = hashlib.md5(info.encode()).hexdigest()
        # load cached if exists
        cache_path = os.path.join('cache', tsv_dir+'.pkl')
        if os.path.exists(cache_path):
            cached=pickle.load(open(cache_path, 'rb'))
            #use cached if hash matches
            if cached.hash == self.hash:
                print("Using cached spectra from", cache_path)
                self.spectra=cached.spectra
                return
        else:
            os.makedirs('cache', exist_ok=True)
        # otherwise load from tsv and update cache
        self.spectra=[spct(f) for f in glob.glob(os.path.join('data',tsv_dir, "**/*.tsv"),recursive=True)]
        pickle.dump(self, open(cache_path, 'wb+'))

    def __getattr__(self,key):
        if key.endswith('s'):
           return [getattr(i,key.removesuffix('s')) for i in self.spectra]
        return super().__getattribute__(key)
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.spectra[key]
        if key in self.names:
            r= [s for s in self.spectra if s.name == key]
            if len(r)>1: warn(f"Multiple spectra found with name {key}. Returning first one.")
            return r[0]
        if len(key)>1: 
            return [self[k] for k in key]
        raise KeyError(f"{key} not found in spectra")

    def __iter__(self):
        return iter(self.spectra)
    def sort(self,s):
        self.spectra.sort(key=lambda x: getattr(x, s))
    def sorted(self, s):
        return spcts(spectra=sorted(self.spectra, key=lambda x: getattr(x, s)))


filters=spcts('filters')
illuminants=spcts('illuminants')
QEs=spcts('QEs')
reflectors=spcts('reflectors')
spcts.QE=QEs['Eye']
