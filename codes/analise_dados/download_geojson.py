import urllib.request
import json

urls = [
    'https://raw.githubusercontent.com/seade-R/dados-sp/master/data-raw/distritos.geojson',
    'https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-3550308-bairros.json',
    'https://raw.githubusercontent.com/datasets-br/bairros-sp/master/data/bairros.geojson'
]

for u in urls:
    try:
        print(f'Trying {u}')
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=10)
        d = json.loads(r.read())
        print(f'SUCCESS! {u} has {len(d.get("features", []))} features')
        
        # Check first feature properties
        if len(d.get("features", [])) > 0:
            print("Properties:", list(d["features"][0]["properties"].keys()))
            
        with open('codes/streamlit/assets/distritos_sp.geojson', 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
        break
    except Exception as e:
        print(f'FAIL {u}: {e}')
