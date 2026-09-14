"""
bake.py — läser data/nordfordon.yaml, gör om innehållet till Cytoscape-format
och bakar in det i en fristående HTML-fil (web/karta.html).

Flöden mellan samma par av system slås ihop till en kant med flera
informationsobjekt i etiketten. System utan utpekad owning_function
markeras visuellt (analysfunktion 1). En väljare för informationsobjekt
ger källspårning (analysfunktion 2) och konsumentspårning (analysfunktion 3).
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
            "owner": system["owning_function"]
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

antal_utan_agare = sum(1 for s in data["systems"] if s["owning_function"] is None)

consumers_by_object = {c["object"]: c["consumers"] for c in data["consumers"]}

info_objects = []
for obj in data["information_objects"]:
    info_objects.append({
        "id": obj["id"],
        "name": obj["name"],
        "source_system": obj["source_system"],
        "consumers": consumers_by_object.get(obj["id"], [])
    })

info_objects_json = json.dumps(info_objects, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <title>Dataägarskap och informationsflöden — Nordfordon AB</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; max-width: 1100px; }}
    #graf {{ width: 100%; height: 700px; border: 1px solid #ccc; }}
    .varning {{ color: #a33; font-weight: bold; }}
    .panel {{ margin: 1rem 0; padding: 1rem; background: #f5f5f5; border-radius: 6px; }}
    #konsumenter {{ margin-top: 0.5rem; }}
    select {{ font-size: 1rem; padding: 0.3rem; }}
  </style>
</head>
<body>
  <h1>Dataägarskap och informationsflöden — Nordfordon AB (fiktivt exempel)</h1>
  <p class="varning">⚠ {antal_utan_agare} system saknar utpekad ägare (röd kant i grafen)</p>

  <div class="panel">
    <label for="objektval"><strong>Spåra ett informationsobjekt:</strong></label><br>
    <select id="objektval">
      <option value="">— välj —</option>
    </select>
    <div id="konsumenter"></div>
  </div>

  <div id="graf"></div>

  <script>
    var infoObjects = {info_objects_json};

    var cy = cytoscape({{
      container: document.getElementById('graf'),
      elements: {elements_json},
      style: [
        {{ selector: 'node', style: {{ 'label': 'data(label)', 'background-color': '#1f3a5f', 'color': '#1f3a5f', 'text-valign': 'bottom', 'text-margin-y': 6 }} }},
        {{ selector: 'node[!owner]', style: {{ 'border-width': 4, 'border-color': '#c0392b', 'border-style': 'solid' }} }},
        {{ selector: 'node.kalla', style: {{ 'background-color': '#1a7a3c', 'border-width': 4, 'border-color': '#1a7a3c' }} }},
        {{ selector: 'edge', style: {{ 'label': 'data(label)', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'font-size': 10, 'color': '#555', 'text-background-color': '#fff', 'text-background-opacity': 1, 'text-background-padding': 2 }} }}
      ],
      layout: {{ name: 'breadthfirst', directed: true, spacingFactor: 1.5 }}
    }});

    var select = document.getElementById('objektval');
    infoObjects.forEach(function(obj) {{
      var option = document.createElement('option');
      option.value = obj.id;
      option.textContent = obj.name;
      select.appendChild(option);
    }});

    select.addEventListener('change', function() {{
      cy.nodes().removeClass('kalla');
      var konsumentDiv = document.getElementById('konsumenter');

      if (!this.value) {{
        konsumentDiv.textContent = '';
        return;
      }}

      var valt = infoObjects.find(function(o) {{ return o.id === select.value; }});

      cy.getElementById(valt.source_system).addClass('kalla');

      konsumentDiv.innerHTML = '<strong>Källsystem:</strong> ' + valt.source_system +
        '<br><strong>Konsumenter (' + valt.consumers.length + '):</strong> ' + valt.consumers.join(', ');
    }});
  </script>
</body>
</html>
"""

with open("web/karta.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Klart: web/karta.html ({len(info_objects)} spårbara informationsobjekt)")
