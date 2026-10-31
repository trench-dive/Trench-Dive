import json, csv, re, subprocess, collections
def clean(x):
    x = re.sub(r'\s+', ' ', str(x)).strip().replace('"', '').replace('|', '/').replace(';', ',').replace('\\', '')
    return x
def join(items): return '|'.join(i for i in items if i)
def dedupe(items):
    seen=set(); out=[]
    for i in items:
        k=i if i.startswith('~') else re.sub(r'[^a-z0-9]','',i.split(';')[0].lower())
        if k and k not in seen: seen.add(k); out.append(i)
    return out
out_extra, out_new = [], []
# ---- films (append to "Name a movie"): ranked by how much Wikipedia writes about them ----
mv = json.load(open('/tmp/movies.json'))
sc = []
for m in mv:
    t = clean(m.get('title','')); 
    if not t or len(t) > 60: continue
    s = len(m.get('extract') or '') + (400 if m.get('thumbnail') else 0) + 25*len(m.get('cast') or []) + (m.get('year',1900)-1900)*3
    sc.append((s,t))
sc.sort(reverse=True); films = dedupe([t for s,t in sc])[:20000]
out_extra.append(('k_movie', films))
# ---- cities (population): new world question + much bigger per-country lists ----
cities = json.loads(subprocess.check_output(['node','-e',"const c=require('all-the-cities');process.stdout.write(JSON.stringify(c.filter(x=>x.population>=1000).map(x=>[x.name,x.country,x.population])))"], cwd='/tmp/ds'))
cities.sort(key=lambda c: -c[2])
def cc(code, minpop): return dedupe([clean(c[0]) for c in cities if c[1]==code and c[2]>=minpop])
for pid, code, mp in [('uscities','US',10000),('ukcities','GB',5000),('austcities','AU',3000),('cancities','CA',5000),('japancities','JP',20000),('italycities','IT',10000),('frcities','FR',8000),('nzcities','NZ',1000)]:
    out_extra.append((pid, cc(code, mp)))
WORLD_HEAD = "Tokyo|New York;New York City;NYC|London|Paris|Los Angeles;LA|Sydney|Dubai|Rome|Berlin|Beijing;Peking|Shanghai|Hong Kong|Singapore|Moscow|Madrid|Barcelona|Amsterdam|Toronto|Mumbai;Bombay|Delhi;New Delhi|Cairo|Istanbul|Rio de Janeiro;Rio|Mexico City|Bangkok|Seoul|Chicago|San Francisco|Las Vegas|Miami|Melbourne|Vienna|Prague|Venice|Florence|Milan|Lisbon|Athens|Dublin|Edinburgh|Buenos Aires|São Paulo;Sao Paulo|Cape Town|Johannesburg|Nairobi|Lagos|Jakarta|Manila|Kuala Lumpur|Vancouver|Montreal|Washington DC;Washington|Boston|Seattle|Auckland|Wellington|Munich|Zurich|Geneva|Stockholm|Copenhagen|Oslo|Helsinki|Brussels|Budapest|Warsaw|Kyiv;Kiev|St Petersburg;Saint Petersburg|Kyoto|Osaka|Taipei|Hanoi|Ho Chi Minh City;Saigon|Lima|Bogotá;Bogota|Santiago|Havana|Jerusalem|Tehran|Baghdad|Riyadh|Doha|Abu Dhabi|Karachi|Lahore|Dhaka|Kolkata;Calcutta|Bangalore;Bengaluru|Chennai;Madras|Perth|Brisbane|Houston|Dallas|Atlanta|Philadelphia|New Orleans|Manchester|Liverpool|Birmingham|Glasgow|Marseille|Lyon|Nice|Naples|Seville|Valencia|Porto|Hamburg|Frankfurt|Cologne|Kraków;Krakow|Reykjavik|Marrakech|Casablanca"
world = WORLD_HEAD.split('|') + dedupe([clean(c[0]) for c in cities if c[2]>=15000])
out_new.append(('worldcities','geo','Name a city (anywhere in the world)', world))
# ---- lakes (Natural Earth, by size rank) ----
LAKE_HEAD = "Lake Superior|Lake Victoria|Lake Michigan|Lake Huron|Lake Erie|Lake Ontario|Caspian Sea|Lake Baikal;Baikal|Lake Titicaca;Titicaca|Loch Ness|Lake Tahoe|Lake Geneva;Lac Léman;Lac Leman|Lake Como|Lake Garda|Great Salt Lake|Lake Tanganyika|Lake Malawi;Lake Nyasa|Dead Sea|Lake Taupō;Lake Taupo|Lake Louise|Lake Constance;Bodensee|Lake Placid|Crater Lake|Lake Lucerne|Lake Bled|Lake Maggiore|Lake Chad|Aral Sea|Lake Ladoga|Great Bear Lake|Great Slave Lake|Lake Winnipeg|Lake Champlain|Lake Okeechobee|Lake Mead|Lake Powell|Lake Nasser|Lake Kariba|Lake Volta|Lake Balaton;Balaton|Windermere;Lake Windermere|Lough Neagh|Loch Lomond|Lake Wakatipu|Lake Tekapo|Lake Eyre;Kati Thanda|Lake Toba|Lake Biwa|Inle Lake|Dal Lake|Hallstätter See;Lake Hallstatt;Hallstatt|Königssee;Konigssee|Lake Annecy|Lake Zurich|Lake Neusiedl;Neusiedler See|Lake Ohrid|Lake Van|Lake Sevan|Issyk-Kul;Issyk Kul|Lake Khövsgöl;Khovsgol|Plitvice Lakes|Lake Atitlán;Lake Atitlan|Lake Nicaragua|Lake Maracaibo"
lk = json.load(open('/tmp/ds/lakes.geojson'))['features']
lk.sort(key=lambda f: (f['properties'].get('scalerank') or 9))
lakes = LAKE_HEAD.split('|') + dedupe([clean(f['properties'].get('name_en') or f['properties'].get('name') or '') for f in lk])
out_new.append(('lakes_world','geo','Name a lake', lakes))
# ---- languages ----
LANG_HEAD = "English|Spanish;Español|French|German|Chinese;Mandarin;Mandarin Chinese|Japanese|Italian|Russian|Portuguese|Arabic|Hindi|Korean|Dutch|Greek|Swedish|Latin|Turkish|Polish|Norwegian|Danish|Finnish|Hebrew|Cantonese|Vietnamese|Thai|Swahili|Bengali;Bangla|Urdu|Punjabi|Persian;Farsi|Indonesian|Malay|Tagalog;Filipino|Irish;Irish Gaelic;Gaelic|Welsh|Scottish Gaelic|Icelandic|Hungarian|Czech|Ukrainian|Romanian|Bulgarian|Serbian|Croatian|Afrikaans|Zulu|Xhosa|Māori;Maori;Te Reo|Hawaiian|Samoan|Tongan|Fijian|Tahitian|Esperanto|Sign Language;British Sign Language;BSL;American Sign Language;ASL;NZ Sign Language|~R|Catalan|Basque|Galician|Yiddish|Sanskrit|Tamil|Telugu|Marathi|Gujarati|Nepali|Sinhala;Sinhalese|Burmese|Khmer|Lao|Mongolian|Tibetan|Kazakh|Uzbek|Armenian|Georgian|Albanian|Macedonian|Slovak|Slovenian|Lithuanian|Latvian|Estonian|Maltese|Luxembourgish|Faroese|Breton|Cornish|Manx|Romansh|Swiss German;Schweizerdeutsch;Schwiizerdütsch|Bavarian|Low German;Plattdeutsch|Frisian|Scots|Occitan|Corsican|Sardinian|Sicilian|Neapolitan|Venetian|~D|Ladino|Romani|Sami|Tatar|Chechen|Kurdish|Pashto|Amharic|Somali|Yoruba|Igbo|Hausa|Wolof|Lingala|Shona|Sesotho;Sotho|Setswana;Tswana|Kinyarwanda|Malagasy|Haitian Creole;Kreyòl|Jamaican Patois;Patois;Jamaican Creole|Papiamento|Tok Pisin|Bislama|Sranan Tongo|Gullah|Krio|Seychellois Creole|Mauritian Creole|Cape Verdean Creole|Nigerian Pidgin|~T|Chamorro|Rarotongan;Cook Islands Māori|Niuean|Tuvaluan|Marshallese|Palauan|Gilbertese;Kiribati|Quechua|Aymara|Guarani|Nahuatl|Yucatec Maya;Maya|Navajo|Cherokee|Inuktitut|Greenlandic|Cree|Ojibwe|Lakota|Hmong|Javanese|Sundanese|Balinese|Cebuano|Ilocano|Klingon|Elvish;Sindarin;Quenya|Dothraki|High Valyrian|Old English|Ancient Greek|Old Norse|Aramaic|Coptic|Akkadian|Sumerian|Ancient Egyptian;Egyptian|Gothic|Etruscan|Alemannic|Swabian|Austro-Bavarian|Silesian|Kashubian|Sorbian|Walloon|Picard|Limburgish|Aromanian|Tok Pisin|Pitkern|Norfuk|Hiri Motu|Pijin|Wallisian|Futunan|Tokelauan|Rapa Nui|Marquesan|Mangarevan|Tuamotuan|Pukapukan|Rotuman|Kosraean|Pohnpeian|Chuukese|Yapese|Nauruan"
langs = subprocess.check_output(['node','--input-type=module','-e',"import {iso6393} from 'iso-639-3'; process.stdout.write(JSON.stringify(iso6393.filter(l=>l.type!=='special').map(l=>l.name)))"], cwd='/tmp/ds')
languages = LANG_HEAD.split('|') + dedupe([clean(n) for n in json.loads(langs)])
out_new.append(('languages','words','Name a language', languages))
# ---- S&P 500 ----
SP_HEAD = "Apple|Microsoft|Amazon|Alphabet;Google|Meta;Meta Platforms;Facebook|Tesla|Nvidia|Netflix|Coca-Cola;Coke|McDonald's;McDonalds|Walmart|Disney;Walt Disney|Nike|JPMorgan Chase;JPMorgan;JP Morgan|Visa|Mastercard|PepsiCo;Pepsi|Starbucks|Intel|AMD;Advanced Micro Devices|Boeing|Ford;Ford Motor|General Motors;GM|ExxonMobil;Exxon Mobil;Exxon|Johnson & Johnson;Johnson and Johnson|Pfizer|Procter & Gamble;P&G|Costco|Home Depot|Berkshire Hathaway|Goldman Sachs|Bank of America|Wells Fargo|IBM|Oracle|Cisco|Adobe|Salesforce|PayPal|Uber|Airbnb|Chevron|AT&T|Verizon|Comcast|Target|Hershey|Delta Air Lines;Delta|United Airlines;United|American Express;Amex|eBay|Domino's;Dominos|Chipotle|Marriott|Hilton"
rows = list(csv.DictReader(open('/tmp/constituents.csv')))
def co(n): n = re.sub(r'\s*\(Class [A-Z]\)', '', n); n = re.sub(r',?\s+(Inc\.?|Corporation|Corp\.?|Co\.?|Company|plc|Ltd\.?|Holdings|Group|N\.V\.|S\.A\.)$', '', n); return clean(n.strip(' ,'))
sp = SP_HEAD.split('|') + [co(r['Security']) + ';' + clean(r['Symbol']) for r in rows]
out_new.append(('sp500','biz','Name a company in the S&P 500', sp))
# ---- music artists and songs (Billboard Hot 100 weeks) ----
wk = collections.Counter(); sw = collections.Counter(); songname = {}
for r in csv.DictReader(open('/tmp/hot-100-current.csv')):
    perf = r['performer']; parts = re.split(r'\s+(?:Featuring|Feat\.?|Ft\.?|With|x|X|Duet With|Introducing)\s+', perf)
    for p in parts:
        wk[p.strip()] += 1
    key = (r['title'].strip().lower()); songname[key] = r['title'].strip()
    sw[key] = max(sw[key], int(r['wks_on_chart'] or 0) * 3 + (101 - int(r['peak_pos'] or 100)))  # its best single chart run
art = collections.Counter()
for p, n in wk.items():
    if (' & ' in p or ', ' in p or ' And ' in p) and n < 25:
        for q in re.split(r'\s*(?:&|,| And )\s*', p):
            if q: art[q] += n
    else: art[p] += n
MUS_HEAD = "Taylor Swift|The Beatles;Beatles|Michael Jackson|Beyoncé;Beyonce|Drake|Ed Sheeran|Rihanna|Adele|Elvis Presley;Elvis|Madonna|Queen|Eminem|Justin Bieber|Ariana Grande|Billie Eilish|Bruno Mars|Lady Gaga|Kanye West;Ye;Kanye|Coldplay|The Weeknd|Elton John|BTS|Harry Styles|Katy Perry|Dua Lipa|Post Malone|ABBA|Bob Marley|Whitney Houston|Prince|David Bowie|The Rolling Stones;Rolling Stones|Led Zeppelin|Nirvana|Pink Floyd|AC/DC;ACDC|Metallica|Oasis|U2|Bob Dylan|Frank Sinatra|Kendrick Lamar|Travis Scott|Olivia Rodrigo|Sabrina Carpenter|Shakira|Bad Bunny|Doja Cat|SZA|Miley Cyrus|Selena Gomez|Britney Spears|Mariah Carey|Celine Dion|Stevie Wonder|Johnny Cash|Dolly Parton|Kylie Minogue|Arctic Monkeys|Imagine Dragons|Maroon 5|One Direction|Linkin Park|Green Day|Red Hot Chili Peppers|Guns N' Roses;Guns N Roses|Bon Jovi|Fleetwood Mac|The Who|Jimi Hendrix|Aretha Franklin|Tupac;2Pac|The Notorious B.I.G.;Biggie;Notorious BIG|Snoop Dogg|Jay-Z;Jay Z|Nicki Minaj|Cardi B|Lizzo|Sia|Lana Del Rey|Lorde|Sam Smith|Shawn Mendes|Charli XCX|Chappell Roan|Gracie Abrams|Benson Boone|Noah Kahan|Zach Bryan|Morgan Wallen|Luke Combs|Kenny Rogers|Tina Turner|Cher|Phil Collins|Sting|Robbie Williams|Spice Girls|Backstreet Boys|NSYNC;*NSYNC|Blackpink|Daft Punk|Avicii|David Guetta|Calvin Harris|Tame Impala|Radiohead|Foo Fighters|Kings of Leon|The Killers|Paramore|Gorillaz|Muse|Rammstein|Kraftwerk|Iron Maiden|Black Sabbath|Kiss|Aerosmith|Eagles|The Beach Boys;Beach Boys|Bee Gees|Michael Bublé;Michael Buble|Andrea Bocelli|Luciano Pavarotti;Pavarotti"
music = MUS_HEAD.split('|') + dedupe([clean(a) for a, n in art.most_common() if a and len(a) <= 50])
out_new.append(('musicartists','music','Name a music artist or band', music[:9000]))
SONG_HEAD = "Bohemian Rhapsody|Shape of You|Blinding Lights|Billie Jean|Hey Jude|Imagine|Thriller|Yesterday|Let It Be|Hotel California|Stairway to Heaven|Smells Like Teen Spirit|Like a Rolling Stone|Sweet Child O' Mine;Sweet Child of Mine|Someone Like You|Rolling in the Deep|Hello|Uptown Funk|Despacito|Happy|Bad Guy|Shake It Off|Anti-Hero|Cruel Summer|Flowers|As It Was|Levitating|Dancing Queen|Wonderwall|Don't Stop Believin';Dont Stop Believing|Purple Rain|Africa|Toxic|Baby|Single Ladies|Crazy in Love|Umbrella|Poker Face|Bad Romance|Firework|Roar|Viva la Vida|Yellow|Mr. Brightside;Mr Brightside|Seven Nation Army|Lose Yourself|Gangnam Style|Macarena|Y.M.C.A.;YMCA|I Will Always Love You|My Heart Will Go On|Hallelujah|Wrecking Ball|Halo|Perfect|Thinking Out Loud|Let It Go|All I Want for Christmas Is You|Jingle Bell Rock|Old Town Road|Espresso|Please Please Please|APT.;APT|Die With a Smile|Birds of a Feather|Not Like Us|Golden|Watermelon Sugar|Drivers License|Good 4 U|Shallow|Rockstar|Sunflower|Believer|Counting Stars|Riptide|Take On Me|Livin' on a Prayer;Living on a Prayer|We Will Rock You|Don't Stop Me Now|Sweet Caroline|Every Breath You Take|Billie Jean"
songs = SONG_HEAD.split('|') + dedupe([clean(songname[k]) for k, n in sw.most_common() if len(songname[k]) <= 60])
out_new.append(('songs','music','Name a song', songs[:14000]))
# ---- write ----
with open('/home/claude/handoff/src/big_extra.js','w') as f:
    f.write('// ---- Large answer lists from open datasets (films: Wikipedia; towns: GeoNames via all-the-cities, ranked by population) ----\n')
    for pid, items in out_extra:
        f.write('EXTRA["%s"] = (EXTRA["%s"] ? EXTRA["%s"] + "|" : "") + "%s";\n' % (pid, pid, pid, join(items)))
with open('/home/claude/handoff/src/gen_big.js','w') as f:
    f.write('// ---- Broad questions with very large answer lists: a hand-ranked head, then open data (Billboard Hot 100 weeks, GeoNames population, Natural Earth lake rank, ISO 639-3, S&P 500) ----\n')
    for pid, cat, pr, items in out_new:
        f.write('A("%s","%s","%s",\n"%s");\n\n' % (pid, cat, pr, join(dedupe(items))))
for pid, items in out_extra: print('EXTRA', pid, len(items))
for pid, cat, pr, items in out_new: print('NEW', pid, len(dedupe(items)), '|', ', '.join(dedupe(items)[130:136]))
