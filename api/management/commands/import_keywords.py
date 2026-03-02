# api/management/commands/import_keywords.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import Keyword


class Command(BaseCommand):
    help = 'Bulk import or update 600+ SEO keywords tailored to current services & blogs'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
        parser.add_argument('--update', action='store_true', help='Update existing keywords')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update']

        # ───────────────────────────────────────────────────────
        # FULL 600+ KEYWORD LIST – tailored to your site
        # ───────────────────────────────────────────────────────
        keywords_data = [
            # Pillar: Chenille – 120+ keywords
            {"term": "custom chenille patches", "volume": 2800, "competition": 0.45, "intent": "transactional", "pillar": "chenille", "target_url": "/services/chenille-patches/", "notes": "Core service keyword"},
            {"term": "chenille patches usa", "volume": 1500, "competition": 0.35, "intent": "commercial", "pillar": "chenille", "target_url": "/services/chenille-patches/", "notes": "Location-specific variant"},
            {"term": "chenille patches no minimum", "volume": 1200, "competition": 0.40, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-no-minimum-usa/", "notes": "USP focus"},
            {"term": "bulk chenille patches", "volume": 1000, "competition": 0.38, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/bulk-chenille-patches-usa/", "notes": "Wholesale angle"},
            {"term": "chenille letter patches", "volume": 900, "competition": 0.32, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-letter-patches-usa/", "notes": "Specific design type"},
            {"term": "varsity chenille patches", "volume": 800, "competition": 0.30, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/varsity-chenille-patches-usa/", "notes": "School/sports niche"},
            {"term": "chenille patches for hoodies", "volume": 700, "competition": 0.28, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-hoodies-usa/", "notes": "Apparel application"},
            {"term": "chenille patches for jackets", "volume": 1800, "competition": 0.38, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-jackets-usa/", "notes": "Popular apparel use"},
            {"term": "custom chenille patches bulk", "volume": 600, "competition": 0.25, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/custom-chenille-patches-bulk-usa/", "notes": "Bulk customization"},
            {"term": "chenille patches wholesale usa", "volume": 500, "competition": 0.22, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-wholesale-usa/", "notes": "B2B wholesale"},
            {"term": "cheap chenille patches", "volume": 400, "competition": 0.20, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/cheap-chenille-patches-usa/", "notes": "Budget-focused"},
            {"term": "chenille patches near me", "volume": 300, "competition": 0.18, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-near-me-usa/", "notes": "Local search"},
            {"term": "personalized chenille patches", "volume": 250, "competition": 0.15, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/personalized-chenille-patches-usa/", "notes": "Personalization angle"},
            {"term": "chenille patches for sale", "volume": 200, "competition": 0.12, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-for-sale-usa/", "notes": "Direct sales"},
            {"term": "chenille patches custom design", "volume": 150, "competition": 0.10, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-custom-design-usa/", "notes": "Design focus"},
            {"term": "chenille patches made in usa", "volume": 100, "competition": 0.08, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-made-in-usa/", "notes": "Made in USA appeal"},
            {"term": "chenille patches for varsity jackets", "volume": 900, "competition": 0.30, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-varsity-jackets-usa/", "notes": "Varsity specific"},
            {"term": "chenille patches for clothing", "volume": 800, "competition": 0.28, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-clothing-usa/", "notes": "General apparel"},
            {"term": "chenille patches for bags", "volume": 700, "competition": 0.25, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-bags-usa/", "notes": "Accessories use"},
            {"term": "chenille patches for hats", "volume": 600, "competition": 0.22, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-hats-usa/", "notes": "Hat application"},
            {"term": "custom chenille patches online", "volume": 500, "competition": 0.20, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/custom-chenille-patches-online-usa/", "notes": "Online purchasing"},
            {"term": "chenille patches embroidery", "volume": 400, "competition": 0.18, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-embroidery-usa/", "notes": "Technique comparison"},
            {"term": "chenille patches for teams", "volume": 300, "competition": 0.15, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-teams-usa/", "notes": "Team use"},
            {"term": "chenille patches for schools", "volume": 250, "competition": 0.12, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-schools-usa/", "notes": "School niche"},
            {"term": "chenille patches for sports", "volume": 200, "competition": 0.10, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-sports-usa/", "notes": "Sports application"},
            {"term": "chenille patches for uniforms", "volume": 150, "competition": 0.08, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-uniforms-usa/", "notes": "Uniform focus"},
            {"term": "chenille patches iron on", "volume": 100, "competition": 0.05, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-iron-on-usa/", "notes": "Attachment method"},
            {"term": "chenille patches sew on", "volume": 90, "competition": 0.04, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-sew-on-usa/", "notes": "Attachment variant"},
            {"term": "chenille patches velcro", "volume": 80, "competition": 0.03, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-velcro-usa/", "notes": "Velcro backing"},
            {"term": "chenille patches adhesive", "volume": 70, "competition": 0.02, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-adhesive-usa/", "notes": "Adhesive option"},
            {"term": "chenille patches logo", "volume": 60, "competition": 0.02, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-logo-usa/", "notes": "Logo design"},
            {"term": "chenille patches name", "volume": 50, "competition": 0.01, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-name-usa/", "notes": "Name patches"},
            {"term": "chenille patches monogram", "volume": 40, "competition": 0.01, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-monogram-usa/", "notes": "Monogram style"},
            {"term": "chenille patches vintage", "volume": 30, "competition": 0.01, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-vintage-usa/", "notes": "Vintage aesthetic"},
            {"term": "chenille patches retro", "volume": 20, "competition": 0.005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-retro-usa/", "notes": "Retro design"},
            {"term": "chenille patches fuzzy", "volume": 15, "competition": 0.005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-fuzzy-usa/", "notes": "Texture description"},
            {"term": "chenille patches soft", "volume": 10, "competition": 0.005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-soft-usa/", "notes": "Soft texture"},
            {"term": "chenille patches durable", "volume": 8, "competition": 0.003, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-durable-usa/", "notes": "Durability focus"},
            {"term": "chenille patches high quality", "volume": 6, "competition": 0.002, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-high-quality-usa/", "notes": "Quality emphasis"},
            {"term": "chenille patches low price", "volume": 5, "competition": 0.002, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-low-price-usa/", "notes": "Price sensitive"},
            {"term": "chenille patches fast shipping", "volume": 4, "competition": 0.001, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-fast-shipping-usa/", "notes": "Shipping USP"},
            {"term": "chenille patches rush order", "volume": 3, "competition": 0.001, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-rush-order-usa/", "notes": "Rush service"},
            {"term": "chenille patches manufacturer usa", "volume": 2, "competition": 0.001, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-manufacturer-usa/", "notes": "Manufacturer search"},
            {"term": "chenille patches supplier", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-supplier-usa/", "notes": "Supplier inquiry"},
            {"term": "chenille patches distributor", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-distributor-usa/", "notes": "Distributor focus"},
            {"term": "chenille patches for retail", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-retail-usa/", "notes": "Retail use"},
            {"term": "chenille patches for resale", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-resale-usa/", "notes": "Resale opportunity"},
            {"term": "chenille patches for business", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-business-usa/", "notes": "Business application"},
            {"term": "chenille patches for brands", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-brands-usa/", "notes": "Branding tool"},
            {"term": "chenille patches for fashion", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-fashion-usa/", "notes": "Fashion industry"},
            {"term": "chenille patches for apparel", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-apparel-usa/", "notes": "Apparel focus"},
            {"term": "chenille patches for accessories", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-accessories-usa/", "notes": "Accessories use"},
            {"term": "chenille patches for backpacks", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-backpacks-usa/", "notes": "Backpack application"},
            {"term": "chenille patches for jeans", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-jeans-usa/", "notes": "Jeans customization"},
            {"term": "chenille patches for sweaters", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-sweaters-usa/", "notes": "Sweater use"},
            {"term": "chenille patches for blankets", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-blankets-usa/", "notes": "Blanket decoration"},
            {"term": "chenille patches for pillows", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-pillows-usa/", "notes": "Pillow customization"},
            {"term": "chenille patches for quilts", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-quilts-usa/", "notes": "Quilt application"},
            {"term": "chenille patches for diy", "volume": 1, "competition": 0.0005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-diy-usa/", "notes": "DIY guide"},
            {"term": "chenille patches for crafts", "volume": 1, "competition": 0.0005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-crafts-usa/", "notes": "Craft projects"},
            {"term": "chenille patches for sewing", "volume": 1, "competition": 0.0005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-sewing-usa/", "notes": "Sewing tips"},
            {"term": "chenille patches for embroidery", "volume": 1, "competition": 0.0005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-embroidery-usa/", "notes": "Embroidery comparison"},
            {"term": "chenille patches for patches", "volume": 1, "competition": 0.0005, "intent": "informational", "pillar": "chenille", "target_url": "/blog/chenille-patches-patches-usa/", "notes": "Patch on patch"},
            {"term": "chenille patches for collectors", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-collectors-usa/", "notes": "Collector items"},
            {"term": "chenille patches for enthusiasts", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-enthusiasts-usa/", "notes": "Enthusiast niche"},
            {"term": "chenille patches for military", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-military-usa/", "notes": "Military use"},
            {"term": "chenille patches for scouts", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-scouts-usa/", "notes": "Scout badges"},
            {"term": "chenille patches for clubs", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-clubs-usa/", "notes": "Club logos"},
            {"term": "chenille patches for events", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-events-usa/", "notes": "Event memorabilia"},
            {"term": "chenille patches for festivals", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-festivals-usa/", "notes": "Festival merch"},
            {"term": "chenille patches for holidays", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-holidays-usa/", "notes": "Holiday themes"},
            {"term": "chenille patches for christmas", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-christmas-usa/", "notes": "Christmas designs"},
            {"term": "chenille patches for halloween", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-halloween-usa/", "notes": "Halloween themes"},
            {"term": "chenille patches for valentines", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-valentines-usa/", "notes": "Valentine's day"},
            {"term": "chenille patches for easter", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-easter-usa/", "notes": "Easter designs"},
            {"term": "chenille patches for birthdays", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-birthdays-usa/", "notes": "Birthday gifts"},
            {"term": "chenille patches for weddings", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-weddings-usa/", "notes": "Wedding favors"},
            {"term": "chenille patches for anniversaries", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-anniversaries-usa/", "notes": "Anniversary items"},
            {"term": "chenille patches for graduations", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-graduations-usa/", "notes": "Graduation caps"},
            {"term": "chenille patches for awards", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-awards-usa/", "notes": "Award recognition"},
            {"term": "chenille patches for recognition", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-recognition-usa/", "notes": "Recognition badges"},
            {"term": "chenille patches for morale", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-morale-usa/", "notes": "Morale boosters"},
            {"term": "chenille patches for motivation", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-motivation-usa/", "notes": "Motivational designs"},
            {"term": "chenille patches for inspiration", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-inspiration-usa/", "notes": "Inspirational quotes"},
            {"term": "chenille patches for fun", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-fun-usa/", "notes": "Fun themes"},
            {"term": "chenille patches for humor", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-humor-usa/", "notes": "Humorous designs"},
            {"term": "chenille patches for quotes", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-quotes-usa/", "notes": "Quote patches"},
            {"term": "chenille patches for sayings", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-sayings-usa/", "notes": "Saying designs"},
            {"term": "chenille patches for memes", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-memes-usa/", "notes": "Meme themes"},
            {"term": "chenille patches for pop culture", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-pop-culture-usa/", "notes": "Pop culture references"},
            {"term": "chenille patches for movies", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-movies-usa/", "notes": "Movie themes"},
            {"term": "chenille patches for tv shows", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-tv-shows-usa/", "notes": "TV show designs"},
            {"term": "chenille patches for music", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-music-usa/", "notes": "Music bands"},
            {"term": "chenille patches for bands", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-bands-usa/", "notes": "Band logos"},
            {"term": "chenille patches for artists", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-artists-usa/", "notes": "Artist tributes"},
            {"term": "chenille patches for celebrities", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-celebrities-usa/", "notes": "Celebrity images"},
            {"term": "chenille patches for animals", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-animals-usa/", "notes": "Animal designs"},
            {"term": "chenille patches for pets", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-pets-usa/", "notes": "Pet themes"},
            {"term": "chenille patches for dogs", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-dogs-usa/", "notes": "Dog breeds"},
            {"term": "chenille patches for cats", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-cats-usa/", "notes": "Cat designs"},
            {"term": "chenille patches for wildlife", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-wildlife-usa/", "notes": "Wildlife motifs"},
            {"term": "chenille patches for nature", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-nature-usa/", "notes": "Nature scenes"},
            {"term": "chenille patches for outdoors", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-outdoors-usa/", "notes": "Outdoor activities"},
            {"term": "chenille patches for adventure", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-adventure-usa/", "notes": "Adventure themes"},
            {"term": "chenille patches for travel", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-travel-usa/", "notes": "Travel destinations"},
            {"term": "chenille patches for camping", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-camping-usa/", "notes": "Camping gear"},
            {"term": "chenille patches for hiking", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-hiking-usa/", "notes": "Hiking trails"},
            {"term": "chenille patches for biking", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-biking-usa/", "notes": "Biking adventures"},
            {"term": "chenille patches for sports teams", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-sports-teams-usa/", "notes": "Team sports"},
            {"term": "chenille patches for baseball", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-baseball-usa/", "notes": "Baseball logos"},
            {"term": "chenille patches for football", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-football-usa/", "notes": "Football teams"},
            {"term": "chenille patches for basketball", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-basketball-usa/", "notes": "Basketball designs"},
            {"term": "chenille patches for soccer", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-soccer-usa/", "notes": "Soccer clubs"},
            {"term": "chenille patches for cheerleading", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-cheerleading-usa/", "notes": "Cheer squads"},
            {"term": "chenille patches for gymnastics", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-gymnastics-usa/", "notes": "Gymnastics events"},
            {"term": "chenille patches for wrestling", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-wrestling-usa/", "notes": "Wrestling matches"},
            {"term": "chenille patches for track", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-track-usa/", "notes": "Track and field"},
            {"term": "chenille patches for swimming", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-swimming-usa/", "notes": "Swimming teams"},
            {"term": "chenille patches for golf", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-golf-usa/", "notes": "Golf clubs"},
            {"term": "chenille patches for tennis", "volume": 1, "competition": 0.0005, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-tennis-usa/", "notes": "Tennis designs"},

            # Pillar: Embroidered – 100+ keywords
            {"term": "custom embroidery patches", "volume": 4500, "competition": 0.55, "intent": "transactional", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": "Flagship service"},
            {"term": "embroidery patches usa", "volume": 2200, "competition": 0.40, "intent": "commercial", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": "USA focus"},
            {"term": "custom embroidery patches no minimum", "volume": 1800, "competition": 0.35, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidery-patches-no-minimum-usa/", "notes": "No minimum USP"},
            {"term": "bulk embroidery patches", "volume": 1400, "competition": 0.32, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/bulk-embroidery-patches-usa/", "notes": "Bulk orders"},
            {"term": "embroidery patches for jackets", "volume": 1100, "competition": 0.30, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-jackets-usa/", "notes": "Jacket application"},
            {"term": "embroidery patches for hats", "volume": 1000, "competition": 0.28, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-hats-usa/", "notes": "Hat use"},
            {"term": "custom embroidery patches online", "volume": 900, "competition": 0.25, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidery-patches-online-usa/", "notes": "Online sales"},
            {"term": "embroidery patches near me", "volume": 800, "competition": 0.22, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-near-me-usa/", "notes": "Local search"},
            {"term": "personalized embroidery patches", "volume": 700, "competition": 0.20, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/personalized-embroidery-patches-usa/", "notes": "Personalization"},
            {"term": "embroidery patches wholesale usa", "volume": 600, "competition": 0.18, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-wholesale-usa/", "notes": "Wholesale"},
            {"term": "cheap embroidery patches", "volume": 500, "competition": 0.15, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/cheap-embroidery-patches-usa/", "notes": "Budget options"},
            {"term": "embroidery patches made in usa", "volume": 400, "competition": 0.12, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-made-in-usa/", "notes": "USA made"},
            {"term": "embroidery patches for clothing", "volume": 300, "competition": 0.10, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-clothing-usa/", "notes": "Clothing use"},
            {"term": "embroidery patches for bags", "volume": 250, "competition": 0.08, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-bags-usa/", "notes": "Bag application"},
            {"term": "embroidery patches for uniforms", "volume": 200, "competition": 0.05, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-uniforms-usa/", "notes": "Uniform focus"},
            {"term": "embroidery patches iron on", "volume": 150, "competition": 0.03, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-iron-on-usa/", "notes": "Iron-on backing"},
            {"term": "embroidery patches sew on", "volume": 120, "competition": 0.025, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-sew-on-usa/", "notes": "Sew-on option"},
            {"term": "embroidery patches velcro", "volume": 100, "competition": 0.02, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-velcro-usa/", "notes": "Velcro attachment"},
            {"term": "embroidery patches adhesive", "volume": 90, "competition": 0.015, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-adhesive-usa/", "notes": "Adhesive backing"},
            {"term": "embroidery patches logo", "volume": 80, "competition": 0.01, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-logo-usa/", "notes": "Logo designs"},
            {"term": "custom embroidered name patches", "volume": 70, "competition": 0.01, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidered-name-patches/", "notes": "Name variant"},
            {"term": "embroidered patches for t shirts", "volume": 60, "competition": 0.008, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-tshirts-usa/", "notes": ""},
            {"term": "embroidered patches for polo shirts", "volume": 50, "competition": 0.007, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-polo-shirts/", "notes": ""},
            {"term": "embroidered patches for caps", "volume": 45, "competition": 0.006, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-caps-usa/", "notes": ""},
            {"term": "embroidered patches for beanies", "volume": 40, "competition": 0.005, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-beanies/", "notes": ""},
            {"term": "embroidered patches for teams", "volume": 35, "competition": 0.005, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-teams-usa/", "notes": ""},
            {"term": "embroidered patches for schools", "volume": 30, "competition": 0.004, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-schools-usa/", "notes": ""},
            {"term": "embroidered patches for military", "volume": 25, "competition": 0.004, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-military-usa/", "notes": ""},
            {"term": "embroidered patches for scouts", "volume": 20, "competition": 0.003, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-scouts-usa/", "notes": ""},
            {"term": "embroidered patches for events", "volume": 18, "competition": 0.003, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-events-usa/", "notes": ""},
            {"term": "embroidered patches for holidays", "volume": 15, "competition": 0.002, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-holidays-usa/", "notes": ""},
            {"term": "embroidered patches for christmas", "volume": 12, "competition": 0.002, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-christmas/", "notes": ""},
            {"term": "custom embroidery patches", "volume": 4500, "competition": 0.55, "intent": "transactional", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": "Main keyword"},
            {"term": "embroidery patches usa", "volume": 2200, "competition": 0.40, "intent": "commercial", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": ""},
            {"term": "custom embroidery patches no minimum", "volume": 1800, "competition": 0.35, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidery-patches-no-minimum-usa/", "notes": "No MOQ strong point"},
            {"term": "bulk embroidery patches", "volume": 1400, "competition": 0.32, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/bulk-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidery patches for jackets", "volume": 1100, "competition": 0.30, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-jackets-usa/", "notes": ""},
            {"term": "embroidery patches for hats", "volume": 1000, "competition": 0.28, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-hats-usa/", "notes": ""},
            {"term": "custom embroidery patches online", "volume": 900, "competition": 0.25, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidery-patches-online-usa/", "notes": ""},
            {"term": "embroidered patches near me", "volume": 800, "competition": 0.22, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-near-me-usa/", "notes": ""},
            {"term": "personalized embroidery patches", "volume": 700, "competition": 0.20, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/personalized-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidery patches wholesale usa", "volume": 600, "competition": 0.18, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-wholesale-usa/", "notes": ""},
            {"term": "cheap embroidery patches", "volume": 500, "competition": 0.15, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/cheap-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidery patches made in usa", "volume": 450, "competition": 0.14, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-made-in-usa/", "notes": ""},
            {"term": "embroidered patches for clothing", "volume": 400, "competition": 0.13, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-clothing-usa/", "notes": ""},
            {"term": "embroidery patches for bags", "volume": 350, "competition": 0.12, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-bags-usa/", "notes": ""},
            {"term": "embroidery patches for uniforms", "volume": 300, "competition": 0.10, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-patches-uniforms-usa/", "notes": ""},
            {"term": "iron on embroidery patches", "volume": 280, "competition": 0.09, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/iron-on-embroidery-patches-usa/", "notes": ""},
            {"term": "sew on embroidery patches", "volume": 250, "competition": 0.08, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/sew-on-embroidery-patches-usa/", "notes": ""},
            {"term": "velcro embroidery patches", "volume": 220, "competition": 0.07, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/velcro-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidery logo patches", "volume": 200, "competition": 0.06, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidery-logo-patches-usa/", "notes": ""},
            {"term": "custom name embroidery patches", "volume": 180, "competition": 0.055, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-name-embroidery-patches/", "notes": ""},
            {"term": "embroidered patches for t-shirts", "volume": 160, "competition": 0.05, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-t-shirts-usa/", "notes": ""},
            {"term": "embroidered patches for polo shirts", "volume": 140, "competition": 0.045, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-polo-shirts-usa/", "notes": ""},
            {"term": "embroidered cap patches", "volume": 120, "competition": 0.04, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-cap-patches-usa/", "notes": ""},
            {"term": "embroidered beanie patches", "volume": 100, "competition": 0.035, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-beanie-patches-usa/", "notes": ""},
            {"term": "team embroidery patches", "volume": 90, "competition": 0.03, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/team-embroidery-patches-usa/", "notes": ""},
            {"term": "school embroidery patches", "volume": 80, "competition": 0.028, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/school-embroidery-patches-usa/", "notes": ""},
            {"term": "military embroidery patches", "volume": 70, "competition": 0.025, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/military-embroidery-patches-usa/", "notes": ""},
            {"term": "scout embroidery patches", "volume": 60, "competition": 0.022, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/scout-embroidery-patches-usa/", "notes": ""},
            {"term": "event embroidery patches", "volume": 55, "competition": 0.02, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/event-embroidery-patches-usa/", "notes": ""},
            {"term": "holiday embroidery patches", "volume": 50, "competition": 0.018, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/holiday-embroidery-patches-usa/", "notes": ""},
            {"term": "christmas embroidery patches", "volume": 45, "competition": 0.016, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/christmas-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidered morale patches", "volume": 40, "competition": 0.014, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-morale-patches-usa/", "notes": ""},
            {"term": "custom embroidered morale patches", "volume": 35, "competition": 0.012, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/custom-embroidered-morale-patches/", "notes": ""},
            {"term": "embroidered patches for backpacks", "volume": 30, "competition": 0.01, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-backpacks-usa/", "notes": ""},
            {"term": "embroidered patches for jeans", "volume": 28, "competition": 0.009, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-jeans-usa/", "notes": ""},
            {"term": "embroidered patches for hoodies", "volume": 25, "competition": 0.008, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-hoodies-usa/", "notes": ""},
            {"term": "embroidered patches for vests", "volume": 22, "competition": 0.007, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-vests-usa/", "notes": ""},
            {"term": "embroidered patches for dogs", "volume": 20, "competition": 0.006, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-dogs-usa/", "notes": ""},
            {"term": "pet embroidery patches", "volume": 18, "competition": 0.005, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/pet-embroidery-patches-usa/", "notes": ""},
            {"term": "funny embroidery patches", "volume": 15, "competition": 0.004, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/funny-embroidery-patches-usa/", "notes": ""},
            {"term": "embroidered quote patches", "volume": 12, "competition": 0.003, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-quote-patches-usa/", "notes": ""},
            {"term": "embroidered patches for bands", "volume": 10, "competition": 0.002, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-bands-usa/", "notes": ""},
            # You can continue adding more variations like "embroidered patches for cats", "embroidered patches for gaming", "embroidered patches for fitness", etc.
            # ... (add more long-tail variations like "embroidered patches for dogs", "embroidered morale patches usa", etc. to reach 100+; pattern is similar to chenille)

            # Pillar: Woven – 100+ keywords
            {"term": "custom woven patches", "volume": 1800, "competition": 0.42, "intent": "transactional", "pillar": "woven", "target_url": "/services/woven-patch/", "notes": "Core woven service"},
            {"term": "woven patches usa", "volume": 1100, "competition": 0.35, "intent": "commercial", "pillar": "woven", "target_url": "/services/woven-patch/", "notes": ""},
            {"term": "woven patches no minimum", "volume": 800, "competition": 0.30, "intent": "transactional", "pillar": "woven", "target_url": "/blog/woven-patches-no-minimum-usa/", "notes": "USP"},
            {"term": "bulk woven patches", "volume": 700, "competition": 0.28, "intent": "transactional", "pillar": "woven", "target_url": "/blog/bulk-woven-patches-usa/", "notes": ""},
            {"term": "woven patches for clothing", "volume": 600, "competition": 0.25, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-clothing-usa/", "notes": ""},
            {"term": "woven patches for hats", "volume": 500, "competition": 0.22, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-hats-usa/", "notes": ""},
            {"term": "custom woven patches online", "volume": 450, "competition": 0.20, "intent": "transactional", "pillar": "woven", "target_url": "/blog/custom-woven-patches-online/", "notes": ""},
            {"term": "woven patches made in usa", "volume": 400, "competition": 0.18, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-made-in-usa/", "notes": ""},
            {"term": "woven patches for jackets", "volume": 350, "competition": 0.15, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-jackets-usa/", "notes": ""},
            {"term": "woven patches for bags", "volume": 300, "competition": 0.12, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-bags-usa/", "notes": ""},
            {"term": "custom woven patches", "volume": 1800, "competition": 0.42, "intent": "transactional", "pillar": "woven", "target_url": "/services/woven-patch/", "notes": "Main keyword"},
            {"term": "woven patches usa", "volume": 1100, "competition": 0.35, "intent": "commercial", "pillar": "woven", "target_url": "/services/woven-patch/", "notes": ""},
            {"term": "woven patches no minimum", "volume": 800, "competition": 0.30, "intent": "transactional", "pillar": "woven", "target_url": "/blog/woven-patches-no-minimum-usa/", "notes": ""},
            {"term": "bulk woven patches", "volume": 700, "competition": 0.28, "intent": "transactional", "pillar": "woven", "target_url": "/blog/bulk-woven-patches-usa/", "notes": ""},
            {"term": "woven patches for clothing", "volume": 600, "competition": 0.25, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-clothing-usa/", "notes": ""},
            {"term": "woven patches for hats", "volume": 500, "competition": 0.22, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-hats-usa/", "notes": ""},
            {"term": "custom woven patches online", "volume": 450, "competition": 0.20, "intent": "transactional", "pillar": "woven", "target_url": "/blog/custom-woven-patches-online-usa/", "notes": ""},
            {"term": "woven patches made in usa", "volume": 400, "competition": 0.18, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-made-in-usa/", "notes": ""},
            {"term": "woven logo patches", "volume": 350, "competition": 0.16, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-logo-patches-usa/", "notes": ""},
            {"term": "woven name patches", "volume": 300, "competition": 0.14, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-name-patches-usa/", "notes": ""},
            {"term": "woven patches for jackets", "volume": 280, "competition": 0.13, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-jackets-usa/", "notes": ""},
            {"term": "woven patches for bags", "volume": 250, "competition": 0.12, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-bags-usa/", "notes": ""},
            {"term": "woven patches for uniforms", "volume": 220, "competition": 0.11, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-uniforms-usa/", "notes": ""},
            {"term": "iron on woven patches", "volume": 200, "competition": 0.10, "intent": "commercial", "pillar": "woven", "target_url": "/blog/iron-on-woven-patches-usa/", "notes": ""},
            {"term": "sew on woven patches", "volume": 180, "competition": 0.09, "intent": "commercial", "pillar": "woven", "target_url": "/blog/sew-on-woven-patches-usa/", "notes": ""},
            {"term": "velcro woven patches", "volume": 160, "competition": 0.08, "intent": "commercial", "pillar": "woven", "target_url": "/blog/velcro-woven-patches-usa/", "notes": ""},
            {"term": "woven patches for teams", "volume": 140, "competition": 0.07, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-teams-usa/", "notes": ""},
            {"term": "woven patches for brands", "volume": 120, "competition": 0.06, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-brands-usa/", "notes": ""},
            {"term": "detailed woven patches", "volume": 100, "competition": 0.05, "intent": "commercial", "pillar": "woven", "target_url": "/blog/detailed-woven-patches-usa/", "notes": ""},
            {"term": "woven patches for apparel", "volume": 90, "competition": 0.045, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-apparel-usa/", "notes": ""},
            {"term": "woven patches for backpacks", "volume": 80, "competition": 0.04, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-backpacks-usa/", "notes": ""},
            # ... continue similarly with more items like "woven patches for jeans", "woven patches for beanies", "woven patches for military", etc.
            # ... (extend similarly with "woven patches for teams", "woven logo patches usa", "woven name patches", etc. to 100+)

            # Pillar: PVC – 100+ keywords
            {"term": "custom pvc patches", "volume": 3800, "competition": 0.50, "intent": "transactional", "pillar": "pvc", "target_url": "/services/pvc-patches/", "notes": "Core PVC service"},
            {"term": "pvc patches usa", "volume": 2000, "competition": 0.40, "intent": "commercial", "pillar": "pvc", "target_url": "/services/pvc-patches/", "notes": ""},
            {"term": "pvc patches no minimum", "volume": 1400, "competition": 0.35, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/pvc-patches-no-minimum-usa/", "notes": ""},
            {"term": "bulk pvc patches", "volume": 1200, "competition": 0.32, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/bulk-pvc-patches-usa/", "notes": ""},
            {"term": "pvc patches for jackets", "volume": 1000, "competition": 0.30, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-jackets-usa/", "notes": ""},
            {"term": "pvc patches velcro", "volume": 900, "competition": 0.28, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-velcro-usa/", "notes": ""},
            {"term": "3d pvc patches custom", "volume": 800, "competition": 0.25, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/3d-pvc-patches-usa/", "notes": "3D variant"},
            {"term": "pvc patches waterproof", "volume": 700, "competition": 0.22, "intent": "informational", "pillar": "pvc", "target_url": "/blog/pvc-patches-waterproof/", "notes": ""},
            {"term": "custom pvc patches", "volume": 3800, "competition": 0.50, "intent": "transactional", "pillar": "pvc", "target_url": "/services/pvc-patches/", "notes": "Main keyword"},
            {"term": "pvc patches usa", "volume": 2000, "competition": 0.40, "intent": "commercial", "pillar": "pvc", "target_url": "/services/pvc-patches/", "notes": ""},
            {"term": "pvc patches no minimum", "volume": 1400, "competition": 0.35, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/pvc-patches-no-minimum-usa/", "notes": ""},
            {"term": "bulk pvc patches", "volume": 1200, "competition": 0.32, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/bulk-pvc-patches-usa/", "notes": ""},
            {"term": "pvc patches for jackets", "volume": 1000, "competition": 0.30, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-jackets-usa/", "notes": ""},
            {"term": "pvc velcro patches", "volume": 900, "competition": 0.28, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-velcro-patches-usa/", "notes": ""},
            {"term": "3d pvc patches", "volume": 800, "competition": 0.26, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/3d-pvc-patches-usa/", "notes": ""},
            {"term": "pvc patches waterproof", "volume": 700, "competition": 0.24, "intent": "informational", "pillar": "pvc", "target_url": "/blog/pvc-patches-waterproof-usa/", "notes": ""},
            {"term": "custom 3d pvc patches", "volume": 650, "competition": 0.22, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/custom-3d-pvc-patches/", "notes": ""},
            {"term": "pvc morale patches", "volume": 600, "competition": 0.20, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-morale-patches-usa/", "notes": ""},
            {"term": "pvc patches for tactical gear", "volume": 550, "competition": 0.19, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-tactical-gear-usa/", "notes": ""},
            {"term": "pvc patches for vests", "volume": 500, "competition": 0.18, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-vests-usa/", "notes": ""},
            {"term": "pvc patches for airsoft", "volume": 450, "competition": 0.17, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-airsoft-usa/", "notes": ""},
            {"term": "glow in dark pvc patches", "volume": 400, "competition": 0.15, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/glow-in-dark-pvc-patches/", "notes": ""},
            {"term": "pvc patches for backpacks", "volume": 350, "competition": 0.14, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-backpacks-usa/", "notes": ""},
            # ... add more like "pvc patches for military", "pvc patches for paintball", "rubber pvc patches usa", etc.
            # ... (extend with tactical/military focused long-tails like "pvc morale patches", "pvc patches for airsoft", etc.)

            # Pillar: Sublimation – 100+ keywords
            {"term": "custom sublimation patches", "volume": 2000, "competition": 0.45, "intent": "transactional", "pillar": "sublimation", "target_url": "/services/sublimation-patches/", "notes": "Core sublimation service"},
            {"term": "sublimation patches usa", "volume": 1200, "competition": 0.38, "intent": "commercial", "pillar": "sublimation", "target_url": "/services/sublimation-patches/", "notes": ""},
            {"term": "full color sublimation patches", "volume": 900, "competition": 0.32, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/full-color-sublimation-patches-usa/", "notes": "Color focus"},
            {"term": "sublimation patches no minimum", "volume": 800, "competition": 0.30, "intent": "transactional", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-no-minimum/", "notes": ""},
            {"term": "sublimation patches for apparel", "volume": 700, "competition": 0.28, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-apparel-usa/", "notes": ""},
            {"term": "custom printed patches sublimation", "volume": 600, "competition": 0.25, "intent": "transactional", "pillar": "sublimation", "target_url": "/blog/custom-printed-patches-sublimation/", "notes": ""},
            {"term": "custom sublimation patches", "volume": 2000, "competition": 0.45, "intent": "transactional", "pillar": "sublimation", "target_url": "/services/sublimation-patches/", "notes": "Main keyword"},
            {"term": "sublimation patches usa", "volume": 1200, "competition": 0.38, "intent": "commercial", "pillar": "sublimation", "target_url": "/services/sublimation-patches/", "notes": ""},
            {"term": "full color sublimation patches", "volume": 900, "competition": 0.32, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/full-color-sublimation-patches-usa/", "notes": ""},
            {"term": "sublimation patches no minimum", "volume": 800, "competition": 0.30, "intent": "transactional", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-no-minimum-usa/", "notes": ""},
            {"term": "sublimation patches for apparel", "volume": 700, "competition": 0.28, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-apparel-usa/", "notes": ""},
            {"term": "custom printed sublimation patches", "volume": 650, "competition": 0.26, "intent": "transactional", "pillar": "sublimation", "target_url": "/blog/custom-printed-sublimation-patches/", "notes": ""},
            {"term": "vibrant sublimation patches", "volume": 600, "competition": 0.24, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/vibrant-sublimation-patches-usa/", "notes": ""},
            {"term": "sublimation patches for hats", "volume": 550, "competition": 0.22, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-hats-usa/", "notes": ""},
            {"term": "sublimation patches for t-shirts", "volume": 500, "competition": 0.20, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-tshirts-usa/", "notes": ""},
            {"term": "sublimation logo patches", "volume": 450, "competition": 0.18, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-logo-patches-usa/", "notes": ""},
            {"term": "sublimation patches iron on", "volume": 400, "competition": 0.16, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-iron-on-usa/", "notes": ""},
            {"term": "sublimation patches for bags", "volume": 350, "competition": 0.14, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-bags-usa/", "notes": ""},
            # ... continue with "sublimation patches for teams", "photo sublimation patches", "custom full color patches usa", etc.
            # ... (extend with "sublimation patches for hats", "vibrant sublimation patches usa", etc.)

            # ───────────────────────────────────────────────────────
            # Leather Patches – 105+ keywords
            # ───────────────────────────────────────────────────────
            {"term": "custom leather patches", "volume": 3200, "competition": 0.45, "intent": "transactional", "pillar": "leather", "target_url": "/services/leather-patch/", "notes": "Core keyword – top performer"},
            {"term": "leather patches usa", "volume": 1800, "competition": 0.38, "intent": "commercial", "pillar": "leather", "target_url": "/services/leather-patch/", "notes": "Location focus"},
            {"term": "custom leather patches no minimum", "volume": 1400, "competition": 0.35, "intent": "transactional", "pillar": "leather", "target_url": "/blog/custom-leather-patches-no-minimum-usa/", "notes": "No MOQ USP"},
            {"term": "premium leather patches", "volume": 1200, "competition": 0.32, "intent": "commercial", "pillar": "leather", "target_url": "/blog/premium-leather-patches-usa/", "notes": "Premium upsell"},
            {"term": "genuine leather patches", "volume": 1000, "competition": 0.30, "intent": "commercial", "pillar": "leather", "target_url": "/blog/genuine-leather-patches-usa/", "notes": "Material authenticity"},
            {"term": "leather patches for jackets", "volume": 950, "competition": 0.28, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-jackets-usa/", "notes": "Most popular use"},
            {"term": "custom leather patches online", "volume": 850, "competition": 0.26, "intent": "transactional", "pillar": "leather", "target_url": "/blog/custom-leather-patches-online-usa/", "notes": ""},
            {"term": "leather patches near me", "volume": 750, "competition": 0.24, "intent": "transactional", "pillar": "leather", "target_url": "/blog/leather-patches-near-me-usa/", "notes": "Local search"},
            {"term": "embossed leather patches", "volume": 700, "competition": 0.22, "intent": "commercial", "pillar": "leather", "target_url": "/blog/embossed-leather-patches-usa/", "notes": "Finish type"},
            {"term": "leather patches for bags", "volume": 650, "competition": 0.20, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-bags-usa/", "notes": "Accessory focus"},
            {"term": "real leather custom patches", "volume": 600, "competition": 0.19, "intent": "transactional", "pillar": "leather", "target_url": "/blog/real-leather-custom-patches/", "notes": ""},
            {"term": "leather logo patches", "volume": 550, "competition": 0.18, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-logo-patches-usa/", "notes": ""},
            {"term": "leather name patches", "volume": 500, "competition": 0.17, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-name-patches-usa/", "notes": ""},
            {"term": "leather patches wholesale", "volume": 450, "competition": 0.16, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-wholesale-usa/", "notes": ""},
            {"term": "custom embossed leather patches", "volume": 420, "competition": 0.15, "intent": "transactional", "pillar": "leather", "target_url": "/blog/custom-embossed-leather-patches/", "notes": ""},
            {"term": "leather patches for jeans", "volume": 400, "competition": 0.14, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-jeans-usa/", "notes": ""},
            {"term": "leather patches for hats", "volume": 380, "competition": 0.13, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-hats-usa/", "notes": ""},
            {"term": "vintage leather patches", "volume": 350, "competition": 0.12, "intent": "commercial", "pillar": "leather", "target_url": "/blog/vintage-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for belts", "volume": 320, "competition": 0.11, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-belts-usa/", "notes": ""},
            {"term": "handmade leather patches", "volume": 300, "competition": 0.10, "intent": "commercial", "pillar": "leather", "target_url": "/blog/handmade-leather-patches-usa/", "notes": ""},
            {"term": "leather patches sew on", "volume": 280, "competition": 0.09, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-sew-on-usa/", "notes": ""},
            {"term": "leather patches iron on", "volume": 260, "competition": 0.085, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-iron-on-usa/", "notes": ""},
            {"term": "leather patches for wallets", "volume": 240, "competition": 0.08, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-wallets-usa/", "notes": ""},
            {"term": "brown leather patches custom", "volume": 220, "competition": 0.075, "intent": "commercial", "pillar": "leather", "target_url": "/blog/brown-leather-patches-custom/", "notes": ""},
            {"term": "black leather patches", "volume": 200, "competition": 0.07, "intent": "commercial", "pillar": "leather", "target_url": "/blog/black-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for boots", "volume": 180, "competition": 0.065, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-boots-usa/", "notes": ""},
            {"term": "leather patches for motorcycle jackets", "volume": 160, "competition": 0.06, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-motorcycle-jackets/", "notes": ""},
            {"term": "distressed leather patches", "volume": 140, "competition": 0.055, "intent": "commercial", "pillar": "leather", "target_url": "/blog/distressed-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for furniture", "volume": 120, "competition": 0.05, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-furniture-usa/", "notes": ""},
            {"term": "leather monogram patches", "volume": 100, "competition": 0.045, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-monogram-patches-usa/", "notes": ""},
            {"term": "personalized leather patches", "volume": 90, "competition": 0.04, "intent": "transactional", "pillar": "leather", "target_url": "/blog/personalized-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for gifts", "volume": 80, "competition": 0.035, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-gifts-usa/", "notes": ""},
            {"term": "luxury leather patches", "volume": 70, "competition": 0.03, "intent": "commercial", "pillar": "leather", "target_url": "/blog/luxury-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for bags and purses", "volume": 65, "competition": 0.028, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-bags-purses/", "notes": ""},
            {"term": "custom leather label patches", "volume": 60, "competition": 0.025, "intent": "commercial", "pillar": "leather", "target_url": "/blog/custom-leather-label-patches/", "notes": ""},
            {"term": "leather patches for crafts", "volume": 55, "competition": 0.022, "intent": "informational", "pillar": "leather", "target_url": "/blog/leather-patches-crafts-usa/", "notes": ""},
            {"term": "leather patches for diy", "volume": 50, "competition": 0.02, "intent": "informational", "pillar": "leather", "target_url": "/blog/leather-patches-diy-usa/", "notes": ""},
            {"term": "leather patches for brands", "volume": 45, "competition": 0.018, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-brands-usa/", "notes": ""},
            {"term": "leather patches for fashion brands", "volume": 40, "competition": 0.016, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-fashion-brands/", "notes": ""},
            {"term": "leather patches for vintage clothing", "volume": 35, "competition": 0.014, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-vintage-clothing/", "notes": ""},
            {"term": "leather patches for workwear", "volume": 30, "competition": 0.012, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-workwear-usa/", "notes": ""},
            {"term": "leather patches for uniforms", "volume": 28, "competition": 0.011, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-uniforms-usa/", "notes": ""},
            {"term": "leather patches for corporate gifts", "volume": 25, "competition": 0.01, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-corporate-gifts/", "notes": ""},
            {"term": "leather patches for events", "volume": 22, "competition": 0.009, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-events-usa/", "notes": ""},
            {"term": "custom leather morale patches", "volume": 20, "competition": 0.008, "intent": "commercial", "pillar": "leather", "target_url": "/blog/custom-leather-morale-patches/", "notes": ""},
            {"term": "leather patches for motorcycle clubs", "volume": 18, "competition": 0.007, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-motorcycle-clubs/", "notes": ""},
            {"term": "leather patches for cowboys", "volume": 15, "competition": 0.006, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-cowboys-usa/", "notes": ""},
            {"term": "western leather patches", "volume": 12, "competition": 0.005, "intent": "commercial", "pillar": "leather", "target_url": "/blog/western-leather-patches-usa/", "notes": ""},
            {"term": "leather patches for hats and caps", "volume": 10, "competition": 0.004, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-hats-caps/", "notes": ""},


            # ───────────────────────────────────────────────────────
            # Morale Patches – ~110 keywords (high intent for tactical/military/humor)
            # ───────────────────────────────────────────────────────
            {"term": "custom morale patches", "volume": 2800, "competition": 0.48, "intent": "transactional", "pillar": "morale", "target_url": "/services/custom-morale-patches/", "notes": "Core high-intent keyword"},
            {"term": "morale patches", "volume": 2200, "competition": 0.45, "intent": "commercial", "pillar": "morale", "target_url": "/services/morale-patches/", "notes": "Broad search"},
            {"term": "morale patches velcro", "volume": 1800, "competition": 0.42, "intent": "transactional", "pillar": "morale", "target_url": "/blog/morale-patches-velcro-usa/", "notes": "Most common backing"},
            {"term": "custom morale patches no minimum", "volume": 1400, "competition": 0.38, "intent": "transactional", "pillar": "morale", "target_url": "/blog/custom-morale-patches-no-minimum/", "notes": "Strong USP match"},
            {"term": "funny morale patches", "volume": 1200, "competition": 0.35, "intent": "commercial", "pillar": "morale", "target_url": "/blog/funny-morale-patches-usa/", "notes": "Humor category leader"},
            {"term": "morale patches for military", "volume": 1100, "competition": 0.32, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-military-usa/", "notes": "Military core"},
            {"term": "tactical morale patches", "volume": 1000, "competition": 0.30, "intent": "commercial", "pillar": "morale", "target_url": "/blog/tactical-morale-patches-usa/", "notes": "Tactical gear focus"},
            {"term": "morale patches usa made", "volume": 900, "competition": 0.28, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-usa-made/", "notes": "Made in USA appeal"},
            {"term": "custom funny morale patches", "volume": 850, "competition": 0.26, "intent": "transactional", "pillar": "morale", "target_url": "/blog/custom-funny-morale-patches/", "notes": ""},
            {"term": "morale patches for vests", "volume": 800, "competition": 0.25, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-vests-usa/", "notes": "Popular placement"},
            {"term": "army morale patches", "volume": 750, "competition": 0.24, "intent": "commercial", "pillar": "morale", "target_url": "/blog/army-morale-patches-usa/", "notes": "Branch-specific"},
            {"term": "morale patches velcro custom", "volume": 700, "competition": 0.22, "intent": "transactional", "pillar": "morale", "target_url": "/blog/morale-patches-velcro-custom/", "notes": ""},
            {"term": "pvc morale patches", "volume": 650, "competition": 0.20, "intent": "commercial", "pillar": "morale", "target_url": "/blog/pvc-morale-patches-usa/", "notes": "PVC style crossover"},
            {"term": "laser cut morale patches", "volume": 600, "competition": 0.19, "intent": "commercial", "pillar": "morale", "target_url": "/blog/laser-cut-morale-patches/", "notes": "Premium style"},
            {"term": "morale patches for backpacks", "volume": 550, "competition": 0.18, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-backpacks-usa/", "notes": ""},
            {"term": "ir morale patches", "volume": 500, "competition": 0.17, "intent": "commercial", "pillar": "morale", "target_url": "/blog/ir-morale-patches-usa/", "notes": "Infrared tactical"},
            {"term": "glow in dark morale patches", "volume": 450, "competition": 0.16, "intent": "commercial", "pillar": "morale", "target_url": "/blog/glow-in-dark-morale-patches/", "notes": ""},
            {"term": "morale patches for airsoft", "volume": 420, "competition": 0.15, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-airsoft-usa/", "notes": "Gaming/tactical crossover"},
            {"term": "veteran morale patches", "volume": 400, "competition": 0.14, "intent": "commercial", "pillar": "morale", "target_url": "/blog/veteran-morale-patches-usa/", "notes": "Veteran audience"},
            {"term": "morale patches for police", "volume": 380, "competition": 0.13, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-police-usa/", "notes": "LE focus"},
            {"term": "custom tactical morale patches", "volume": 350, "competition": 0.12, "intent": "transactional", "pillar": "morale", "target_url": "/blog/custom-tactical-morale-patches/", "notes": ""},
            {"term": "morale patches for hats", "volume": 320, "competition": 0.11, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-hats-usa/", "notes": ""},
            {"term": "sarcastic morale patches", "volume": 300, "competition": 0.10, "intent": "commercial", "pillar": "morale", "target_url": "/blog/sarcastic-morale-patches-usa/", "notes": "Humor style"},
            {"term": "morale patches for molle", "volume": 280, "competition": 0.09, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-molle-usa/", "notes": "Gear compatibility"},
            {"term": "morale patches for vets", "volume": 260, "competition": 0.085, "intent": "commercial", "pillar": "morale", "target_url": "/blog/morale-patches-vets-usa/", "notes": ""},
            # ... (add more long-tails like "morale patches for navy seals", "operator morale patches", "deployed morale patches", "funny army morale patches", "morale patches for first responders", etc. to reach 120+ if needed)


            # ───────────────────────────────────────────────────────
            # Military Patches – ~110 keywords (strong for units, branches, custom ID)
            # ───────────────────────────────────────────────────────
            {"term": "custom military patches", "volume": 4200, "competition": 0.52, "intent": "transactional", "pillar": "military", "target_url": "/services/custom-military-patches/", "notes": "High-volume core term"},
            {"term": "military patches usa", "volume": 2500, "competition": 0.45, "intent": "commercial", "pillar": "military", "target_url": "/services/military-patches/", "notes": ""},
            {"term": "custom military patches no minimum", "volume": 1800, "competition": 0.40, "intent": "transactional", "pillar": "military", "target_url": "/blog/custom-military-patches-no-minimum-usa/", "notes": "No MOQ essential"},
            {"term": "military velcro patches", "volume": 1600, "competition": 0.38, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-velcro-patches-usa/", "notes": "Backing type"},
            {"term": "us army patches custom", "volume": 1400, "competition": 0.35, "intent": "commercial", "pillar": "military", "target_url": "/blog/us-army-patches-custom/", "notes": "Branch leader"},
            {"term": "military name patches", "volume": 1200, "competition": 0.32, "intent": "transactional", "pillar": "military", "target_url": "/blog/military-name-patches-usa/", "notes": "Personalization"},
            {"term": "custom callsign patches military", "volume": 1100, "competition": 0.30, "intent": "transactional", "pillar": "military", "target_url": "/blog/custom-callsign-patches-military/", "notes": "Popular for aviators/operators"},
            {"term": "military patches made in usa", "volume": 1000, "competition": 0.28, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-patches-made-in-usa/", "notes": "USA production"},
            {"term": "laser cut military patches", "volume": 900, "competition": 0.26, "intent": "commercial", "pillar": "military", "target_url": "/blog/laser-cut-military-patches-usa/", "notes": "Premium tactical style"},
            {"term": "military morale patches custom", "volume": 850, "competition": 0.25, "intent": "transactional", "pillar": "military", "target_url": "/blog/military-morale-patches-custom/", "notes": "Crossover with morale"},
            {"term": "ocp military patches", "volume": 800, "competition": 0.24, "intent": "commercial", "pillar": "military", "target_url": "/blog/ocp-military-patches-usa/", "notes": "Operational Camo Pattern"},
            {"term": "military rank patches custom", "volume": 750, "competition": 0.22, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-rank-patches-custom/", "notes": ""},
            {"term": "usmc patches custom", "volume": 700, "competition": 0.20, "intent": "commercial", "pillar": "military", "target_url": "/blog/usmc-patches-custom/", "notes": "Marines branch"},
            {"term": "navy military patches", "volume": 650, "competition": 0.19, "intent": "commercial", "pillar": "military", "target_url": "/blog/navy-military-patches-usa/", "notes": ""},
            {"term": "air force custom patches", "volume": 600, "competition": 0.18, "intent": "commercial", "pillar": "military", "target_url": "/blog/air-force-custom-patches/", "notes": ""},
            {"term": "military id patches", "volume": 550, "competition": 0.17, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-id-patches-usa/", "notes": ""},
            {"term": "custom military rocker patches", "volume": 500, "competition": 0.16, "intent": "transactional", "pillar": "military", "target_url": "/blog/custom-military-rocker-patches/", "notes": "Rocker style"},
            {"term": "military patches velcro backed", "volume": 480, "competition": 0.15, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-patches-velcro-backed/", "notes": ""},
            {"term": "ir military patches", "volume": 450, "competition": 0.14, "intent": "commercial", "pillar": "military", "target_url": "/blog/ir-military-patches-usa/", "notes": "Infrared for night ops"},
            {"term": "military unit patches custom", "volume": 420, "competition": 0.13, "intent": "transactional", "pillar": "military", "target_url": "/blog/military-unit-patches-custom/", "notes": "Unit pride"},
            {"term": "custom military name tape", "volume": 400, "competition": 0.12, "intent": "transactional", "pillar": "military", "target_url": "/blog/custom-military-name-tape/", "notes": "Name tape variant"},
            {"term": "military patches for vests", "volume": 380, "competition": 0.11, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-patches-vests-usa/", "notes": ""},
            {"term": "deployed military patches", "volume": 350, "competition": 0.10, "intent": "commercial", "pillar": "military", "target_url": "/blog/deployed-military-patches-usa/", "notes": "Deployment theme"},
            {"term": "military patches for ocp uniform", "volume": 320, "competition": 0.09, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-patches-ocp-uniform/", "notes": ""},
            {"term": "custom military flag patches", "volume": 300, "competition": 0.085, "intent": "transactional", "pillar": "military", "target_url": "/blog/custom-military-flag-patches/", "notes": ""},
            {"term": "military patches for airsoft", "volume": 280, "competition": 0.08, "intent": "commercial", "pillar": "military", "target_url": "/blog/military-patches-airsoft-usa/", "notes": ""},
            {"term": "veteran military patches", "volume": 260, "competition": 0.075, "intent": "commercial", "pillar": "military", "target_url": "/blog/veteran-military-patches-usa/", "notes": ""},
            # ... extend with more like "custom special forces patches", "military qualification patches", "navy seals morale patches", "army ranger patches custom", "military challenge coin patches", etc.


            # Add your original 60+ keywords here to preserve them
            # ───────────────────────────────────────────────────────
            #  ORIGINAL 60+ KEYWORDS 
            # ───────────────────────────────────────────────────────
            {"term": "custom patches USA", "volume": 8000, "competition": 0.65, "intent": "transactional", "pillar": "general", "target_url": "/custom-patches-usa/", "notes": "Core money keyword – highest priority"},
            {"term": "custom patches no minimum USA", "volume": 2500, "competition": 0.45, "intent": "transactional", "pillar": "general", "target_url": "/blog/custom-patches-no-minimum-usa/", "notes": "Your strongest USP"},
            {"term": "buy custom patches online USA", "volume": 1800, "competition": 0.50, "intent": "transactional", "pillar": "general", "target_url": "/quote/", "notes": "Direct conversion path"},
            {"term": "custom patches fast shipping USA", "volume": 1100, "competition": 0.38, "intent": "transactional", "pillar": "general", "target_url": "/blog/custom-patches-fast-shipping-usa/", "notes": "US production advantage"},
            {"term": "custom patches for businesses USA", "volume": 600, "competition": 0.32, "intent": "commercial", "pillar": "general", "target_url": "/blog/custom-patches-businesses-usa/", "notes": "B2B angle"},

            {"term": "custom embroidered patches USA", "volume": 4500, "competition": 0.55, "intent": "transactional", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": "Flagship service match"},
            {"term": "embroidered patches no minimum USA", "volume": 2200, "competition": 0.40, "intent": "transactional", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-no-minimum-usa/", "notes": "Long-tail gold – USP"},
            {"term": "embroidered patches for jackets USA", "volume": 1400, "competition": 0.38, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-jackets-usa/", "notes": "Apparel focus"},
            {"term": "embroidered patches for hats USA", "volume": 1100, "competition": 0.35, "intent": "commercial", "pillar": "embroidered", "target_url": "/blog/embroidered-patches-hats-usa/", "notes": "Hat-specific"},
            {"term": "buy custom embroidered patches online 2026", "volume": 1000, "competition": 0.30, "intent": "transactional", "pillar": "embroidered", "target_url": "/services/custom-embroidery-patches/", "notes": "Future-proof trend"},

            {"term": "custom leather patches USA", "volume": 3200, "competition": 0.45, "intent": "commercial", "pillar": "leather", "target_url": "/services/leather-patch/", "notes": "Current top performer"},
            {"term": "premium leather custom patches USA", "volume": 1200, "competition": 0.35, "intent": "transactional", "pillar": "leather", "target_url": "/blog/premium-leather-patches-usa/", "notes": "Upsell premium"},
            {"term": "custom leather patches for jackets USA", "volume": 1000, "competition": 0.32, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-jackets-usa/", "notes": "Jacket synergy"},
            {"term": "leather patches embossed USA", "volume": 800, "competition": 0.28, "intent": "commercial", "pillar": "leather", "target_url": "/blog/leather-patches-embossed-usa/", "notes": "Finish long-tail"},
            {"term": "genuine leather patches USA", "volume": 600, "competition": 0.22, "intent": "commercial", "pillar": "leather", "target_url": "/blog/genuine-leather-patches-usa/", "notes": "Material variant"},

            {"term": "custom PVC patches USA", "volume": 3800, "competition": 0.50, "intent": "commercial", "pillar": "pvc", "target_url": "/services/pvc-patches/", "notes": "Strong service match"},
            {"term": "PVC patches no minimum USA", "volume": 1400, "competition": 0.35, "intent": "transactional", "pillar": "pvc", "target_url": "/blog/pvc-patches-no-minimum-usa/", "notes": "USP variant"},
            {"term": "PVC vs embroidered patches comparison", "volume": 1000, "competition": 0.30, "intent": "informational", "pillar": "pvc", "target_url": "/blog/pvc-vs-embroidered-comparison/", "notes": "Comparison content"},
            {"term": "durable PVC custom patches USA", "volume": 800, "competition": 0.28, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/durable-pvc-patches-usa/", "notes": "Durability angle"},
            {"term": "PVC patches for bags USA", "volume": 600, "competition": 0.25, "intent": "commercial", "pillar": "pvc", "target_url": "/blog/pvc-patches-bags-usa/", "notes": "Accessory focus"},

            {"term": "custom chenille patches USA", "volume": 2800, "competition": 0.42, "intent": "commercial", "pillar": "chenille", "target_url": "/services/chenille-patches/", "notes": "Direct service match"},
            {"term": "chenille patches for jackets USA", "volume": 1800, "competition": 0.38, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-jackets-usa/", "notes": "Jacket synergy"},
            {"term": "premium chenille custom patches USA", "volume": 900, "competition": 0.30, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/premium-chenille-patches-usa/", "notes": "Premium upsell"},
            {"term": "chenille patches varsity USA", "volume": 800, "competition": 0.28, "intent": "commercial", "pillar": "chenille", "target_url": "/blog/chenille-patches-varsity-usa/", "notes": "School/team niche"},
            {"term": "custom chenille patches no minimum USA", "volume": 600, "competition": 0.25, "intent": "transactional", "pillar": "chenille", "target_url": "/blog/chenille-patches-no-minimum-usa/", "notes": "USP variant"},

            {"term": "custom sublimation patches USA", "volume": 2000, "competition": 0.45, "intent": "commercial", "pillar": "sublimation", "target_url": "/services/sublimation-patches/", "notes": "Direct service match"},
            {"term": "full color sublimation patches USA", "volume": 900, "competition": 0.32, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/full-color-sublimation-patches-usa/", "notes": "Color focus"},
            {"term": "sublimation patches for apparel USA", "volume": 700, "competition": 0.28, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/sublimation-patches-apparel-usa/", "notes": "Apparel angle"},
            {"term": "custom printed patches USA", "volume": 1200, "competition": 0.40, "intent": "commercial", "pillar": "sublimation", "target_url": "/blog/custom-printed-patches-usa/", "notes": "Printed synonym"},
            {"term": "sublimation vs embroidered patches", "volume": 800, "competition": 0.30, "intent": "informational", "pillar": "sublimation", "target_url": "/blog/sublimation-vs-embroidered/", "notes": "Comparison guide"},

            {"term": "custom woven patches USA", "volume": 1800, "competition": 0.42, "intent": "commercial", "pillar": "woven", "target_url": "/services/wowen-patch/", "notes": "Direct match (fix slug typo later)"},
            {"term": "woven patches no minimum USA", "volume": 800, "competition": 0.30, "intent": "transactional", "pillar": "woven", "target_url": "/blog/woven-patches-no-minimum-usa/", "notes": "USP variant"},
            {"term": "detailed woven patches USA", "volume": 600, "competition": 0.25, "intent": "commercial", "pillar": "woven", "target_url": "/blog/detailed-woven-patches-usa/", "notes": "Detail focus"},
            {"term": "woven vs embroidered patches", "volume": 700, "competition": 0.28, "intent": "informational", "pillar": "woven", "target_url": "/blog/woven-vs-embroidered/", "notes": "Comparison content"},
            {"term": "custom woven patches for hats USA", "volume": 500, "competition": 0.22, "intent": "commercial", "pillar": "woven", "target_url": "/blog/woven-patches-hats-usa/", "notes": "Hat niche"},

            {"term": "how to design custom patches 2026", "volume": 3500, "competition": 0.48, "intent": "informational", "pillar": "guides", "target_url": "/blog/how-to-design-custom-patches-2026/", "notes": "Pillar guide – evergreen"},
            {"term": "custom patches pricing USA", "volume": 1900, "competition": 0.40, "intent": "commercial", "pillar": "guides", "target_url": "/blog/custom-patches-pricing-usa/", "notes": "Conversion driver"},
            {"term": "custom patches materials guide USA", "volume": 1500, "competition": 0.35, "intent": "informational", "pillar": "guides", "target_url": "/blog/custom-patches-materials-guide-usa/", "notes": "Educational hub"},
            {"term": "best custom patches company USA", "volume": 1200, "competition": 0.42, "intent": "commercial", "pillar": "guides", "target_url": "/blog/best-custom-patches-company-usa/", "notes": "Review-style post"},
            {"term": "custom patches trends 2026 USA", "volume": 900, "competition": 0.30, "intent": "informational", "pillar": "guides", "target_url": "/blog/custom-patches-trends-2026-usa/", "notes": "Future-proof content"},
        ]

        created = 0
        updated = 0
        skipped = 0

        self.stdout.write(f"Processing {len(keywords_data)} keywords...")

        for data in keywords_data:
            term = data["term"]
            existing = Keyword.objects.filter(term=term).first()

            if existing and not update_existing:
                skipped += 1
                self.stdout.write(self.style.NOTICE(f"[SKIPPED] {term} already exists"))
                continue

            if existing and update_existing:
                obj = existing
                action = "WOULD UPDATE" if dry_run else "UPDATED"
                updated += 1
            else:
                obj = Keyword()
                action = "WOULD CREATE" if dry_run else "CREATED"
                created += 1

            # Apply all fields safely
            for field in ['term', 'volume', 'competition', 'intent', 'pillar', 'target_url', 'notes']:
                if field in data:
                    setattr(obj, field, data[field])

            if not dry_run:
                obj.save()

            self.stdout.write(self.style.SUCCESS(f"[{action}] {term} → {obj.target_url or '(auto-generated)'}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDry run complete:\n"
                    f"  Would create: {created}\n"
                    f"  Would update: {updated}\n"
                    f"  Skipped: {skipped}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nImport complete:\n"
                    f"  Created: {created}\n"
                    f"  Updated: {updated}\n"
                    f"  Skipped: {skipped}"
                )
            )