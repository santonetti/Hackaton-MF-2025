import click
from pathlib import Path
from tqdm import tqdm
from icechunk.xarray import to_icechunk
from dask.diagnostics import ProgressBar

import xarray as xr
import icechunk
import numpy as np

import warnings

warnings.filterwarnings(
    "ignore",
    message="Numcodecs codecs are not in the Zarr version 3 specification*",
    category=UserWarning,
)
icechunk.set_logs_filter(
    "icechunk::storage::object_store=error"
)  # remove the warning due to the local icechunk store

ROOT_DIR = Path("/Volumes/T7")
RAW_FILES_DIR = ROOT_DIR / "raw_files/hackathon-meteo-france"

BUCKETS_DIR = ROOT_DIR / "buckets"
ICECHUNK_BUCKET = BUCKETS_DIR / "hackathon-meteo-france"
PREFIX_RCM = "RCM"

prefix = "file:///Volumes/"


def get_rcm_repo():
    storage = icechunk.local_filesystem_storage(path=str(ICECHUNK_BUCKET / PREFIX_RCM))
    config = icechunk.RepositoryConfig.default()

    repo = icechunk.Repository.open_or_create(
        storage, config, authorize_virtual_chunk_access={prefix: None}
    )
    return repo


def save_dataset(ds: xr.Dataset, repo: icechunk.Repository, path: str):
    session = repo.writable_session("main")
    with ProgressBar():
        to_icechunk(ds, session, group=path)
    msg = f"Import dataset {path}"
    snapshot = session.commit(msg)
    print(f"{snapshot} - {msg}")


def get_files(data_variables: list[str]):
    files = {
        k: list((RAW_FILES_DIR / "RCM").rglob(f"**/historical/**/{k}*.nc"))
        for k in data_variables
    }
    print({k: len(v) for k, v in files.items()})
    return files


def process_ds(ds: xr.Dataset) -> xr.Dataset:
    ds = ds.drop_vars(["lat_bnds", "lon_bnds"])

    dims = [
        "input_driving_source_id",
        "input_driving_variant_label",
        "input_source_id",
    ]
    for d in dims:
        ds = ds.expand_dims({d: np.array([ds.attrs[d]], dtype=str)})

    # restrict to >1950, since some models are missing 1950
    ds = ds.sel(time=slice("1951", "2014"))

    # create a unique dimension
    # 1. create a multi-index
    ds = ds.stack(source_id=dims)
    # 2. flatten the multi-index
    source_id_index = ds.indexes["source_id"].map(lambda x: f"{x[0]}:{x[1]}:{x[2]}")
    ds = ds.assign_coords(source_id_bis=("source_id", source_id_index))
    # 3. and only keep the flattened index
    ds = ds.set_index(source_id="source_id_bis")

    # drop bnds dim and associated time_bnds variable
    ds = ds.drop_dims("bnds")

    # ensure this order
    ds = ds.transpose("source_id", "time", "y", "x")
    return ds


def import_variable(var_name: str, repo: icechunk.Repository):
    print(f"Importing {var_name}: opening .nc files")
    files = get_files([var_name])[var_name]
    datasets = []
    for f in tqdm(files):
        ds = xr.open_dataset(f, chunks={})
        ds = process_ds(ds)
        datasets.append(ds)

    print("Combining into single dataset")
    combined = xr.combine_nested(
        datasets,
        concat_dim="source_id",
        combine_attrs="drop_conflicts",
        join="outer",
    )

    print("Rechunk")
    sizes = dict(combined[var_name].sizes)
    sizes["time"] = 128
    sizes["source_id"] = 1
    # 9.36M
    assert sizes == {"source_id": 1, "time": 128, "y": 134, "x": 143}
    combined = combined.chunk(sizes)

    print("Process and save to disk")
    save_dataset(combined, repo, var_name)


@click.command()
@click.argument(
    # Data variables to import, one after the other
    "data-variables",
    nargs=-1,
    type=str,
)
def import_variables(data_variables: list[str]):
    repo = get_rcm_repo()
    for var_name in data_variables:
        import_variable(var_name, repo)


if __name__ == "__main__":
    import_variables()
