#!/usr/bin/python3

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "qNXpLJ1Fhfls4yiGkUhswQISjXUWxwTG_DHUEu81_L0TiMANS2hC-6QT4Mch_q8QoYSJXDQIlT4f0trMpVXD3Q=="
org = "my-org"
bucket = "kpimon"

with InfluxDBClient(url="http://192.168.8.209:32086", token=token, org=org) as client:
    query = 'from(bucket: "kpimon") |> range(start: -1m)'
    # query = 'from(bucket:"kpimon") |> range(start: -2880m) |> filter(fn:(r) => r._measurement == "UeMetrics") |> filter(fn:(r) => r._field == "DRB_UECqiUl")'
    tables = client.query_api().query(query, org=org)
    i = 0
    for table in tables:
        for record in table.records:
            if i%10 == 0:
                print(i)
                break
            print(record)
            i = i + 1
    client.close()