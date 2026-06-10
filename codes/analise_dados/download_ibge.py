import urllib.request
import json

url = 'https://servicodados.ibge.gov.br/api/v3/malhas/estados/35?formato=application/vnd.geo+json&intrarregiao=distrito'

try:
    print(f'Fetching {url}')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req, timeout=30)
    data = json.loads(r.read())
    
    # Filter features for São Paulo city (codarea starts with 3550308)
    sp_features = []
    for f in data.get('features', []):
        # O id no IBGE para distrito é 3550308xx
        if str(f['properties']['codarea']).startswith('3550308'):
            sp_features.append(f)
            
    print(f"Found {len(sp_features)} districts for SP city.")
    
    data['features'] = sp_features
    with open('codes/streamlit/assets/distritos_sp.geojson', 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False)
    print("Saved SP city districts to GeoJSON.")
except Exception as e:
    print(f'Error: {e}')
