import os
import glob
from .classes import spct

def load_filters():
    folder = os.path.join("data", "filters_data")
    os.makedirs(folder, exist_ok=True)
    files = glob.glob(os.path.join(folder, "**", "*.tsv"), recursive=True)
    filters = []
    for file in files:
        filters.append(spct(file))
    return filters

def load_reflectors():
    folder = os.path.join("data", "reflectance_absorption")
    os.makedirs(folder, exist_ok=True)
    files = glob.glob(os.path.join(folder, "**", "*.tsv"), recursive=True)
    reflectors = []
    for file in files:
        reflectors.append(spct(file))
    return reflectors

def load_illuminants():
    folder = os.path.join("data", "illuminants")
    os.makedirs(folder, exist_ok=True)
    files = glob.glob(os.path.join(folder, "**", "*.tsv"), recursive=True)
    illuminants = []
    for file in files:
        illuminants.append(spct(file))
    return illuminants

def load_QEs():
    folder = os.path.join("data", "QE_data")
    os.makedirs(folder, exist_ok=True)
    files = glob.glob(os.path.join(folder, "**", "*.tsv"), recursive=True)
    QEs = []
    for file in files:
        QEs.append(spct(file))
    return QEs

















