from yt_dlp.extractor.common import variadic
import json

with open('tmp.json') as f:
    jsondata = json.load(f)


def traverse(data, condition, path=()):
    paths = []
    iterator = None
    if isinstance(data, list):
        iterator = enumerate(data)
    if isinstance(data, dict):
        iterator = data.items()
    if iterator is None:
        try:
            if condition(data):
                return (*path, data)
            return None
        except Exception:
            return None
    for k, v in iterator:
        paths.extend(variadic(traverse(v, condition, (*path, k))))
    return list(filter(lambda x: x is not None, paths))


query = 2015
for i in traverse(jsondata, lambda x: query in x):
    prefix, _, suffix = i[-1].partition(query)
    line = f'or traverse_obj(data, {i[:-1]})'
    if prefix:
        line += f'.removeprefix(\'{prefix}\')'
    if suffix:
        line += f'.removesuffix(\'{suffix}\')'
    line += '\\'
    print(line)
