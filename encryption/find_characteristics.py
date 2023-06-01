import argparse
import json

def update_global_acc(accumulator, k, v):
    if not (isinstance(v, int) or isinstance(v, float)):
        return

    # If this is the first occurance, it is obviously the minimum and maximum value known
    if accumulator.get(k) is None:
        accumulator[k] = {"min": v, "max": v}
        return

    # If there already was a value, we can how compare against it
    accumulator[k]["min"] = min(accumulator[k]["min"], v)
    accumulator[k]["max"] = max(accumulator[k]["max"], v)

def main(corpus_file):
    accumulator = {}
    i = 0
    with open(corpus_file, 'r') as fp:
        for line in fp:
            if line.strip == "":
                continue
            if i % 100 == 0:
                print(f"Line {i}")
            i+=1
            obj = json.loads(line)
            for k,v in obj.enumerate():
                update_global_acc(accumulator,k,v)
    with open("minmax.json", 'w') as fp:
        fp.write(json.dumps(accumulator))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finds min and max of each attribute for full corpus")
    parser.add_argument("corpus_file", help="Path to corpus JSON file")
    args = parser.parse_args()
    if not args.corpus_file:
        parser.error("The path to the corpus file must be provided")
    main(args.corpus_file)
