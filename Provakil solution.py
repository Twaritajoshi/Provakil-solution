import argparse
import json
import re
import sys


def search_json_lines(lines, pattern, search_keys, search_values, ignore_invalid_json, case_insensitive, count_only, invert_match):
    """
    Search for the given pattern in each line of a list of JSON-encoded strings.
    Returns a list of matched lines or the count of matched lines, depending on the value of count_only.
    """
    matches = []
    count = 0
    for i, line in enumerate(lines):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            if ignore_invalid_json:
                continue
            else:
                print(f"Invalid JSON on line number {i+1}", file=sys.stderr)
                sys.exit(1)
        if search_keys:
            keys = [str(key) for key in data.keys()]
            matches.extend([line] if pattern_match(keys, pattern, case_insensitive) else [])
        elif search_values:
            values = [str(value) for value in data.values()]
            matches.extend([line] if pattern_match(values, pattern, case_insensitive) else [])
        else:
            json_string = json.dumps(data)
            matches.extend([line] if pattern_match(json_string, pattern, case_insensitive) else [])
        if invert_match:
            matches = []
        else:
            count += len(matches)
    if count_only:
        return count
    else:
        return matches


def pattern_match(strings, pattern, case_insensitive):
    """
    Check if any of the given strings match the given pattern.
    Returns True if there is a match, False otherwise.
    """
    flags = re.IGNORECASE if case_insensitive else 0
    for string in strings:
        if re.search(pattern, string, flags):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description='JSON grep')
    parser.add_argument('pattern', type=str, help='Pattern to search for')
    parser.add_argument('file', type=str, help='JSON log file to search')
    parser.add_argument('-k', '--keys', action='store_true', help='Search only in keys of the JSON object')
    parser.add_argument('-v', '--values', action='store_true', help='Search only in values of the JSON object')
    parser.add_argument('-x', '--ignore-invalid-json', action='store_true', help='Ignore lines containing invalid JSON')
    parser.add_argument('-i', '--case-insensitive', action='store_true', help='Perform case-insensitive search')
    parser.add_argument('-c', '--count-only', action='store_true', help='Show only the total number of lines matched')
    parser.add_argument('-d', '--invert-match', action='store_true', help='Print only the lines which do not match the pattern')
    args = parser.parse_args()

    with open(args.file) as f:
        lines = f.readlines()

    matches = search_json_lines(lines, args.pattern, args.keys, args.values, args.ignore_invalid_json, args.case_insensitive, args.count_only, args.invert_match)

    if args.count_only:
        print(f"Total number of lines matched: {matches}")
    else:
        for match in matches:
            print(match, end='')

if __name__ == '__main__':
    main()