import copy
import json
import math
import os
import shutil
import csv


def assert_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def assert_not_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def dict_mutate(dictionary, key, mutation):
    dictionary[key] = mutation(dictionary[key])


def main():
    dir_pack = '../src/main/resources'
    dir_layers = dir_pack + '/data/origins/origin_layers/'
    dir_origins = dir_pack + '/data/tinkerer/origins/'
    dir_powers = dir_pack + '/data/tinkerer/powers/'
    assert_not_dir(dir_layers)
    assert_not_dir(dir_powers)
    assert_not_dir(dir_origins)
    shutil.copytree('override', dir_pack, dirs_exist_ok=True)
    assert_dir(dir_layers)
    assert_dir(dir_origins)
    assert_dir(dir_powers)

    with open("template/layer.json", "r") as layer_template_file:
        layer_template_json = json.load(layer_template_file)
    with open("template/origin.json", "r") as origin_template_file:
        origin_template_json = json.load(origin_template_file)
    with open("template/power.json", "r") as power_template_file:
        power_template_json = json.load(power_template_file)
    with open("data/presets.csv", "r") as preset_data_file:
        order = 0
        old_height = 0

        for preset in [{k: v for k, v in row.items()} for row in csv.DictReader(preset_data_file, skipinitialspace=True)]:
            origin_template = copy.deepcopy(origin_template_json)
            power_template = copy.deepcopy(power_template_json)

            order = (round(order, -2) + 100) if old_height != float(preset["height"]) else order + 10
            old_height = float(preset["height"])

            block_height = math.ceil(float(preset["height"]) * 1.8 * 10) / 10
            block_sneak_height = math.ceil(float(preset["height"]) * 1.5 * 10) / 10
            block_width = math.ceil(float(preset["width"]) * 0.6 * 10) / 10

            layer_template_json["origins"][0]["origins"].insert(-1, "tinkerer:{}".format(preset['id']))

            origin_template["powers"][0] = origin_template["powers"][0].format(preset['id'])
            origin_template["icon"] = origin_template["icon"].format(preset["icon"])
            origin_template["name"] = origin_template["name"].format(preset["name"])
            origin_template["description"] = origin_template["description"].format(preset["description"]).replace("Â§", "§")
            origin_template["impact"] = 3 if block_width > 1 else 2 if block_sneak_height > 2 else 1 if block_height > 2 or block_sneak_height <= 1 else 0
            origin_template["order"] = order

            power_template["name"] = power_template["name"].format(preset["name"])
            power_template["description"] = power_template["description"].format(
                preset["adjective"],
                math.floor(float(preset["height"]) * 100),
                block_height,
                "" if block_height == 1 else "s",
                block_sneak_height,
                "" if block_sneak_height == 1 else "s",
                block_width,
                " Exactly" if block_width == 1 else "s"
            )
            dict_mutate(power_template["entity_action_chosen"]["actions"][0], "command", (lambda s: s.format(preset["height"])))
            dict_mutate(power_template["entity_action_chosen"]["actions"][1], "command", (lambda s: s.format(preset["width"])))

            with open(dir_origins + preset["id"] + ".json", "w") as out_file:
                json.dump(origin_template, out_file, indent='\t')
            with open(dir_powers + preset["id"] + ".json", "w") as out_file:
                json.dump(power_template, out_file, indent='\t')
        with open(dir_layers + "stature" + ".json", "w") as out_file:
            json.dump(layer_template_json, out_file, indent='\t')


if __name__ == "__main__":
    main()
