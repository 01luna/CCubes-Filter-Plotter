# /utils/importers/filter_importer.py

import pandas as pd
import numpy as np
import os
from scipy.interpolate import interp1d

def safe_float(val):
    try:
        return float(str(val).replace(',', '.').strip())
    except Exception:
        return np.nan

def import_filter_from_csv(uploaded_file, meta, extrap_lower, extrap_upper):
    try:   
        raw_data = pd.read_csv(uploaded_file, sep=';', header=None, engine='python')
        if raw_data.shape[1] < 2:
            raw_data = pd.read_csv(uploaded_file, sep=',', header=None, engine='python')
        if raw_data.shape[1] < 2:
               return False, "Could not read two columns from the CSV."

        raw_data = raw_data.applymap(safe_float)
        wavelengths = raw_data.iloc[:, 0].dropna().values
        transmissions = raw_data.iloc[:, 1].dropna().values

        if wavelengths.size == 0 or transmissions.size == 0:
            return False, "Wavelength or transmission columns are empty."

        sort_idx = np.argsort(wavelengths)
        wavelengths = wavelengths[sort_idx]
        transmissions = transmissions[sort_idx]

        base_min = int(np.ceil(wavelengths.min() / 5.0)) * 5
        base_max = int(np.floor(wavelengths.max() / 5.0)) * 5

        min_wl = 300 if extrap_lower else base_min
        max_wl = 1100 if extrap_upper else min(1100, base_max)

        if min_wl > max_wl:
            return False, "Data range is outside allowable bounds."

        new_wavelengths = np.arange(min_wl, max_wl + 1, 1)
        interpolator = interp1d(wavelengths, transmissions, kind='linear', bounds_error=False, fill_value=np.nan)
        interpolated = interpolator(new_wavelengths)

        if extrap_lower:
            below_mask = new_wavelengths < wavelengths.min()
            interpolated[below_mask] = transmissions[0]
        if extrap_upper:
            above_mask = new_wavelengths > wavelengths.max()
            interpolated[above_mask] = transmissions[-1]

        interpolated = np.clip(np.round(interpolated, 3), 0.0, None)

        output_df = pd.DataFrame([interpolated], columns=new_wavelengths)
        output_df.insert(0, 'Filter Number', meta["filter_number"])
        output_df.insert(1, 'Filter Name', meta["filter_name"])
        output_df.insert(2, 'Manufacturer', meta["manufacturer"])
        output_df.insert(3, 'Hex Color', meta["hex_color"])

        base = f"{meta['manufacturer']}_{meta['filter_number']}_{meta['filter_name']}"
        sanitized = ''.join(c for c in base if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')

        suffix_parts = []
        if extrap_lower: suffix_parts.append("300")
        if extrap_upper: suffix_parts.append("1100")
        suffix = f"_extrapolated_{'_'.join(suffix_parts)}" if suffix_parts else ""

        filename = f"{sanitized}{suffix}.tsv"
        out_dir = os.path.join("data", "filters_data", meta["manufacturer"])
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)
        output_df.to_csv(out_path, sep='\t', index=False)

        return True, f"Filter data saved to {out_path}"
    except Exception as e:
        return False, f"Error: {str(e)}"
