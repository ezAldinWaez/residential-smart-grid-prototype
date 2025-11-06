import requests

url = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-GOES-aggregated-v4-0-0-download.json?api_key=S9EfmFCqhUyvo2TWTB97OILdA1m1M9dK6nKT8dtW"

payload = (
    "api_key=S9EfmFCqhUyvo2TWTB97OILdA1m1M9dK6nKT8dtW"
    "&names=2020,2021,2022,2023"
    "&utc=true"
    "&leap_day=true"
    "&interval=30"
    "&email=ez.aldin.waez@gmail.com"
    "&wkt=POINT(-112.0740 33.4484)"
)

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)
