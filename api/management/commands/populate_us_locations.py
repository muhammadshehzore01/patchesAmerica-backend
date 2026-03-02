from django.core.management.base import BaseCommand
from api.models import Country, State, City

US_STATES = [
    # (state_code, state_name, population, top_10_cities)
    ("AL", "Alabama", 5024279, ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa", "Hoover", "Dothan", "Auburn", "Decatur", "Madison"]),
    ("AK", "Alaska", 733391, ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan", "Wasilla", "Kenai", "Kodiak", "Bethel", "Palmer"]),
    ("AZ", "Arizona", 7276316, ["Phoenix", "Tucson", "Mesa", "Chandler", "Glendale", "Scottsdale", "Gilbert", "Tempe", "Peoria", "Surprise"]),
    ("AR", "Arkansas", 3011524, ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro", "North Little Rock", "Conway", "Rogers", "Pine Bluff", "Bentonville"]),
    ("CA", "California", 39538223, ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento", "Long Beach", "Oakland", "Bakersfield", "Anaheim"]),
    ("CO", "Colorado", 5773714, ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood", "Thornton", "Arvada", "Westminster", "Pueblo", "Centennial"]),
    ("CT", "Connecticut", 3605944, ["Bridgeport", "New Haven", "Stamford", "Hartford", "Waterbury", "Norwalk", "Danbury", "New Britain", "West Hartford", "Milford"]),
    ("DE", "Delaware", 989948, ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna", "Milford", "Seaford", "Georgetown", "Elsmere", "Dover AFB"]),
    ("FL", "Florida", 21538187, ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah", "Tallahassee", "Port St. Lucie", "Fort Lauderdale", "Cape Coral"]),
    ("GA", "Georgia", 10711908, ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens", "Sandy Springs", "Roswell", "Johns Creek", "Albany"]),
    ("HI", "Hawaii", 1455271, ["Honolulu", "Hilo", "Kailua", "Kapolei", "Kaneohe", "Waipahu", "Mililani", "Ewa Beach", "Pearl City", "Kihei"]),
    ("ID", "Idaho", 1839106, ["Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello", "Caldwell", "Coeur d'Alene", "Twin Falls", "Lewiston", "Rexburg"]),
    ("IL", "Illinois", 12812508, ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford", "Springfield", "Elgin", "Peoria", "Champaign", "Waukegan"]),
    ("IN", "Indiana", 6785528, ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel", "Fishers", "Bloomington", "Hammond", "Gary", "Muncie"]),
    ("IA", "Iowa", 3190369, ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City", "Council Bluffs", "Ames", "Waterloo", "West Des Moines", "Dubuque"]),
    ("KS", "Kansas", 2937880, ["Wichita", "Overland Park", "Kansas City", "Olathe", "Topeka", "Lawrence", "Shawnee", "Manhattan", "Lenexa", "Salina"]),
    ("KY", "Kentucky", 4505836, ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington", "Hopkinsville", "Richmond", "Florence", "Georgetown", "Elizabethtown"]),
    ("LA", "Louisiana", 4657757, ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles", "Kenner", "Bossier City", "Monroe", "Alexandria", "Houma"]),
    ("ME", "Maine", 1362359, ["Portland", "Lewiston", "Bangor", "South Portland", "Auburn", "Biddeford", "Sanford", "Saco", "Westbrook", "Augusta"]),
    ("MD", "Maryland", 6177224, ["Baltimore", "Columbia", "Germantown", "Silver Spring", "Waldorf", "Ellicott City", "Rockville", "Bethesda", "Frederick", "Gaithersburg"]),
    ("MA", "Massachusetts", 7029917, ["Boston", "Worcester", "Springfield", "Lowell", "Cambridge", "New Bedford", "Brockton", "Quincy", "Lynn", "Fall River"]),
    ("MI", "Michigan", 10077331, ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing", "Flint", "Dearborn", "Livonia", "Westland"]),
    ("MN", "Minnesota", 5706494, ["Minneapolis", "St. Paul", "Rochester", "Duluth", "Bloomington", "Brooklyn Park", "Plymouth", "St. Cloud", "Eagan", "Maple Grove"]),
    ("MS", "Mississippi", 2961279, ["Jackson", "Gulfport", "Southaven", "Hattiesburg", "Biloxi", "Meridian", "Tupelo", "Olive Branch", "Greenville", "Horn Lake"]),
    ("MO", "Missouri", 6154913, ["Kansas City", "St. Louis", "Springfield", "Independence", "Columbia", "Lee's Summit", "O'Fallon", "St. Joseph", "St. Charles", "St. Peters"]),
    ("MT", "Montana", 1084225, ["Billings", "Missoula", "Great Falls", "Bozeman", "Butte", "Helena", "Kalispell", "Anaconda", "Havre", "Belgrade"]),
    ("NE", "Nebraska", 1961504, ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney", "Fremont", "Hastings", "North Platte", "Norfolk", "Columbus"]),
    ("NV", "Nevada", 3104614, ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks", "Carson City", "Elko", "Fernley", "Mesquite", "Boulder City"]),
    ("NH", "New Hampshire", 1377529, ["Manchester", "Nashua", "Concord", "Dover", "Rochester", "Derry", "Dunbarton", "Keene", "Portsmouth", "Laconia"]),
    ("NJ", "New Jersey", 9288994, ["Newark", "Jersey City", "Paterson", "Elizabeth", "Edison", "Woodbridge", "Lakewood", "Toms River", "Hamilton", "Trenton"]),
    ("NM", "New Mexico", 2117522, ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell", "Farmington", "Clovis", "Hobbs", "Carlsbad", "Gallup"]),
    ("NY", "New York", 20201249, ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany", "New Rochelle", "Mount Vernon", "Schenectady", "Utica"]),
    ("NC", "North Carolina", 10439388, ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville", "Cary", "Wilmington", "High Point", "Asheville"]),
    ("ND", "North Dakota", 779094, ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo", "Williston", "Dickinson", "Mandan", "Jamestown", "Valley City"]),
    ("OH", "Ohio", 11799448, ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton", "Parma", "Canton", "Youngstown", "Lorain"]),
    ("OK", "Oklahoma", 3959353, ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond", "Lawton", "Moore", "Midwest City", "Enid", "Stillwater"]),
    ("OR", "Oregon", 4237256, ["Portland", "Salem", "Eugene", "Gresham", "Hillsboro", "Beaverton", "Bend", "Medford", "Springfield", "Corvallis"]),
    ("PA", "Pennsylvania", 13002700, ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton", "Bethlehem", "Lancaster", "Harrisburg", "York"]),
    ("RI", "Rhode Island", 1097379, ["Providence", "Warwick", "Cranston", "Pawtucket", "East Providence", "Woonsocket", "Coventry", "Cumberland", "Cranston Heights", "North Providence"]),
    ("SC", "South Carolina", 5118425, ["Charleston", "Columbia", "North Charleston", "Mount Pleasant", "Rock Hill", "Greenville", "Summerville", "Sumter", "Hilton Head Island", "Spartanburg"]),
    ("SD", "South Dakota", 886667, ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown", "Mitchell", "Pierre", "Huron", "Yankton", "Vermillion"]),
    ("TN", "Tennessee", 6910840, ["Memphis", "Nashville", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro", "Franklin", "Jackson", "Johnson City", "Bartlett"]),
    ("TX", "Texas", 29145505, ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo"]),
    ("UT", "Utah", 3271616, ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem", "Sandy", "Ogden", "St. George", "Layton", "Taylorsville"]),
    ("VT", "Vermont", 643077, ["Burlington", "South Burlington", "Rutland", "Barre", "Montpelier", "St. Albans", "Winooski", "St. Johnsbury", "Middlebury", "Essex Junction"]),
    ("VA", "Virginia", 8631393, ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News", "Alexandria", "Hampton", "Roanoke", "Portsmouth", "Suffolk"]),
    ("WA", "Washington", 7693612, ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent", "Everett", "Renton", "Yakima", "Kirkland"]),
    ("WV", "West Virginia", 1793716, ["Charleston", "Huntington", "Morgantown", "Parkersburg", "Wheeling", "Weirton", "Martinsburg", "Fairmont", "Beckley", "Clarksburg"]),
    ("WI", "Wisconsin", 5893718, ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine", "Appleton", "Waukesha", "Eau Claire", "Janesville", "La Crosse"]),
    ("WY", "Wyoming", 576851, ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs", "Sheridan", "Green River", "Evanston", "Riverton", "Jackson"]),
    ("DC", "District of Columbia", 689545, ["Washington"]),
]

class Command(BaseCommand):
    help = "Populate USA country, states, and cities"

    def handle(self, *args, **options):
        country, created = Country.objects.update_or_create(
            code="US", defaults={"name": "United States", "is_default": True}
        )
        self.stdout.write(self.style.SUCCESS(f"Country created: {country.name}"))

        for code, name, population, cities in US_STATES:
            state, s_created = State.objects.update_or_create(
                country=country,
                code=code,
                defaults={"name": name, "population": population},
            )
            self.stdout.write(self.style.SUCCESS(f"State created: {state.name}"))

            for city_name in cities:
                city, c_created = City.objects.update_or_create(
                    state=state,
                    name=city_name,
                    defaults={"population": 0},
                )
                self.stdout.write(
                    self.style.SUCCESS(f"   City created: {city.name} ({state.code})")
                )

        self.stdout.write(self.style.SUCCESS("All states and cities populated successfully!"))
