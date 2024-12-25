# Write your code here
import json
import re
from typing import Optional

data_types = {
    "bus_id": [int, True, None],
    "stop_id": [int, True, None],
    "stop_name": [str, True, r"^[A-Z][a-z]*(?: [A-Z][a-z]*)*(?: (Road|Avenue|Boulevard|Street))$"],
    "next_stop": [int, True, None],
    "stop_type": [str, False, r"^(S|O|F)?$"],
    "a_time": [str, True, r"^(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"]
}


def get_stops_classif_key(stop_type):
    if stop_type == "S":
        route_key = "Start stops"
    elif stop_type == "F":
        route_key = "Finish stops"
    else:
        route_key = "On demand stops"
    return route_key


def get_transfer_stops(routes):
    stop_count = {}
    # Iterate over each route and its stops
    for route_data in routes.values():
        for stop in route_data['stops']:
            if stop in stop_count:
                stop_count[stop] += 1  # Increment the count if the stop already exists
            else:
                stop_count[stop] = 1  # Otherwise, set the count to 1

    # Find stops that exist in more than one route
    transfer_stops = {stop for stop, count in stop_count.items() if count > 1}
    return transfer_stops


def convert_time_to_minute(a_time: str) -> int:
    return int(a_time.split(":")[0]) * 60 + int(a_time.split(":")[1])


def check_data(input_str: Optional[str] = None):
    buses = json.loads(input_str)
    errors = {}
    routes = {}
    stops_classif = {
        "Start stops": set(),
        "Transfer stops": set(),
        "Finish stops": set(),
        "On demand stops": set()
    }
    for key in data_types.keys():
        errors[key] = 0

    for bus in buses:
        is_correct_stop_name = True
        is_correct_time = True

        if bus["bus_id"] not in routes.keys():
            routes[bus["bus_id"]] = {'have_start': False,
                                     'have_stop': False,
                                     'number_of_stops': 0,
                                     'stops': set(),
                                     'prev_stop_minute': 0}
        for key, value in bus.items():
            if key == "stop_type":
                stop_type = value
                if value == 'S':
                    routes[bus["bus_id"]]['have_start'] = True
                if value == 'F':
                    routes[bus["bus_id"]]['have_stop'] = True
            if key == "stop_name":
                stop_name = value
            if type(value) == data_types[key][0]:
                if type(value) == str and len(value) == 0 and data_types[key][1]:
                    errors[key] += 1
                if type(value) == str and not (re.match(data_types[key][2], value) if data_types[key][2] else True):
                    errors[key] += 1
                    if key == "stop_name":
                        is_correct_stop_name = False
                    if key == "a_time":
                        is_correct_stop_name = False
            else:
                errors[key] += 1
            if key == "a_time" and is_correct_stop_name and routes[bus["bus_id"]]["prev_stop_minute"] != -1:
                if convert_time_to_minute(value) > routes[bus["bus_id"]]["prev_stop_minute"]:
                    routes[bus["bus_id"]]["prev_stop_minute"] = convert_time_to_minute(value)
                else:
                    errors[key] += 1
                    routes[bus["bus_id"]]["prev_stop_minute"] = -1

        routes[bus["bus_id"]]["number_of_stops"] = routes[bus["bus_id"]]["number_of_stops"] + 1 \
            if "number_of_stops" in routes[bus["bus_id"]].keys() \
            else 1
        if is_correct_stop_name:
            stops_classif[get_stops_classif_key(stop_type)].add(stop_name)
            routes[bus["bus_id"]]['stops'].add(stop_name)

    print(f"Type and field validation: {sum(errors.values())} errors")
    print("\n".join(f"{key}: {value}" for key, value in errors.items()))
    print("\nLine names and number of stops:")
    is_break = False
    for key, value in routes.items():
        print(f"bus_id: {key} stops: {value['number_of_stops']}")
        if not (value['have_start'] and value['have_stop']):
            is_break = True
            print(f"There is no start or end stop for the line: {key}")
    if not is_break:
        stops_classif["Transfer stops"] = get_transfer_stops(routes)
        stops_classif["On demand stops"] = stops_classif["On demand stops"] - stops_classif["Transfer stops"]

        print("")
        print("\n".join(f"{key}: {len(value)} {sorted(value)}" for key, value in stops_classif.items()))


if __name__ == '__main__':
    input_str = input("Print input: ")
    check_data(input_str)
