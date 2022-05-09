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
    # Branch E
    'Heath Street',
    'Back of the Hill',
    'Riverway',
    'Mission Park',
    'Fenwood Road',
    'Brigham Circle',
    'Longwood Medical Area',
    'Museum of Fine Arts',
    'Northeastern University',
    'Symphony',
    'Prudential',
    # Branch D
    'Riverside',
    'Woodland',
    'Waban',
    'Eliot',
    'Newton Highlands',
    'Newton Centre',
    'Chestnut Hill',
    'Reservoir',
    'Beaconsfield',
    'Brookline Hills',
    'Brookline Village',
    'Longwood',
    'Fenway',
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
    'Boston College',
    'South Street',
    'Chestnut Hill Avenue',
    'Chiswick Road',
    'Sutherland Road',
    'Washington Street',
    'Warren Street',
    'Allston Street',
    'Griggs Street',
    'Harvard Avenue',
    'Packard\'s Corner',
    'Babcock Street',
    'Amory Street',
    'Boston University Central',
    'Boston University East',
    'Blandford Street',
    # Non-branch
    'Kenmore',
    'Hynes Convention Center',
    'Copley',
    'Arlington',
    'Boylston',
    'Government Center',
    'Haymarket',
    'North Station',
    'Science Park/West End',
    'Lechmere',
    'Union Square',
    'East Somerville',
    'Gilman Square',
    'Magoun Square',
    'Ball Square',
    'Medford/Tufts',
]

BLUE_LINE = [
    'Wonderland',
    'Revere Beach',
    'Beachmont',
    'Suffolk Downs',
    'Orient Heights',
    'Wood Island',
    'Maverick',
    'Aquarium',
]

SILVER_LINE = [
    'Nubian',
    'Melnea Cass Boulevard',
    'Lenox Street',
    'Massachusetts Avenue',
    'Worcester Square',
    'Newton Street',
    'Union Park Street',
    'East Berkeley Street',
    'Herald Street',
    'Tufts Medical Center',
    'Boylston',
    'Chinatown',
    'South Station',
    'Courthouse',
    'World Trade Center',
    'Silver Line Way',
    'Harbor Street',
    'Tide Street',
    'Design Center',
    'Design Center',
    'Design Center',
    'Design Center',
    'Terminal A',
    'Terminal B Stop 1 - Arrivals Level',
    'Terminal B Stop 2 - Arrivals Level',
    'Terminal C - Arrivals Level',
    'Terminal E - Arrivals Level',
    'Airport',
    'Eastern Avenue',
    'Box District',
    'Bellingham Square',
    'Chelsea',
]

ALL_STOPS = RED_LINE + SILVER_LINE + ORANGE_LINE + GREEN_LINE + BLUE_LINE

STATUSES = {
    'STOPPED_AT': 0,
    'IN_TRANSIT_TO': 1,
    'INCOMING_AT': 2
}


@app.route('/')
async def get_trains():
    async with aiohttp.ClientSession() as session:
        headers = {'accept': 'application/vnd.api+json',
                   'x-api-key': os.environ['API_KEY']}
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
