import argparse
import json

def file_len(filename):
    i = 0
    with open(filename, 'r') as fp:
        for _ in fp:
            i+=1
    return i

def _cmp(fn, old, new):
    if not isinstance(new, list):
        return fn(old, new)
    if len(old) != len(new):
        raise Exception("Len unequal! This should never happen")

    res = []
    for i in range(len(new)):
        res.append(fn(old[i], new[i]))
    return res

def update_acc(fn, acc_min, k, v):
    if isinstance(v, str):
        return acc_min
    if acc_min.get(k) is None:
        acc_min[k] = v
        return acc_min
    acc_min[k] = _cmp(fn, acc_min[k], v)
    return acc_min

def main(corpus_file):
    acc_min = {}
    acc_max = {}
    i = 0
    n = file_len(corpus_file)
    with open(corpus_file, 'r') as fp:
        for line in fp:
            if line.strip == "":
                continue
            if i % 100 == 0:
                print(f"Line {i}/{n}")
            i+=1
            obj = json.loads(line)
            for k,v in obj.items():
                acc_min = update_acc(min, acc_min, k, v)
                acc_max = update_acc(max, acc_max, k, v)
    with open("minmax.json", 'w') as fp:
        fp.write(json.dumps(acc_min))
        fp.write(json.dumps(acc_max))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finds min and max of each attribute for full corpus")
    parser.add_argument("corpus_file", help="Path to corpus JSON file")
    args = parser.parse_args()
    if not args.corpus_file:
        parser.error("The path to the corpus file must be provided")
    main(args.corpus_file)
