import argparse
import json
from pprint import pprint

def main():
    # add a command line argument so that you can specify which file you want to load
    # and also, make it give useful help if it's invoked without an argument
    parser = argparse.ArgumentParser(description='Read the output of the living_wage_spider')
    parser.add_argument('file', help='which file to read')
    args = parser.parse_args()

    with open(args.file) as data_file:
        # load the entire json into a python structure
        # (it will be an array of dictionaries if coming from living_wage_spider)
        data = json.load(data_file)


    # pprint is useful, it will print the dictionary in a nicely formatted manner
    pprint(data[0])

    # Let's work with the data some
    # for example, let's divide up the metro and county data
    counties = []
    metros = []
    for entry in data:
        if 'counties' in entry['url']:
            counties.append(entry)
        elif 'metros' in entry['url']:
            metros.append(entry)
    print('There are {} counties'.format(len(counties)))
    print('There are {} metros'.format(len(metros)))

    # now lets count counties by state
    state_counties = {}
    for entry in counties:
        # grab the fips code from the URL by first splitting the url on the '/' character, then taking the last entry
        # for instance http://livingwage.mit.edu/counties/17065 
        # we will get 17065
        fips = entry['url'].split('/')[-1]
        # the state code is the first two characters of that fips code
        state_code = fips[0:2]
        # make sure the dictionary has an empty array for this state if we haven't already set it
        if state_code not in state_counties:
            state_counties[state_code] = []
        # add this entry to that state
        state_counties[state_code].append(entry)

    # use a dictionary comprehension to make a new dictionary with all the same keys, but instead of the array of all the county
    # data for a value, use the length of that array
    state_counties_length = {k: len(v) for k, v in state_counties.items()}
    pprint(state_counties_length)
    # pprint(state_counties, depth=1)

if __name__ == '__main__':
    main()
