import csv
import json

input_file = 'covid19_india_04_apr_2020.csv'
json_file = 'covid19_india_04_apr_20202.json'


def remove_nulls_from_dict(d):
    """ Remove NULL elements/keys in dictionary """
    # return {k: v for k, v in d.items() if v is not None}
    unwanted = ['', u'', None, False, [], 'SPAM']
    # return new_d = { k: v for k, v in d.items() if not any([v is i for i in unwanted]) }
    return dict((k, v) for k, v in d.items() if v)


def read_CSV(input_file, json_file):
    """ Read CSV File """
    csv_rows = []
    with open(input_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        field = reader.fieldnames
        for row in reader:
            # key is forced to lowercase
            # replace " " in key with "_" underscore
            # Add entries only if key is present ( no nulls )
            csv_rows.extend([
                {field[i].lower().replace(" ", "_"):row[field[i]]
                 for i in range(len(field)) if field[i]}
            ])

        convert_write_json(csv_rows, json_file)


def convert_write_json(data, json_file):
    """ Convert csv data into json """
    with open(json_file, "w", encoding="utf-8-sig") as f:
        f.write(json.dumps(data, sort_keys=False, indent=4,
                           separators=(',', ': ')))  # for pretty
        # f.write(json.dumps(data))


read_CSV(input_file, json_file)
