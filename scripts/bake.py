"""
bake.py — läser data/nordfordon.yaml, gör om innehållet till Cytoscape-format
och bakar in det i en fristående HTML-fil (web/karta.html).

Flöden mellan samma par av system slås ihop till en kant med flera
informationsobjekt i etiketten. System utan utpekad owning_function
markeras visuellt i grafen (analysfunktion: "system utan ägare").
"""

import yaml
import json
from collections import defaultdict

with open("data/nordfordon.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

elements = []

for system in data["systems"]:
    elements.append({
        "data": {
            "id": system["id"],
            "label": system["name"],
            "owner": system["owning_function"]  # None om ingen ägare finns
        }
    })

grouped_flows = defaultdict(list)
for flow in data["flows"]:
    key = (flow["from"], flow["to"])
    grouped_flows[key].append(flow["object"])

for i, ((source, target), objects) in enumerate(grouped_flows.items()):
    elements.append({
        "data": {
            "id": f"flow-{i}",
            "source": source,
            "target": target,
            "label": ", ".join(objects)
        }
    })

elements_json = json.dumps(elements, ensure_ascii=False)

# Räkna ut hur många system som saknar ägare, för en textrad ovanför grafen
antal_utan_agare = sum(1 for s in data["systems"] if s["owning_function"] is None)

html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <title>Dataägarskap och informationsflöden — Nordfordon AB</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    #graf {{ width: 100%; height: 700px; border: 1px solid #ccc; }}
    .varning {{ color: #a33; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Dataägarskap och informationsflöden — Nordfordon AB (fiktivt exempel)</h1>
  <p class="varning">⚠ {antal_utan_agare} system saknar utpekad ägare (röd kant nedan)</p>
  <div id="graf"></div>

  <script>
    var cy = cytoscape({{
      container: document.getElementById('graf'),
      elements: {elements_json},
      style: [
        {{ selector: 'node', style: {{ 'label': 'data(label)', 'background-color': '#1f3a5f', 'color': '#1f3a5f', 'text-valign': 'bottom', 'text-margin-y': 6 }} }},
        {{ selector: 'node[owner]', style: {{ 'border-width': 0 }} }},
        {{ selector: 'node[?owner]', style: {{ 'border-width': 0 }} }},
        {{ selector: 'node[!owner]', style: {{ 'border-width': 4, 'border-color': '#c0392b', 'border-style': 'solid' }} }},
        {{ selector: 'edge', style: {{ 'label': 'data(label)', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'font-size': 10, 'color': '#555', 'text-background-color': '#fff', 'text-background-opacity': 1, 'text-background-padding': 2 }} }}
      ],
      layout: {{ name: 'breadthfirst', directed: true, spacingFactor: 1.5 }}
    }});
  </script>
</body>
</html>
"""

with open("web/karta.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Klart: web/karta.html ({antal_utan_agare} system utan ägare)")
