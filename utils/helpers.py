import numpy as np
def rgb2hex(rgb):
    return np.apply_along_axis(_1rgb2hex,-1,rgb)
def _1rgb2hex(rgb):
    c=np.nan_to_num(rgb*255).astype(int)
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
