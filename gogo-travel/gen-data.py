#!/usr/bin/env python3
"""Single source of truth for GOGO! destinations.

Edit DESTINATIONS below, then run:  python3 gen-data.py
It patches, consistently and in place:
  - assets/js/data.js         (GOGO.grad map, GOGO.trips array, DRIVE + FLY)
  - assets/css/styles.css      (the .ph--<id> photo/gradient rules)
  - assets/img/fetch-photos.py (the QUERIES search terms)

Destinations and hotels are REAL places; prices, ratings and availability are
REPRESENTATIVE SAMPLE values for the demo. Gradients are placeholders shown
until a real photo (assets/img/<id>.jpg) is dropped in.
"""
import colorsys, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent

# muted "quiet-luxury" gradient generator (teal / gold-wine / plum / forest) ----
def hx(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s / 100)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))

def auto_grad(kind, i):
    j = (i * 11) % 20 - 10
    if kind == "Beach":
        h = 185 + j
        return f"linear-gradient(155deg,{hx(h,30,54)},{hx(h+6,40,33)} 58%,{hx(h+3,32,17)})"
    if kind == "Cultural":
        return f"linear-gradient(155deg,{hx(38+j*0.4,44,55)},{hx(350+j*0.3,42,33)} 56%,{hx(345,34,15)})"
    if kind == "City":
        return f"linear-gradient(155deg,{hx(42+j*0.3,40,55)},{hx(300+j,22,40)} 58%,{hx(288,24,16)})"
    return f"linear-gradient(155deg,{hx(140+j,30,50)},{hx(150+j,36,30)} 55%,{hx(150,30,15)})"

# keep the original nine looking exactly as they do now -----------------------
FIXED = {
    "amphawa":      "linear-gradient(155deg,#8A9A6E,#4E6B57 55%,#262E28)",
    "ayutthaya":    "linear-gradient(155deg,#C0904E,#7A3E4A 55%,#2E2026)",
    "pattaya":      "linear-gradient(155deg,#C6A15E,#7C5A3A 58%,#332723)",
    "bangkok":      "linear-gradient(155deg,#C6A15E,#7A3E4A 55%,#241C22)",
    "kanchanaburi": "linear-gradient(155deg,#7E9A6E,#3E6B57 55%,#22322A)",
    "samet":        "linear-gradient(155deg,#5E907A,#2E6157 60%,#20342E)",
    "huahin":       "linear-gradient(155deg,#6E9B98,#2E5A5E 58%,#22343A)",
    "chiangmai":    "linear-gradient(155deg,#9A6E86,#5E3E5A 60%,#241E2A)",
    "khaoyai":      "linear-gradient(155deg,#6E9A72,#2E6147 55%,#1E2E24)",
}

def R(name, kind, area, nightly, rating):
    return {"name": name, "kind": kind, "area": area, "nightly": nightly, "rating": rating}

# id, title, region, days, rating, price, drive(h from BKK, or door-to-door by
# air when fly), fly, type, tags, blurb, stays, photo search terms ------------
DESTINATIONS = [
  # ---- original nine (Bangkok weekend getaways) ----
  dict(id="amphawa", title="Amphawa Floating Market", region="Samut Songkhram", days=2, rating=4.3, price=2900, drive=1.5, fly=False, type="Cultural",
       tags=["Floating market","Fireflies"], blurb="Canalside markets, a longtail firefly cruise and the Maeklong railway market.",
       stays=[R("Baan Amphawa Resort & Spa","Resort","Canalside",2800,4.3), R("Amphawa Na Non Hotel & Spa","Hotel","By the floating market",2400,4.4), R("Canalside homestay (representative)","Homestay","Amphawa canal",900,4.2)],
       terms=["Amphawa floating market","Amphawa canal Samut Songkhram","Maeklong railway market"]),
  dict(id="ayutthaya", title="Ayutthaya Temple Weekend", region="Ayutthaya", days=2, rating=4.6, price=3200, drive=1.5, fly=False, type="Cultural",
       tags=["Temples","Riverside"], blurb="The ruined temples of Siam's old capital, best by bicycle and at sunset.",
       stays=[R("Sala Ayutthaya","Hotel","Riverside, temple view",3600,4.7), R("Classic Kameo Hotel & Serviced Apartments","Residence","City centre",1600,4.3), R("iuDia on the river","Residence","Riverside",2200,4.5)],
       terms=["Wat Chaiwatthanaram Ayutthaya","Ayutthaya historical park temple","Wat Mahathat Ayutthaya"]),
  dict(id="pattaya", title="Pattaya Beach Break", region="Chonburi", days=2, rating=4.4, price=3900, drive=2, fly=False, type="Beach",
       tags=["Beach","Islands"], blurb="Two easy hours from Bangkok — beach clubs, Koh Larn day-trips and night markets.",
       stays=[R("Holiday Inn Pattaya","Resort","Pattaya Beach Road",3200,4.5), R("Hilton Pattaya","Hotel","Central Pattaya",4100,4.6), R("Amari Pattaya","Hotel","North Pattaya",2600,4.4)],
       terms=["Pattaya Beach aerial","Pattaya Beach Thailand","Pattaya city viewpoint"]),
  dict(id="bangkok", title="Bangkok Riverside Staycation", region="Bangkok", days=2, rating=4.5, price=4200, drive=0.3, fly=False, type="City",
       tags=["Riverside","Rooftops"], blurb="A weekend of temples, river ferries, rooftop bars and endless street food.",
       stays=[R("Chatrium Hotel Riverside Bangkok","Hotel","Charoen Krung, riverside",3400,4.6), R("Avani+ Riverside Bangkok","Hotel","Thonburi riverside",3900,4.6), R("Bangkok Marriott Marquis Queen's Park","Hotel","Sukhumvit",4200,4.6)],
       terms=["Wat Arun Bangkok","Bangkok Chao Phraya river skyline","Grand Palace Bangkok"]),
  dict(id="kanchanaburi", title="River Kwai & Erawan Falls", region="Kanchanaburi", days=3, rating=4.6, price=5500, drive=2.5, fly=False, type="Adventure",
       tags=["Waterfalls","History"], blurb="The Bridge on the River Kwai, the Death Railway, and Erawan's seven-tier falls.",
       stays=[R("The Float House River Kwai","Villa","Floating, on the River Kwai",6800,4.6), R("U Inchantree Kanchanaburi","Hotel","Riverside, near the bridge",2900,4.5), R("X2 River Kwai Resort","Resort","Riverfront",5600,4.5)],
       terms=["Bridge over the River Kwai Kanchanaburi","Erawan Falls Kanchanaburi","River Kwai Kanchanaburi"]),
  dict(id="samet", title="Koh Samet Island Escape", region="Rayong", days=3, rating=4.3, price=5800, drive=3.5, fly=False, type="Beach",
       tags=["White sand","Snorkelling"], blurb="The closest white-sand island to Bangkok — powder beaches and clear water.",
       stays=[R("Sai Kaew Beach Resort","Resort","Sai Kaew Beach",3400,4.3), R("Ao Prao Resort","Resort","Ao Prao (sunset side)",4200,4.4), R("Paradee Resort","Resort","Quiet south end",7800,4.6)],
       terms=["Sai Kaew Beach Ko Samet","Ko Samet beach","Koh Samet island Thailand"]),
  dict(id="huahin", title="Hua Hin Seaside Weekend", region="Prachuap Khiri Khan", days=3, rating=4.7, price=6500, drive=3, fly=False, type="Beach",
       tags=["Beach","Night markets"], blurb="A relaxed royal beach town — long sands, night markets and a water park.",
       stays=[R("Holiday Inn Resort Vana Nava Hua Hin","Resort","Near Vana Nava water park",4500,4.5), R("Centara Grand Beach Resort & Villas Hua Hin","Resort","On the beach",6200,4.6), R("InterContinental Hua Hin Resort","Resort","Beachfront",5400,4.7)],
       terms=["Hua Hin Railway Station","Hua Hin beach Thailand","Hua Hin Prachuap Khiri Khan"]),
  dict(id="chiangmai", title="Chiang Mai City & Temples", region="Chiang Mai", days=3, rating=4.7, price=7900, drive=2.5, fly=True, type="City",
       tags=["Temples","Mountains"], blurb="Old-city temples, Nimman cafés and Doi Suthep above the northern capital.",
       stays=[R("Shangri-La Chiang Mai","Hotel","Near the Night Bazaar",5200,4.7), R("U Nimman Chiang Mai","Hotel","Nimmanhaemin",3800,4.6), R("Anantara Chiang Mai Resort","Resort","Riverside",6900,4.7)],
       terms=["Wat Phra That Doi Suthep Chiang Mai","Wat Chedi Luang Chiang Mai","Chiang Mai old city temple"]),
  dict(id="khaoyai", title="Khao Yai Nature & Wineries", region="Nakhon Ratchasima", days=3, rating=4.8, price=8900, drive=2.5, fly=False, type="Adventure",
       tags=["National park","Vineyards"], blurb="Thailand's oldest national park, waterfalls and wine country, cool-air cafés.",
       stays=[R("InterContinental Khao Yai Resort","Resort","Pak Chong",9500,4.8), R("Kirimaya Golf Resort & Spa","Resort","By the national park",6400,4.5), R("Pool villa near Toscana (representative)","Villa","Khao Yai valley",3900,4.3)],
       terms=["Haew Suwat Waterfall Khao Yai","Khao Yai National Park viewpoint","Khao Yai National Park landscape"]),

  # ---- Central & near Bangkok ----
  dict(id="lopburi", title="Lopburi Monkey City & Sunflowers", region="Lopburi", days=2, rating=4.2, price=2600, drive=2, fly=False, type="Cultural",
       tags=["Khmer ruins","Monkeys"], blurb="Khmer-era prangs overrun by monkeys, and sunflower fields in the cool season.",
       stays=[R("Lopburi Inn Resort","Hotel","City edge",1500,4.1), R("Noom Guesthouse","Guesthouse","Old town",700,4.2), R("Baan Krua Nara (representative)","Homestay","Near Phra Prang Sam Yot",950,4.2)],
       terms=["Phra Prang Sam Yot Lopburi","Lopburi monkey temple","Lopburi sunflower field"]),

  # ---- East ----
  dict(id="kohchang", title="Koh Chang Rainforest & Beaches", region="Trat", days=3, rating=4.4, price=6800, drive=5, fly=False, type="Beach",
       tags=["Jungle","White Sand Beach"], blurb="Thailand's second-largest island — jungle waterfalls and long west-coast sands.",
       stays=[R("The Dewa Koh Chang","Resort","Klong Prao Beach",4200,4.4), R("Emerald Cove Koh Chang","Resort","Klong Prao",3800,4.4), R("Panviman Resort Koh Chang","Resort","Kai Bae",4600,4.5)],
       terms=["Koh Chang Thailand beach","White Sand Beach Koh Chang","Koh Chang island viewpoint"]),
  dict(id="kohkood", title="Koh Kood Pristine Island", region="Trat", days=3, rating=4.6, price=7900, drive=6, fly=False, type="Beach",
       tags=["Clear water","Waterfalls"], blurb="The far-eastern island — palm coves, clear water and near-empty beaches.",
       stays=[R("Soneva Kiri","Resort","Private, west coast",42000,4.9), R("Away Koh Kood","Resort","Ngamkho Beach",4300,4.5), R("The Beach Natural Resort Koh Kood","Resort","Bang Bao Bay",3600,4.4)],
       terms=["Koh Kood island beach","Ko Kut Thailand","Koh Kood waterfall"]),
  dict(id="chanthaburi", title="Chanthaburi Gems & Waterfalls", region="Chanthaburi", days=2, rating=4.3, price=3400, drive=3.5, fly=False, type="Cultural",
       tags=["Old town","Gem market"], blurb="A riverfront old town, Thailand's gem trade, and Namtok Phlio in the hills.",
       stays=[R("Maneechan Resort","Resort","Riverside",2200,4.3), R("K.P. Grand Hotel Chanthaburi","Hotel","City centre",1600,4.2), R("Chanthaboon riverside homestay (representative)","Homestay","Old town",1100,4.3)],
       terms=["Chanthaburi Cathedral","Chanthaburi old town riverfront","Namtok Phlio waterfall"]),

  # ---- North ----
  dict(id="chiangrai", title="Chiang Rai & the White Temple", region="Chiang Rai", days=3, rating=4.6, price=8200, drive=3, fly=True, type="Cultural",
       tags=["White Temple","Golden Triangle"], blurb="Wat Rong Khun's white temple, the Blue Temple and the Golden Triangle.",
       stays=[R("The Riverie by Katathani","Hotel","Kok River",4600,4.6), R("Le Meridien Chiang Rai Resort","Resort","Riverside",5200,4.6), R("Anantara Golden Triangle Elephant Camp","Resort","Golden Triangle",18000,4.8)],
       terms=["Wat Rong Khun White Temple Chiang Rai","Wat Rong Suea Ten Blue Temple","Chiang Rai Singha Park"]),
  dict(id="pai", title="Pai Mountain Retreat", region="Mae Hong Son", days=3, rating=4.5, price=6900, drive=4, fly=True, type="Adventure",
       tags=["Canyon","Hot springs"], blurb="Hairpin roads up to a hippie valley — canyon sunsets, hot springs and bamboo bridges.",
       stays=[R("Reverie Siam Resort","Resort","Pai River valley",4200,4.6), R("Pai Island Resort","Resort","By the river",2600,4.4), R("Pai Village Boutique Resort","Resort","Walking street",2100,4.4)],
       terms=["Pai Canyon Mae Hong Son","Pai valley Thailand","Pai bamboo bridge Boon Ko Ku So"]),
  dict(id="nan", title="Nan Old Town & Valleys", region="Nan", days=3, rating=4.5, price=5600, drive=3, fly=True, type="Cultural",
       tags=["Murals","Slow travel"], blurb="A quiet northern valley — the Wat Phumin murals and terraced hills at Doi Samer Dao.",
       stays=[R("Pukha Nanfa Hotel","Hotel","Old town",2400,4.5), R("Nan Boutique Hotel","Hotel","Town centre",1500,4.3), R("Nan riverside homestay (representative)","Homestay","By the Nan River",1000,4.3)],
       terms=["Wat Phumin Nan","Wat Phra That Khao Noi Nan","Nan province Thailand landscape"]),
  dict(id="sukhothai", title="Sukhothai Historical Park", region="Sukhothai", days=2, rating=4.7, price=5200, drive=3, fly=True, type="Cultural",
       tags=["World Heritage","Ruins"], blurb="The first Thai kingdom's capital — serene ruins and lotus ponds, magic at dawn.",
       stays=[R("Sriwilai Sukhothai","Resort","By the old city",5200,4.7), R("Legendha Sukhothai Resort","Resort","Historical park",2800,4.5), R("Le Charme Sukhothai Resort","Resort","Near the park",2100,4.4)],
       terms=["Sukhothai Historical Park Wat Mahathat","Wat Si Chum Sukhothai","Sukhothai Buddha statue"]),

  # ---- Northeast (Isan) ----
  dict(id="ubon", title="Ubon Ratchathani & Pha Taem", region="Ubon Ratchathani", days=3, rating=4.4, price=6400, drive=3, fly=True, type="Adventure",
       tags=["Grand Canyon","Cliff art"], blurb="Sam Phan Bok's rocky 'grand canyon' of the Mekong and Pha Taem's prehistoric cliff paintings.",
       stays=[R("Sunee Grand Hotel Ubon","Hotel","City centre",1900,4.3), R("Tohsang Khongjiam Resort","Resort","Mekong at Khong Chiam",3200,4.4), R("The Outside Resort (representative)","Resort","Near Pha Taem",1800,4.2)],
       terms=["Sam Phan Bok Ubon Ratchathani","Pha Taem National Park","Ubon Ratchathani candle festival"]),
  dict(id="chiangkhan", title="Chiang Khan Riverside", region="Loei", days=2, rating=4.5, price=4800, drive=3, fly=True, type="Cultural",
       tags=["Mekong","Walking street"], blurb="A wooden old town on the Mekong — morning alms, a lantern-lit walking street and Phu Thok mist.",
       stays=[R("Chiang Khan Hill Resort","Resort","Kaeng Khut Khu",2200,4.4), R("Chiangkhan River Mountain Resort","Resort","Riverside",2600,4.5), R("Loei riverside guesthouse (representative)","Guesthouse","Walking street",1200,4.3)],
       terms=["Chiang Khan Walking Street Loei","Chiang Khan Mekong river","Phu Thok Chiang Khan"]),

  # ---- Gulf islands (via Surat Thani) ----
  dict(id="samui", title="Koh Samui Island Luxe", region="Surat Thani", days=3, rating=4.6, price=9800, drive=2, fly=True, type="Beach",
       tags=["Palm beaches","Big Buddha"], blurb="Chaweng's palm-lined sands, the Big Buddha and hilltop infinity pools.",
       stays=[R("Banyan Tree Samui","Resort","Lamai, private bay",14000,4.8), R("Santiburi Koh Samui","Resort","Mae Nam Beach",8600,4.7), R("Anantara Bophut Koh Samui","Resort","Bophut Beach",7200,4.6)],
       terms=["Koh Samui beach Thailand","Big Buddha Koh Samui","Chaweng Beach Samui"]),
  dict(id="phangan", title="Koh Pha Ngan Beaches", region="Surat Thani", days=3, rating=4.4, price=7600, drive=3, fly=True, type="Beach",
       tags=["Secret coves","Waterfalls"], blurb="Beyond the Full Moon Party — quiet northern coves, jungle waterfalls and viewpoints.",
       stays=[R("Anantara Rasananda Koh Phangan","Resort","Thong Nai Pan Noi",9800,4.7), R("SANTHIYA Koh Phangan Resort & Spa","Resort","Thong Nai Pan",7400,4.6), R("Buri Rasa Village Koh Phangan","Resort","Baan Tai",4200,4.4)],
       terms=["Koh Phangan beach","Than Sadet waterfall Koh Phangan","Koh Phangan viewpoint"]),
  dict(id="kohtao", title="Koh Tao Diving Weekend", region="Surat Thani", days=3, rating=4.5, price=6800, drive=4, fly=True, type="Adventure",
       tags=["Diving","Koh Nang Yuan"], blurb="Thailand's dive-school island — easy reefs, the Koh Nang Yuan viewpoint and sunset bays.",
       stays=[R("Koh Tao Cabana","Resort","Sairee, headland",4600,4.4), R("Jamahkiri Resort & Spa","Resort","Thian Og Bay",5200,4.5), R("Charm Churee Villa","Resort","Jansom Bay",3600,4.3)],
       terms=["Koh Nang Yuan","Koh Tao island viewpoint","Koh Tao beach Thailand"]),

  # ---- Andaman & South ----
  dict(id="khaosok", title="Khao Sok Rainforest & Lake", region="Surat Thani", days=3, rating=4.7, price=7200, drive=3, fly=True, type="Adventure",
       tags=["Cheow Lan Lake","Rainforest"], blurb="Limestone karsts over emerald Cheow Lan Lake, floating bungalows and ancient rainforest.",
       stays=[R("Elephant Hills","Camp","Luxury tented camp",12000,4.8), R("500 Rai Floating Resort","Resort","Cheow Lan Lake",5200,4.6), R("Khao Sok Rainforest Resort (representative)","Resort","Park entrance",2200,4.3)],
       terms=["Khao Sok National Park Cheow Lan Lake","Khao Sok limestone","Khao Sok rainforest"]),
  dict(id="phuket", title="Phuket Beaches & Old Town", region="Phuket", days=3, rating=4.5, price=8900, drive=2, fly=True, type="Beach",
       tags=["Sino-Portuguese","Beach clubs"], blurb="Andaman beaches, Sino-Portuguese old town lanes and clifftop sunset bars.",
       stays=[R("The Nai Harn","Resort","Nai Harn Beach",9800,4.7), R("Rosewood Phuket","Resort","Emerald Bay",18000,4.8), R("Amari Phuket","Resort","Patong headland",5200,4.5)],
       terms=["Phuket Old Town","Kata Beach Phuket","Phuket Big Buddha viewpoint"]),
  dict(id="krabi", title="Krabi & Railay Cliffs", region="Krabi", days=3, rating=4.7, price=7800, drive=2.5, fly=True, type="Beach",
       tags=["Limestone","Railay"], blurb="Boat-only Railay, towering limestone, Phra Nang cave beach and island-hopping.",
       stays=[R("Rayavadee","Resort","Railay / Phra Nang",22000,4.8), R("Dusit Thani Krabi Beach Resort","Resort","Klong Muang Beach",6200,4.6), R("Sofitel Krabi Phokeethra","Resort","Klong Muang",5400,4.6)],
       terms=["Railay Beach Krabi","Phra Nang Beach Krabi","Krabi Thailand limestone"]),
  dict(id="phiphi", title="Koh Phi Phi Islands", region="Krabi", days=3, rating=4.5, price=8600, drive=3.5, fly=True, type="Beach",
       tags=["Maya Bay","Viewpoint"], blurb="The famous viewpoint, Maya Bay and turquoise bays best seen by longtail at dawn.",
       stays=[R("Phi Phi Island Village Beach Resort","Resort","Loh Ba Kao Bay",9200,4.6), R("SAii Phi Phi Island Village","Resort","Loh Ba Kao",8800,4.6), R("Zeavola Resort","Resort","Laem Tong",10500,4.7)],
       terms=["Koh Phi Phi viewpoint","Maya Bay Phi Phi","Phi Phi islands Thailand"]),
  dict(id="phangnga", title="Phang Nga Bay & James Bond Island", region="Phang Nga", days=3, rating=4.6, price=7200, drive=3, fly=True, type="Adventure",
       tags=["Sea caves","Kayaking"], blurb="Sheer karsts rising from the bay — sea-cave kayaking, Koh Panyee and James Bond Island.",
       stays=[R("Aleenta Phuket-Phang Nga Resort","Resort","Natai Beach",8800,4.7), R("The Sarojin","Resort","Khao Lak edge",9200,4.7), R("Phang Nga bay homestay (representative)","Homestay","Near the pier",1400,4.3)],
       terms=["James Bond Island Phang Nga","Phang Nga Bay Thailand","Koh Panyee"]),
  dict(id="kholanta", title="Koh Lanta Slow Islands", region="Krabi", days=3, rating=4.5, price=7400, drive=4, fly=True, type="Beach",
       tags=["Long beaches","Old town"], blurb="Long, laid-back west-coast beaches, a stilted old town and sunset from the lighthouse cape.",
       stays=[R("Pimalai Resort & Spa","Resort","Ba Kantiang Beach",11000,4.7), R("Layana Resort & Spa","Resort","Long Beach (adults-only)",8600,4.7), R("Costa Lanta","Resort","Klong Dao",4200,4.4)],
       terms=["Koh Lanta beach Thailand","Koh Lanta old town","Mu Ko Lanta lighthouse"]),
  dict(id="khaolak", title="Khao Lak & Similan Diving", region="Phang Nga", days=3, rating=4.5, price=8100, drive=3.5, fly=True, type="Beach",
       tags=["Similans","Quiet sands"], blurb="Long quiet beaches and the launch point for the Similan Islands' world-class diving.",
       stays=[R("JW Marriott Khao Lak Resort & Spa","Resort","Khuk Khak Beach",8200,4.7), R("The Sarojin","Resort","Pakarang Beach",9200,4.8), R("Casa de La Flora","Resort","Khuk Khak",7600,4.6)],
       terms=["Khao Lak beach Thailand","Similan Islands","Khao Lak sunset"]),
  dict(id="lipe", title="Koh Lipe Andaman Gem", region="Satun", days=3, rating=4.6, price=9200, drive=5, fly=True, type="Beach",
       tags=["Clearest water","Snorkelling"], blurb="The 'Maldives of Thailand' — powder sand and glass-clear water at the far Andaman edge.",
       stays=[R("Idyllic Concept Resort","Resort","Sunrise Beach",6800,4.5), R("Serendipity Beach Resort","Resort","Quiet north cape",7600,4.6), R("Castaway Resort Koh Lipe","Resort","Sunrise Beach",5200,4.5)],
       terms=["Koh Lipe beach Thailand","Sunrise Beach Koh Lipe","Koh Lipe Andaman"]),
]

# id -> broad region zone (for the region filter) ----------------------------
ZONE = {
    "chiangmai": "North", "chiangrai": "North", "pai": "North", "nan": "North", "sukhothai": "North",
    "khaoyai": "Isan", "ubon": "Isan", "chiangkhan": "Isan",
    "bangkok": "Central", "ayutthaya": "Central", "amphawa": "Central", "kanchanaburi": "Central", "lopburi": "Central",
    "pattaya": "East", "samet": "East", "kohchang": "East", "kohkood": "East", "chanthaburi": "East",
    "huahin": "Gulf", "samui": "Gulf", "phangan": "Gulf", "kohtao": "Gulf",
    "phuket": "Andaman", "krabi": "Andaman", "phiphi": "Andaman", "phangnga": "Andaman",
    "kholanta": "Andaman", "khaolak": "Andaman", "lipe": "Andaman", "khaosok": "Andaman",
}

# ------------------------------------------------------------------ derive ----
ORIG = {"amphawa","ayutthaya","pattaya","bangkok","kanchanaburi","samet","huahin","chiangmai","khaoyai"}
ids = [d["id"] for d in DESTINATIONS]
assert len(ids) == len(set(ids)), "duplicate id"
assert all(d["id"] in ZONE for d in DESTINATIONS), "every destination needs a ZONE"

grad = {}
for i, d in enumerate(DESTINATIONS):
    grad[d["id"]] = FIXED.get(d["id"]) or auto_grad(d["type"], i)

def js_str(s): return '"' + s.replace('"', '\\"') + '"'

def trip_obj(d):
    stays = ",\n        ".join(
        '{ name: %s, kind: %s, area: %s, nightly: %d, rating: %s }' % (
            js_str(s["name"]), js_str(s["kind"]), js_str(s["area"]), s["nightly"], s["rating"])
        for s in d["stays"])
    tags = "[" + ", ".join(js_str(t) for t in d["tags"]) + "]"
    return (
        '    { id: %s, title: %s, country: "Thailand", region: %s, zone: %s, days: %d, rating: %s, price: %d, type: %s, grad: %s, tags: %s, blurb: %s,\n'
        '      stays: [\n        %s\n      ] }'
    ) % (js_str(d["id"]), js_str(d["title"]), js_str(d["region"]), js_str(ZONE[d["id"]]), d["days"], d["rating"], d["price"],
         js_str(d["type"]), js_str(d["id"]), tags, js_str(d["blurb"]), stays)

trips_js = "  GOGO.trips = [\n" + ",\n".join(trip_obj(d) for d in DESTINATIONS) + "\n  ];"

grad_js = "  GOGO.grad = {\n" + ",\n".join(
    '    %s: %s' % (d["id"], js_str(grad[d["id"]])) for d in DESTINATIONS) + "\n  };"

drive_js = "  var DRIVE = { " + ", ".join("%s: %s" % (d["id"], d["drive"]) for d in DESTINATIONS) + " };"
fly_js   = "  var FLY = { " + ", ".join("%s: 1" % d["id"] for d in DESTINATIONS if d["fly"]) + " };"

ph_css = "\n".join(
    ".ph--%s { background: url('../img/%s.jpg') center/cover no-repeat, %s; }" % (d["id"], d["id"], grad[d["id"]])
    for d in DESTINATIONS)

queries_py = "QUERIES = {\n" + "\n".join(
    '    "%s":%s[%s],' % (d["id"], " " * max(1, 14 - len(d["id"])), ", ".join('"%s"' % t for t in d["terms"]))
    for d in DESTINATIONS) + "\n}"

# ------------------------------------------------------------------ patch -----
def sub1(text, pattern, repl, label, flags=re.S):
    new, n = re.subn(pattern, lambda m: repl, text, flags=flags)
    assert n == 1, f"{label}: expected 1 replacement, got {n}"
    return new

# data.js
dpath = ROOT / "assets/js/data.js"
data = dpath.read_text()
data = sub1(data, r"  GOGO\.grad = \{.*?\n  \};", grad_js, "grad")
data = sub1(data, r"  GOGO\.trips = \[.*?\n  \];", trips_js, "trips")
# these two are idempotent: they match either the pristine or already-patched form
data = sub1(data, r"  var DRIVE = \{[^}]*\};(?:\n  var FLY = \{[^}]*\};)?", drive_js + "\n" + fly_js, "DRIVE")
data = sub1(data, r't\.fly = (?:\(t\.id === "chiangmai"\)|FLY\[t\.id\] === 1);', "t.fly = FLY[t.id] === 1;", "fly", flags=0)
# mute the two bright fallback-gallery gradients so new trips stay on-theme
data = data.replace('{ bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "On the trip" }',
                    '{ bg: "linear-gradient(155deg,#B98F4C,#6E3A44 55%,#241C22)", cap: "On the trip" }')
data = data.replace('{ bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Local life" }',
                    '{ bg: "linear-gradient(155deg,#6E9B98,#2E5A5E 58%,#22343A)", cap: "Local life" }')
dpath.write_text(data)

# styles.css
spath = ROOT / "assets/css/styles.css"
styles = spath.read_text()
# match the whole consecutive run of .ph--<id> rules (order-independent, idempotent)
styles = sub1(styles, r"(?:\.ph--[a-z]+ \{[^}]*\}\n)+", ph_css + "\n", "ph-css")
spath.write_text(styles)

# fetch-photos.py
fpath = ROOT / "assets/img/fetch-photos.py"
fetch = fpath.read_text()
fetch = sub1(fetch, r"QUERIES = \{.*?\n\}", queries_py, "queries")
fpath.write_text(fetch)

print("Destinations:", len(DESTINATIONS))
print("  by type:", {t: sum(1 for d in DESTINATIONS if d["type"] == t) for t in ["Beach","City","Cultural","Adventure"]})
print("  fly:", sum(1 for d in DESTINATIONS if d["fly"]), " drive:", sum(1 for d in DESTINATIONS if not d["fly"]))
print("Patched data.js, styles.css, fetch-photos.py")
