/* ==========================================================================
   GOGO! Travel — shared data + helpers  (window.GOGO)
   Thailand weekend getaways. Destinations and hotel names are REAL places;
   prices, ratings and availability are REPRESENTATIVE SAMPLE values for the
   demo — confirm live figures via an Agoda / Trip.com partner API before use.
   ========================================================================== */
(function () {
  "use strict";
  var GOGO = (window.GOGO = window.GOGO || {});

  /* ---- money (Thai baht) ------------------------------------------------- */
  GOGO.money = function (n) { return "฿" + Math.round(n).toLocaleString(); };

  /* ---- gradient "photo" strings (mirror the .ph--* CSS classes) ---------- */
  GOGO.grad = {
    amphawa: "linear-gradient(155deg,#8A9A6E,#4E6B57 55%,#262E28)",
    ayutthaya: "linear-gradient(155deg,#C0904E,#7A3E4A 55%,#2E2026)",
    pattaya: "linear-gradient(155deg,#C6A15E,#7C5A3A 58%,#332723)",
    bangkok: "linear-gradient(155deg,#C6A15E,#7A3E4A 55%,#241C22)",
    kanchanaburi: "linear-gradient(155deg,#7E9A6E,#3E6B57 55%,#22322A)",
    samet: "linear-gradient(155deg,#5E907A,#2E6157 60%,#20342E)",
    huahin: "linear-gradient(155deg,#6E9B98,#2E5A5E 58%,#22343A)",
    chiangmai: "linear-gradient(155deg,#9A6E86,#5E3E5A 60%,#241E2A)",
    khaoyai: "linear-gradient(155deg,#6E9A72,#2E6147 55%,#1E2E24)",
    lopburi: "linear-gradient(155deg,#BFA05A,#773139 56%,#331920)",
    kohchang: "linear-gradient(155deg,#67A7AD,#326976 58%,#1D3639)",
    kohkood: "linear-gradient(155deg,#67ADA8,#327476 58%,#1D3939)",
    chanthaburi: "linear-gradient(155deg,#BF9B5A,#77313C 56%,#331920)",
    chiangrai: "linear-gradient(155deg,#BF955A,#77313F 56%,#331920)",
    pai: "linear-gradient(155deg,#59A678,#316850 55%,#1B3226)",
    nan: "linear-gradient(155deg,#BF965A,#77313E 56%,#331920)",
    sukhothai: "linear-gradient(155deg,#BF9E5A,#77313A 56%,#331920)",
    ubon: "linear-gradient(155deg,#59A66F,#31684A 55%,#1B3226)",
    chiangkhan: "linear-gradient(155deg,#BF9F5A,#77313A 56%,#331920)",
    samui: "linear-gradient(155deg,#67A8AD,#326B76 58%,#1D3639)",
    phangan: "linear-gradient(155deg,#67ADA7,#327576 58%,#1D3938)",
    kohtao: "linear-gradient(155deg,#59A674,#31684D 55%,#1B3226)",
    khaosok: "linear-gradient(155deg,#59A669,#316845 55%,#1B3226)",
    phuket: "linear-gradient(155deg,#67A4AD,#326676 58%,#1D3439)",
    krabi: "linear-gradient(155deg,#67ADAC,#327076 58%,#1D3839)",
    phiphi: "linear-gradient(155deg,#67A1AD,#326476 58%,#1D3339)",
    phangnga: "linear-gradient(155deg,#59A66E,#316849 55%,#1B3226)",
    kholanta: "linear-gradient(155deg,#679FAD,#326276 58%,#1D3239)",
    khaolak: "linear-gradient(155deg,#67A9AD,#326C76 58%,#1D3639)",
    lipe: "linear-gradient(155deg,#679CAD,#325F76 58%,#1D3139)"
  };
  GOGO.gradCss = function (name) { return GOGO.grad[name] || GOGO.grad.pattaya; };

  /* ---- catalogue (weekend getaways from Bangkok) ------------------------- */
  GOGO.trips = [
    { id: "amphawa", title: "Amphawa Floating Market", country: "Thailand", region: "Samut Songkhram", days: 2, rating: 4.3, price: 2900, type: "Cultural", grad: "amphawa", tags: ["Floating market", "Fireflies"], blurb: "Canalside markets, a longtail firefly cruise and the Maeklong railway market.",
      stays: [
        { name: "Baan Amphawa Resort & Spa", kind: "Resort", area: "Canalside", nightly: 2800, rating: 4.3 },
        { name: "Amphawa Na Non Hotel & Spa", kind: "Hotel", area: "By the floating market", nightly: 2400, rating: 4.4 },
        { name: "Canalside homestay (representative)", kind: "Homestay", area: "Amphawa canal", nightly: 900, rating: 4.2 }
      ] },
    { id: "ayutthaya", title: "Ayutthaya Temple Weekend", country: "Thailand", region: "Ayutthaya", days: 2, rating: 4.6, price: 3200, type: "Cultural", grad: "ayutthaya", tags: ["Temples", "Riverside"], blurb: "The ruined temples of Siam's old capital, best by bicycle and at sunset.",
      stays: [
        { name: "Sala Ayutthaya", kind: "Hotel", area: "Riverside, temple view", nightly: 3600, rating: 4.7 },
        { name: "Classic Kameo Hotel & Serviced Apartments", kind: "Residence", area: "City centre", nightly: 1600, rating: 4.3 },
        { name: "iuDia on the river", kind: "Residence", area: "Riverside", nightly: 2200, rating: 4.5 }
      ] },
    { id: "pattaya", title: "Pattaya Beach Break", country: "Thailand", region: "Chonburi", days: 2, rating: 4.4, price: 3900, type: "Beach", grad: "pattaya", tags: ["Beach", "Islands"], blurb: "Two easy hours from Bangkok — beach clubs, Koh Larn day-trips and night markets.",
      stays: [
        { name: "Holiday Inn Pattaya", kind: "Resort", area: "Pattaya Beach Road", nightly: 3200, rating: 4.5 },
        { name: "Hilton Pattaya", kind: "Hotel", area: "Central Pattaya", nightly: 4100, rating: 4.6 },
        { name: "Amari Pattaya", kind: "Hotel", area: "North Pattaya", nightly: 2600, rating: 4.4 }
      ] },
    { id: "bangkok", title: "Bangkok Riverside Staycation", country: "Thailand", region: "Bangkok", days: 2, rating: 4.5, price: 4200, type: "City", grad: "bangkok", tags: ["Riverside", "Rooftops"], blurb: "A weekend of temples, river ferries, rooftop bars and endless street food.",
      stays: [
        { name: "Chatrium Hotel Riverside Bangkok", kind: "Hotel", area: "Charoen Krung, riverside", nightly: 3400, rating: 4.6 },
        { name: "Avani+ Riverside Bangkok", kind: "Hotel", area: "Thonburi riverside", nightly: 3900, rating: 4.6 },
        { name: "Bangkok Marriott Marquis Queen's Park", kind: "Hotel", area: "Sukhumvit", nightly: 4200, rating: 4.6 }
      ] },
    { id: "kanchanaburi", title: "River Kwai & Erawan Falls", country: "Thailand", region: "Kanchanaburi", days: 3, rating: 4.6, price: 5500, type: "Adventure", grad: "kanchanaburi", tags: ["Waterfalls", "History"], blurb: "The Bridge on the River Kwai, the Death Railway, and Erawan's seven-tier falls.",
      stays: [
        { name: "The Float House River Kwai", kind: "Villa", area: "Floating, on the River Kwai", nightly: 6800, rating: 4.6 },
        { name: "U Inchantree Kanchanaburi", kind: "Hotel", area: "Riverside, near the bridge", nightly: 2900, rating: 4.5 },
        { name: "X2 River Kwai Resort", kind: "Resort", area: "Riverfront", nightly: 5600, rating: 4.5 }
      ] },
    { id: "samet", title: "Koh Samet Island Escape", country: "Thailand", region: "Rayong", days: 3, rating: 4.3, price: 5800, type: "Beach", grad: "samet", tags: ["White sand", "Snorkelling"], blurb: "The closest white-sand island to Bangkok — powder beaches and clear water.",
      stays: [
        { name: "Sai Kaew Beach Resort", kind: "Resort", area: "Sai Kaew Beach", nightly: 3400, rating: 4.3 },
        { name: "Ao Prao Resort", kind: "Resort", area: "Ao Prao (sunset side)", nightly: 4200, rating: 4.4 },
        { name: "Paradee Resort", kind: "Resort", area: "Quiet south end", nightly: 7800, rating: 4.6 }
      ] },
    { id: "huahin", title: "Hua Hin Seaside Weekend", country: "Thailand", region: "Prachuap Khiri Khan", days: 3, rating: 4.7, price: 6500, type: "Beach", grad: "huahin", tags: ["Beach", "Night markets"], blurb: "A relaxed royal beach town — long sands, night markets and a water park.",
      stays: [
        { name: "Holiday Inn Resort Vana Nava Hua Hin", kind: "Resort", area: "Near Vana Nava water park", nightly: 4500, rating: 4.5 },
        { name: "Centara Grand Beach Resort & Villas Hua Hin", kind: "Resort", area: "On the beach", nightly: 6200, rating: 4.6 },
        { name: "InterContinental Hua Hin Resort", kind: "Resort", area: "Beachfront", nightly: 5400, rating: 4.7 }
      ] },
    { id: "chiangmai", title: "Chiang Mai City & Temples", country: "Thailand", region: "Chiang Mai", days: 3, rating: 4.7, price: 7900, type: "City", grad: "chiangmai", tags: ["Temples", "Mountains"], blurb: "Old-city temples, Nimman cafés and Doi Suthep above the northern capital.",
      stays: [
        { name: "Shangri-La Chiang Mai", kind: "Hotel", area: "Near the Night Bazaar", nightly: 5200, rating: 4.7 },
        { name: "U Nimman Chiang Mai", kind: "Hotel", area: "Nimmanhaemin", nightly: 3800, rating: 4.6 },
        { name: "Anantara Chiang Mai Resort", kind: "Resort", area: "Riverside", nightly: 6900, rating: 4.7 }
      ] },
    { id: "khaoyai", title: "Khao Yai Nature & Wineries", country: "Thailand", region: "Nakhon Ratchasima", days: 3, rating: 4.8, price: 8900, type: "Adventure", grad: "khaoyai", tags: ["National park", "Vineyards"], blurb: "Thailand's oldest national park, waterfalls and wine country, cool-air cafés.",
      stays: [
        { name: "InterContinental Khao Yai Resort", kind: "Resort", area: "Pak Chong", nightly: 9500, rating: 4.8 },
        { name: "Kirimaya Golf Resort & Spa", kind: "Resort", area: "By the national park", nightly: 6400, rating: 4.5 },
        { name: "Pool villa near Toscana (representative)", kind: "Villa", area: "Khao Yai valley", nightly: 3900, rating: 4.3 }
      ] },
    { id: "lopburi", title: "Lopburi Monkey City & Sunflowers", country: "Thailand", region: "Lopburi", days: 2, rating: 4.2, price: 2600, type: "Cultural", grad: "lopburi", tags: ["Khmer ruins", "Monkeys"], blurb: "Khmer-era prangs overrun by monkeys, and sunflower fields in the cool season.",
      stays: [
        { name: "Lopburi Inn Resort", kind: "Hotel", area: "City edge", nightly: 1500, rating: 4.1 },
        { name: "Noom Guesthouse", kind: "Guesthouse", area: "Old town", nightly: 700, rating: 4.2 },
        { name: "Baan Krua Nara (representative)", kind: "Homestay", area: "Near Phra Prang Sam Yot", nightly: 950, rating: 4.2 }
      ] },
    { id: "kohchang", title: "Koh Chang Rainforest & Beaches", country: "Thailand", region: "Trat", days: 3, rating: 4.4, price: 6800, type: "Beach", grad: "kohchang", tags: ["Jungle", "White Sand Beach"], blurb: "Thailand's second-largest island — jungle waterfalls and long west-coast sands.",
      stays: [
        { name: "The Dewa Koh Chang", kind: "Resort", area: "Klong Prao Beach", nightly: 4200, rating: 4.4 },
        { name: "Emerald Cove Koh Chang", kind: "Resort", area: "Klong Prao", nightly: 3800, rating: 4.4 },
        { name: "Panviman Resort Koh Chang", kind: "Resort", area: "Kai Bae", nightly: 4600, rating: 4.5 }
      ] },
    { id: "kohkood", title: "Koh Kood Pristine Island", country: "Thailand", region: "Trat", days: 3, rating: 4.6, price: 7900, type: "Beach", grad: "kohkood", tags: ["Clear water", "Waterfalls"], blurb: "The far-eastern island — palm coves, clear water and near-empty beaches.",
      stays: [
        { name: "Soneva Kiri", kind: "Resort", area: "Private, west coast", nightly: 42000, rating: 4.9 },
        { name: "Away Koh Kood", kind: "Resort", area: "Ngamkho Beach", nightly: 4300, rating: 4.5 },
        { name: "The Beach Natural Resort Koh Kood", kind: "Resort", area: "Bang Bao Bay", nightly: 3600, rating: 4.4 }
      ] },
    { id: "chanthaburi", title: "Chanthaburi Gems & Waterfalls", country: "Thailand", region: "Chanthaburi", days: 2, rating: 4.3, price: 3400, type: "Cultural", grad: "chanthaburi", tags: ["Old town", "Gem market"], blurb: "A riverfront old town, Thailand's gem trade, and Namtok Phlio in the hills.",
      stays: [
        { name: "Maneechan Resort", kind: "Resort", area: "Riverside", nightly: 2200, rating: 4.3 },
        { name: "K.P. Grand Hotel Chanthaburi", kind: "Hotel", area: "City centre", nightly: 1600, rating: 4.2 },
        { name: "Chanthaboon riverside homestay (representative)", kind: "Homestay", area: "Old town", nightly: 1100, rating: 4.3 }
      ] },
    { id: "chiangrai", title: "Chiang Rai & the White Temple", country: "Thailand", region: "Chiang Rai", days: 3, rating: 4.6, price: 8200, type: "Cultural", grad: "chiangrai", tags: ["White Temple", "Golden Triangle"], blurb: "Wat Rong Khun's white temple, the Blue Temple and the Golden Triangle.",
      stays: [
        { name: "The Riverie by Katathani", kind: "Hotel", area: "Kok River", nightly: 4600, rating: 4.6 },
        { name: "Le Meridien Chiang Rai Resort", kind: "Resort", area: "Riverside", nightly: 5200, rating: 4.6 },
        { name: "Anantara Golden Triangle Elephant Camp", kind: "Resort", area: "Golden Triangle", nightly: 18000, rating: 4.8 }
      ] },
    { id: "pai", title: "Pai Mountain Retreat", country: "Thailand", region: "Mae Hong Son", days: 3, rating: 4.5, price: 6900, type: "Adventure", grad: "pai", tags: ["Canyon", "Hot springs"], blurb: "Hairpin roads up to a hippie valley — canyon sunsets, hot springs and bamboo bridges.",
      stays: [
        { name: "Reverie Siam Resort", kind: "Resort", area: "Pai River valley", nightly: 4200, rating: 4.6 },
        { name: "Pai Island Resort", kind: "Resort", area: "By the river", nightly: 2600, rating: 4.4 },
        { name: "Pai Village Boutique Resort", kind: "Resort", area: "Walking street", nightly: 2100, rating: 4.4 }
      ] },
    { id: "nan", title: "Nan Old Town & Valleys", country: "Thailand", region: "Nan", days: 3, rating: 4.5, price: 5600, type: "Cultural", grad: "nan", tags: ["Murals", "Slow travel"], blurb: "A quiet northern valley — the Wat Phumin murals and terraced hills at Doi Samer Dao.",
      stays: [
        { name: "Pukha Nanfa Hotel", kind: "Hotel", area: "Old town", nightly: 2400, rating: 4.5 },
        { name: "Nan Boutique Hotel", kind: "Hotel", area: "Town centre", nightly: 1500, rating: 4.3 },
        { name: "Nan riverside homestay (representative)", kind: "Homestay", area: "By the Nan River", nightly: 1000, rating: 4.3 }
      ] },
    { id: "sukhothai", title: "Sukhothai Historical Park", country: "Thailand", region: "Sukhothai", days: 2, rating: 4.7, price: 5200, type: "Cultural", grad: "sukhothai", tags: ["World Heritage", "Ruins"], blurb: "The first Thai kingdom's capital — serene ruins and lotus ponds, magic at dawn.",
      stays: [
        { name: "Sriwilai Sukhothai", kind: "Resort", area: "By the old city", nightly: 5200, rating: 4.7 },
        { name: "Legendha Sukhothai Resort", kind: "Resort", area: "Historical park", nightly: 2800, rating: 4.5 },
        { name: "Le Charme Sukhothai Resort", kind: "Resort", area: "Near the park", nightly: 2100, rating: 4.4 }
      ] },
    { id: "ubon", title: "Ubon Ratchathani & Pha Taem", country: "Thailand", region: "Ubon Ratchathani", days: 3, rating: 4.4, price: 6400, type: "Adventure", grad: "ubon", tags: ["Grand Canyon", "Cliff art"], blurb: "Sam Phan Bok's rocky 'grand canyon' of the Mekong and Pha Taem's prehistoric cliff paintings.",
      stays: [
        { name: "Sunee Grand Hotel Ubon", kind: "Hotel", area: "City centre", nightly: 1900, rating: 4.3 },
        { name: "Tohsang Khongjiam Resort", kind: "Resort", area: "Mekong at Khong Chiam", nightly: 3200, rating: 4.4 },
        { name: "The Outside Resort (representative)", kind: "Resort", area: "Near Pha Taem", nightly: 1800, rating: 4.2 }
      ] },
    { id: "chiangkhan", title: "Chiang Khan Riverside", country: "Thailand", region: "Loei", days: 2, rating: 4.5, price: 4800, type: "Cultural", grad: "chiangkhan", tags: ["Mekong", "Walking street"], blurb: "A wooden old town on the Mekong — morning alms, a lantern-lit walking street and Phu Thok mist.",
      stays: [
        { name: "Chiang Khan Hill Resort", kind: "Resort", area: "Kaeng Khut Khu", nightly: 2200, rating: 4.4 },
        { name: "Chiangkhan River Mountain Resort", kind: "Resort", area: "Riverside", nightly: 2600, rating: 4.5 },
        { name: "Loei riverside guesthouse (representative)", kind: "Guesthouse", area: "Walking street", nightly: 1200, rating: 4.3 }
      ] },
    { id: "samui", title: "Koh Samui Island Luxe", country: "Thailand", region: "Surat Thani", days: 3, rating: 4.6, price: 9800, type: "Beach", grad: "samui", tags: ["Palm beaches", "Big Buddha"], blurb: "Chaweng's palm-lined sands, the Big Buddha and hilltop infinity pools.",
      stays: [
        { name: "Banyan Tree Samui", kind: "Resort", area: "Lamai, private bay", nightly: 14000, rating: 4.8 },
        { name: "Santiburi Koh Samui", kind: "Resort", area: "Mae Nam Beach", nightly: 8600, rating: 4.7 },
        { name: "Anantara Bophut Koh Samui", kind: "Resort", area: "Bophut Beach", nightly: 7200, rating: 4.6 }
      ] },
    { id: "phangan", title: "Koh Pha Ngan Beaches", country: "Thailand", region: "Surat Thani", days: 3, rating: 4.4, price: 7600, type: "Beach", grad: "phangan", tags: ["Secret coves", "Waterfalls"], blurb: "Beyond the Full Moon Party — quiet northern coves, jungle waterfalls and viewpoints.",
      stays: [
        { name: "Anantara Rasananda Koh Phangan", kind: "Resort", area: "Thong Nai Pan Noi", nightly: 9800, rating: 4.7 },
        { name: "SANTHIYA Koh Phangan Resort & Spa", kind: "Resort", area: "Thong Nai Pan", nightly: 7400, rating: 4.6 },
        { name: "Buri Rasa Village Koh Phangan", kind: "Resort", area: "Baan Tai", nightly: 4200, rating: 4.4 }
      ] },
    { id: "kohtao", title: "Koh Tao Diving Weekend", country: "Thailand", region: "Surat Thani", days: 3, rating: 4.5, price: 6800, type: "Adventure", grad: "kohtao", tags: ["Diving", "Koh Nang Yuan"], blurb: "Thailand's dive-school island — easy reefs, the Koh Nang Yuan viewpoint and sunset bays.",
      stays: [
        { name: "Koh Tao Cabana", kind: "Resort", area: "Sairee, headland", nightly: 4600, rating: 4.4 },
        { name: "Jamahkiri Resort & Spa", kind: "Resort", area: "Thian Og Bay", nightly: 5200, rating: 4.5 },
        { name: "Charm Churee Villa", kind: "Resort", area: "Jansom Bay", nightly: 3600, rating: 4.3 }
      ] },
    { id: "khaosok", title: "Khao Sok Rainforest & Lake", country: "Thailand", region: "Surat Thani", days: 3, rating: 4.7, price: 7200, type: "Adventure", grad: "khaosok", tags: ["Cheow Lan Lake", "Rainforest"], blurb: "Limestone karsts over emerald Cheow Lan Lake, floating bungalows and ancient rainforest.",
      stays: [
        { name: "Elephant Hills", kind: "Camp", area: "Luxury tented camp", nightly: 12000, rating: 4.8 },
        { name: "500 Rai Floating Resort", kind: "Resort", area: "Cheow Lan Lake", nightly: 5200, rating: 4.6 },
        { name: "Khao Sok Rainforest Resort (representative)", kind: "Resort", area: "Park entrance", nightly: 2200, rating: 4.3 }
      ] },
    { id: "phuket", title: "Phuket Beaches & Old Town", country: "Thailand", region: "Phuket", days: 3, rating: 4.5, price: 8900, type: "Beach", grad: "phuket", tags: ["Sino-Portuguese", "Beach clubs"], blurb: "Andaman beaches, Sino-Portuguese old town lanes and clifftop sunset bars.",
      stays: [
        { name: "The Nai Harn", kind: "Resort", area: "Nai Harn Beach", nightly: 9800, rating: 4.7 },
        { name: "Rosewood Phuket", kind: "Resort", area: "Emerald Bay", nightly: 18000, rating: 4.8 },
        { name: "Amari Phuket", kind: "Resort", area: "Patong headland", nightly: 5200, rating: 4.5 }
      ] },
    { id: "krabi", title: "Krabi & Railay Cliffs", country: "Thailand", region: "Krabi", days: 3, rating: 4.7, price: 7800, type: "Beach", grad: "krabi", tags: ["Limestone", "Railay"], blurb: "Boat-only Railay, towering limestone, Phra Nang cave beach and island-hopping.",
      stays: [
        { name: "Rayavadee", kind: "Resort", area: "Railay / Phra Nang", nightly: 22000, rating: 4.8 },
        { name: "Dusit Thani Krabi Beach Resort", kind: "Resort", area: "Klong Muang Beach", nightly: 6200, rating: 4.6 },
        { name: "Sofitel Krabi Phokeethra", kind: "Resort", area: "Klong Muang", nightly: 5400, rating: 4.6 }
      ] },
    { id: "phiphi", title: "Koh Phi Phi Islands", country: "Thailand", region: "Krabi", days: 3, rating: 4.5, price: 8600, type: "Beach", grad: "phiphi", tags: ["Maya Bay", "Viewpoint"], blurb: "The famous viewpoint, Maya Bay and turquoise bays best seen by longtail at dawn.",
      stays: [
        { name: "Phi Phi Island Village Beach Resort", kind: "Resort", area: "Loh Ba Kao Bay", nightly: 9200, rating: 4.6 },
        { name: "SAii Phi Phi Island Village", kind: "Resort", area: "Loh Ba Kao", nightly: 8800, rating: 4.6 },
        { name: "Zeavola Resort", kind: "Resort", area: "Laem Tong", nightly: 10500, rating: 4.7 }
      ] },
    { id: "phangnga", title: "Phang Nga Bay & James Bond Island", country: "Thailand", region: "Phang Nga", days: 3, rating: 4.6, price: 7200, type: "Adventure", grad: "phangnga", tags: ["Sea caves", "Kayaking"], blurb: "Sheer karsts rising from the bay — sea-cave kayaking, Koh Panyee and James Bond Island.",
      stays: [
        { name: "Aleenta Phuket-Phang Nga Resort", kind: "Resort", area: "Natai Beach", nightly: 8800, rating: 4.7 },
        { name: "The Sarojin", kind: "Resort", area: "Khao Lak edge", nightly: 9200, rating: 4.7 },
        { name: "Phang Nga bay homestay (representative)", kind: "Homestay", area: "Near the pier", nightly: 1400, rating: 4.3 }
      ] },
    { id: "kholanta", title: "Koh Lanta Slow Islands", country: "Thailand", region: "Krabi", days: 3, rating: 4.5, price: 7400, type: "Beach", grad: "kholanta", tags: ["Long beaches", "Old town"], blurb: "Long, laid-back west-coast beaches, a stilted old town and sunset from the lighthouse cape.",
      stays: [
        { name: "Pimalai Resort & Spa", kind: "Resort", area: "Ba Kantiang Beach", nightly: 11000, rating: 4.7 },
        { name: "Layana Resort & Spa", kind: "Resort", area: "Long Beach (adults-only)", nightly: 8600, rating: 4.7 },
        { name: "Costa Lanta", kind: "Resort", area: "Klong Dao", nightly: 4200, rating: 4.4 }
      ] },
    { id: "khaolak", title: "Khao Lak & Similan Diving", country: "Thailand", region: "Phang Nga", days: 3, rating: 4.5, price: 8100, type: "Beach", grad: "khaolak", tags: ["Similans", "Quiet sands"], blurb: "Long quiet beaches and the launch point for the Similan Islands' world-class diving.",
      stays: [
        { name: "JW Marriott Khao Lak Resort & Spa", kind: "Resort", area: "Khuk Khak Beach", nightly: 8200, rating: 4.7 },
        { name: "The Sarojin", kind: "Resort", area: "Pakarang Beach", nightly: 9200, rating: 4.8 },
        { name: "Casa de La Flora", kind: "Resort", area: "Khuk Khak", nightly: 7600, rating: 4.6 }
      ] },
    { id: "lipe", title: "Koh Lipe Andaman Gem", country: "Thailand", region: "Satun", days: 3, rating: 4.6, price: 9200, type: "Beach", grad: "lipe", tags: ["Clearest water", "Snorkelling"], blurb: "The 'Maldives of Thailand' — powder sand and glass-clear water at the far Andaman edge.",
      stays: [
        { name: "Idyllic Concept Resort", kind: "Resort", area: "Sunrise Beach", nightly: 6800, rating: 4.5 },
        { name: "Serendipity Beach Resort", kind: "Resort", area: "Quiet north cape", nightly: 7600, rating: 4.6 },
        { name: "Castaway Resort Koh Lipe", kind: "Resort", area: "Sunrise Beach", nightly: 5200, rating: 4.5 }
      ] }
  ];

  GOGO.getTrip = function (id) {
    for (var i = 0; i < GOGO.trips.length; i++) if (GOGO.trips[i].id === id) return GOGO.trips[i];
    return null;
  };

  /* ---- distance from Bangkok + "usable weekend hours" (a GOGO original) --- */
  var DRIVE = { amphawa: 1.5, ayutthaya: 1.5, pattaya: 2, bangkok: 0.3, kanchanaburi: 2.5, samet: 3.5, huahin: 3, chiangmai: 2.5, khaoyai: 2.5, lopburi: 2, kohchang: 5, kohkood: 6, chanthaburi: 3.5, chiangrai: 3, pai: 4, nan: 3, sukhothai: 3, ubon: 3, chiangkhan: 3, samui: 2, phangan: 3, kohtao: 4, khaosok: 3, phuket: 2, krabi: 2.5, phiphi: 3.5, phangnga: 3, kholanta: 4, khaolak: 3.5, lipe: 5 };
  var FLY = { chiangmai: 1, chiangrai: 1, pai: 1, nan: 1, sukhothai: 1, ubon: 1, chiangkhan: 1, samui: 1, phangan: 1, kohtao: 1, khaosok: 1, phuket: 1, krabi: 1, phiphi: 1, phangnga: 1, kholanta: 1, khaolak: 1, lipe: 1 };
  GOGO.trips.forEach(function (t) { t.driveHrs = DRIVE[t.id] || 2; t.fly = FLY[t.id] === 1; });
  // A Friday 18:00 -> Sunday 20:00 escape is a 50-hour window; subtract the round trip.
  GOGO.usableHours = function (t) { return Math.max(8, Math.round(50 - 2 * t.driveHrs)); };
  GOGO.driveLabel = function (t) {
    if (t.id === "bangkok") return "Right here in the city";
    if (t.fly) return "~" + t.driveHrs + "h door-to-door by air";
    return "~" + t.driveHrs + "h drive from Bangkok";
  };

  /* ---- shared detail fragments ------------------------------------------ */
  var INCLUDED = ["2 nights at your chosen stay", "Return transfers from Bangkok", "Daily breakfast", "A local guide on day trips", "24/7 support before and during"];
  var NOT_INCLUDED = ["Flights (Chiang Mai trips)", "Travel insurance", "Some lunches & dinners"];
  var REVIEWS = [
    { who: "Ploy S.", when: "Travelled recently", initials: "PS", grad: "huahin", text: "Perfectly paced weekend and zero logistics stress — the transfers from Bangkok were on time both ways." },
    { who: "Nattapong K.", when: "Travelled recently", initials: "NK", grad: "khaoyai", text: "The stay was lovely and the price really was the price. Great for a quick escape from the city." }
  ];

  /* ---- rich details for featured trips ---------------------------------- */
  GOGO.details = {
    huahin: {
      gallery: [
        { bg: "linear-gradient(150deg,#6FD3E8,#2C9FC4 58%,#1E6C8A)", cap: "Hua Hin beach" },
        { bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "Cicada night market" },
        { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Monsoon Valley vineyard" },
        { bg: "linear-gradient(150deg,#F58FB0,#B65AC0 60%,#5B3E9E)", cap: "Vana Nava water park" },
        { bg: "linear-gradient(150deg,#12B39B,#0E7CA8 60%,#F2B33C)", cap: "Sam Roi Yot" }
      ],
      itinerary: [
        { d: 1, t: "Arrive in Hua Hin", text: "Transfer down from Bangkok, check in, and an evening at the Cicada artsy night market." },
        { d: 2, t: "Beach & water park", text: "Morning on the sand, an afternoon at Vana Nava water park, then seafood at the Hua Hin night market." },
        { d: 3, t: "Vineyard & departure", text: "Brunch at Monsoon Valley vineyard (or Sam Roi Yot caves), then the transfer back to Bangkok." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    },
    khaoyai: {
      gallery: [
        { bg: "linear-gradient(150deg,#8FD9A0,#3E9C6C 55%,#215E3E)", cap: "Khao Yai National Park" },
        { bg: "linear-gradient(150deg,#6FC7E8,#2C7FC4 58%,#243B7A)", cap: "Haew Suwat waterfall" },
        { bg: "linear-gradient(150deg,#FFD36A,#FF8A3D 52%,#3AA6C4)", cap: "Hillside vineyard" },
        { bg: "linear-gradient(160deg,#FFC24B,#FF6A3D 50%,#C4326B)", cap: "Farm café at dusk" },
        { bg: "linear-gradient(150deg,#A7D98F,#3E9CC4 55%,#2F5E7E)", cap: "Forest viewpoint" }
      ],
      itinerary: [
        { d: 1, t: "Drive to Khao Yai", text: "Head northeast to the hills, a tasting at PB Valley or GranMonte winery, then check in." },
        { d: 2, t: "National park day", text: "Into Thailand's oldest national park — Haew Suwat and Haew Narok falls, wildlife and viewpoints." },
        { d: 3, t: "Farm cafés & departure", text: "A slow morning around the design cafés and farms, then the transfer back to Bangkok." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    },
    kanchanaburi: {
      gallery: [
        { bg: "linear-gradient(150deg,#A7D98F,#3E9CC4 55%,#2F5E7E)", cap: "River Kwai" },
        { bg: "linear-gradient(150deg,#8FD9C0,#3E9CC4 55%,#2F7E52)", cap: "Erawan Falls" },
        { bg: "linear-gradient(160deg,#F2A65A,#E0533B 55%,#8E2D6B)", cap: "The Death Railway" },
        { bg: "linear-gradient(150deg,#6FC7E8,#2C7FC4 58%,#243B7A)", cap: "Floating villa" },
        { bg: "linear-gradient(150deg,#12B39B,#0E7CA8 60%,#F2B33C)", cap: "Sai Yok" }
      ],
      itinerary: [
        { d: 1, t: "Bridge on the River Kwai", text: "Transfer from Bangkok, the WWII bridge and museum, then a ride on the historic Death Railway." },
        { d: 2, t: "Erawan Falls", text: "A full day at the seven-tier Erawan waterfall, with time to swim, plus Hellfire Pass." },
        { d: 3, t: "River morning & departure", text: "Kayaking or an ethical elephant visit, a floating lunch, then the drive back." }
      ],
      included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS
    }
  };

  /* Build a full detail object for ANY trip (rich if featured, else fallback). */
  GOGO.buildDetail = function (trip) {
    if (GOGO.details[trip.id]) return GOGO.details[trip.id];
    var base = GOGO.gradCss(trip.grad);
    var gallery = [
      { bg: base, cap: trip.region + " views" },
      { bg: "linear-gradient(155deg,#B98F4C,#6E3A44 55%,#241C22)", cap: "On the trip" },
      { bg: "linear-gradient(155deg,#6E9B98,#2E5A5E 58%,#22343A)", cap: "Local life" }
    ];
    var itinerary = [];
    for (var d = 1; d <= trip.days; d++) {
      if (d === 1) itinerary.push({ d: d, t: "Arrive in " + trip.region, text: "Transfer from Bangkok, check in, and a relaxed first evening to settle in." });
      else if (d === trip.days) itinerary.push({ d: d, t: "Departure", text: "A final morning at your own pace, then the transfer back to Bangkok." });
      else itinerary.push({ d: d, t: "Explore " + trip.region, text: "A guided day through the highlights, with free time to wander." });
    }
    return { gallery: gallery, itinerary: itinerary, included: INCLUDED, notIncluded: NOT_INCLUDED, reviews: REVIEWS };
  };

  /* ---- wishlist (localStorage, per-viewer) ------------------------------- */
  var WKEY = "gogo:wishlist";
  GOGO.wish = {
    get: function () { try { return JSON.parse(localStorage.getItem(WKEY) || "[]"); } catch (e) { return []; } },
    has: function (id) { return this.get().indexOf(id) !== -1; },
    toggle: function (id) {
      var list = this.get(), i = list.indexOf(id);
      if (i === -1) list.push(id); else list.splice(i, 1);
      try { localStorage.setItem(WKEY, JSON.stringify(list)); } catch (e) {}
      return this.has(id);
    }
  };

  /* ---- inline SVG icons -------------------------------------------------- */
  GOGO.icon = {
    pinFilled: '<svg width="18" height="18" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 12.5 7 12.5s7-7.3 7-12.5a7 7 0 0 0-7-7z" fill="#fff"/><circle cx="12" cy="9" r="2.7" fill="#7B1E2B"/></svg>',
    pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.4"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    chevron: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.9 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
    heart: '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-.9-1.1a5.5 5.5 0 1 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="3"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>',
    list: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
    map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>',
    bed: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6M3 14h18M3 18v2M21 18v2M7 10V8a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v2"/></svg>',
    car: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11l1.6-4.2A2 2 0 0 1 7.5 5.5h9a2 2 0 0 1 1.9 1.3L20 11v5H4z"/><path d="M4 11h16"/><circle cx="7.5" cy="16" r="1.4"/><circle cx="16.5" cy="16" r="1.4"/></svg>',
    plane: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13L3 11l1.2-2 6.3 1 5-5.4a1.6 1.6 0 0 1 2.4 2L18 15l1 5-2 .8-3-5.2-4 3.8-.5-2.4z"/></svg>',
    dice: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="8.5" cy="8.5" r="1.15" fill="currentColor" stroke="none"/><circle cx="15.5" cy="15.5" r="1.15" fill="currentColor" stroke="none"/><circle cx="15.5" cy="8.5" r="1.15" fill="currentColor" stroke="none"/><circle cx="8.5" cy="15.5" r="1.15" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.15" fill="currentColor" stroke="none"/></svg>'
  };
})();
