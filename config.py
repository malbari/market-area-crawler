
"""Configurazione del Market Area Crawler"""

# Mercati da monitorare
MARKET_AREAS = [
    'tecnologia',
    'finanza', 
    'energia',
    'automotive',
    'immobiliare',
    'salute',
    'turismo'
]

# Località da monitorare
LOCATIONS = [
    'italia',
    'europa', 
    'usa',
    'cina',
    'giappone',
    'germania',
    'francia',
    'regno unito'
]

# Siti web da analizzare
WEBSITES = [
    'https://www.ansa.it',
    'https://www.repubblica.it', 
    'https://www.corriere.it',
    'https://www.ilsole24ore.com',
    'https://www.lastampa.it',
    'https://www.ilgiornale.it'
]

# Parole chiave per mercati (personalizzabili)
MARKET_KEYWORDS = {
    'tecnologia': [
        'tech', 'tecnologia', 'software', 'ai', 'intelligenza artificiale', 
        'startup', 'digitale', 'internet', 'cloud', 'blockchain', 'crypto'
    ],
    'finanza': [
        'finanza', 'banking', 'banche', 'investimenti', 'mercati finanziari',
        'borsa', 'trading', 'azioni', 'obbligazioni', 'fondi'
    ],
    'energia': [
        'energia', 'petrolio', 'gas', 'rinnovabili', 'solare', 'eolico',
        'nucleare', 'carbone', 'elettricità', 'idrogeno'
    ],
    'automotive': [
        'auto', 'automotive', 'veicoli', 'trasporti', 'mobilità',
        'elettriche', 'guida autonoma', 'tesla', 'volkswagen'
    ],
    'immobiliare': [
        'immobiliare', 'real estate', 'case', 'proprietà', 'edilizia',
        'costruzioni', 'affitti', 'mutui', 'residential'
    ],
    'salute': [
        'salute', 'sanità', 'farmaceutico', 'medicina', 'ospedale',
        'covid', 'vaccini', 'biotech', 'healthcare'
    ],
    'turismo': [
        'turismo', 'viaggi', 'hotel', 'airline', 'crociere',
        'vacanze', 'hospitality', 'booking'
    ]
}

# Parole chiave per località
LOCATION_KEYWORDS = {
    'italia': [
        'italia', 'italy', 'romano', 'milano', 'napoli', 'torino',
        'florence', 'venice', 'italian', 'italiano'
    ],
    'europa': [
        'europa', 'europe', 'ue', 'european union', 'bruxelles',
        'eurozona', 'bce', 'european'
    ],
    'usa': [
        'usa', 'america', 'stati uniti', 'washington', 'new york',
        'california', 'texas', 'american', 'americano'
    ],
    'cina': [
        'cina', 'china', 'beijing', 'shanghai', 'hong kong',
        'chinese', 'cinese', 'pechino'
    ],
    'giappone': [
        'giappone', 'japan', 'tokyo', 'osaka', 'japanese',
        'giapponese', 'nikkei'
    ],
    'germania': [
        'germania', 'germany', 'berlino', 'monaco', 'frankfurt',
        'german', 'tedesco', 'dax'
    ],
    'francia': [
        'francia', 'france', 'parigi', 'paris', 'french',
        'francese', 'cac40'
    ],
    'regno unito': [
        'regno unito', 'uk', 'britain', 'london', 'londra',
        'british', 'britannico', 'ftse'
    ]
}

# Configurazione crawler
CRAWLER_CONFIG = {
    'max_articles_per_site': 20,
    'request_timeout': 30,
    'concurrent_requests': 5,
    'min_content_length': 200,
    'sentiment_threshold_positive': 60,
    'sentiment_threshold_negative': 40
}
