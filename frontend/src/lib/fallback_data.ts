export const FALLBACK_FOREX = {
  status: "success",
  source: "Nepal Rastra Bank (NRB) Official Reference",
  source_url: "https://www.nrb.org.np/forex/",
  date: "2026-10-14",
  rates: [
    { currency: "INR", name: "Indian Rupee (100)", unit: 100, buy: 160.00, sell: 160.15 },
    { currency: "USD", name: "U.S. Dollar", unit: 1, buy: 134.85, sell: 135.45 },
    { currency: "EUR", name: "European Euro", unit: 1, buy: 146.20, sell: 146.85 },
    { currency: "GBP", name: "UK Pound Sterling", unit: 1, buy: 175.40, sell: 176.18 },
    { currency: "CAD", name: "Canadian Dollar", unit: 1, buy: 97.55, sell: 97.98 },
    { currency: "AUD", name: "Australian Dollar", unit: 1, buy: 89.90, sell: 90.30 },
    { currency: "AED", name: "UAE Dirham", unit: 1, buy: 36.72, sell: 36.88 },
    { currency: "SAR", name: "Saudi Riyal", unit: 1, buy: 35.92, sell: 36.08 },
    { currency: "QAR", name: "Qatari Riyal", unit: 1, buy: 37.01, sell: 37.17 },
    { currency: "JPY", name: "Japanese Yen (10)", unit: 10, buy: 8.95, sell: 8.99 }
  ]
};

export const FALLBACK_STORIES = [
  {
    id: "np-jhapalish",
    display_title: "RONB Viral: Nepal Police Cyber Bureau Detains Content Creator 'Jhapalish' Over Obscene Social Media Content",
    topic: "national",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Routine of Nepal Banda reported that Kathmandu Valley Police and the Cyber Bureau took popular internet creator and rapper 'Jhapalish' into custody following complaints over obscene language and public nuisance on social media.",
    full_content: "Nepal Police Cyber Bureau and Kathmandu Valley Crime Investigation Office detained controversial content creator and internet personality Samir (widely known as 'Jhapalish') from Kathmandu for formal interrogation. The law enforcement action followed numerous complaints lodged by citizens regarding explicit language, abusive slurs, and disturbing public pranks distributed across TikTok and Facebook. Senior police officials confirmed that Jhapalish is being investigated under Section 47 of the Electronic Transactions Act regarding public decency and online conduct.",
    image_url: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Routine of Nepal Banda (RONB)",
    articles: [
      {
        id: "art-jhapalish",
        source_id: "src-ronb",
        publisher_name: "Routine of Nepal Banda (RONB)",
        canonical_url: "https://facebook.com/routineofnepalbanda/posts/jhapalish-detained-police",
        title: "Nepal Police Cyber Bureau Detains Content Creator Jhapalish",
        excerpt: "Police took internet creator Jhapalish into custody for questioning following public complaints.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-jhapalish",
        story_id: "np-jhapalish",
        claim_text: "Nepal Police Cyber Bureau took social media creator Jhapalish into custody for questioning.",
        context: "Kathmandu Valley Police Office Media Briefing",
        claim_status: "corroborated",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-jhapalish",
            source_url: "https://facebook.com/routineofnepalbanda/posts/jhapalish-detained-police",
            source_name: "Kathmandu Valley Police Office Media Cell",
            evidence_type: "official_statement",
            stance: "supports",
            excerpt: "Cyber Bureau confirmed the apprehension of Samir alias Jhapalish for questioning on public decency complaints."
          }
        ],
        reviews: [
          {
            id: "rev-jhapalish",
            reviewer_name: "Editorial Fact Desk",
            decision: "promoted_to_verified",
            rationale: "Verified with Kathmandu Valley Police Office Cyber Bureau press briefing.",
            policy_version: "v1.0",
            created_at: new Date().toISOString()
          }
        ]
      }
    ]
  },
  {
    id: "np-gold",
    display_title: "RONB Bullion Alert: Fine Gold Price Surges to All-Time Record of NPR 160,500 per Tola",
    topic: "business",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Routine of Nepal Banda shared bullion market data showing hallmark gold reaching an unprecedented NPR 160,500 per tola in Kathmandu amid global price spikes.",
    full_content: "According to Federation of Nepal Gold and Silver Dealers' Association (FENEGOSIDA), the domestic price of fine gold surged by NPR 1,200 in a single trading session, marking a new historical high. Routine of Nepal Banda highlighted the impact on festive wedding shoppers and local jewellery traders who reported moderated retail transactions despite heavy inquiries.",
    image_url: "https://images.unsplash.com/photo-1610375461246-83df859d849d?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Routine of Nepal Banda (RONB)",
    articles: [
      {
        id: "art-gold",
        source_id: "src-ronb",
        publisher_name: "Routine of Nepal Banda (RONB)",
        canonical_url: "https://facebook.com/routineofnepalbanda/posts/gold-historic-record-high",
        title: "Fine Gold Price Surges to All-Time Record of NPR 160,500 per Tola",
        excerpt: "Domestic 24-carat gold price hit a record high of NPR 160,500 per tola.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: []
  },
  {
    id: "np-1",
    display_title: "Nepal Rastra Bank Monetary Review: Foreign Exchange Reserves Surge Past $15.2 Billion",
    topic: "business",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Nepal's gross foreign exchange reserves reached an all-time high of NPR 2,041 billion ($15.2 billion), sufficient to finance prospective merchandise and services imports for over 12.8 months.",
    full_content: "The macroeconomic and financial report unveiled by Nepal Rastra Bank (NRB) for the current fiscal quarter confirms strong external sector stability. Buoyed by resilient remittance inflows averaging over NPR 115 billion per month and moderated import expenditure, the balance of payments (BOP) registered a healthy surplus. According to NRB Governor Maha Prasad Adhikari, the unprecedented buffer strengthens foreign currency reserves to absorb geopolitical supply chain volatilities while offering fiscal space for lower lending interest rates across commercial banks.",
    image_url: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Nepal Rastra Bank (NRB)",
    articles: [
      {
        id: "art-1",
        source_id: "src-1",
        publisher_name: "Nepal Rastra Bank",
        canonical_url: "https://www.nrb.org.np/notices/macroeconomic-report-oct2026",
        title: "Current Macroeconomic and Financial Situation of Nepal",
        excerpt: "Gross foreign exchange reserves increased by 19.8 percent in US Dollar terms.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-1",
        story_id: "np-1",
        claim_text: "Nepal's gross foreign exchange reserves exceeded NPR 2.04 trillion ($15.2 billion).",
        context: "NRB Quarterly Macroeconomic Review Table 2.1",
        claim_status: "corroborated",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-1",
            claim_id: "cl-1",
            source_url: "https://www.nrb.org.np/notices/macroeconomic-report-oct2026",
            source_name: "Nepal Rastra Bank Central Bank Release",
            evidence_type: "primary_doc",
            stance: "supports",
            excerpt: "Table 2.1 confirms total foreign exchange reserves reached NPR 2,041.10 billion equivalent to USD 15.27 billion as of the review period.",
            retrieved_at: new Date().toISOString()
          }
        ],
        reviews: [
          {
            id: "rev-1",
            claim_id: "cl-1",
            reviewer_name: "Senior Fact Checker (Economics Desk)",
            decision: "promoted_to_verified",
            rationale: "Verified directly against official Nepal Rastra Bank primary statistical bulletins.",
            policy_version: "v1.0",
            created_at: new Date().toISOString()
          }
        ]
      }
    ]
  },
  {
    id: "np-2",
    display_title: "Kathmandu-Tarai Expressway: Mahadevtar 3.3-km Twin Tunnel Achieves Full Breakthrough",
    topic: "national",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Nepal Army engineering units have completed the excavation and breakthrough of the 3.3-kilometer Mahadevtar tunnel, marking a major milestone for the Asian Highway standard expressway.",
    full_content: "The Kathmandu-Tarai/Madhesh Fast Track (Expressway) Project, being developed under the management of the Nepal Army, achieved breakthrough in both tubes of the Mahadevtar tunnel in Makwanpur. The 70.97-kilometer strategic highway will reduce travel time between the capital city Kathmandu and Nijgadh to barely one hour. Project Director Brigadier General Keshav Raj Bohara stated that 90.2% of the tunnel civil works and concrete lining are completed, two months ahead of the project timeline.",
    image_url: "https://images.unsplash.com/photo-1541888946425-d0fbb1861564?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Nepal Army Directorate of Public Relations",
    articles: [
      {
        id: "art-2",
        source_id: "src-2",
        publisher_name: "Nepal Army DPR",
        canonical_url: "https://nepalarmy.mil.np/news/fast-track-tunnel-breakthrough",
        title: "Nepal Army Confirms Mahadevtar Tunnel Breakthrough",
        excerpt: "Both eastern and western tubes successfully pierced through the mountain pass.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-2",
        story_id: "np-2",
        claim_text: "The 3.3 km Mahadevtar tunnel breakthrough has been fully achieved ahead of schedule.",
        context: "Nepal Army Directorate of Public Relations Press Statement",
        claim_status: "corroborated",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-2",
            claim_id: "cl-2",
            source_url: "https://nepalarmy.mil.np/news/fast-track-tunnel-breakthrough",
            source_name: "Nepal Army Directorate of Public Relations",
            evidence_type: "primary_doc",
            stance: "supports",
            excerpt: "Physical breakthrough completed for both 3,355-meter tubes with comprehensive geotechnical reinforcement.",
            retrieved_at: new Date().toISOString()
          }
        ],
        reviews: [
          {
            id: "rev-2",
            claim_id: "cl-2",
            reviewer_name: "Infrastructure Verification Desk",
            decision: "promoted_to_verified",
            rationale: "Confirmed via on-site inspection briefing and official military engineering gazette.",
            policy_version: "v1.0",
            created_at: new Date().toISOString()
          }
        ]
      }
    ]
  },
  {
    id: "np-3",
    display_title: "Routine of Nepal Banda Alert: Dense Fog and Rain Disrupt Domestic Flights at TIA",
    topic: "national",
    state: "developing",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Routine of Nepal Banda reported heavy morning fog and reduced runway visibility causing flight delays and diverts at Tribhuvan International Airport (TIA).",
    full_content: "According to breaking social wire alerts published by Routine of Nepal Banda (RONB), visibility at Kathmandu's Tribhuvan International Airport dropped below 1,500 meters during peak morning hours. Five domestic flights arriving from Pokhara, Biratnagar, and Bhairahawa were placed in holding patterns or diverted back to alternate regional aerodromes. Airlines have urged passengers to verify their flight statuses directly via airline counter hotlines while meteorological teams monitor the clearance window.",
    image_url: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 0,
    primary_source: "Routine of Nepal Banda (RONB)",
    articles: [
      {
        id: "art-3",
        source_id: "src-3",
        publisher_name: "Routine of Nepal Banda",
        canonical_url: "https://facebook.com/routineofnepalbanda/posts/tia-flight-weather-alert",
        title: "RONB Alert: TIA Domestic Flights Affected Due to Weather",
        excerpt: "Visibility dropped below minimum IFR landing thresholds.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-3",
        story_id: "np-3",
        claim_text: "Five inbound domestic flights were diverted away from Kathmandu airport due to weather.",
        context: "Social wire post by Routine of Nepal Banda",
        claim_status: "checking",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-3",
            claim_id: "cl-3",
            source_url: "https://caanepal.gov.np/tia/live-notam",
            source_name: "CAAN Airport Operations Control Center",
            evidence_type: "official_statement",
            stance: "context_only",
            excerpt: "NOTAM indicates CAT-I approach restrictions active between 06:30 and 08:45 AM due to low cloud ceiling.",
            retrieved_at: new Date().toISOString()
          }
        ],
        reviews: []
      }
    ]
  },
  {
    id: "np-4",
    display_title: "Nepal Tourism Board Records 1.15 Million International Tourists in Landmark Rebound",
    topic: "national",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Nepal welcomed 1,154,000 foreign tourists via air travel over the past calendar period, crossing pre-pandemic travel benchmarks with India, USA, and China leading arrivals.",
    full_content: "Data compiled by the Nepal Tourism Board (NTB) and Department of Immigration shows tourism arrivals surged by 21.4% year-over-year. High-altitude trekking permits issued for the Annapurna, Everest, and Manaslu conservation areas experienced unprecedented occupancy. The Ministry of Culture, Tourism and Civil Aviation commended the hospitality sector's resilience and announced new visa processing simplifications for overland and air transit travelers.",
    image_url: "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "The Kathmandu Post",
    articles: [
      {
        id: "art-4",
        source_id: "src-4",
        publisher_name: "The Kathmandu Post",
        canonical_url: "https://kathmandupost.com/travel/nepal-tourist-arrivals-hit-1-million-milestone",
        title: "Foreign tourist arrivals in Nepal surpass 1.15 million milestone",
        excerpt: "Official immigration figures confirm highest influx in four years as trekking season reaches peak.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-4",
        story_id: "np-4",
        claim_text: "Over 1.15 million international air visitors arrived in Nepal during the review cycle.",
        context: "Department of Immigration & NTB Monthly Bulletin",
        claim_status: "corroborated",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-4",
            claim_id: "cl-4",
            source_url: "https://ntb.gov.np/research-and-statistics",
            source_name: "Nepal Tourism Board (NTB) Research Directorate",
            evidence_type: "primary_doc",
            stance: "supports",
            excerpt: "Immigration port registers confirm cumulative air arrivals of 1,154,228 passengers across international terminals.",
            retrieved_at: new Date().toISOString()
          }
        ],
        reviews: [
          {
            id: "rev-4",
            claim_id: "cl-4",
            reviewer_name: "National Newsroom Lead",
            decision: "promoted_to_verified",
            rationale: "Cross-validated against Department of Immigration border control databases.",
            policy_version: "v1.0",
            created_at: new Date().toISOString()
          }
        ]
      }
    ]
  },
  {
    id: "np-5",
    display_title: "Upper Tamakoshi Hydropower Project Restores Full 456 MW Generation to National Grid",
    topic: "business",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    summary: "Nepal's premier 456-megawatt Upper Tamakoshi Hydroelectric Project in Dolakha has resumed peak turbine dispatch following comprehensive silt de-sedimentation works.",
    full_content: "Nepal Electricity Authority (NEA) load dispatch centers confirmed all six Pelton turbines at Upper Tamakoshi are operating at rated 456 MW output. Managing Director of Tamakoshi Hydropower Mohan Gautam verified that transmission voltage along the 220 kV Gongar-Khimti line is stable, significantly minimizing load balancing stress and enabling power exports to neighboring sub-regional transmission grids.",
    image_url: "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "OnlineKhabar English",
    articles: [
      {
        id: "art-5",
        source_id: "src-5",
        publisher_name: "OnlineKhabar English",
        canonical_url: "https://english.onlinekhabar.com/upper-tamakoshi-456mw-restored.html",
        title: "Upper Tamakoshi resumes 456 MW electricity dispatch at full capacity",
        excerpt: "All six turbines synchronised to national grid after seasonal maintenance completion.",
        language: "en",
        published_at: new Date().toISOString(),
        fetched_at: new Date().toISOString()
      }
    ],
    claims: [
      {
        id: "cl-5",
        story_id: "np-5",
        claim_text: "All six generating units at Upper Tamakoshi are dispatching at rated 456 MW capacity.",
        context: "Nepal Electricity Authority Load Dispatch Control Data",
        claim_status: "corroborated",
        extracted_at: new Date().toISOString(),
        evidence_items: [
          {
            id: "ev-5",
            claim_id: "cl-5",
            source_url: "https://nea.org.np/load-dispatch-daily-bulletin",
            source_name: "Nepal Electricity Authority Daily Generation Record",
            evidence_type: "primary_doc",
            stance: "supports",
            excerpt: "Gongar power house operational dispatch record logs 456.0 MW instantaneous power delivered at 50 Hz frequency.",
            retrieved_at: new Date().toISOString()
          }
        ],
        reviews: [
          {
            id: "rev-5",
            claim_id: "cl-5",
            reviewer_name: "Energy & Resource Editor",
            decision: "promoted_to_verified",
            rationale: "Validated against NEA telemetry grid telemetry feed.",
            policy_version: "v1.0",
            created_at: new Date().toISOString()
          }
        ]
      }
    ]
  },
  {
    id: "np-archive-rain",
    display_title: "RONB Archive: Historic Rainfall Breaks 44-Year Record in Kathmandu; Bagmati Water Levels Subside",
    topic: "weather",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
    summary: "Routine of Nepal Banda shared ground alerts as Kathmandu recorded 240mm precipitation in 24 hours before weather conditions stabilized.",
    full_content: "The Department of Hydrology and Meteorology (DHM) confirmed that the Kathmandu Valley recorded the highest single-day precipitation since 1981. Routine of Nepal Banda shared round-the-clock emergency helpline numbers and relief updates. The National Disaster Risk Reduction and Management Authority (NDRRMA) reported water levels across Bagmati, Bishnumati, and Hanumante rivers receded safely below danger thresholds.",
    image_url: "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Routine of Nepal Banda (RONB)",
    articles: [
      {
        id: "art-archive-rain",
        source_id: "src-ronb",
        publisher_name: "Routine of Nepal Banda (RONB)",
        canonical_url: "https://facebook.com/routineofnepalbanda/posts/archive-kathmandu-record-rain",
        title: "Historic Rainfall Breaks Record in Kathmandu Valley",
        excerpt: "Kathmandu recorded historic 240mm rainfall before water levels receded.",
        language: "en",
        published_at: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
        fetched_at: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString()
      }
    ],
    claims: []
  },
  {
    id: "np-archive-cricket",
    display_title: "RONB Archive: Nepal Defeats UAE by 7 Wickets to Lift ACC Men's Premier Cup",
    topic: "sports",
    state: "verified_summary",
    country_iso2: "NP",
    first_seen_at: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
    summary: "Routine of Nepal Banda captured euphoric scenes at Tribhuvan University Cricket Ground as Nepal secured qualification to the Asia Cup with a commanding 7-wicket victory.",
    full_content: "An inspired bowling spell from Lalit Rajbanshi and steady half-century from Gulsan Jha powered Nepal to a historic victory over the United Arab Emirates in the ACC Premier Cup final. Routine of Nepal Banda shared real-time video clips of 25,000 passionate spectators celebrating amidst celebratory fireworks at TU grounds.",
    image_url: "https://images.unsplash.com/photo-1531415074868-83633dd5e45c?auto=format&fit=crop&w=1200&q=80",
    articles_count: 1,
    claims_count: 1,
    verified_claims_count: 1,
    primary_source: "Routine of Nepal Banda (RONB)",
    articles: [
      {
        id: "art-archive-cricket",
        source_id: "src-ronb",
        publisher_name: "Routine of Nepal Banda (RONB)",
        canonical_url: "https://facebook.com/routineofnepalbanda/posts/archive-nepal-acc-premier-cup-champions",
        title: "Nepal Defeats UAE to Win ACC Men's Premier Cup",
        excerpt: "Nepal secured qualification to Asia Cup after lifting the trophy at TU grounds.",
        language: "en",
        published_at: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
        fetched_at: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString()
      }
    ],
    claims: []
  }
];
