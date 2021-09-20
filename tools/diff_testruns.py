"""Compare two test runs and report the deltas"""
from sys import argv
from collections import OrderedDict

def build_dict(lines):
    result = OrderedDict()
    for line in lines:
        if "FAILURES" in line:
            return result
        if ("%" not in line) or ("test" not in line):  # skip non-result and continuation lines
            continue
        (name, dots, _) = line.split(" ",2)
        # simplify name down to the class part
        upto = name.index("test_") + len("test_")
        result[name[upto:]] = dots

def got_worse(d1, d2):
    result = []
    for k in d2.keys():
        if k in d1.keys():
            dots1 = d1[k]
            dots2 = d2[k]
            common = min(len(dots1), len(dots2))
            for i in range(common):
                if dots2[i] == 'F' and dots1[i] != 'F':
                    result.append(k)
                    break
    return result


def build_diff(file1, file2):
    with open(file1) as f:
        lines1 = f.read().splitlines()
    with open(file2) as f:
        lines2 = f.read().splitlines()

    # print out the headers of both
    for line in lines1:
        if len(line) == 0: break
        print(line)
    for line in lines2:
        if len(line) == 0: break
        print(line)
    print("================================================================================\n")
    
    d1 = build_dict(lines1)
    d2 = build_dict(lines2)

    worse = got_worse(d1, d2)
    if len(worse):
        print("\nGOT WORSE:\n")
        for name in worse:
            print(name + ": " + d1[name] + "/" + d2[name])

    # For others, print out the results only if they differ
    print("\nDIFFERENT:\n")
    for name in d1.keys():
        if name in worse: continue
        dots1 = d1[name] if name in d1 else ""
        dots2 = d2[name] if name in d2 else ""
        if dots1 != dots2:
            print(name + ": " + dots1 + " / " + dots2)

    addedkeys = []
    for k in list(d2.keys()):
        if k not in d1:
            addedkeys.append(k)
    
    if len(addedkeys):
        print("\nNEW ITEMS:\n")
        for name in addedkeys:
            print(name + " / " + d2[name])       


if __name__ == "__main__":
    build_diff(argv[1], argv[2])