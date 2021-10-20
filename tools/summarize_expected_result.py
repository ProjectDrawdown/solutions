"""" Compact report on test failures for solutions """
import re
import sys
import argparse
from pathlib import Path

def share_prefixes(error_list):
    # Remove the common sheet name out of the error messages, returning a single, combined string.
    # Note that for key results, they'll just all end up sharing the empty prefix
    groupby = {}
    for e in error_list:
        parts = e.split(" ")
        errno = parts[-1]
        prefix = " ".join(parts[:-1])
        if prefix not in groupby:
            groupby[prefix] = []
        groupby[prefix].append(errno)
    return ";".join( prefix + " " + ",".join( groupby[prefix]) for prefix in groupby.keys())

# this works because we put some structure in the output for the main solution tests

def summarize_results(input, verbose=False, module=None):
    textlines = input.read().splitlines()
    
    solname_test = None
    scenario_name = None
    error_accum = {}

    for line in textlines:
        if not line.startswith("E   "):
            # if we've just exited an error output block, print solution results
            if solname_test:  # print results and reset
                if module and module in solname_test:
                    if verbose:
                        print(solname_test + "\n    " + "\n    ".join( [scenario + ":" + share_prefixes(error_accum[scenario]) for scenario in error_accum.keys()] ))
                    else:
                        # dedup error list over all scenarios
                        allerrs = set()
                        allerrs.update( *error_accum.values() )
                        allers = list(allerrs)
                        cnt = len(allers)
                        if cnt > 8:
                            allers = allers[:8] + ["..."]
                        print(f"{solname_test}:\t{len(error_accum)}S/{cnt}E " + share_prefixes(allerrs))
                # reset
                solname_test = scenario_name = None
                error_accum = {}
        else: # line starts with "E   " indicating an error output line, which we want to check
            # we're going to trust our patterns are unique, and not worry they are in the right order or whatever
            if line.startswith("E   Solution"):
                solname_test = line.replace("E   Solution ","").replace(" results","")
                error_accum = {}
            elif line.startswith("E   scenario"):
                start = len("E   scenario")
                scenario_name = line[start+1:line.find(':')]
                error_accum[scenario_name] = []
            elif line.startswith("E   |"):  # testname is between two |'s
                end = line.find("|",6)
                testname = line[5:end]
                error_accum[scenario_name].append(testname)
                    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Summarize expected result tests from test output file.')
    parser.add_argument('testfile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-v', '--verbose', action='store_true', help='List tests as well as counts')
    parser.add_argument('-m', '--module', default=None, help="Restrict output to matching module")
    args = parser.parse_args()

    summarize_results(args.testfile, args.verbose, args.module)