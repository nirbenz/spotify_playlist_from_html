import yaml


def read_yaml(yaml_path):
    with open(yaml_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise RuntimeError("YAML error")
    return config


def remove_duplicates_keep_order(lst):
    lst_no_dup = []
    [lst_no_dup.append(t) for t in lst if t not in lst_no_dup]
    return lst_no_dup


def track_ids_from_infos(track_infos):
    return [u['id'] for u in track_infos]