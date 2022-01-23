from flask import Flask, request, render_template

import requests

app = Flask(__name__)

BASE_URL = "https://seabreeze.conteir.no"
REFERENCE_SET = '447562003'
BRANCH = 'MAIN'
ACTIVE = 'true'
LIMIT = 50


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        map_target = request.form['map_target']
        if map_target != "":
            concept_ids = get_concept_id_by_map_target(map_target)
            if len(concept_ids) == 0:
                return render_template("index.html", text="0 results found")
            else:
                snomed_cts = get_snomed_ct(concept_ids)
                icd_10 = map_target
                # render here in div
                return render_template("index.html", snomed_cts=snomed_cts, icd_10=icd_10)
        else:
            # render here in div
            return render_template("index.html", text="Unknown ICD-10")


def get_concept_id_by_map_target(map_target):
    url = f"{BASE_URL}/{BRANCH}/members?referenceSet={REFERENCE_SET}&active={ACTIVE}&mapTarget={map_target}&offset=0" \
          f"&limit={LIMIT} "
    response = requests.get(url)
    data = response.json()
    concept_ids = []
    all_items = data['items']
    if len(all_items) == 0:
        # no map target
        return concept_ids
    else:
        for item in all_items:
            concept_ids.append(item['referencedComponent']['conceptId'])
        unique_concept_ids = list(set(concept_ids))
        return unique_concept_ids


def get_snomed_ct(concept_ids):
    response_data = {}
    query_params = '&conceptIds='.join(concept_ids)
    url = f"{BASE_URL}/browser/{BRANCH}/concepts?conceptIds={query_params}"
    response = requests.get(url).json()
    for item in response['items']:
        # for each item get conceptId, active, term
        concept_id = item["conceptId"]
        active = item["active"]
        term = item['descriptions'][0]['term']
        if active:
            response_data[concept_id] = term
    return response_data
