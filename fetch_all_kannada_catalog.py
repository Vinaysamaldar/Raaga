import concurrent.futures
import html
import json
import os
import re
import urllib.parse
import urllib.request

from fetch_full_kannada_songs import decrypt_jiosaavn_url

# Comprehensive 4-Pillar Kannada Music Queries covering the 150,000–200,000+ Kannada musical heritage:
# 1. sandalwood (1934–2026 Film Songs across 5,000+ movies)
# 2. devotional (Dasa Sahitya, Purandara Dasa, Kanaka Dasa, Vachanas, Carnatic & Temple music)
# 3. folk (Janapada Geethegalu, Tatvapada, Kolata, Kamsale, Bhavageethe)
# 4. indie (Modern Independent Kannada Pop, Rap/Hip-Hop, Folk-Rock, Acoustic & Lo-Fi)

KANNADA_PILLAR_QUERIES = [
    # ==================== PILLAR 1: SANDALWOOD FILM SONGS (1934–2026) ====================
    # Golden Era & Early Talkies (1934–1979)
    ("sandalwood", "old", "Bedara Kannappa Bhakta Kanakadasa Rajkumar Kannada", "devotional", 1954),
    ("sandalwood", "old", "Bangarada Manushya Kasturi Nivasa Dr Rajkumar", "feelgood", 1972),
    ("sandalwood", "old", "Babruvahana Mayura Satya Harishchandra Kannada", "devotional", 1975),
    ("sandalwood", "old", "Naagarahaavu Vishnuvardhan P B Sreenivas Kannada", "romance", 1972),
    ("sandalwood", "old", "Gandhada Gudi Sampathige Saval Dr Rajkumar", "folk", 1973),
    ("sandalwood", "old", "Sanaadi Appanna Shankar Guru Huliya Haalina Mevu", "relax", 1977),
    ("sandalwood", "old", "Sharapanjara Gejje Pooje Kalpana Kannada Songs", "romance", 1970),
    ("sandalwood", "old", "G K Venkatesh Vijaya Bhaskar Kannada Film Hits", "relax", 1968),
    ("sandalwood", "old", "Rajan Nagendra Kannada Evergreen Film Songs", "romance", 1976),
    ("sandalwood", "old", "P B Sreenivas Kannada Golden Hits", "romance", 1965),
    ("sandalwood", "old", "S Janaki P Susheela Vani Jairam Kannada Hits", "romance", 1974),
    ("sandalwood", "old", "Udaykumar Kalyan Kumar Rajashankar Kannada Old Songs", "relax", 1962),
    ("sandalwood", "old", "Srinath Aarathi Manjula Kannada 1970s Songs", "romance", 1976),

    # 1980s & 1990s Sandalwood Classics
    ("sandalwood", "old", "Kaviratna Kalidasa Chalisuva Modagalu Haalu Jenu", "romance", 1983),
    ("sandalwood", "old", "Jeevana Chaitra Akasmika Odahuttidavaru Dr Rajkumar", "feelgood", 1992),
    ("sandalwood", "old", "Bandhana Muthina Haara Suprabhatha Vishnuvardhan", "romance", 1988),
    ("sandalwood", "old", "Geetha Pallavi Anupallavi Shankar Nag Ilaiyaraaja", "romance", 1983),
    ("sandalwood", "old", "Premaloka Ranadheera Anjada Gandu Ravichandran Hamsalekha", "romance", 1987),
    ("sandalwood", "old", "Ramachari Belli Kalungura Mannina Doni Kannada", "romance", 1991),
    ("sandalwood", "old", "Amruthavarshini America America Nammoora Mandara Hoove", "romance", 1997),
    ("sandalwood", "old", "Janumada Jodi Om Chigurida Kanasu Shiva Rajkumar", "folk", 1996),
    ("sandalwood", "old", "Anant Nag Lakshmi Kannada Movie Songs", "feelgood", 1985),
    ("sandalwood", "old", "Ambareesh Olavina Udugore Mandyada Gandu Kannada", "folk", 1988),
    ("sandalwood", "old", "Ramesh Aravind Preethse Karpoorada Gombe Kannada", "romance", 1999),
    ("sandalwood", "old", "Upendra A Preethse Rakta Kanneeru Kannada Songs", "workout", 1999),
    ("sandalwood", "old", "Hamsalekha Kannada Super Hit Film Songs", "folk", 1993),
    ("sandalwood", "old", "Upendra Kumar M Ranga Rao Kannada Film Hits", "devotional", 1989),
    ("sandalwood", "old", "S P Balasubrahmanyam Kannada Evergreen Hits", "romance", 1990),
    ("sandalwood", "old", "K S Chithra Manjula Gururaj B R Chaya Kannada", "romance", 1991),

    # 2000s & Early 2010s Sandalwood Blockbusters
    ("sandalwood", "old", "Appu Abhi Akash Arasu Puneeth Rajkumar", "workout", 2004),
    ("sandalwood", "old", "Milana Jackie Hudugaru Paramathma Puneeth Rajkumar", "feelgood", 2010),
    ("sandalwood", "old", "Mungaru Male Gaalipata Maleyali Jotheyali Ganesh", "romance", 2007),
    ("sandalwood", "old", "Jogi Jogaiah Mylari Bhajarangi Shiva Rajkumar", "workout", 2005),
    ("sandalwood", "old", "Yajamana Apthamitra Aptharakshaka Vishnuvardhan", "feelgood", 2004),
    ("sandalwood", "old", "Kariya Majestic Gaja Saarathi Darshan Kannada", "workout", 2008),
    ("sandalwood", "old", "Huchcha Kiccha My Autograph Just Maath Maathalli Sudeep", "romance", 2006),
    ("sandalwood", "old", "Moggina Manasu Drama Googly Mr and Mrs Ramachari Yash", "romance", 2013),
    ("sandalwood", "old", "Duniya Jarasandha Junglee Duniya Vijay Kannada", "folk", 2007),
    ("sandalwood", "old", "Nenapirali Prem Kahani Ajay Rao Prem Kannada", "romance", 2006),
    ("sandalwood", "old", "Cheluvina Chittara Krishnan Love Story Kannada", "romance", 2009),
    ("sandalwood", "old", "Mano Murthy Rajesh Krishnan Sonu Nigam Kannada", "romance", 2008),
    ("sandalwood", "old", "V Harikrishna Gurukiran Arjun Janya Kannada Hits", "workout", 2011),
    ("sandalwood", "old", "Kunal Ganjawala Udit Narayan Rajesh Krishnan Kannada", "romance", 2007),

    # Latest Sandalwood Cinema (2016–2026)
    ("sandalwood", "latest", "Raajakumara Yuvarathnaa James Natasaarvabhowma Puneeth", "feelgood", 2018),
    ("sandalwood", "latest", "KGF Chapter 1 KGF Chapter 2 Ravi Basrur Yash", "workout", 2022),
    ("sandalwood", "latest", "Kantara Rishab Shetty Ajaneesh Loknath Kannada", "devotional", 2022),
    ("sandalwood", "latest", "Kirik Party 777 Charlie Avane Srimannarayana Rakshit", "feelgood", 2019),
    ("sandalwood", "latest", "Sapta Sagaradaache Ello Side A Side B Charan Raj", "romance", 2023),
    ("sandalwood", "latest", "Kaatera Roberrt Kurukshetra Kranti Darshan Kannada", "workout", 2023),
    ("sandalwood", "latest", "Vikrant Rona Pailwaan Hebbuli Max Kiccha Sudeep", "workout", 2022),
    ("sandalwood", "latest", "Tagaru Mufti Bhairathi Ranagal Vedha Shiva Rajkumar", "workout", 2018),
    ("sandalwood", "latest", "Krishnam Pranaya Sakhi Golden Star Ganesh 2024", "romance", 2024),
    ("sandalwood", "latest", "Bheema Salaga Duniya Vijay Charan Raj Kannada", "workout", 2024),
    ("sandalwood", "latest", "Bagheera Yuva Martin UI Kannada Songs 2024", "workout", 2024),
    ("sandalwood", "latest", "Love Mocktail Dia Kousalya Supraja Rama Kannada", "romance", 2021),
    ("sandalwood", "latest", "Garuda Gamana Vrishabha Vahana Raj B Shetty", "folk", 2021),
    ("sandalwood", "latest", "Bell Bottom Hero Kantara Rishab Shetty Kannada", "feelgood", 2020),
    ("sandalwood", "latest", "Hostel Hudugaru Bekagiddare Ibbani Tabbida Ileyali", "feelgood", 2024),
    ("sandalwood", "latest", "Su From So Kannada Movie Songs 2025", "feelgood", 2025),
    ("sandalwood", "latest", "Kannada New Movie Songs 2025 2026", "feelgood", 2025),
    ("sandalwood", "latest", "Sanjith Hegde Kannada Movie Songs", "romance", 2022),
    ("sandalwood", "latest", "Vijay Prakash Kannada Superhit Songs", "feelgood", 2021),
    ("sandalwood", "latest", "Shreya Ghoshal Anuradha Bhat Kannada Melody", "romance", 2020),
    ("sandalwood", "latest", "Armaan Malik Sid Sriram Jaskaran Singh Kannada", "romance", 2023),

    # ==================== PILLAR 2: DEVOTIONAL, DASA SAHITYA, VACHANAS & CARNATIC ====================
    ("devotional", "old", "Purandaradasa Keerthanegalu Kannada", "devotional", 1980),
    ("devotional", "old", "Jagadodharana Krishna Nee Begane Baro Bhagyada Lakshmi", "devotional", 1978),
    ("devotional", "old", "Kanakadasa Keerthanegalu Baagilanu Teredu Kannada", "devotional", 1982),
    ("devotional", "old", "Vidyabhushana Kannada Dasa Sahitya Devotional Songs", "devotional", 1995),
    ("devotional", "old", "Pandit Bhimsen Joshi Venkatesh Kumar Kannada Dasara Pada", "devotional", 1988),
    ("devotional", "old", "Basavanna Vachana Sahitya Kannada Vachanagalu", "devotional", 1990),
    ("devotional", "old", "Akka Mahadevi Allama Prabhu Kannada Vachanagalu", "devotional", 1992),
    ("devotional", "old", "Dr Rajkumar Devotional Songs Mantralaya Mahatme", "devotional", 1985),
    ("devotional", "old", "Raghavendra Swamy Kannada Devotional Songs", "devotional", 1994),
    ("devotional", "old", "Dharmasthala Manjunatha Kukke Subramanya Kannada", "devotional", 1996),
    ("devotional", "old", "Chamundeshwari Kollur Mookambika Sringeri Sharadamba", "devotional", 1995),
    ("devotional", "old", "Male Mahadeshwara MM Hills Kannada Devotional Folk", "devotional", 1993),
    ("devotional", "old", "Udupi Sri Krishna Venkataramana Kannada Bhajans", "devotional", 1991),
    ("devotional", "old", "Kannada Suprabhata Shiva Ganesha Hanuman Bhajans", "devotional", 1989),
    ("devotional", "old", "Carnatic Classical Kannada Kritis R K Srikantan", "devotional", 1984),
    ("devotional", "old", "Mysore Vasudevachar Purandara Dasa Carnatic Kannada", "devotional", 1980),
    ("devotional", "latest", "Sojugada Sooju Mallige Ananya Bhat Shiva Kannada", "devotional", 2019),

    # ==================== PILLAR 3: FOLK & TRADITIONAL (JANAPADA GEETHEGALU & BHAVAGEETHE) ====================
    ("folk", "old", "Kannada Janapada Geethegalu Folk Songs", "folk", 1988),
    ("folk", "old", "Chellidaru Malligeya Bhagyada Balegara Kannada Folk", "folk", 1990),
    ("folk", "old", "Kolu Kolanna Kolu Kolata Kamsale Kannada Folk", "folk", 1986),
    ("folk", "old", "Shishunala Sharif Tatvapada Kannada Songs C Ashwath", "folk", 1987),
    ("folk", "old", "Kodagana Koli Nungitha Taravalla Tagi Ninna", "folk", 1989),
    ("folk", "old", "Gururaj Hoskote North Karnataka Janapada Songs", "folk", 1995),
    ("folk", "old", "Appagere Thimmaraju Banandur Kempaiah Kannada Folk", "folk", 1994),
    ("folk", "old", "B Jayashree M D Pallavi Kannada Folk Songs", "folk", 1998),
    ("folk", "old", "C Ashwath Kannada Bhavageethe Evergreens", "relax", 1988),
    ("folk", "old", "Mysore Ananthaswamy Kannada Bhavageethe", "relax", 1984),
    ("folk", "old", "Kuvempu D R Bendre Kannada Bhavageethe", "relax", 1985),
    ("folk", "old", "K S Narasimhaswamy Mysore Mallige Kannada Songs", "relax", 1986),
    ("folk", "old", "G S Shivarudrappa K S Nissar Ahmed Nityotsava", "relax", 1989),
    ("folk", "old", "H S Venkateshamurthy B R Lakshmana Rao Bhavageethe", "relax", 1993),
    ("folk", "old", "Sangeetha Katti Ratnamala Prakash Shimoga Subbanna", "relax", 1991),
    ("folk", "old", "Kannada Rajyotsava Patriotic Naadu Nudi Songs", "rajyotsava", 1992),
    ("folk", "latest", "Ananya Bhat Kannada Janapada Folk Songs", "folk", 2021),

    # ==================== PILLAR 4: MODERN INDEPENDENT, POP, HIP-HOP, RAP & ROCK ====================
    ("indie", "latest", "Raghu Dixit Project Kannada Folk Rock Songs", "folk", 2018),
    ("indie", "latest", "Lokada Kalaji Gudugudiya Sedi Nodo Raghu Dixit", "folk", 2016),
    ("indie", "latest", "Vasu Dixit Swarathma Peepal Tree Kannada Rock", "workout", 2021),
    ("indie", "latest", "Chandan Shetty Kannada Rap Pop Party Songs", "workout", 2020),
    ("indie", "latest", "All OK Alok Babu Kannada Rap Hip Hop Songs", "workout", 2021),
    ("indie", "latest", "Rahul Dit O Gubbi MC Bijju Kannada Rap", "workout", 2022),
    ("indie", "latest", "Sanjith Hegde Vasuki Vaibhav Kannada Indie Singles", "romance", 2023),
    ("indie", "latest", "Varijashree Venugopal Siddhartha Belmannu Kannada", "relax", 2023),
    ("indie", "latest", "Kannada Independent Pop Singles 2023 2024 2025", "feelgood", 2024),
    ("indie", "latest", "Kannada Acoustic Unplugged LoFi Chill Songs", "relax", 2024),
    ("indie", "latest", "Chaitra J Achar Sangeetha Rajeev Kannada Pop", "feelgood", 2023),
]

EN_TO_KN_INIT = {
    'A': 'ಅ', 'B': 'ಬ', 'C': 'ಚ', 'D': 'ದ', 'E': 'ಎ', 'F': 'ಫ',
    'G': 'ಗ', 'H': 'ಹ', 'I': 'ಇ', 'J': 'ಜ', 'K': 'ಕ', 'L': 'ಲ',
    'M': 'ಮ', 'N': 'ನ', 'O': 'ಒ', 'P': 'ಪ', 'Q': 'ಕ', 'R': 'ರ',
    'S': 'ಸ', 'T': 'ತ', 'U': 'ಉ', 'V': 'ವ', 'W': 'ವ', 'X': 'ಕ್ಷ',
    'Y': 'ಯ', 'Z': 'ಜ'
}

def clean_text(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r'\s*\(From\s+"[^"]+"\)', '', s)
    return s.strip()

def fetch_query_page(task):
    pillar, era_hint, query, default_mood, fallback_year, page = task
    url = (
        "https://www.jiosaavn.com/api.php?__call=search.getResults"
        "&_format=json&_marker=0&api_version=4&ctx=web6dot0"
        f"&n=40&p={page}&q={urllib.parse.quote(query)}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    })
    extracted = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            results = data.get("results", [])
    except Exception:
        return extracted

    for item in results:
        lang = str(item.get("language", "")).lower()
        if lang and lang not in ("kannada", "sanskrit"):
            continue
        more = item.get("more_info", {}) or {}
        enc = more.get("encrypted_media_url")
        if not enc:
            continue
        try:
            stream320 = decrypt_jiosaavn_url(enc)
        except Exception:
            continue
        if not stream320:
            continue

        title_en = clean_text(item.get("title", ""))
        if not title_en:
            continue

        dur = int(more.get("duration") or 240)
        if dur < 45:
            continue

        yr_str = str(item.get("year") or fallback_year)
        try:
            year = int(yr_str[:4])
            if year < 1934 or year > 2026:
                year = fallback_year
        except Exception:
            year = fallback_year

        # Preserve historical accuracy for early/golden era queries re-released on digital albums
        if era_hint == "old" and fallback_year <= 1995 and year >= 2015:
            year = fallback_year

        album = clean_text(more.get("album") or item.get("subtitle") or "Kannada Album")
        artist_map = more.get("artistMap", {}) or {}
        primary_artists = artist_map.get("primary_artists", [])
        if primary_artists:
            artist = ", ".join(clean_text(a.get("name", "")) for a in primary_artists[:2] if a.get("name"))
        else:
            artist = clean_text(more.get("music") or item.get("subtitle") or "Kannada Artist")
        if not artist:
            artist = "Kannada Artist"

        art_url = str(item.get("image") or "").replace("150x150", "500x500").replace("http://", "https://")
        stream160 = stream320.replace("_320.mp4", "_160.mp4")

        en_init = title_en[0].upper() if title_en[0].isalpha() else 'K'
        kn_init = EN_TO_KN_INIT.get(en_init, 'ಕ')

        extracted.append({
            "titleEn": title_en,
            "titleKn": f"{title_en} ({kn_init})",
            "artist": artist,
            "movie": album,
            "year": year,
            "mood": default_mood,
            "pillar": pillar,
            "duration": dur,
            "enInit": en_init,
            "knInit": kn_init,
            "cdn320Url": stream320,
            "cdn160Url": stream160,
            "artworkUrl": art_url,
        })
    return extracted

def fetch_all_kannada():
    tasks = []
    for pillar, era_hint, query, default_mood, fallback_year in KANNADA_PILLAR_QUERIES:
        tasks.append((pillar, era_hint, query, default_mood, fallback_year, 1))
        tasks.append((pillar, era_hint, query, default_mood, fallback_year, 2))

    seen_urls = set()
    seen_titles = set()
    all_tracks = []
    pillar_counts = {"sandalwood": 0, "devotional": 0, "folk": 0, "indie": 0}

    print(f"Dispatching {len(tasks)} parallel Kannada catalog harvest tasks across 4 pillars...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for batch in executor.map(fetch_query_page, tasks):
            for t in batch:
                u = t["cdn320Url"]
                norm_title = re.sub(r'[^a-z0-9]', '', (t["titleEn"] + t["artist"][:8]).lower())
                if u in seen_urls or norm_title in seen_titles or len(norm_title) < 3:
                    continue
                seen_urls.add(u)
                seen_titles.add(norm_title)
                all_tracks.append(t)
                p = t.get("pillar", "sandalwood")
                pillar_counts[p] = pillar_counts.get(p, 0) + 1

    print(f"Total unique full-length Kannada songs fetched: {len(all_tracks)}")
    print(f"Breakdown by Pillar: {pillar_counts}")
    out_path = os.path.join("mobile", "web_preview", "audio", "originals", "all_kannada_songs.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    fetch_all_kannada()
