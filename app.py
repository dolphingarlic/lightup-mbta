"""
Proxy for light-up MBTA map project.
"""

import os

import asyncio
import aiohttp
from flask import Flask

loop = asyncio.get_event_loop()
app = Flask(__name__)


RED_LINE = [
    'Alewife',
    'Davis',
    'Porter',
    'Harvard',
    'Central',
    'Kendall/MIT',
    'Charles/MGH',
    'Park Street',
    'Downtown Crossing',
    'South Station',
    'Broadway',
    'Andrew',
    'JFK/UMass',
    # Left branch
    'Savin Hill',
    'Fields Corner',
    'Shawmut',
    'Ashmont',
    'Cedar Grove',
    'Butler',
    'Milton',
    'Central Avenue',
    'Valley Road',
    'Capen Street',
    'Mattapan',
    # Right branch
    'North Quincy',
    'Wollaston',
    'Quincy Center',
    'Quincy Adams',
    'Braintree',
]

ORANGE_LINE = [
    'Oak Grove',
    'Malden Center',
    'Wellington',
    'Assembly',
    'Sullivan Square',
    'Community College',
    'North Station',
    'Haymarket',
    'State',
    # 'Downtown Crossing',
    'Chinatown',
    'Tufts Medical Center',
    'Back Bay',
    'Massachusetts Avenue',
    'Ruggles',
    'Roxbury Crossing',
    'Jackson Square',
    'Stony Brook',
    'Green Street',
    'Forest Hills',
]

GREEN_LINE = [
    'Medford/Tufts',
    'Ball Square',
    'Magoun Square',
    'Gilman Square',
    'East Somerville',
    'Union Square',
    'Lechmere',
    'Science Park/West End',
    'North Station',
    'Haymarket',
    'Government Center',
    # 'Park Street',
    'Boylston',
    'Arlington',
    'Copley',
    # Branch E
    'Prudential',
    'Symphony',
    'Northeastern University',
    'Museum of Fine Arts',
    'Longwood Medical Area',
    'Brigham Circle',
    'Fenwood Road',
    'Mission Park',
    'Riverway',
    'Back of the Hill',
    'Heath Street',
    # Branch D
    'Hynes Convention Center',
    'Kenmore',
    'Fenway',
    'Longwood',
    'Brookline Village',
    'Brookline Hills',
    'Beaconsfield',
    'Reservoir',
    'Chestnut Hill',
    'Newton Centre',
    'Newton Highlands',
    'Eliot',
    'Waban',
    'Woodland',
    'Riverside',
    # Branch C
    'Saint Mary\'s Street',
    'Hawes Street',
    'Kent Street',
    'Saint Paul Street',
    'Coolidge Corner',
    'Summit Avenue',
    'Brandon Hall',
    'Fairbanks Street',
    'Washington Square',
    'Tappan Street',
    'Dean Road',
    'Englewood Avenue',
    'Cleveland Circle',
    # Branch B
    'Blandford Street',
    'Boston University East',
    'Boston University Central',
    'Amory Street',
    'Babcock Street',
    'Packard\'s Corner',
    'Harvard Avenue',
    'Griggs Street',
    'Allston Street',
    'Warren Street',
    'Washington Street',
    'Sutherland Road',
    'Chiswick Road',
    'Chestnut Hill Avenue',
    'South Street',
    'Boston College',
]

BLUE_LINE = [
    'Wonderland',
    'Revere Beach',
    'Beachmont',
    'Suffolk Downs',
    'Orient Heights',
    'Wood Island',
    'Airport',
    'Maverick',
    'Aquarium',
    # 'State',
    # 'Government Center',
    'Bowdoin',
]

SILVER_LINE = [
    'Chelsea',
    'Bellingham Square',
    'Box District',
    'Eastern Avenue',
    # 'Airport',
    'Terminal A',
    'Terminal B Stop 1 - Arrivals Level',
    'Terminal B Stop 2 - Departures Level',
    'Terminal C - Arrivals Level',
    'Terminal E - Arrivals Level',
    'Silver Line Way',
    'Harbor Street',
    'Tide Street',
    # TODO: The Design Center stops
    'World Trade Center',
    'Courthouse',
    # 'South Station',
    # 'Chinatown',
    # 'Downtown Crossing',
    # 'Boylston',
    # 'Tufts Medical Center',
    'Herald Street',
    'East Berkeley Street',
    'Union Park Street',
    'Newton Street',
    'Worcester Square',
    'Massachusetts Avenue',
    'Lenox Street',
    'Melnea Cass Boulevard',
    'Nubian',
]

ALL_STOPS = [
    *RED_LINE,
    *ORANGE_LINE,
    *GREEN_LINE,
    *BLUE_LINE,
    *SILVER_LINE,
]


STATUSES = {
    'STOPPED_AT': 0,
    'IN_TRANSIT_TO': 1,
    'INCOMING_AT': 2
}


@app.route('/')
async def get_trains():
    async with aiohttp.ClientSession() as session:
        headers = {'accept': 'application/vnd.api+json', 'x-api-key': os.environ['API_KEY']}
        async with session.get(('https://api-v3.mbta.com/vehicles?'
                                'fields%5Bvehicle%5D=current_status&include=stop'
                                '&filter%5Broute%5D=Red%2CMattapan%2COrange%2C'
                                'Green-B%2CGreen-C%2CGreen-D%2CGreen-E%2CBlue%2'
                                'C741%2C742%2C743%2C751'),
                               headers=headers, ssl=False) as response:
            json = await response.json()

            trains = [t['relationships']['stop']['data']['id'] for t in json['data'] if t['relationships']
                      ['stop']['data'] != None and STATUSES[t['attributes']['current_status']] != 1]
            stops = {s['id']: s['attributes']['name']
                     for s in json['included']}
            # Lit-up stops are the ones with a train incoming or stopped there
            lit_stops = frozenset(stops[train] for train in trains)
            for i in lit_stops:
                if i not in ALL_STOPS:
                    print(i)

            return f"^{''.join('1' if stop in lit_stops else '0' for stop in ALL_STOPS)}$"
