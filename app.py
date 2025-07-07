import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from send_email import send_email

app = Flask(__name__)
DATA_FILE = 'plants.json'


def load_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def format_plants(plants):
    formatted = []
    for name, details in plants.items():
        entry = (
            f"🪴 {name}\n"
            f"  Last Watered: {details.get('lastWatered', 'N/A') or 'Not yet'}\n"
            f"  Last Fertilized: {details.get('fertilized', 'N/A') or 'Not yet'}\n"
            f"  Water Every: {details.get('waterFreq')} days\n"
            f"  Fertilize Every: {details.get('fertilizeFreq')} days\n"
        )
        formatted.append(entry)
    return "\n".join(formatted)


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_plants_needing_water(plants):
    today = datetime.today().date()
    needs_water = []

    for name, info in plants.items():
        last_watered = info.get("lastWatered")
        freq = info.get("waterFreq")

        if not last_watered or not freq:
            continue

        try:
            last_date = datetime.strptime(last_watered, "%Y-%m-%d").date()
        except ValueError:
            continue

        if today >= last_date + timedelta(days=int(freq)):
            needs_water.append(name)

    return needs_water


def get_plants_needing_fertilizer(plants):
    today = datetime.today().date()
    needs_fertilizer = []

    for name, info in plants.items():
        last_fertilized = info.get("fertilized")
        freq = info.get("fertilizeFreq")

        if not freq:
            continue  # Skip if no fertilizing schedule

        try:
            last_date = datetime.strptime(
                last_fertilized, "%Y-%m-%d").date() if last_fertilized else None
        except ValueError:
            continue  # Skip bad date format

        # If never fertilized or due again
        if last_date is None or today >= last_date + timedelta(days=int(freq)):
            needs_fertilizer.append(name)

    return needs_fertilizer


@app.route('/', methods=['GET'])
def home():
    return "<p>Welcome to my plant app<p>"


@app.route('/update-plant', methods=['POST'])
def update_plant():
    data = request.get_json(force=True)
    plants = load_data()  # This should return a dict as shown above

    print("Received data:", data)

    plant_name = data.get("name")
    if not plant_name or plant_name not in plants:
        plants[plant_name] = {
            "lastWatered": "",
            "fertilized": "",
            "waterFreq": None,
            "fertilizeFreq": None
        }

    # Update the fields (if provided)
    if "lastWatered" in data:
        plants[plant_name]["lastWatered"] = data["lastWatered"]
    if "fertilized" in data:
        plants[plant_name]["fertilized"] = data["fertilized"]

    save_data(plants)
    return jsonify({plant_name: plants[plant_name]}), 200


@app.route('/due-plants', methods=['GET'])
def due_plants():
    plants = load_data()
    due = get_plants_needing_water(plants)
    if due:
        body = "The following plants need fertilizing today:\n\n" + \
            "\n".join(due)
        send_email("Plants that need watering today", body)
    else:
        send_email("No plants need watering today", ":)")
    return jsonify({"needsWater": due}), 200


@app.route('/due-fertilizing', methods=['GET'])
def due_fertilizing():
    plants = load_data()
    due = get_plants_needing_fertilizer(plants)
    if due:
        body = "The following plants need fertilizing today:\n\n" + \
            "\n".join(due)
        send_email("Plants that need fertilizing today", body)
    else:
        send_email("No plants need fertilizing today", ":)")
    return jsonify({"needsFertilizer": due}), 200


@app.route('/plants', methods=['GET'])
def get_plants():
    plants = load_data()
    formatted = format_plants(plants)
    return f"<pre>{formatted}</pre>"  # Show it nicely in browser


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
