#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

from datetimee import FIVE_DAYS_IN_MS, add_time
from local_api import (
    download_forecasts,
    get_models,
    get_manage_regions,
    get_run_datetimes,
    retrieve_station_measures,
)


if __name__ == "__main__":
    try:
        all_forecasts = pd.read_csv("all_forecasts.csv")
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
        regions = get_manage_regions()
        regions = regions[regions.name == "BR-116 - 01 Curitiba - PR"]

        all_forecasts = []
        for _, model in models.iterrows():
            run_dates = get_run_datetimes(model.id)
            for rdate in run_dates:
                if rdate < 1744934400000:
                    continue
                edate = rdate + FIVE_DAYS_IN_MS
                for _, region in regions.iterrows():
                    print(f"{model['name']} | {region['name']} | {add_time(rdate)} | {add_time(edate)}")
                    forecasts = download_forecasts(model.id, region.id, rdate, rdate, edate)
                    forecasts["model"] = model["name"]
                    forecasts["run_datetime"] = rdate
                    all_forecasts.append(forecasts)

        all_forecasts = pd.concat(all_forecasts)
        all_forecasts.to_csv("all_forecasts.csv", index=False)
        print()

    sdate = all_forecasts.datetime.min()
    edate = all_forecasts.datetime.max()

    measures = retrieve_station_measures(sdate, edate, [547])

    all_forecasts = all_forecasts.merge(measures, on="datetime", how="inner")

    all_forecasts.datetime = all_forecasts.datetime.apply(add_time)
    all_forecasts.run_datetime = all_forecasts.run_datetime.apply(add_time)

    all_forecasts = all_forecasts[["model", "run_datetime", "datetime", "precipitation", "precipitation_obs"]]

    all_forecasts.to_csv("dataset.csv", index=False)
