import folium
import pandas as pd

df = pd.read_csv('concorrentes.csv')

# Criando mapa centralizado na empresa
mapa = folium.Map(location=[-3.0789644748130747, -60.012589815229234], zoom_start=13)

# Marcadores para cada concorrente
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['lat'], row['lng']],
        popup=f"{row['nome']} - Avaliação: {row['avaliacao']}"
    ).add_to(mapa)

# Marcador da sua empresa
folium.Marker(
    location=[-3.0789644748130747, -60.012589815229234],
    popup='Minha Empresa',
    icon=folium.Icon(color='red')
).add_to(mapa)

mapa.save('mapa_concorrentes.html')
