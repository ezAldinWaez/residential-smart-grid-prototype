import requests

# Aleppo coordinates
latitude = 36.21
longitude = 37.16

url = (
    f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
    f"parameters=T2M,WS2M,RH2M"
    f"&community=RE"
    f"&longitude={longitude}"
    f"&latitude={latitude}"
    f"&start=2017&end=2017"
    f"&format=JSON"
)

response = requests.get(url)
print(response.json())
