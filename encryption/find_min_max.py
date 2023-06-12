import argparse
import json

def file_len(filename):
    i = 0
    with open(filename, 'r') as fp:
        for _ in fp:
            i+=1
    return i

def _min(old, new):
    if not isinstance(new, list):
        return min(old, new)
    if len(old) != len(new):
        raise Exception("Len unequal! This should never happen")

    min_arr = []
    for i in range(len(new)):
        min_arr.append(min(old[i], new[i]))
    return min_arr

def update_acc(acc, k, v):
    if isinstance(v, str):
        return acc
    if acc.get(k) is None:
        acc[k] = v
        return acc
    acc[k] = _min(acc[k], v)
    return acc

def main(corpus_file):
    acc = {}
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
                acc = update_acc(acc,k,v)
    with open("minmax.json", 'w') as fp:
        fp.write(json.dumps(acc))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finds min and max of each attribute for full corpus")
    parser.add_argument("corpus_file", help="Path to corpus JSON file")
    args = parser.parse_args()
    if not args.corpus_file:
        parser.error("The path to the corpus file must be provided")
    main(args.corpus_file)
