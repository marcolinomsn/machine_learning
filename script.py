#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

from datetimee import add_time
from local_api import (
    download_forecasts,
    get_models,
    get_manage_regions,
    get_run_datetimes,
    get_states,
    retrieve_station_measures,
)

PATH = "/home/production/mba/machine_learning/"

if __name__ == "__main__":
    try:
        df_forecasts = pd.read_csv(PATH + "forecasts.csv")
    except:
        model_list = [
            "gfs3h",
            "wrf_tps_myj",
            "icon",
            "ecmwf",
            "wrf_kess_myj",
            "wrf",
            "wrf_wdm7_myj",
        ]
        models = get_models(model_list)
        states = get_states()
        regions = get_manage_regions()
        regions["state"] = regions.state_id.map(states.set_index("id").uf)
        regions = regions[regions.state == "SC"]
        regions.reset_index(drop=True, inplace=True)

        all_forecasts = []
        for i, region in regions.iterrows():
            for _, model in models.iterrows():
                run_datetimes = get_run_datetimes(model.id)
                for i, run_datetime in enumerate(run_datetimes):
                    print(f"{region['name']} | {model['name']} | {add_time(run_datetime)} [{i+1}/{len(run_datetimes)}]")
                    forecasts = download_forecasts(model.id, region.id, run_datetime)
                    forecasts["run_datetime"] = run_datetime
                    forecasts["model"] = model["name"]
                    forecasts["region"] = region["name"]
                    forecasts["state"] = region.state
                    forecasts["station_id"] = region.station_id
                    all_forecasts.append(forecasts)

                df_forecasts = pd.concat(all_forecasts)
                df_forecasts.to_csv(PATH     + "forecasts.csv", index=False)

    for region in df_forecasts.region.unique():
        df_region = df_forecasts[df_forecasts.region == region]
        station_ids = df_region.station_id.unique().astype(int).tolist()

        measures = retrieve_station_measures(
            df_region.datetime.min(),
            df_region.datetime.max(),
            station_ids,
        )

        measures = measures[["datetime", "precipitation_obs"]]

        merged = df_region.merge(measures, on="datetime", how="left")

        if "precipitation_obs_y" in merged.columns:
            values = merged["precipitation_obs_y"].values
        else:
            values = merged["precipitation_obs"].values

        df_forecasts.loc[df_forecasts.region == region, "precipitation_obs"] = values

    df_forecasts.datetime = df_forecasts.datetime.apply(add_time)
    df_forecasts.run_datetime = df_forecasts.run_datetime.apply(add_time)

    df_forecasts = df_forecasts[[
        "region",
        "state",
        "model",
        "run_datetime",
        "datetime",
        "precipitation",
        "precipitation_obs"
    ]]
    df_forecasts.to_csv(PATH + "dataset.csv", index=False)
