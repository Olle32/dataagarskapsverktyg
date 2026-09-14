"""
bake.py — läser data/nordfordon.yaml och gör om innehållet till det
format Cytoscape.js förväntar sig (en lista av "elements": noder och kanter).

Steg 1 av 2: skriv bara ut JSON i terminalen, för att se att omvandlingen
blir rätt innan vi bakar in den i HTML-filen.
"""

import yaml
import json

with open("data/nordfordon.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

elements = []

# Noder: ett element per system
for system in data["systems"]:
    elements.append({
        "data": {
            "id": system["id"],
            "label": system["name"]
        }
    })

# Kanter: ett element per flöde
for i, flow in enumerate(data["flows"]):
    elements.append({
        "data": {
            "id": f"flow-{i}",
            "source": flow["from"],
            "target": flow["to"],
            "label": flow["object"]
        }
    })

print(json.dumps(elements, indent=2, ensure_ascii=False))
