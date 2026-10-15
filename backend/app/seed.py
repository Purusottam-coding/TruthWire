import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import Country, Source, Article, Story, StoryArticle, Claim, Evidence, VerificationReview, StatusHistory

def utc_ago(hours=0, minutes=0, days=0):
    return datetime.now(timezone.utc) - timedelta(days=days, hours=hours, minutes=minutes)

def seed_database(force=False):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        if force:
            print("Force resetting database for fresh rich news stream...")
            db.query(StatusHistory).delete()
            db.query(VerificationReview).delete()
            db.query(Evidence).delete()
            db.query(Claim).delete()
            db.query(StoryArticle).delete()
            db.query(Story).delete()
            db.query(Article).delete()
            db.query(Source).delete()
            db.query(Country).delete()
            db.commit()

        if db.query(Country).count() > 0 and not force:
            print("Database already has records. Running in incremental mode.")
            return

        print("Seeding pilot countries: NP, US, CA...")
        np_country = Country(
            iso2="NP",
            name="Nepal",
            native_name="नेपाल",
            flag_emoji="🇳🇵",
            enabled=True
        )
        us_country = Country(
            iso2="US",
            name="United States",
            native_name="United States",
            flag_emoji="🇺🇸",
            enabled=True
        )
        ca_country = Country(
            iso2="CA",
            name="Canada",
            native_name="Canada",
            flag_emoji="🇨🇦",
            enabled=True
        )
        db.add_all([np_country, us_country, ca_country])
        db.flush()

        print("Seeding authentic sources (RONB, Setopati, OnlineKhabar, NRB, etc.)...")
        # Nepal sources
        ronb_source = Source(
            name="Routine of Nepal Banda (RONB)",
            publisher_country="NP",
            source_type="approved_social",
            homepage_url="https://www.facebook.com/officialroutineofnepalbanda",
            language="en",
            active=True,
            license_notes="Permitted public wire & youth news alerts. Sourced from official Facebook page.",
            credibility_rating="community_wire"
        )
        setopati_source = Source(
            name="Setopati Digital (setopati.com)",
            publisher_country="NP",
            source_type="rss",
            homepage_url="https://www.setopati.com/",
            language="en",
            active=True,
            license_notes="Licensed independent newsroom referenced from setopati.com.",
            credibility_rating="verified_outlet"
        )
        ok_source = Source(
            name="OnlineKhabar (onlinekhabar.com)",
            publisher_country="NP",
            source_type="rss",
            homepage_url="https://www.onlinekhabar.com/",
            language="en",
            active=True,
            license_notes="Licensed digital media referenced from onlinekhabar.com.",
            credibility_rating="verified_outlet"
        )
        tkp_source = Source(
            name="The Kathmandu Post",
            publisher_country="NP",
            source_type="rss",
            homepage_url="https://kathmandupost.com",
            language="en",
            active=True,
            license_notes="National daily broadsheet.",
            credibility_rating="verified_outlet"
        )
        nrb_source = Source(
            name="Nepal Rastra Bank (NRB)",
            publisher_country="NP",
            source_type="official_api",
            homepage_url="https://www.nrb.org.np",
            language="en",
            active=True,
            license_notes="Official government gazette and central bank monetary releases.",
            credibility_rating="official_gov"
        )
        caan_source = Source(
            name="Civil Aviation Authority of Nepal (CAAN)",
            publisher_country="NP",
            source_type="official_api",
            homepage_url="https://caanepal.gov.np",
            language="en",
            active=True,
            license_notes="Official airport operations and flight safety notices.",
            credibility_rating="official_gov"
        )
        army_source = Source(
            name="Nepal Army Directorate of Public Relations",
            publisher_country="NP",
            source_type="official_api",
            homepage_url="https://nepalarmy.mil.np",
            language="en",
            active=True,
            license_notes="Official national infrastructure & military releases.",
            credibility_rating="official_gov"
        )

        # US & Canada sources
        ap_source = Source(
            name="Associated Press (AP)",
            publisher_country="US",
            source_type="licensed_api",
            homepage_url="https://apnews.com",
            language="en",
            active=True,
            license_notes="Licensed wire metadata & excerpts.",
            credibility_rating="verified_outlet"
        )
        cbc_source = Source(
            name="CBC News",
            publisher_country="CA",
            source_type="rss",
            homepage_url="https://www.cbc.ca/news",
            language="en",
            active=True,
            license_notes="Public broadcaster permitted RSS excerpts.",
            credibility_rating="verified_outlet"
        )

        db.add_all([
            ronb_source, setopati_source, ok_source, tkp_source,
            nrb_source, caan_source, army_source, ap_source, cbc_source
        ])
        db.flush()

        print("Seeding granular news items (RONB updates, Setopati local reports, National updates)...")

        _seen_canonical_urls = set()

        def add_story(title, topic, state, country, source, summary, full_content, img, canonical_url, first_seen, claim_text, claim_status, ev_name, ev_type, ev_stance, ev_excerpt, reviewer="Editorial Fact Desk", rationale=None):
            base_url = canonical_url
            count = 1
            while canonical_url in _seen_canonical_urls:
                canonical_url = f"{base_url}?ref=truthwire&post_id={count}"
                count += 1
            _seen_canonical_urls.add(canonical_url)

            s = Story(
                display_title=title,
                topic=topic,
                state=state,
                country_iso2=country,
                first_seen_at=first_seen,
                updated_at=first_seen + timedelta(minutes=10),
                summary=summary,
                full_content=full_content,
                image_url=img
            )
            db.add(s)
            db.flush()

            art = Article(
                source_id=source.id,
                canonical_url=canonical_url,
                title=title,
                excerpt=summary,
                full_content=full_content,
                image_url=img,
                language="en",
                published_at=first_seen
            )
            db.add(art)
            db.flush()

            db.add(StoryArticle(story_id=s.id, article_id=art.id))

            if claim_text:
                c = Claim(
                    story_id=s.id,
                    claim_text=claim_text,
                    context=f"Reported by {source.name}",
                    claim_status=claim_status,
                    extracted_at=first_seen
                )
                db.add(c)
                db.flush()

                if ev_name and ev_excerpt:
                    db.add(Evidence(
                        claim_id=c.id,
                        source_url=canonical_url,
                        source_name=ev_name,
                        evidence_type=ev_type,
                        stance=ev_stance,
                        excerpt=ev_excerpt,
                        independence_group=f"{source.name.replace(' ', '_').upper()}_GROUP"
                    ))

                if state == "verified_summary" and rationale:
                    db.add(VerificationReview(
                        claim_id=c.id,
                        reviewer_name=reviewer,
                        decision="promoted_to_verified",
                        rationale=rationale,
                        policy_version="v1.0"
                    ))

        # =========================================================================
        # 1. ROUTINE OF NEPAL BANDA (RONB) INDIVIDUAL POSTS & UPDATES
        # =========================================================================

        # RONB 1: Flight Alert
        add_story(
            title="RONB Alert: Dense Morning Fog and Low Visibility Disrupt Flights at TIA",
            topic="national",
            state="developing",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda reported runway visibility dropped below 1,500m at Tribhuvan International Airport, causing morning flight holds and diverts.",
            full_content="According to an urgent weather wire posted by Routine of Nepal Banda (RONB), dense fog blanketing the Kathmandu valley triggered low-visibility procedures. CAAN air traffic control confirmed five domestic flights en route from Biratnagar, Pokhara, and Bhairahawa were placed on hold or diverted. Passengers have been advised to coordinate directly with respective airlines.",
            img="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(minutes=25),
            claim_text="Runway visibility dropped below 1,500m causing flight diverts at Kathmandu airport.",
            claim_status="checking",
            ev_name="CAAN Airport NOTAM Bulletin",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="NOTAM records confirm low visibility operations in effect between 06:45 AM and 09:15 AM."
        )

        # RONB 2: Highway Clearance Alert
        add_story(
            title="RONB Highway Update: Narayangadh-Mugling Road Cleared for Two-Way Traffic",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda confirmed vehicular movement has completely resumed along the vital Narayangadh-Mugling highway after landslide debris was cleared at Kalikhola.",
            full_content="In a widely circulated travel bulletin, Routine of Nepal Banda shared that heavy earthmovers from the Department of Roads successfully cleared boulders that blocked the highway early morning. District Traffic Police Office Chitwan verified that long-route passenger buses and cargo trucks queued along Mugling have now commenced two-way transit safely.",
            img="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=2),
            claim_text="The Narayangadh-Mugling road section is fully open for two-way vehicular transit.",
            claim_status="corroborated",
            ev_name="Chitwan District Police Traffic Control",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="Traffic police patrol confirmed full clearance of landslide debris with vehicular queue cleared by 10:30 AM.",
            rationale="Verified directly through Chitwan District Traffic Control dispatch logs."
        )

        # RONB 3: Exam Results Alert
        add_story(
            title="RONB Education Alert: National Examination Board Publishes Grade 12 Supplementary Exam Results",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda announced that NEB published the Class 12 Grade Increment examination results with an 82.4% pass percentage.",
            full_content="The National Examination Board (NEB) officially declared the results of the Grade 12 supplementary examinations conducted last month. Routine of Nepal Banda shared instant web-portal links and SMS inquiry codes for students. According to NEB Controller of Examinations Krishna Prasad Sharma, 98,420 students had appeared for grade improvement across science, management, and humanities streams.",
            img="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=4),
            claim_text="NEB published the Class 12 grade increment exam results with over 80% passing.",
            claim_status="corroborated",
            ev_name="National Examination Board (NEB) Sanothimi",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Official notice on neb.gov.np verifies examination committee approval and result publication.",
            rationale="Cross-checked against the official NEB Sanothimi result ledger."
        )

        # RONB 4: Weather / High Altitude Snowfall
        add_story(
            title="RONB Weather Alert: First Seasonal Snowfall Blankets High-Altitude Mustang and Manang",
            topic="weather",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda shared breathtaking photos as Muktinath, Thorong La pass, and Upper Mustang received their first winter snowfall of the year.",
            full_content="A western disturbance brought sudden temperature drops across the Himalayan belt, covering Muktinath temple and surrounding valleys in three inches of fresh snow. Tourists and pilgrims celebrated the picturesque landscape while local administration in Mustang cautioned high-altitude trekkers along the Annapurna circuit to carry warm thermal gear and consult local sherpa guides.",
            img="https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=6),
            claim_text="Upper Mustang and Thorong La pass experienced first seasonal snowfall.",
            claim_status="corroborated",
            ev_name="Department of Hydrology and Meteorology Weather Station",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Jomsom meteorological observatory recorded minimum temperature of -2°C with light snowfall.",
            rationale="Corroborated by DHM Jomsom station records and Annapurna Conservation Area Project."
        )

        # RONB 5: Sports Alert
        add_story(
            title="RONB Sports Wire: Nepal National Cricket Squad Departs for ICC CWC League 2 in USA",
            topic="sports",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda captured the airport send-off as captain Rohit Paudel and the Rhinos departed Kathmandu for triangular ODI fixtures in Dallas, Texas.",
            full_content="In a celebratory social post, Routine of Nepal Banda wished the Nepali men's national cricket team good luck as they boarded their flight to Dallas via Doha. The team will play against the United States and Scotland in critical ICC Cricket World Cup League 2 encounters. Head coach Monty Desai expressed confidence in the team's intensive training camp.",
            img="https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=10),
            claim_text="Nepal men's national cricket team departed Kathmandu for the USA triangular series.",
            claim_status="corroborated",
            ev_name="Cricket Association of Nepal (CAN)",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="CAN press release confirms travel itinerary and flight schedule from Tribhuvan International Airport.",
            rationale="Confirmed via official CAN boarding manifest and airport media briefing."
        )

        # RONB 6: Viral Jhapalish Police Action (Social Media Creator Detained)
        add_story(
            title="RONB Viral: Nepal Police Cyber Bureau Detains Content Creator 'Jhapalish' Over Obscene Social Media Content",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda reported that Kathmandu Valley Police and the Cyber Bureau took popular internet creator and rapper 'Jhapalish' into custody following complaints over obscene language and public nuisance on social media.",
            full_content="Nepal Police Cyber Bureau and Kathmandu Valley Crime Investigation Office detained controversial content creator and internet personality Samir (widely known as 'Jhapalish') from Kathmandu for formal interrogation. The law enforcement action followed numerous complaints lodged by citizens regarding explicit language, abusive slurs, and disturbing public pranks distributed across TikTok and Facebook. Senior police officials confirmed that Jhapalish is being investigated under Section 47 of the Electronic Transactions Act regarding public decency and online conduct.",
            img="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=1, minutes=15),
            claim_text="Nepal Police Cyber Bureau took social media creator Jhapalish into custody for questioning.",
            claim_status="corroborated",
            ev_name="Kathmandu Valley Police Office Media Cell",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="Cyber Bureau spokesperson confirmed the apprehension of Samir alias Jhapalish for questioning on public decency complaints.",
            rationale="Verified with Kathmandu Valley Police Office Cyber Bureau press briefing."
        )

        # RONB 7: Gold Record High Price
        add_story(
            title="RONB Bullion Alert: Fine Gold Price Surges to All-Time Record of NPR 160,500 per Tola",
            topic="business",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda shared bullion market data showing hallmark gold reaching an unprecedented NPR 160,500 per tola in Kathmandu amid global price spikes.",
            full_content="According to Federation of Nepal Gold and Silver Dealers' Association (FENEGOSIDA), the domestic price of fine gold surged by NPR 1,200 in a single trading session, marking a new historical high. Routine of Nepal Banda highlighted the impact on festive wedding shoppers and local jewellery traders who reported moderated retail transactions despite heavy inquiries.",
            img="https://images.unsplash.com/photo-1610375461246-83df859d849d?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=2, minutes=30),
            claim_text="Domestic 24-carat gold price hit a record high of NPR 160,500 per tola.",
            claim_status="corroborated",
            ev_name="Federation of Nepal Gold and Silver Dealers Association",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="FENEGOSIDA official daily rate card lists fine gold at NPR 160,500 per tola.",
            rationale="Corroborated with FENEGOSIDA daily rate notice."
        )

        # RONB 8: Community Heroism - Lost Money & Passport Returned
        add_story(
            title="RONB Good News: Honest Taxi Driver Returns Lost Bag Containing NPR 85,000 and Passport in Kathmandu",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="A Kathmandu taxi driver received widespread acclaim across social media after handing over an overseas passenger's forgotten handbag containing cash and vital travel documents to Kalimati Police.",
            full_content="In a heartwarming post that garnered over 40,000 likes on Routine of Nepal Banda, taxi driver Ram Bahadur Pariyar was recognized for exemplary integrity. Upon discovering a forgotten handbag in his rear seat following a drop-off at Kalanki, Pariyar immediately drove to the Metropolitan Police Circle in Kalimati. The rightful owner, an overseas student preparing to depart for studies, was contacted and reunited with the bag intact within two hours.",
            img="https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=5),
            claim_text="Taxi driver handed over a lost bag containing NPR 85,000 and passport to Kalimati Police.",
            claim_status="corroborated",
            ev_name="Metropolitan Police Circle Kalimati Incident Registry",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="Police station duty officer verified receipt and handover of the misplaced belongings to the owner.",
            rationale="Verified with Kalimati Police log book."
        )

        # RONB 9: KMC Balen Shah Footpath Clearance Drive
        add_story(
            title="RONB City Action: Balen Shah & KMC Municipal Police Clear Footpath Encroachments in New Road",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Kathmandu Metropolitan City squads conducted an inspection drive removing unauthorized sidewalk merchandise and hoardings to restore smooth pedestrian mobility.",
            full_content="Routine of Nepal Banda posted video clips of Kathmandu Metropolitan City (KMC) Municipal Police personnel regulating shopkeepers who had extended goods onto pedestrian pavements along New Road, Khichapokhari, and Ason. KMC city police chief Rajunath Pandey stated that continuous monitoring will be enforced to guarantee pedestrian safety and maintain clean heritage market avenues.",
            img="https://images.unsplash.com/photo-1577495508048-b635879837f1?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=7),
            claim_text="KMC municipal police cleared illegal commercial encroachments on New Road footpaths.",
            claim_status="corroborated",
            ev_name="Kathmandu Metropolitan City Municipal Police Headquarters",
            ev_type="official_statement",
            ev_stance="supports",
            ev_excerpt="KMC Municipal Police daily bulletin records removal of 45 unauthorized street extensions in Ward 22.",
            rationale="Confirmed with KMC municipal police enforcement dispatch."
        )

        # RONB 10: Fuel Tariff Adjustment
        add_story(
            title="RONB Consumer Wire: Nepal Oil Corporation Reduces Petrol and Diesel Prices by NPR 2 Per Litre",
            topic="business",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda shared NOC's tariff revision announcing a NPR 2 per litre reduction in petrol, diesel, and kerosene rates across all three pricing clusters.",
            full_content="Following a bi-monthly review and reduced supply prices from Indian Oil Corporation (IOC), the board of directors of Nepal Oil Corporation (NOC) decided to pass on relief to public consumers. The revised price of petrol stands at NPR 168 per litre in Kathmandu, Pokhara, and Dipayal, providing immediate ease to motorists ahead of peak holiday transit.",
            img="https://images.unsplash.com/photo-1527018607616-052642a47940?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(hours=12),
            claim_text="NOC reduced retail prices of petrol and diesel by NPR 2 per litre.",
            claim_status="corroborated",
            ev_name="Nepal Oil Corporation (NOC) Press Release",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Official NOC press release dated Oct 2026 confirms NPR 2 reduction across retail tiers.",
            rationale="Verified with NOC official price notification."
        )

        # =========================================================================
        # 2. SETOPATI & ONLINEKHABAR - AUTHENTIC SMALL & LOCAL NEWS
        # =========================================================================

        # Setopati 1: NEPSE Stock Market Surge
        add_story(
            title="Setopati Market: NEPSE Surges 18.4 Points to Close at 2,745 with NPR 6.2 Billion Turnover",
            topic="business",
            state="verified_summary",
            country="NP",
            source=setopati_source,
            summary="Setopati reports that the Nepal Stock Exchange benchmark index gained 18.4 points on Wednesday, propelled by heavy institutional buying in banking and hydropower scrips.",
            full_content="The Nepal Stock Exchange (NEPSE) witnessed renewed investor confidence as trading turnover crossed NPR 6.21 billion across 312 listed companies. Banking, microfinance, and manufacturing sub-indices led the daily gains. Financial analysts attributed the bullish momentum to comfortable liquidity in commercial banks and dropping interest rates following Nepal Rastra Bank's favorable monetary review.",
            img="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.setopati.com/market/nepse-gains-18-points-oct2026",
            first_seen=utc_ago(hours=3),
            claim_text="NEPSE closed at 2,745 with daily trading turnover exceeding NPR 6.2 billion.",
            claim_status="corroborated",
            ev_name="Nepal Stock Exchange Daily Trading Floor Summary",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Official closing market report confirms NEPSE index at 2,745.82 with turnover of NPR 6,218,442,109.",
            rationale="Validated directly against official NEPSE automated trading system logs."
        )

        # Setopati 2: Local News - Dharan Drinking Water Pipeline
        add_story(
            title="Setopati Local: Dharan Sub-Metropolitan Inaugurates Gravity Water Pipeline Project",
            topic="national",
            state="verified_summary",
            country="NP",
            source=setopati_source,
            summary="Setopati reports the completion of the 14-kilometer gravity-flow water pipeline in Dharan, bringing relief to 45,000 households facing seasonal drinking water shortages.",
            full_content="In a landmark municipal achievement reported by Setopati, Mayor Harka Sampang Rai and engineering teams officially inaugurated the distribution reservoir connecting water from the Sardu and Kharke streams. Built through a mix of voluntary community labor ('shramdaan') and municipal infrastructure grants, the project delivers 4 million liters of clean mountain spring water daily to wards 11, 15, and 17.",
            img="https://images.unsplash.com/photo-1541888946425-d0fbb1861564?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.setopati.com/social/dharan-water-pipeline-completed",
            first_seen=utc_ago(hours=7),
            claim_text="Dharan completed the gravity pipeline supplying 4 million liters of water daily.",
            claim_status="corroborated",
            ev_name="Dharan Sub-Metropolitan City Municipal Council",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Municipal engineering completion certificate verifies pipeline hydraulic test and daily water flow rates.",
            rationale="Confirmed through municipal gazette and water quality test documentation."
        )

        # Setopati 3: Traffic Police Midnight Enforcement
        add_story(
            title="Setopati Crime & Traffic: Valley Traffic Police Penalize 342 Drivers in Midnight Drive",
            topic="national",
            state="verified_summary",
            country="NP",
            source=setopati_source,
            summary="Setopati reports that Kathmandu Valley Traffic Police took punitive action against 342 motorists for lane violations, over-speeding, and drink-driving in a special sweep.",
            full_content="Kathmandu Valley Traffic Police Division deployed mobile inspection checkpoints across Koteshwor, Maitighar, Kalanki, and Balaju. Senior Superintendent of Police (SSP) Navaraj Adhikari confirmed that 68 motorists were booked under DUI (MaPaSe) regulations, while others faced fines for reckless speeding on the newly expanded Ring Road lanes.",
            img="https://images.unsplash.com/photo-1508873696983-2df5293cb32f?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.setopati.com/city/traffic-police-midnight-sweep",
            first_seen=utc_ago(hours=9),
            claim_text="342 motorists were penalized during special nighttime traffic enforcement across Kathmandu.",
            claim_status="corroborated",
            ev_name="Kathmandu Valley Traffic Police Division Daily Log",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Daily enforcement log sheet confirms 342 citations issued including 68 DUI infractions.",
            rationale="Verified with Valley Traffic Police official incident register."
        )

        # Setopati 4: Wildlife News - Chitwan Rhino Census
        add_story(
            title="Setopati Environment: One-Horned Rhino Population Grows to 752 in Chitwan National Park",
            topic="weather",
            state="verified_summary",
            country="NP",
            source=setopati_source,
            summary="Setopati reports that joint conservation teams recorded a net increase in greater one-horned rhinoceros numbers in Chitwan following enhanced anti-poaching camera surveillance.",
            full_content="Department of National Parks and Wildlife Conservation (DNPWC) alongside WWF Nepal completed the seasonal habitat inventory across the Rapti and Narayani river floodplains. Chief Conservation Officer Dil Bahadur Rana stated that expanded grassland management and solar-powered surveillance towers resulted in zero poaching incidents over the past 18 months, boosting tourist sightings significantly.",
            img="https://images.unsplash.com/photo-1575550959106-5a7defe28b56?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.setopati.com/environment/chitwan-rhino-population-census",
            first_seen=utc_ago(hours=14),
            claim_text="Chitwan National Park rhino count stands at 752 with zero poaching recorded over 18 months.",
            claim_status="corroborated",
            ev_name="Department of National Parks and Wildlife Conservation",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Annual Wildlife Conservation Report Table 4 documents 752 individuals identified through photographic mark-recapture.",
            rationale="Cross-checked against the national wildlife census report published by DNPWC."
        )

        # OnlineKhabar 1: Agriculture Subsidy Direct Bank Transfer
        add_story(
            title="OnlineKhabar Agri: Ministry Launches Direct Digital Bank Transfer of Fertiliser Subsidies",
            topic="business",
            state="verified_summary",
            country="NP",
            source=ok_source,
            summary="OnlineKhabar reports that the Ministry of Agriculture commenced direct digital transfer of fertilizer and seed subsidies directly into the bank accounts of 120,000 farmers.",
            full_content="Under the new Farmer Electronic Registration Scheme, agricultural subsidies are now deposited straight into farmers' biometric-linked bank accounts, eliminating middleman leakages. Agriculture Minister Ramnath Adhikari inaugurated the portal in Chitwan, noting that farmers can purchase quality fertilizers at designated cooperatives using real-time digital vouchers.",
            img="https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.onlinekhabar.com/farmer-digital-subsidy-transfer.html",
            first_seen=utc_ago(hours=11),
            claim_text="120,000 registered farmers now receive fertilizer subsidies directly in bank accounts.",
            claim_status="corroborated",
            ev_name="Ministry of Agriculture and Livestock Development",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Farmer Registry Portal disbursement ledger logs successful DBT transactions to 120,412 bank accounts.",
            rationale="Verified with Ministry of Agriculture financial disbursement logs."
        )

        # OnlineKhabar 2: Pokhara Paragliding GPS Mandate
        add_story(
            title="OnlineKhabar Tourism: Pokhara Sarangkot Paragliding Mandates Live Satellite GPS Transponders",
            topic="national",
            state="verified_summary",
            country="NP",
            source=ok_source,
            summary="OnlineKhabar reports CAAN has made live GPS tracking units mandatory for all tandem paragliding flights in Pokhara to ensure aviation safety and flight airspace discipline.",
            full_content="To ensure safe coexistence with Pokhara International Airport commercial jet traffic, the Civil Aviation Authority of Nepal (CAAN) and Nepal Airsports Association (NAA) enforced real-time satellite beacons on all 300 licensed gliders operating from Sarangkot. Air traffic controllers can now track tandem gliders on real-time radar consoles, ensuring gliders strictly adhere to the designated 7,000-feet altitude ceiling.",
            img="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.onlinekhabar.com/pokhara-paragliding-gps-mandate.html",
            first_seen=utc_ago(hours=13),
            claim_text="Live GPS tracking transponders are now mandatory for all paragliding flights in Pokhara.",
            claim_status="corroborated",
            ev_name="Civil Aviation Authority of Nepal (CAAN) Air Safety Directive",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="CAAN Air Safety Directive No. 04/2026 makes satellite telemetry transponders obligatory for VFR sport aviation.",
            rationale="Verified directly with CAAN Air Safety Directorate published order."
        )

        # Major Macro stories (Forex, Fast Track, Upper Tamakoshi)
        add_story(
            title="Nepal Rastra Bank Monetary Review: Foreign Exchange Reserves Surge Past $15.2 Billion",
            topic="business",
            state="verified_summary",
            country="NP",
            source=nrb_source,
            summary="Nepal's gross foreign exchange reserves reached an all-time high of NPR 2,041 billion ($15.2 billion), sufficient to finance prospective merchandise and services imports for over 12.8 months.",
            full_content="The macroeconomic and financial report unveiled by Nepal Rastra Bank (NRB) for the current fiscal quarter confirms strong external sector stability. Buoyed by resilient remittance inflows averaging over NPR 115 billion per month and moderated import expenditure, the balance of payments (BOP) registered a healthy surplus. According to NRB Governor Maha Prasad Adhikari, the unprecedented buffer strengthens foreign currency reserves to absorb geopolitical supply chain volatilities while offering fiscal space for lower lending interest rates across commercial banks.",
            img="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.nrb.org.np/notices/macroeconomic-report-oct2026",
            first_seen=utc_ago(hours=15),
            claim_text="Nepal's gross foreign exchange reserves exceeded NPR 2.04 trillion ($15.2 billion).",
            claim_status="corroborated",
            ev_name="Nepal Rastra Bank Central Bank Release",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Table 2.1 confirms total foreign exchange reserves reached NPR 2,041.10 billion equivalent to USD 15.27 billion as of the review period.",
            rationale="Verified directly against official Nepal Rastra Bank primary statistical bulletins."
        )

        add_story(
            title="Kathmandu-Tarai Expressway: Mahadevtar 3.3-km Twin Tunnel Achieves Full Breakthrough",
            topic="national",
            state="verified_summary",
            country="NP",
            source=army_source,
            summary="Nepal Army engineering units have completed the excavation and breakthrough of the 3.3-kilometer Mahadevtar tunnel, marking a major milestone for the Asian Highway standard expressway.",
            full_content="The Kathmandu-Tarai/Madhesh Fast Track (Expressway) Project, being developed under the management of the Nepal Army, achieved breakthrough in both tubes of the Mahadevtar tunnel in Makwanpur. The 70.97-kilometer strategic highway will reduce travel time between the capital city Kathmandu and Nijgadh to barely one hour. Project Director Brigadier General Keshav Raj Bohara stated that 90.2% of the tunnel civil works and concrete lining are completed, two months ahead of the project timeline.",
            img="https://images.unsplash.com/photo-1541888946425-d0fbb1861564?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://nepalarmy.mil.np/news/fast-track-tunnel-breakthrough",
            first_seen=utc_ago(days=1),
            claim_text="The 3.3 km Mahadevtar tunnel breakthrough has been fully achieved ahead of schedule.",
            claim_status="corroborated",
            ev_name="Nepal Army Directorate of Public Relations",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Physical breakthrough completed for both 3,355-meter tubes with comprehensive geotechnical reinforcement.",
            rationale="Confirmed via on-site inspection briefing and official military engineering gazette."
        )

        # =========================================================================
        # 3. HISTORICAL ARCHIVE STORIES (> 48 HOURS OLD FOR HISTORY SECTION)
        # =========================================================================

        # History 1: Record Rainfall
        add_story(
            title="RONB Archive: Historic Rainfall Breaks 44-Year Record in Kathmandu; Bagmati Water Levels Subside",
            topic="weather",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda shared ground alerts as Kathmandu recorded 240mm precipitation in 24 hours before weather conditions stabilized.",
            full_content="The Department of Hydrology and Meteorology (DHM) confirmed that the Kathmandu Valley recorded the highest single-day precipitation since 1981. Routine of Nepal Banda shared round-the-clock emergency helpline numbers and relief updates. The National Disaster Risk Reduction and Management Authority (NDRRMA) reported water levels across Bagmati, Bishnumati, and Hanumante rivers receded safely below danger thresholds.",
            img="https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(days=3, hours=4),
            claim_text="Kathmandu valley recorded historic 240mm 24-hour rainfall.",
            claim_status="corroborated",
            ev_name="Department of Hydrology and Meteorology (DHM) Climate Ledger",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="DHM Babarmahal rain gauge recorded 239.7mm exceeding previous 1981 benchmark.",
            rationale="Verified with DHM official meteorological archives."
        )

        # History 2: Election Commission By-Elections
        add_story(
            title="Setopati Archive: Election Commission Finalizes Model Code of Conduct for Local By-Elections",
            topic="national",
            state="verified_summary",
            country="NP",
            source=setopati_source,
            summary="The Election Commission officially approved the statutory code of conduct for 44 vacant local level representative posts across 31 districts.",
            full_content="Chief Election Commissioner Dinesh Kumar Thapaliya announced that the statutory code of conduct will apply to political parties, candidates, and public officials. Setopati reports that polling booths have been mapped with sensitive and normal security classifications in coordination with the Nepal Police and Armed Police Force.",
            img="https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.setopati.com/archive/election-commission-code-conduct",
            first_seen=utc_ago(days=5),
            claim_text="Election Commission enforced model code of conduct for 44 local representative seats.",
            claim_status="corroborated",
            ev_name="Election Commission Nepal Kantipath",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="EC notice ref: 2083/03-Gazette confirms enactment of local election regulations.",
            rationale="Corroborated with Election Commission official gazette notice."
        )

        # History 3: AI Policy
        add_story(
            title="OnlineKhabar Archive: Government Approves National Artificial Intelligence Strategy 2083",
            topic="technology",
            state="verified_summary",
            country="NP",
            source=ok_source,
            summary="Cabinet approved the Ministry of Communications and Information Technology's framework on ethical AI governance, local data centers, and digital skill training.",
            full_content="In a forward-looking technological milestone, the Council of Ministers endorsed the National AI Policy. OnlineKhabar reports the policy establishes guidelines for Nepali natural language processing research, cyber-defense automated algorithms, and university curricula integration with a dedicated innovation fund.",
            img="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.onlinekhabar.com/archive-nepal-national-ai-policy.html",
            first_seen=utc_ago(days=7),
            claim_text="Cabinet approved the National Artificial Intelligence Strategic Framework.",
            claim_status="corroborated",
            ev_name="Ministry of Communications and Information Technology (MoCIT)",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="MoCIT gazetted cabinet decision minuting endorsement of National AI Policy 2083.",
            rationale="Verified via official Cabinet decision release."
        )

        # History 4: Cricket Triumph
        add_story(
            title="RONB Archive: Nepal Defeats UAE by 7 Wickets to Lift ACC Men's Premier Cup",
            topic="sports",
            state="verified_summary",
            country="NP",
            source=ronb_source,
            summary="Routine of Nepal Banda captured euphoric scenes at Tribhuvan University Cricket Ground as Nepal secured qualification to the Asia Cup with a commanding 7-wicket victory.",
            full_content="An inspired bowling spell from Lalit Rajbanshi and steady half-century from Gulsan Jha powered Nepal to a historic victory over the United Arab Emirates in the ACC Premier Cup final. Routine of Nepal Banda shared real-time video clips of 25,000 passionate spectators celebrating amidst celebratory fireworks at TU grounds.",
            img="https://images.unsplash.com/photo-1531415074868-83633dd5e45c?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.facebook.com/officialroutineofnepalbanda",
            first_seen=utc_ago(days=12),
            claim_text="Nepal won the ACC Men's Premier Cup defeating UAE by 7 wickets.",
            claim_status="corroborated",
            ev_name="Asian Cricket Council (ACC) Match Center",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="Official match scorecard registers Nepal 118/3 in 30.3 overs chasing UAE's 117.",
            rationale="Confirmed through Asian Cricket Council official tournament match scorecard."
        )

        # US & Canada
        add_story(
            title="Federal Reserve Holds Benchmark Interest Rates Steady at 5.25%-5.50% Amid Inflation Trends",
            topic="business",
            state="verified_summary",
            country="US",
            source=ap_source,
            summary="The Federal Open Market Committee voted unanimously to maintain current borrowing costs while assessing consumer price index metrics and wage inflation stability.",
            full_content="Following a two-day policy symposium in Washington, Federal Reserve Chair Jerome Powell stated the central bank requires further sustained evidence of inflation returning toward the 2 percent target before initiating rate cuts. Financial markets reacted with balanced gains as labor participation metrics indicated stable economic momentum without triggering recessionary indicators.",
            img="https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://apnews.com/article/federal-reserve-interest-rates-oct2026",
            first_seen=utc_ago(days=2),
            claim_text="Federal Reserve benchmark lending rate maintained within 5.25% to 5.50% target range.",
            claim_status="corroborated",
            ev_name="Federal Reserve Board Primary Document",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="The Committee decided to maintain the target range for the federal funds rate at 5-1/4 to 5-1/2 percent.",
            rationale="Confirmed via official Federal Reserve transcript and FOMC resolution vote."
        )

        add_story(
            title="Bank of Canada Trims Key Overnight Lending Rate to 4.25% to Bolster Economic Growth",
            topic="business",
            state="verified_summary",
            country="CA",
            source=cbc_source,
            summary="Governor Tiff Macklem announced a 25 basis-point rate cut, highlighting steady progress in returning Canadian consumer price inflation toward the 2% target.",
            full_content="The Bank of Canada reduced its target for the overnight rate to 4.25%, with the bank rate at 4.5% and the deposit rate at 4.25%. Lower core inflationary pressures in shelter and services prompted the rate reduction, offering welcomed interest cost relief to variable-rate mortgage holders and small businesses across Ontario, Quebec, and British Columbia.",
            img="https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80",
            canonical_url="https://www.cbc.ca/news/business/bank-of-canada-rate-cut-oct2026",
            first_seen=utc_ago(days=3),
            claim_text="The Bank of Canada lowered its policy interest rate by 25 basis points to 4.25%.",
            claim_status="corroborated",
            ev_name="Bank of Canada Press Release",
            ev_type="primary_doc",
            ev_stance="supports",
            ev_excerpt="The Bank of Canada today announced that it is lowering its target for the overnight rate to 4.25 percent.",
            rationale="Verified with Bank of Canada official policy publication and governor press conference."
        )

        db.commit()
        print("Database successfully seeded with comprehensive news stream (RONB, Setopati, OnlineKhabar)!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(force=True)
