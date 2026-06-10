import urllib.request
import json

# Tentar várias URLs possíveis
urls = [
    "https://raw.githubusercontent.com/codigourbano/distritos-sp/master/distritos-sao-paulo.geojson",
    "https://raw.githubusercontent.com/codigourbano/distritos-sp/main/distritos-sao-paulo.geojson",
    "https://raw.githubusercontent.com/codigourbano/distritos-sp/master/distritos.geojson",
    "https://raw.githubusercontent.com/codigourbano/distritos-sp/main/distritos.geojson",
]

for url in urls:
    try:
        print(f"Trying: {url}")
        r = urllib.request.urlopen(url, timeout=10)
        data = json.loads(r.read())
        print(f"  SUCCESS! Type: {data['type']}, Features: {len(data['features'])}")
        f = data['features'][0]
        print(f"  Property keys: {list(f['properties'].keys())}")
        print(f"  Example: {f['properties']}")
        
        # Salvar
        with open("codes/streamlit/assets/distritos_sp.geojson", "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        print(f"  Saved to codes/streamlit/assets/distritos_sp.geojson")
        break
    except Exception as e:
        print(f"  FAILED: {e}")
