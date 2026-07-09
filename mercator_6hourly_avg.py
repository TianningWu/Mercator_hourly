import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr


FILL_VALUE = np.float32(9.96921e36)
WINDOW_SIZE = 24  # hours
STEP = 6  # hours
DATA_VARS = ("zos", "uo", "vo")

GLOBAL_ATTRS = {
    "source": "MOI GLO12",
    "credit": "E.U. Copernicus Marine Service Information (CMEMS)",
    "references": "http://marine.copernicus.eu",
    "institution": "Mercator Ocean International",
    "title": "hourly mean fields from Global Ocean Physics Analysis and Forecast updated Daily",
    "producer": "CMEMS - Global Monitoring and Forecasting Centre",
    "Conventions": "CF-1.8",
    "contact": "https://marine.copernicus.eu/contact",
    "copernicusmarine_version": "2.0.1",
}

VARIABLE_ATTRS = {
    "zos": {
        "valid_min": np.float32(-5.0),
        "valid_max": np.float32(5.0),
        "unit_long": "Meters",
        "long_name": "Sea surface height",
        "units": "m",
        "standard_name": "sea_surface_height_above_geoid",
    },
    "uo": {
        "valid_min": np.float32(-10.0),
        "valid_max": np.float32(10.0),
        "unit_long": "Meters per second",
        "long_name": "Eastward surface velocity",
        "units": "m s-1",
        "standard_name": "eastward_sea_water_velocity",
    },
    "vo": {
        "valid_min": np.float32(-10.0),
        "valid_max": np.float32(10.0),
        "unit_long": "Meters per second",
        "long_name": "Northward surface velocity",
        "units": "m s-1",
        "standard_name": "northward_sea_water_velocity",
    },
}

COORD_ATTRS = {
    "depth": {
        "unit_long": "Meters",
        "long_name": "Depth",
        "units": "m",
        "standard_name": "depth",
        "positive": "down",
        "axis": "Z",
    },
    "latitude": {
        "unit_long": "Degrees North",
        "long_name": "Latitude",
        "units": "degrees_north",
        "standard_name": "latitude",
        "axis": "Y",
    },
    "longitude": {
        "unit_long": "Degrees East",
        "long_name": "Longitude",
        "units": "degrees_east",
        "standard_name": "longitude",
        "axis": "X",
    },
    "time": {
        "unit_long": "Hours Since 1950-01-01",
        "axis": "T",
        "long_name": "Time",
        "standard_name": "time",
        "units": "hours since 1950-01-01",
        "calendar": "gregorian",
    },
}


def parse_args():
    today_str = datetime.today().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(
        description="Create Mercator_IC.nc with 24-hour rolling means every 6 hours."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=f"./archives/Mercator_{today_str}_zos_uovo.nc",
        help="Hourly Mercator input NetCDF file.",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="./Mercator_IC.nc",
        help="Output initial-condition NetCDF file.",
    )
    return parser.parse_args()


def required_dim_order(data_array):
    return data_array.transpose("time", "depth", "latitude", "longitude")


def build_averaged_dataset(input_file):
    with xr.open_dataset(input_file, decode_times=False) as source:
        starts = list(range(0, source.sizes["time"] - WINDOW_SIZE + 1, STEP))
        if not starts:
            raise ValueError(
                f"{input_file} has {source.sizes['time']} time records; "
                f"at least {WINDOW_SIZE} are required."
            )

        for start in starts:
            print(source["time"].isel(time=start).item())

        output_time = source["time"].isel(time=starts).astype("float32")
        output_time.attrs = COORD_ATTRS["time"]

        coords = {
            "time": output_time,
            "depth": source["depth"].astype("float32"),
            "latitude": source["latitude"].astype("float32"),
            "longitude": source["longitude"].astype("float32"),
        }

        for coord_name in ("depth", "latitude", "longitude"):
            coords[coord_name].attrs = COORD_ATTRS[coord_name]

        data_vars = {}
        for var_name in DATA_VARS:
            averages = []
            for start in starts:
                average = (
                    source[var_name]
                    .isel(time=slice(start, start + WINDOW_SIZE))
                    .mean("time")
                )
                averages.append(average)

            data_array = xr.concat(averages, dim=output_time)
            data_array = required_dim_order(data_array).astype("float32")
            data_array.attrs = VARIABLE_ATTRS[var_name]
            data_vars[var_name] = data_array

        dataset = xr.Dataset(data_vars=data_vars, coords=coords, attrs=GLOBAL_ATTRS)
        return dataset.load()


def write_dataset(dataset, output_file):
    encoding = {
        var_name: {"dtype": "float32", "_FillValue": FILL_VALUE}
        for var_name in DATA_VARS
    }
    encoding.update(
        {
            "time": {"dtype": "float32", "_FillValue": None},
            "depth": {"dtype": "float32", "_FillValue": None},
            "latitude": {"dtype": "float32", "_FillValue": None},
            "longitude": {"dtype": "float32", "_FillValue": None},
        }
    )
    dataset.to_netcdf(
        output_file,
        format="NETCDF4",
        unlimited_dims=["time"],
        encoding=encoding,
    )


def main():
    args = parse_args()
    output_file = Path(args.output_file)
    if output_file.exists():
        output_file.unlink()

    dataset = build_averaged_dataset(args.input_file)
    write_dataset(dataset, output_file)


if __name__ == "__main__":
    main()
