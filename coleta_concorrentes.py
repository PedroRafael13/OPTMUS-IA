import requests
import pandas as pd

API_KEY = "AIzaSyAveoB26MVISXZ6tbv6OX42k0MmpTIhRsE"
LOCATION = "-3.0789644748130747,-60.012589815229234"  # sem espaço depois da vírgula
RADIUS = 5000
TYPE = "establishment"  # use "establishment" primeiro para validar

url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={LOCATION}&radius={RADIUS}&type={TYPE}&key={API_KEY}"

res = requests.get(url).json()
print(res)  # debug da resposta

data = []
for place in res.get("results", []):
    data.append({
        "nome": place["name"],
        "endereco": place.get("vicinity", ""),
        "avaliacao": place.get("rating", 0),
        "lat": place["geometry"]["location"]["lat"],
        "lng": place["geometry"]["location"]["lng"]
    })

df = pd.DataFrame(data)
print(df)
df.to_csv("concorrentes.csv", index=False)
