import yaml
import csv


def load_yaml(file_path):
    with open(file_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def load_csv(file_path):
    with open(file_path, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        return list(csv_reader)
