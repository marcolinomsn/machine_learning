#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests

import numpy as np
import pandas as pd

from datetimee import FIVE_DAYS_IN_MS
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
headers = {"authorization": os.getenv("AUTHORIZATION"), "api_key": os.getenv("API_KEY")}

def post(complement, data=None, files=None, _json=None, params=None):
    response = requests.post(
        API_URL + complement,
        data=data,
        files=files,
        json=_json,
        params=params,
        headers=headers,
        timeout=2000,
    )
    return response


def get(complement, params=None, as_text=False, as_df=False, mode=None):
    response = requests.get(API_URL + complement, headers=headers, params=params)
    # print(f"[GET] {complement} {response}")

    try:
        result = response.json()
    except Exception as e:
        print(f"{complement} | Error: {e}")

    try:
        response.raise_for_status()
        result = result["data"]
    except:
        pass

    if as_text:
        result = response.text
    elif as_df:
        result = pd.DataFrame(result)

    return result


def get_models(model_list=None, rename_columns=None):
    models = get("/forecast-models", as_df=True)
    if model_list:
        models = models[models.alias.isin(model_list)]
    if rename_columns:
        models.rename(columns=rename_columns, inplace=True)
    return models


def get_states():
    return get("/states", as_df=True)


def get_manage_regions(rename_columns=None, mode=None):
    regions = get("/manage/forecast-regions", as_df=True, mode=mode)
    regions = regions[(~regions.inactive) & (~np.isnan(regions.station_id))]
    regions.loc[:, "station_id"] = regions.station_id.astype(int)

    regions = regions.sort_values(by="name")
    if rename_columns:
        regions.rename(columns=rename_columns, inplace=True)
    return regions


def download_forecasts(model_id, region_id, rdate, sdate, edate, var_params):
    complement = f"/forecast-models/{model_id}/download"
    params = {
        "region_id": region_id,
        "run_datetime": rdate,
        "datetimeStart": sdate,
        "datetimeEnd": edate,
    }
    params.update(var_params)
    return get(complement, as_df=True, params=params)


def download_forecasts(model_id, region_id, rdate):
    complement = f"/forecast-models/{model_id}/download"
    params = {
        "region_id": region_id,
        "run_datetime": rdate,
        "datetimeStart": rdate,
        "datetimeEnd": rdate + FIVE_DAYS_IN_MS,
        "precipitation": "abs",
        "frequency": 3600000,
    }
    return get(complement, as_df=True, params=params)


def get_run_datetimes(model_id):
    params = {"model_id": model_id}
    return get("/forecasts/run-datetimes", params=params)


def retrieve_station_measures(sdate, edate, station_ids, as_df=True):
    params = {
        "datetime_start": sdate,
        "datetime_end": edate,
        "station_ids": station_ids,
        "variables": [{"variable_id": 34, "operations": ["sum"]}],
    }
    try:
        result = post("/stations/measures", _json=params)
        data = result.json()["data"]
        if as_df:
            df = pd.DataFrame(data[0]["results"])
            df = df.dropna(
                how="all", subset=df.columns.difference(["datetime"])
            )
            df.precipitation = df.precipitation.apply(
                lambda x: float(x["abs"]) if isinstance(x, dict) else x
            )
            df.rename(columns={"precipitation": "precipitation_obs"}, inplace=True)
            return df
        else:
            return data
    except:
        return pd.DataFrame()
