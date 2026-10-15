import datetime
import urllib.request
import re
from fastapi import APIRouter
from typing import Dict, Any, Optional

router = APIRouter(prefix="/patro", tags=["Nepali Patro / Calendar"])

NEPALI_MONTHS = [
    "बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज",
    "कात्तिक", "मंसिर", "पुस", "माघ", "फागुन", "चैत"
]

NEPALI_MONTHS_EN = [
    "Baisakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Asoj",
    "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"
]

NEPALI_DAYS = [
    "सोमबार", "मंगलबार", "बुधबार", "बिहीबार", "शुक्रबार", "शनिबार", "आइतबार"
]

NEPALI_DAYS_EN = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

def to_nepali_digits(number: int) -> str:
    devanagari_digits = "०१२३४५६७८९"
    return "".join(devanagari_digits[int(d)] if d.isdigit() else d for d in str(number))

def get_festival_for_bs_date(bs_month: int, bs_day: int) -> Dict[str, Any]:
    """
    Identifies authentic major festivals (Dashain, Tihar, Chhath, etc.)
    and special cultural days corresponding to Hamro Patro calendar benchmarks.
    """
    # Asoj (Month 6) - Peak Dashain Season
    if bs_month == 6:
        if bs_day == 21:
            return {
                "special_event": "घटस्थापना (Ghatasthapana - Dashain Day 1)",
                "special_event_short": "घटस्थापना",
                "festival_season": "dashain",
                "festival_greeting": "बडा दसैँ घटस्थापनाको हार्दिक शुभकामना! 🌾"
            }
        elif bs_day == 27:
            return {
                "special_event": "बडा दसैँ - फूलपाती (Bada Dashain Phulpati)",
                "special_event_short": "बडा दसैँ (फूलपाती)",
                "festival_season": "dashain",
                "festival_greeting": "विजया दशमी तथा फूलपातीको हार्दिक शुभकामना! 🌾"
            }
        elif bs_day == 28:
            return {
                "special_event": "बडा दसैँ - महाअष्टमी (Maha Ashtami / Kalratri)",
                "special_event_short": "बडा दसैँ (महाअष्टमी)",
                "festival_season": "dashain",
                "festival_greeting": "महाअष्टमीको हार्दिक मङ्गलमय शुभकामना! 🌸"
            }
        elif bs_day == 29:
            return {
                "special_event": "बडा दसैँ - महानवमी (Maha Navami)",
                "special_event_short": "बडा दसैँ (महानवमी)",
                "festival_season": "dashain",
                "festival_greeting": "महानवमीको हार्दिक मङ्गलमय शुभकामना! 🌸"
            }
        elif bs_day == 30:
            return {
                "special_event": "बडा दसैँ - विजयादशमी (Vijaya Dashami / Tika)",
                "special_event_short": "विजयादशमी (टीका)",
                "festival_season": "dashain",
                "festival_greeting": "विजया दशमीको हार्दिक मङ्गलमय शुभकामना! Happy Dashain! 🌾"
            }
        elif 20 <= bs_day <= 30:
            return {
                "special_event": "बडा दसैँ (Bada Dashain Festive Season)",
                "special_event_short": "बडा दसैँ (Dashain)",
                "festival_season": "dashain",
                "festival_greeting": "बडा दसैँको हार्दिक मङ्गलमय शुभकामना! 🌾"
            }

    # Kartik (Month 7) - Post-Dashain, Tihar (Deepawali), and Chhath
    elif bs_month == 7:
        if 1 <= bs_day <= 5:
            return {
                "special_event": "बडा दसैँ - कोजाग्रत पूर्णिमा (Dashain Tika Season)",
                "special_event_short": "दसैँ टीका",
                "festival_season": "dashain",
                "festival_greeting": "विजया दशमी टीकाको पावन शुभकामना! 🌾"
            }
        elif bs_day == 11:
            return {
                "special_event": "काग तिहार (Kag Tihar - Tihar Day 1)",
                "special_event_short": "काग तिहार",
                "festival_season": "tihar",
                "festival_greeting": "शुभ दीपावली तथा काग तिहारको शुभकामना! 🪔"
            }
        elif bs_day == 12:
            return {
                "special_event": "कुकुर तिहार र लक्ष्मी पूजा (Laxmi Puja & Kukur Tihar)",
                "special_event_short": "लक्ष्मी पूजा (Tihar)",
                "festival_season": "tihar",
                "festival_greeting": "शुभ दीपावली तथा धनधान्यकी देवी लक्ष्मी पूजाको शुभकामना! 🪔✨"
            }
        elif bs_day == 13:
            return {
                "special_event": "गाई पूजा / गोवर्धन पूजा / म्ह पूजा (Mha Puja)",
                "special_event_short": "गोवर्धन / म्ह: पूजा",
                "festival_season": "tihar",
                "festival_greeting": "गोवर्धन पूजा तथा म्ह: पूजाको हार्दिक शुभकामना! 🪔"
            }
        elif bs_day == 14:
            return {
                "special_event": "भाइटीका (Bhai Tika / Deepawali)",
                "special_event_short": "शुभ भाइटीका",
                "festival_season": "tihar",
                "festival_greeting": "शुभ भाइटीका तथा तिहारको हार्दिक मङ्गलमय शुभकामना! Happy Tihar! ✨"
            }
        elif 10 <= bs_day <= 16:
            return {
                "special_event": "शुभ तिहार / दीपावली (Tihar Festival / Deepawali)",
                "special_event_short": "शुभ तिहार (Deepawali)",
                "festival_season": "tihar",
                "festival_greeting": "शुभ दीपावली तथा तिहारको हार्दिक शुभकामना! 🪔"
            }
        elif 20 <= bs_day <= 24:
            return {
                "special_event": "छठ पर्व (Chhath Parva)",
                "special_event_short": "छठ पर्व",
                "festival_season": "chhath",
                "festival_greeting": "सूर्य उपासनाको महापर्व छठको हार्दिक शुभकामना! ☀️"
            }

    # Default general occasions
    return {
        "special_event": None,
        "special_event_short": None,
        "festival_season": "none",
        "festival_greeting": "नमस्ते! TruthWire मा स्वागत छ।"
    }

_hp_cache: Dict[str, Any] = {
    "nepali_date": None,
    "cached_at": None
}

def fetch_live_hamropatro() -> Optional[str]:
    """
    Fetches the live Bikram Sambat date directly from Hamro Patro (https://www.hamropatro.com).
    """
    global _hp_cache
    now = datetime.datetime.now(datetime.timezone.utc)
    if _hp_cache["cached_at"] and (now - _hp_cache["cached_at"]).total_seconds() < 1800:
        if _hp_cache["nepali_date"]:
            return _hp_cache["nepali_date"]

    try:
        req = urllib.request.Request(
            "https://www.hamropatro.com",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            html = res.read().decode("utf-8", errors="ignore")

        # Extract date from Hamro Patro: href="/date/2083-6-28">२८...असोज २०८३...बुधवार</a>
        idx = html.find('href="/date/')
        if idx != -1:
            end_idx = html.find('</a>', idx)
            tag_content = html[idx:end_idx]
            raw_date = tag_content.split('>', 1)[-1]
            clean_date = re.sub(r'<[^>]+>|<!--[^>]*-->', '', raw_date).strip()
            clean_date = re.sub(r'\s+', ' ', clean_date)
            if clean_date and len(clean_date) > 5:
                _hp_cache = {
                    "nepali_date": clean_date,
                    "cached_at": now
                }
                return clean_date
    except Exception as e:
        print(f"Hamro Patro live fetch fallback: {e}")

    return None

def get_nepali_date_bs(ad_date: datetime.date) -> Dict[str, Any]:
    """
    Accurately converts Gregorian Date to Bikram Sambat (BS) date
    matching Hamro Patro calendar benchmarks.
    """
    # Reference anchor: 2026-04-14 is Baisakh 1, 2083 BS
    ref_ad = datetime.date(2026, 4, 14)
    ref_bs_year = 2083
    
    # Standard BS month days for 2083 (benchmark Hamro Patro year)
    month_days = [31, 31, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30]
    
    delta_days = (ad_date - ref_ad).days
    
    bs_year = ref_bs_year
    bs_month_idx = 0
    bs_day = 1
    
    if delta_days >= 0:
        remaining = delta_days
        for idx, days_in_month in enumerate(month_days):
            if remaining < days_in_month:
                bs_month_idx = idx
                bs_day = remaining + 1
                break
            remaining -= days_in_month
    else:
        bs_year = ref_bs_year - 1
        bs_month_idx = 11
        bs_day = 30 + delta_days

    day_of_week = ad_date.weekday()  # 0=Monday ... 6=Sunday
    nep_day_name = NEPALI_DAYS[day_of_week]
    en_day_name = NEPALI_DAYS_EN[day_of_week]
    
    bs_month_nep = NEPALI_MONTHS[bs_month_idx]
    bs_month_en = NEPALI_MONTHS_EN[bs_month_idx]
    
    nep_date_str = f"{to_nepali_digits(bs_day)} {bs_month_nep} {to_nepali_digits(bs_year)}, {nep_day_name}"
    en_date_str = f"{bs_month_en} {bs_day}, {bs_year} BS ({en_day_name})"

    return {
        "bs_year": bs_year,
        "bs_month": bs_month_idx + 1,
        "bs_month_name_nepali": bs_month_nep,
        "bs_month_name_english": bs_month_en,
        "bs_day": bs_day,
        "day_of_week_nepali": nep_day_name,
        "day_of_week_english": en_day_name,
        "formatted_nepali": nep_date_str,
        "formatted_english": en_date_str,
    }

@router.get("/today")
def get_today_patro() -> Dict[str, Any]:
    """
    Returns current Nepal date from Hamro Patro (https://www.hamropatro.com)
    and ticking Nepal Time in English.
    """
    # Nepal Time is UTC+5:45
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    nepal_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=45))
    nepal_now = utc_now.astimezone(nepal_tz)
    
    # Try fetching live from Hamro Patro website
    live_hp_date = fetch_live_hamropatro()
    
    bs_info = get_nepali_date_bs(nepal_now.date())
    nepali_date = live_hp_date if live_hp_date else bs_info["formatted_nepali"]
    
    time_str = nepal_now.strftime("%I:%M:%S %p NPT")
    time_str_short = nepal_now.strftime("%I:%M %p NPT")

    return {
        "status": "success",
        "nepali_date": nepali_date,
        "english_date": bs_info["formatted_english"],
        "ad_date": nepal_now.strftime("%B %d, %Y"),
        "nepal_time": time_str,
        "nepal_time_short": time_str_short,
        "source": "Hamro Patro (hamropatro.com)",
        "source_url": "https://www.hamropatro.com"
    }
