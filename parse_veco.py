import json
import re
import time
import datetime
import os
import sys
import io
import unicodedata  # 特殊ユニコード太字を標準英字に直すために追加
from urllib.parse import urljoin
from curl_cffi import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
try:
    from dotenv import load_dotenv  # ローカル環境変数読み込み用
    load_dotenv()
except ImportError:
    pass

# ==========================================
# 🛡️ Windows環境でのエンコードエラー (CP932) 回避設定
# ==========================================
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ローカル実行時に同じフォルダの .env ファイルから環境変数を自動ロード

# ==========================================
# ⚙️ 設定 & マスターデータ
# ==========================================
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
CACHE_FILE = "translation_cache.json"  # ディスクキャッシュファイル

CEBU_AREAS = [
  { "id": "cebu-itpark", "nameEn": "Cebu City (IT Park / Lahug)", "nameJa": "セブ市 (ITパーク / ラフグ)" },
  { "id": "cebu-banilad", "nameEn": "Cebu City (Banilad / AS Fortuna)", "nameJa": "セブ市 (バニラッド / ASフォーチュナ)" },
  { "id": "cebu-talamban", "nameEn": "Cebu City (Talamban)", "nameJa": "セブ市 (タランバン)" },
  { "id": "cebu-guadalupe", "nameEn": "Cebu City (Guadalupe)", "nameJa": "セブ市 (グアダルーペ)" },
  { "id": "cebu-downtown", "nameEn": "Cebu City (Downtown / Colon)", "nameJa": "セブ市 (ダウンタウン / コロン)" },
  { "id": "cebu-other", "nameEn": "Cebu City (Other Areas)", "nameJa": "セブ市 (その他エリア)" },
  { "id": "mandaue-basak", "nameEn": "Mandaue City (Basak / Jagobiao)", "nameJa": "マンダウエ市 (バサック / ハゴビヤオ)" },
  { "id": "mandaue-centro", "nameEn": "Mandaue City (Centro / Looc)", "nameJa": "マンダウエ市 (セントロ / ルック)" },
  { "id": "mandaue-other", "nameEn": "Mandaue City (Other Areas)", "nameJa": "マンダウエ市 (その他エリア)" },
  { "id": "lapulapu-mactan", "nameEn": "Lapu-Lapu City (Mactan / Newtown)", "nameJa": "ラプラプ市 (マクタン / ニュータウン)" },
  { "id": "lapulapu-other", "nameEn": "Lapu-Lapu City (Other Areas)", "nameJa": "ラプラプ市 (その他エリア)" },
  { "id": "talisay", "nameEn": "Talisay City", "nameJa": "タリサイ市" },
  { "id": "consolacion", "nameEn": "Consolacion", "nameJa": "コンソラシオン" },
  { "id": "liloan", "nameEn": "Liloan", "nameJa": "リロアン" },
  { "id": "minglanilla", "nameEn": "Minglanilla", "nameJa": "ミングラニラ" },
  { "id": "cordova", "nameEn": "Cordova", "nameJa": "コルドバ" },
  { "id": "other", "nameEn": "Other (Manual Input)", "nameJa": "その他（手書き入力）" }
]

months_map = {
    "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
    "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
}
months_abbrev = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}
days_map = {
    "Sunday": "Sun", "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat",
    "Sun": "Sun", "Mon": "Mon", "Tue": "Tue", "Wed": "Wed", "Thu": "Thu", "Fri": "Fri", "Sat": "Sat"
}
cities_map_ja = {
    "Cebu City": "セブ市", "Mandaue City": "マンダウエ市", "Talisay City": "タリサイ市",
    "Liloan": "リロアン", "Minglanilla": "ミングラニラ", "Consolacion": "コンソラシオン", "Cordova": "コルドバ",
    "City of Naga": "ナガ市", "Naga City": "ナガ市"
}

pht_tz = datetime.timezone(datetime.timedelta(hours=8))
CURRENT_YEAR = datetime.datetime.now(pht_tz).year

# ==========================================
# 🔄 翻訳キャッシュシステム（永続ディスクキャッシュ）
# ==========================================
translation_cache = {}
translator = GoogleTranslator(source='en', target='ja')

# ディスクキャッシュのロード
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            translation_cache = json.load(f)
        print(f"💾 翻訳ディスクキャッシュを読み込みました（{len(translation_cache)} 件の履歴）")
    except Exception as e:
        print(f"⚠️ キャッシュの読み込みに失敗しました: {e}")

def cached_translate(text):
    if not text:
        return ""
    text_clean = text.strip()
    if text_clean in translation_cache:
        return translation_cache[text_clean]
    
    if len(text_clean) > 1000:
        return text_clean
        
    try:
        translated = translator.translate(text_clean)
        translation_cache[text_clean] = translated
        return translated
    except Exception as e:
        print(f"⚠️ 翻訳エラーが発生しました（英語表記のまま処理を継続します）")
        return text_clean

# ==========================================
# 🛠️ 変換用ヘルパー関数群
# ==========================================
def parse_date(date_str):
    # "July 17-18, 2026 (Friday-Saturday)" のような複数日ハイフン表記に対応
    # ハイフン以降の終了日を削って、"July 17, 2026 (Friday-Saturday)" に変形
    date_str_clean = re.sub(r"(\d+)-\d+", r"\1", date_str)
    
    match = re.search(r"(\w+)\s+(\d+),\s+(\d{4})\s*\((.*?)\)", date_str_clean)
    if match:
        m_en, d_str, y_str, day_en = match.groups()
        m_num = months_map.get(m_en.capitalize(), "01")
        d_num = f"{int(d_str):02d}"
        
        # 曜日がハイフンで繋がっている場合（例: "Friday-Saturday"）は開始側の曜日だけにする
        day_first = day_en.split('-')[0].strip()
        day_abbrev = days_map.get(day_first, "Sun")
        
        return f"{y_str}/{m_num}/{d_num}", day_abbrev
    return f"{CURRENT_YEAR}/06/01", "Sun"

def extract_mcwd_date(line):
    months_pattern = "|".join(list(months_map.keys()) + list(months_abbrev.keys()))
    
    # パターン0: "1JUL26" のようなフォーマット (日 月 年2桁)
    match_compact = re.search(rf"\b(\d{{1,2}})({months_pattern})(\d{{2}})\b", line, re.IGNORECASE)
    if match_compact:
        d_str, m_en, y_str = match_compact.groups()
        m_capital = m_en.capitalize()
        m_num = months_abbrev.get(m_capital[:3], "01")
        year = f"20{y_str}" if len(y_str) == 2 else y_str
        return f"{year}/{m_num}/{int(d_str):02d}"

    # パターン1: "July 26, 2026" / "Jul 26, 2026"
    match_ymd = re.search(rf"\b({months_pattern})\s*(\d{{1,2}}),\s*(\d{{4}})\b", line, re.IGNORECASE)
    if match_ymd:
        m_en, d_str, y_str = match_ymd.groups()
        m_capital = m_en.capitalize()
        m_num = months_abbrev.get(m_capital[:3], "01")
        return f"{y_str}/{m_num}/{int(d_str):02d}"
        
    # パターン2: "26 July 2026"
    match_dym = re.search(rf"\b(\d{{1,2}})\s*({months_pattern})\s*(\d{{4}})\b", line, re.IGNORECASE)
    if match_dym:
        d_str, m_en, y_str = match_dym.groups()
        m_capital = m_en.capitalize()
        m_num = months_abbrev.get(m_capital[:3], "01")
        return f"{y_str}/{m_num}/{int(d_str):02d}"

    # パターン3: "July 26" / "Jul 26" (年は現在)
    match_md = re.search(rf"\b({months_pattern})\s*(\d{{1,2}})\b(?!\s*,\s*\d{{4}}|\s+\d{{4}})", line, re.IGNORECASE)
    if match_md:
        m_en, d_str = match_md.groups()
        m_capital = m_en.capitalize()
        m_num = months_abbrev.get(m_capital[:3], "01")
        return f"{CURRENT_YEAR}/{m_num}/{int(d_str):02d}"

    # パターン4: "26 July" (年は現在)
    match_dm = re.search(rf"\b(\d{{1,2}})\s*({months_pattern})\b", line, re.IGNORECASE)
    if match_dm:
        d_str, m_en = match_dm.groups()
        m_capital = m_en.capitalize()
        m_num = months_abbrev.get(m_capital[:3], "01")
        return f"{CURRENT_YEAR}/{m_num}/{int(d_str):02d}"
        
    return None

def to_24h(hour, minute, ampm):
    h = int(hour)
    m = int(minute)
    ampm = ampm.upper()
    if ampm == "PM" and h != 12: h += 12
    elif ampm == "AM" and h == 12: h = 0
    return f"{h:02d}:{m:02d}"

def parse_time(time_str):
    # ダッシュ類記号 (–, —, ~) や 'to' をすべて標準ハイフン '-' に統一
    time_str_clean = re.sub(r"–|—|~", "-", time_str)
    time_str_clean = re.sub(r"\bto\b", "-", time_str_clean, flags=re.IGNORECASE)
    time_str_clean = re.sub(r"\(\d+hrs?\)", "", time_str_clean).strip()
    
    # 終了時間の分が省略されている場合（例: 9:55 AM - 10 AM）は自動補正
    time_str_clean = re.sub(r"-\s*(\d{1,2})\s*(AM|PM)\b", r"- \1:00 \2", time_str_clean, flags=re.IGNORECASE)
    
    # 形式: 10:00 AM - 5:00 PM / 10:00 - 11:00 PM / 22:00 - 23:00 などに対応
    pattern_std = r"(\d{1,2}):(\d{2})\s*(AM|PM)?\s*-\s*(\d{1,2}):(\d{2})\s*(AM|PM)?"
    match_std = re.search(pattern_std, time_str_clean, re.IGNORECASE)
    if match_std:
        sh, sm, sampm, eh, em, eampm = match_std.groups()
        
        # 片方の AM/PM が省略されている場合は、もう片方の値を引き継ぐ補正
        if not sampm and eampm:
            sampm = eampm
        elif not eampm and sampm:
            eampm = sampm
            
        # 両方とも AM/PM がない場合はそのまま返す
        if not sampm and not eampm:
            return f"{int(sh):02d}:{int(sm):02d} - {int(eh):02d}:{int(em):02d}"
            
        return f"{to_24h(sh, sm, sampm)} - {to_24h(eh, em, eampm)}"
        
    # Overnightパターン (toまたはハイフンの両方に対応)
    pattern_overnight = r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*of\s*(\w+)\s*(\d+)\s*(?:to|-)\s*(\d{1,2}):(\d{2})\s*(AM|PM)\s*of\s*(\w+)\s*(\d+)"
    match_overnight = re.search(pattern_overnight, time_str_clean, re.IGNORECASE)
    if match_overnight:
        sh, sm, sampm, smonth, sday, eh, em, eampm, emonth, eday = match_overnight.groups()
        start_24 = to_24h(sh, sm, sampm)
        end_24 = to_24h(eh, em, eampm)
        return f"{start_24} - {end_24} (+1d)"
    return time_str_clean

def clean_translated_japanese(text):
    if not text:
        return ""
        
    # バランガイやサービス提供の表現をインフラ用語として自然に
    text = re.sub(r"Brgy\s*にサービスを提供する", "周辺地域へ電力を供給する", text, flags=re.IGNORECASE)
    text = re.sub(r"Brgy\s*に電力を供給する", "周辺地域へ電力を供給する", text, flags=re.IGNORECASE)
    
    # 1. 【超重要】「〜を促進することにより[Brgy名]。」のような語順崩れを正規表現で先に補正する！
    text = re.sub(
        r"([\w・（）]+)の(アップグレード|設置|移設|再建|タップ|交換|整備)を(促進することにより|促進することで|容易にすることにより|容易にすることで|促進することによって|行うことで|行うことにより|行うことによって)(\w+)。$",
        r"\1の\2工事を行うためです（対象エリア: \4）。",
        text
    )
    # 単純な目的語の補正
    text = re.sub(
        r"(\w+)を(促進することにより|促進することで|容易にすることにより|容易にすることで|促進することによって|行うことで|行うことにより|行うことによって)(\w+)。$",
        r"\1工事を行うためです（対象エリア: \3）。",
        text
    )
    # 顧客の要請に基づくシャットダウン要求の語順崩れ補正
    # 例: 「Tisa は、顧客からのシャットダウン要求を容易にします。」 ➔ 「顧客の要請に基づく送電停止工事を行うためです（対象エリア: Tisa）。」
    text = re.sub(
        r"([\w\s・]+)\s*は、顧客からの(?:シャットダウン要求|シャットダウン要請)を(?:容易にします|行います)。",
        r"顧客の要請に基づく送電停止（シャットダウン）工事を行うためです（対象エリア: \1）。",
        text
    )
    replacements = {
        r"配信システム": "配電システム",
        r"配信系統": "配電系統",
        r"主極": "高圧電柱",
        r"一次電柱": "高圧電柱",
        r"容易になります": "行うためです",
        r"容易にします": "行います",
        r"容易にすることで": "行うことで",
        r"容易にするため": "行うため",
        r"を容易にすることによって": "を行うことによって",
        r"の障害による不要な s を防ぐ": "の障害による不要な停電を防ぐ",
        r"不要な電力供給を防止": "突発的な停電を防止",
        r"不要な停電を防止": "突発的な停電を防止",
        r"不要な中断を防止": "突発的な停電を防止",
        r"の信頼性を向上させるため。": "の信頼性を向上させるため、"
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
        
    return text

def parse_area_summary(affected_en):
    # パターン1: Portion of Brgy. XXX, City
    pattern1 = r"Portion[s]? of\s+([^,]+),\s+(Cebu City|Mandaue City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova)"
    match1 = re.search(pattern1, affected_en, re.IGNORECASE)
    if match1:
        brgys, city = match1.groups()
        brgys_clean = brgys.replace("Brgy. ", "").replace("Brgys. ", "").strip()
        city_ja = cities_map_ja.get(city, city)
        brgys_ja = cached_translate(brgys_clean).rstrip('。').rstrip('.')
        return f"{city} ({brgys_clean})", f"{city_ja} ({brgys_ja})"
        
    # パターン2: Portion of City (Brgy. XXX)
    pattern2 = r"Portion[s]? of\s+(Cebu City|Mandaue City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova)\s*\((.*?)\)"
    match2 = re.search(pattern2, affected_en, re.IGNORECASE)
    if match2:
        city, brgys = match2.groups()
        brgys_clean = brgys.replace("Brgy. ", "").replace("Brgys. ", "").strip()
        city_ja = cities_map_ja.get(city, city)
        brgys_ja = cached_translate(brgys_clean).rstrip('。').rstrip('.')
        return f"{city} ({brgys_clean})", f"{city_ja} ({brgys_ja})"
    
    for city, city_ja in cities_map_ja.items():
        if city in affected_en:
            return f"{city} (Other Areas)", f"{city_ja} (その他エリア)"
    return "Other (Manual Input)", "その他（手書き入力）"

def parse_time_for_sorting(time_str):
    try:
        # 開始時間と終了時間の両方を抽出
        # 例: "09:00 - 17:00" -> 開始 (9, 0), 終了 (17, 0)
        times = re.findall(r'(\d{2}):(\d{2})', time_str)
        if len(times) >= 2:
            start_h, start_m = int(times[0][0]), int(times[0][1])
            end_h, end_m = int(times[1][0]), int(times[1][1])
            # 日付またぎ (+1d) の場合は終了時間に24時間を足して順序を正確にする
            if "+1d" in time_str:
                end_h += 24
            return (start_h, start_m, end_h, end_m)
        elif len(times) == 1:
            start_h, start_m = int(times[0][0]), int(times[0][1])
            return (start_h, start_m, 23, 59)
    except:
        pass
    return (23, 59, 23, 59)

def clean_text_pipeline(text):
    if not text: return ""
    
    text = unicodedata.normalize('NFKC', text)
    
    footers_to_strip = [
        r"Your safety is important to us.*",
        r"The complete details of the scheduled.*",
        r"We apologize for the inconvenience.*",
        r"For further inquiries.*",
        r"Your safety is our priority.*"
    ]
    for footer in footers_to_strip:
        text = re.sub(footer, "", text, flags=re.IGNORECASE | re.DOTALL)
    
    text = re.sub(r"(?:view|v[i|ｉ]ew|ｖｉｅｗ|[ｖ𝐯][ｉｉ][ｅｅ][ｗ𝐰])\s*(?:the\s*map|ｔｈｅ\s*ｍａｐ|[ｔ𝐭][ｈｈ][ｅｅ]\s+[ｍ𝐦][ａａ][ｐｐ])\s*(?:here|ｈｅｒｅ|[ｈｈ][ｅｅ][ｒｒ][ｅｅ])\s*:?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://\S+", "", text, flags=re.IGNORECASE)
    
    text = re.sub(r"#CARD_SUBTITLE#", "", text, flags=re.IGNORECASE)
    text = re.sub(r"#SCHEDULE#", "", text, flags=re.IGNORECASE)
    text = re.sub(r"INTERRUPTION", "", text, flags=re.IGNORECASE)
    text = re.sub(r"EMERGENCY", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+[\s,]+[\d,]*\s*views.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Post not marked as liked.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Service Advisory\s*\d*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(Areas Affected\s*:\s*)+", "", text, flags=re.IGNORECASE)
    
    parts = [p.strip() for p in text.split(',') if p.strip()]
    unique_parts = []
    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)
                
    text = ", ".join(unique_parts)
    sentences = [s.strip() for s in re.split(r'(?<=[.\n?])\s+', text) if s.strip()]
    seen = set()
    unique_sentences = []
    for s in sentences:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_sentences.append(s)
            
    return " ".join(unique_sentences).strip()

def is_event_finished(item_date, item_time, current_dt_pht):
    today_pht = current_dt_pht.date()
    
    try:
        item_dt_obj = datetime.datetime.strptime(item_date, "%Y/%m/%d").date()
    except:
        return False
        
    if item_dt_obj < today_pht:
        return True
    if item_dt_obj > today_pht:
        return False
        
    if "flexible" in item_time.lower() or "tbd" in item_time.lower() or "as of" in item_time.lower():
        return False
        
    match = re.search(r'-\s*(\d{2}):(\d{2})', item_time)
    if match:
        end_h, end_m = int(match.group(1)), int(match.group(2))
        current_h, current_m = current_dt_pht.hour, current_dt_pht.minute
        
        if (current_h > end_h) or (current_h == end_h and current_m >= end_m):
            return True
            
    return False

# ==========================================
# 🧩 輪番停電(Rotational Brownouts)専用 高度分解パーサー
# ==========================================
def parse_rotational_brownout_complex(text, date_formatted, today_str):
    text = unicodedata.normalize('NFKC', text)
    text_lower = text.lower()
    if "rotational brownout" not in text_lower and "possible rotational" not in text_lower:
        return []
        
    entries = []
    
    conditional_split = re.split(r"(EARLIER ADVISORY|RED ALERT|if a red alert is declared)", text, flags=re.IGNORECASE)
    
    active_part = conditional_split[0]
    conditional_part = "".join(conditional_split[1:]) if len(conditional_split) > 1 else ""
    
    def process_section(section_text, is_conditional):
        section_entries = []
        slots = section_text.split("⏰")
        for slot in slots:
            slot = slot.strip()
            if not slot:
                continue
                
            time_match = re.match(r"^(\d{1,2}:\d{2}\s*(?:AM|PM)\s*(?:-|to)\s*\d{1,2}:\d{2}\s*(?:AM|PM))", slot, re.IGNORECASE)
            if not time_match:
                time_match = re.match(r"^(\d{1,2}:\d{2}[AP]M-\d{1,2}:\d{2}[AP]M)", slot, re.IGNORECASE)
            if not time_match:
                time_match = re.match(r"^(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)", slot, re.IGNORECASE)
                
            if time_match:
                raw_time = time_match.group(1)
                time_formatted = parse_time(raw_time)
                areas_part = slot[time_match.end():].strip()
                
                bullets = [b.strip() for b in areas_part.split("•") if b.strip()]
                
                city_groups = {}
                for bullet in bullets:
                    bullet_clean = clean_text_pipeline(bullet)
                    if not bullet_clean:
                        continue
                        
                    city_pattern = r"Portion[s]? of\s+([^,]+),\s*(.*)"
                    m = re.match(city_pattern, bullet_clean, re.IGNORECASE)
                    if m:
                        city_name, barangays_str = m.groups()
                        city_name = city_name.strip()
                        
                        barangays_str = re.sub(r"\s*View the map.*", "", barangays_str, flags=re.IGNORECASE).strip()
                        brgy_list = [b.strip().rstrip('.') for b in re.split(r",|\band\b|&", barangays_str) if b.strip()]
                        
                        if city_name not in city_groups:
                            city_groups[city_name] = []
                        city_groups[city_name].extend(brgy_list)
                    else:
                        for known_city in ["Cebu City", "Mandaue City", "Talisay City", "Liloan", "Minglanilla", "Consolacion", "Cordova", "City of Naga", "Naga City"]:
                            if known_city.lower() in bullet_clean.lower():
                                rest = re.sub(rf".*?{known_city}\s*,?\s*", "", bullet_clean, flags=re.IGNORECASE).strip()
                                brgy_list = [b.strip().rstrip('.') for b in re.split(r",|\band\b|&", rest) if b.strip()]
                                if known_city not in city_groups:
                                    city_groups[known_city] = []
                                city_groups[known_city].extend(brgy_list)
                                break
                
                for city, brgys in city_groups.items():
                    brgys = sorted(list(set([b for b in brgys if len(b) > 1])))
                    if not brgys:
                        continue
                        
                    city_ja = cities_map_ja.get(city, city)
                    translated_brgys = [cached_translate(b) for b in brgys]
                    
                    affected_en = f"Portion of {city}: {', '.join(brgys)}"
                    affected_ja = f"{city_ja}の一部エリア: {', '.join(translated_brgys)}"
                    
                    status_tag_en = "🚨 [ROTATIONAL BROWNOUT]" if not is_conditional else "⚠️ [CONDITIONAL - RED ALERT]"
                    status_tag_ja = "🚨 【計画供給制限（確定）】" if not is_conditional else "⚠️ 【赤アラート時のみ実施（可能性あり）】"
                    
                    try:
                        dt_obj = datetime.datetime.strptime(date_formatted, "%Y/%m/%d")
                        day_abbrev = dt_obj.strftime("%a")
                    except:
                        day_abbrev = "Sun"
                        
                    section_entries.append({
                        "id": 0,
                        "type": "electricity",
                        "date": date_formatted,
                        "day": day_abbrev,
                        "time": time_formatted,
                        "areaEn": f"{city} ({', '.join(brgys[:2])}...)" if len(brgys) > 2 else f"{city} ({', '.join(brgys)})",
                        "areaJa": f"{city_ja} ({', '.join(translated_brgys[:2])}...)" if len(translated_brgys) > 2 else f"{city_ja} ({', '.join(translated_brgys)})",
                        "affectedEn": affected_en,
                        "affectedJa": affected_ja,
                        "detailsEn": f"{status_tag_en} Scheduled power reduction due to limited grid generation capacity.",
                        "detailsJa": f"{status_tag_ja} 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
                    })
        return section_entries
        
    if active_part:
        entries.extend(process_section(active_part, is_conditional=False))
    if conditional_part:
        entries.extend(process_section(conditional_part, is_conditional=True))
        
    return entries

# ==========================================
# ⚡ 統合マージプロセッサ (異なる工事の誤マージを防止)
# ==========================================
def merge_duplicate_outages(outages):
    grouped = {}
    for item in outages:
        is_conditional = "CONDITIONAL" in item["detailsEn"] or "赤アラート" in item["detailsJa"]
        is_cancelled = "CANCELLED" in item["detailsEn"]
        
        # 目的 (detailsEn) をキーに含めることで、同じ日時だからといって別々の工事が誤合体されるのを防ぐ
        purpose_key = clean_text_pipeline(item["detailsEn"]).lower()
        
        key = (item["date"], item["time"], item["type"], is_conditional, is_cancelled, purpose_key)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
        
    merged = []
    for key, items in grouped.items():
        if len(items) == 1:
            merged.append(items[0])
            continue
            
        first = items[0]
        date, time_str, item_type, is_conditional, is_cancelled, _ = key
        
        city_brgys_map = {}
        for it in items:
            item_city = "Other"
            for known_city in ["Cebu City", "Mandaue City", "Talisay City", "Liloan", "Minglanilla", "Consolacion", "Cordova", "City of Naga", "Naga City"]:
                if known_city.lower() in it["areaEn"].lower():
                    item_city = known_city
                    break
            
            en_brgys = []
            en_match = re.search(r"Portion[s]? of\s+[^:]+:\s*(.*)", it["affectedEn"], re.IGNORECASE)
            if en_match:
                en_brgys = [b.strip() for b in en_match.group(1).split(",") if b.strip()]
            else:
                parentheses_match = re.search(r"\((.*?)\)", it["areaEn"])
                if parentheses_match:
                    en_brgys = [b.strip() for b in parentheses_match.group(1).split(",") if b.strip()]
                else:
                    en_brgys = [b.strip() for b in it["affectedEn"].split(",") if b.strip()]
                    
            ja_brgys = []
            ja_match = re.search(r"[^:]+の一部エリア:\s*(.*)", it["affectedJa"], re.IGNORECASE)
            if ja_match:
                ja_brgys = [b.strip() for b in ja_match.group(1).split(",") if b.strip()]
            else:
                parentheses_match = re.search(r"\((.*?)\)", it["areaJa"])
                if parentheses_match:
                    ja_brgys = [b.strip() for b in parentheses_match.group(1).split(",") if b.strip()]
                else:
                    ja_brgys = [b.strip() for b in it["affectedJa"].split(",") if b.strip()]
            
            if len(en_brgys) == len(ja_brgys):
                pairs = list(zip(en_brgys, ja_brgys))
            else:
                pairs = [(b, cached_translate(b)) for b in en_brgys]
                
            if item_city not in city_brgys_map:
                city_brgys_map[item_city] = set()
                
            for en_b, ja_b in pairs:
                if len(en_b) > 1:
                    city_brgys_map[item_city].add((en_b, ja_b))
        
        area_en_parts = []
        area_ja_parts = []
        affected_en_lines = []
        affected_ja_lines = []
        
        sorted_cities = sorted(list(city_brgys_map.keys()))
        for city in sorted_cities:
            city_ja = cities_map_ja.get(city, city)
            
            unique_pairs = sorted(list(city_brgys_map[city]), key=lambda x: x[0])
            brgys_en = [p[0] for p in unique_pairs]
            brgys_ja = [p[1] for p in unique_pairs]
            
            limit = 2
            brgys_en_summary = ", ".join(brgys_en[:limit]) + "..." if len(brgys_en) > limit else ", ".join(brgys_en)
            brgys_ja_summary = ", ".join(brgys_ja[:limit]) + "..." if len(brgys_ja) > limit else ", ".join(brgys_ja)
            
            area_en_parts.append(f"{city} ({brgys_en_summary})")
            area_ja_parts.append(f"{city_ja} ({brgys_ja_summary})")
            
            affected_en_lines.append(f"Portion of {city}: {', '.join(brgys_en)}")
            affected_ja_lines.append(f"{city_ja}の一部エリア: {', '.join(brgys_ja)}")
            
        combined_area_en = " / ".join(area_en_parts)
        combined_area_ja = " / ".join(area_ja_parts)
        combined_affected_en = " \n ".join(affected_en_lines)
        combined_affected_ja = " \n ".join(affected_ja_lines)
        
        merged_item = {
            "id": 0,
            "type": item_type,
            "date": date,
            "day": first["day"],
            "time": time_str,
            "areaEn": combined_area_en,
            "areaJa": combined_area_ja,
            "affectedEn": combined_affected_en,
            "affectedJa": combined_affected_ja,
            "detailsEn": first["detailsEn"],
            "detailsJa": first["detailsJa"]
        }
        merged.append(merged_item)
        
    return merged

# ==========================================
# 🌐 VECO公式サイト スクレイピング部 (接続タイムアウト・ネットワーク遅延耐久強化)
# ==========================================
def scrape_veco_raw_content():
    base_url = "https://www.visayanelectric.com"
    advisory_url = f"{base_url}/customer-services/service-advisory"
    
    print("\n⚡ 1. VECO公式サイトのスクレイピングを開始します...")
    articles_data = [] # 各記事の行データを個別で保持する二次元リスト
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            page.goto(advisory_url, timeout=30000, wait_until="domcontentloaded")
            # タグが完全に描画されるまで10秒だけ待つ（ networkidle は避ける ）
            page.wait_for_selector('a', timeout=10000)
            soup = BeautifulSoup(page.content(), 'html.parser')
        except Exception as e:
            print(f"⚠️ VECO公式サイトへの接続に失敗しました: {e}")
            browser.close()
            return []
        
        links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            text = a.get_text(strip=True)
            if href and ("Service Interruption" in text or "Interruption" in text):
                full_url = urljoin(base_url, href)
                if full_url not in links:
                    links.append(full_url)
        
        if not links:
            print("❌ VECOの停電リンクが見つかりませんでした。")
            browser.close()
            return []
            
        target_links = links[:3]
        print(f"👉 VECO最新の {len(target_links)} 件の記事を巡回スクレイピングします...")
        
        for url in target_links:
            print(f"   - 巡回中: {url}")
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_selector("article", timeout=10000) # articleが画面に出るまで待機
                
                detail_soup = BeautifulSoup(page.content(), 'html.parser')
                article = detail_soup.find('article')
                target_area = article if article else detail_soup
                
                # --- [改善①: 連続重複のみを排除し、別日程での同じ時間表現は残す] ---
                article_lines = []
                last_line = None
                for s in target_area.stripped_strings:
                    s_clean = s.strip()
                    # 特殊フォントUnicode (mathematical bold等) をNFKCで即座に英字に正規化
                    s_clean = unicodedata.normalize('NFKC', s_clean)
                    if s_clean and len(s_clean) > 5:
                        # 連続する同一テキストのみ排除
                        if s_clean != last_line:
                            article_lines.append(s_clean)
                            last_line = s_clean
                
                if article_lines:
                    articles_data.append(article_lines)
            except Exception as e:
                print(f"⚠️ 記事の取得中にエラーが発生しました ({url}): {e}")
                
        browser.close()
        
    return articles_data

# ==========================================
# 💧 MCWD公式サイト スクレイピング部
# ==========================================
def scrape_mcwd_raw_content():
    base_url = "https://www.mcwd.gov.ph/ords/production/r/mcwd-website/news?p55_news_selected=interruption"
    
    print("\n💧 2. 水道局（MCWD）公式サイトの非同期スクレイピングを開始します...")
    raw_texts = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(8000)
            
            soup = BeautifulSoup(page.content(), 'html.parser')
            browser.close()
            
            # --- [改善: stripped_strings で末端のテキストだけを重複なく取得] ---
            for s in soup.stripped_strings:
                text = s.strip()
                text = unicodedata.normalize('NFKC', text) # 特殊Unicodeの正規化
                if text and len(text) > 15:
                    if text not in raw_texts:
                        raw_texts.append(text)
    except Exception as e:
        print(f"⚠️ MCWDスクレイピング中にエラーが発生しました: {e}")
    return raw_texts

# ==========================================
# 👥 Apify経由：Facebook公式ページのスクレイピング部
# ==========================================
def scrape_facebook_posts_via_apify(page_url):
    if not APIFY_TOKEN:
        return []
        
    print(f"\n👥 2-B. Apify API経由でFacebook公式ページ ({page_url}) の投稿を取得します...")
    raw_texts = []
    try:
        api_url = f"https://api.apify.com/v2/acts/apify~facebook-posts-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"
        
        run_input = {
            "startUrls": [{"url": page_url}],
            "resultsLimit": 3,
        }
        
        response = requests.post(api_url, json=run_input, timeout=60)
        
        if response.status_code in [200, 201]:
            items = response.json()
            for item in items:
                post_text = item.get("text", "")
                if post_text and len(post_text) > 15:
                    raw_texts.append(post_text)
        else:
            print(f"⚠️ Apify APIエラー: HTTP {response.status_code} ({response.text})")
                
    except Exception as e:
        print(f"⚠️ Apify Facebookスクレイピング中にエラーが発生しました: {e}")
        
    return raw_texts

def parse_facebook_post_prose(text, is_water=False, today_str=""):
    text = unicodedata.normalize('NFKC', text)
    text_lower = text.lower()
    
    is_weekly_digest = "complete details of the scheduled power interruptions" in text_lower or "scheduled power interruptions on" in text_lower
    if is_weekly_digest:
        return None

    date_formatted = extract_mcwd_date(text)
    
    is_urgent_alert = any(k in text_lower for k in ["rotational", "brownout", "blackout", "grid alert", "emergency", "update"])
    if is_urgent_alert:
        date_formatted = today_str
        
    if not date_formatted:
        return None
    if date_formatted < today_str:
        return None
        
    time_formatted = "TBD / Flexible"
    time_match = re.search(r"(?:Time|⏰):\s*(\d{1,2}:\d{2}\s*(?:AM|PM)\s*(?:to|-)\s*\d{1,2}:\d{2}\s*(?:AM|PM))", text, re.IGNORECASE)
    if not time_match:
        time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM)\s*(?:to|-)\s*\d{1,2}:\d{2}\s*(?:AM|PM))", text, re.IGNORECASE)
    if time_match:
        time_formatted = parse_time(time_match.group(1))
    elif is_urgent_alert:
        as_of_match = re.search(r"As\s+of\s+(\d{1,2}:\d{2}\s*(?:AM|PM))", text, re.IGNORECASE)
        if as_of_match:
            time_formatted = f"As of {as_of_match.group(1)}"
        
    purpose_clean = "Rotational Brownouts / Grid Alert" if is_urgent_alert else ("Scheduled Maintenance Advisory" if not is_water else "Scheduled Water Interruption")
    purpose_match = re.search(r"Purpose:\s*(.*?)(?=\bAreas Affected:|\bAreas:|\Z)", text, re.DOTALL | re.IGNORECASE)
    
    if purpose_match:
        purpose_clean = clean_text_pipeline(purpose_match.group(1))
        
    affected_clean = ""
    areas_match = re.search(r"(?:Areas Affected|Areas):\s*(.*)", text, re.DOTALL | re.IGNORECASE)
    if areas_match:
        affected_clean = clean_text_pipeline(areas_match.group(1))
    else:
        affected_clean = clean_text_pipeline(text)
        
    if not affected_clean:
        return None

    is_cancelled = "cancelled" in text_lower or "cancel" in text_lower
    if is_cancelled:
        purpose_clean = f"【CANCELLED】{purpose_clean}"
        
    affected_ja = cached_translate(affected_clean)
    purpose_ja = cached_translate(purpose_clean)
    
    area_en, area_ja = parse_area_summary(affected_clean)
    
    try:
        dt_obj = datetime.datetime.strptime(date_formatted, "%Y/%m/%d")
        day_abbrev = dt_obj.strftime("%a")
    except:
        day_abbrev = "Sun"

    return {
        "id": 0,
        "type": "water" if is_water else "electricity",
        "date": date_formatted,
        "day": day_abbrev,
        "time": time_formatted,
        "areaEn": area_en,
        "areaJa": area_ja,
        "affectedEn": affected_clean,
        "affectedJa": affected_ja,
        "detailsEn": purpose_clean,
        "detailsJa": purpose_ja
    }

# ==========================================
# ⚙️ メインパイプライン処理
# ==========================================
def main():
    today_str = datetime.datetime.now(pht_tz).strftime("%Y/%m/%d")
    print(f"=== Cebu Outage Auto Update Pipeline (セブ現地時間: {today_str}) ===")

    veco_raw_articles = scrape_veco_raw_content()
    
    if APIFY_TOKEN:
        veco_fb_raw = scrape_facebook_posts_via_apify("https://www.facebook.com/visayanelectriccompany/")
    else:
        veco_fb_raw = []

    final_veco_outages = []

    # A. 通常のウェブサイトデータを処理
    if veco_raw_articles:
        print("\n⚡ 3. VECO停電スケジュールデータの解析処理中...")
        for veco_raw in veco_raw_articles:
            current_date = None
            current_time = None
            month_names = list(months_map.keys())
            
            # --- [改善②: 状態マシン（State Machine）によるパース処理] ---
            active_item = None
            veco_outages = [] # この記事内でパースされた一時レコードを格納

            for line in veco_raw:
                if "rotational brownout" in line.lower() or "possible rotational" in line.lower():
                    print("📝 輪番停電の大規模情報を検出しました。専用分解パーサーを実行します...")
                    date_formatted = extract_mcwd_date(line)
                    if not date_formatted:
                        date_formatted = today_str
                    
                    parsed_entries = parse_rotational_brownout_complex(line, date_formatted, today_str)
                    final_veco_outages.extend(parsed_entries)
                    continue

                # 1. 日付行の判定
                is_date_line = any(line.startswith(m) for m in month_names) and any(c.isdigit() for c in line) and ("AM" not in line.upper() and "PM" not in line.upper())
                if is_date_line:
                    current_date = line
                    # 日付が変わったら仕掛かり中データを保存してリセット
                    if active_item and active_item.get("area"):
                        veco_outages.append(active_item)
                        
                    # 日付が出現した時点で、新しいアイテムをデフォルト時間 "TBD / Flexible" で仮初期化する
                    current_time = "TBD / Flexible"
                    active_item = {
                        "date_raw": current_date,
                        "time_raw": current_time,
                        "purpose": "",
                        "area": "",
                        "cancelled": False
                    }
                    continue
                
                if not current_date:
                    continue
                
                # 2. 時間行の判定
                is_time_line = bool(re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)", line, re.IGNORECASE))
                if is_time_line:
                    is_cancelled = "CANCELLED" in line.upper()
                    clean_time = re.sub(r"CANCELLED", "", line, flags=re.IGNORECASE).strip()
                    current_time = clean_time
                    
                    # まだ目的もエリアも入っていない初期状態なら、時間の値を上書きする
                    if active_item and not active_item["purpose"] and not active_item["area"]:
                        active_item["time_raw"] = clean_time
                        active_item["cancelled"] = is_cancelled
                    else:
                        # すでにデータが入っている場合は、前のアイテムを保存して新しく作成
                        if active_item and active_item.get("area"):
                            veco_outages.append(active_item)
                        active_item = {
                            "date_raw": current_date,
                            "time_raw": clean_time,
                            "purpose": "",
                            "area": "",
                            "cancelled": is_cancelled
                        }
                    continue
                    
                # 3. 目的および地域データの蓄積
                if active_item:
                    clean_line = re.sub(r"^(Purpose|Areas Affected)\s*:\s*", "", line, flags=re.IGNORECASE).strip()
                    
                    # 不要行のスキップ
                    if line.strip() in ["Purpose:", "Areas Affected:", "Time:", "Map:", ""] or \
                       clean_line in active_item["purpose"] or clean_line in active_item["area"]:
                        continue
                        
                    if line.upper() == "CANCELLED":
                        active_item["cancelled"] = True
                        continue

                    # 現在の行の属性判定
                    is_purpose = line.lower().startswith("purpose:") or line.lower().startswith("to ")
                    is_area = line.lower().startswith("areas affected:") or line.lower().startswith("portion") or \
                              any(k in line for k in ["Brgy", "St.", "Road", "Avenue", "Ave", "Subd", "City", "Liloan", "Talisay", "Minglanilla"])
                    
                    # すでにデータが埋まっている状態で、次の項目（To.. や Portion..）が来たら
                    # 同じ時間帯を引き継いだまま、新しい別の工事としてレコードを切り分ける
                    if (is_purpose and active_item["purpose"]) or (is_area and active_item["area"]):
                        if active_item.get("area"):
                            veco_outages.append(active_item)
                        active_item = {
                            "date_raw": current_date,
                            "time_raw": current_time,
                            "purpose": active_item["purpose"],
                            "area": "",
                            "cancelled": active_item["cancelled"]
                        }
                    
                    if is_purpose:
                        if not active_item["purpose"]: active_item["purpose"] = clean_line
                        else: active_item["purpose"] += " " + clean_line
                    elif is_area:
                        if not active_item["area"]: active_item["area"] = clean_line
                        else: active_item["area"] += " " + clean_line
                    else:
                        # 判定できない行のフォールバック
                        if not active_item["purpose"]:
                            active_item["purpose"] = clean_line
                        elif not active_item["area"]:
                            active_item["area"] = clean_line
                        else:
                            active_item["area"] += " " + clean_line

            # 記事スキャン終了後に残っている仕掛かり中データを保存
            if active_item and active_item.get("area"):
                veco_outages.append(active_item)

            # 解析した各アイテムを最終出力形式にマッピング
            for raw in veco_outages:
                date_formatted, day_abbrev = parse_date(raw["date_raw"])
                if date_formatted < today_str:
                    continue

                affected_en = clean_text_pipeline(raw["area"])
                details_en = clean_text_pipeline(raw["purpose"])
                if not affected_en: 
                    continue
                    
                affected_ja = clean_translated_japanese(cached_translate(affected_en))
                details_ja = clean_translated_japanese(cached_translate(details_en))
                
                if raw["cancelled"]:
                    details_en = f"【CANCELLED】{details_en}"
                    details_ja = f"【中止】{details_ja}"

                time_formatted = parse_time(raw["time_raw"])
                area_en, area_ja = parse_area_summary(affected_en)
                
                final_veco_outages.append({
                    "id": 0,
                    "type": "electricity",
                    "date": date_formatted,
                    "day": day_abbrev,
                    "time": time_formatted,
                    "areaEn": area_en,
                    "areaJa": area_ja,
                    "affectedEn": affected_en,
                    "affectedJa": affected_ja,
                    "detailsEn": details_en,
                    "detailsJa": details_ja
                })

    # B. Facebookからの投稿をマージ
    if veco_fb_raw:
        print("\n⚡ 3-B. VECO公式Facebookのアドバイザリー解析処理中...")
        for post in veco_fb_raw:
            post_lower = post.lower()
            
            unplanned_keywords = ["safety device to help protect", "automatically switched off", "unplanned power outage"]
            if any(k in post_lower for k in unplanned_keywords):
                print("⏭️ 計画外の自動遮断（突発停電）アナウンスをスキップしました。")
                continue

            if "rotational brownout" in post_lower or "possible rotational" in post_lower:
                date_formatted = extract_mcwd_date(post)
                if not date_formatted:
                    date_formatted = today_str
                
                if date_formatted < today_str:
                    continue
                    
                parsed_entries = parse_rotational_brownout_complex(post, date_formatted, today_str)
                final_veco_outages.extend(parsed_entries)
            else:
                parsed_post = parse_facebook_post_prose(post, is_water=False, today_str=today_str)
                if parsed_post:
                    final_veco_outages.append(parsed_post)

    print("\n⚡ 3-C. 重複する停電スケジュールの統合マージ処理を実行中...")
    final_veco_outages = merge_duplicate_outages(final_veco_outages)

    # ------------------------------------------
    # 💧 MCWD（水道）処理
    # ------------------------------------------
    mcwd_raw = scrape_mcwd_raw_content()
    final_mcwd_outages = []
    
    if mcwd_raw:
        print("\n💧 4. MCWD計画断水スケジュールデータの解析処理中...")
        for line in mcwd_raw:
            line_lower = line.lower()
            is_valid_advisory = ("interruption" in line_lower) or ("shut off" in line_lower) or ("waterless" in line_lower)
            
            if is_valid_advisory:
                date_formatted = extract_mcwd_date(line)
                if not date_formatted or date_formatted < today_str:
                    continue
                
                # クリーン化したテキスト同士で重複判定
                affected_en = clean_text_pipeline(line)
                if not affected_en:
                    continue
                    
                if any(item["affectedEn"] == affected_en for item in final_mcwd_outages):
                    continue

                try:
                    dt_obj = datetime.datetime.strptime(date_formatted, "%Y/%m/%d")
                    day_abbrev = dt_obj.strftime("%a")
                except:
                    day_abbrev = "Sun"

                affected_ja = clean_translated_japanese(cached_translate(affected_en))
                area_en, area_ja = parse_area_summary(affected_en)

                # 時間抽出
                time_formatted = "TBD / Flexible"
                # 特殊パターン: 9:55AM-2JUL 10AM (日付が挟まる場合)
                time_match_special = re.search(
                    r"(\d{1,2}:\d{2}\s*(?:AM|PM)?)\s*(?:to|-|–|—|~)\s*(?:\d{1,2}[A-Z]{3})\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM))",
                    line,
                    re.IGNORECASE
                )
                if time_match_special:
                    start_t, end_t = time_match_special.groups()
                    if ":" not in end_t:
                        end_t = re.sub(r"(\d{1,2})\s*(AM|PM)", r"\1:00 \2", end_t, flags=re.IGNORECASE)
                    time_formatted = parse_time(f"{start_t} - {end_t}")
                else:
                    # 通常パターン (終了時間の分なし対応)
                    time_match = re.search(
                        r"(\d{1,2}:\d{2}\s*(?:AM|PM)?\s*(?:to|-|–|—|~)\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)?)", 
                        line, 
                        re.IGNORECASE
                    )
                    if time_match:
                        time_formatted = parse_time(time_match.group(1))

                is_emergency = "emergency" in line_lower or "leak" in line_lower
                details_en_val = "Emergency water service interruption announced by MCWD. Please store water in advance." if is_emergency else "Scheduled water service interruption announced by MCWD. Please store water."
                details_ja_val = "水道局（MCWD）から発表された、突発的な緊急断水情報です。現在お住まいの方は貯水などの備えを行ってください。" if is_emergency else "水道局（MCWD）から発表された、計画的な断水情報です。事前の貯水や備えを推奨します。"

                final_mcwd_outages.append({
                    "id": 0,
                    "type": "water",
                    "date": date_formatted,
                    "day": day_abbrev,
                    "time": time_formatted,
                    "areaEn": area_en,
                    "areaJa": area_ja,
                    "affectedEn": affected_en,
                    "affectedJa": affected_ja,
                    "detailsEn": details_en_val,
                    "detailsJa": details_ja_val
                })

    # ------------------------------------------
    # 🏁 データの結合、ソート、書き出し
    # ------------------------------------------
    merged_outages = final_veco_outages + final_mcwd_outages
    
    now_pht = datetime.datetime.now(pht_tz)
    
    filtered_outages = []
    for item in merged_outages:
        if is_event_finished(item["date"], item["time"], now_pht):
            print(f"⏰ 終了済みのイベントを自動除外しました: {item['date']} {item['time']} ({item['areaJa']})")
            continue
        filtered_outages.append(item)
    
    filtered_outages.sort(key=lambda x: (x['date'], parse_time_for_sorting(x['time'])))
    
    for index, item in enumerate(filtered_outages, start=100):
        item["id"] = index

    cebu_areas_str = json.dumps(CEBU_AREAS, ensure_ascii=False, indent=2)
    outages_json_str = json.dumps(filtered_outages, ensure_ascii=False, indent=2)
    
    new_data_js_content = f"""/**
 * Cebu Infrastructure Checker - Integrated Data Source
 */
export const CEBU_AREAS = {cebu_areas_str};

export const VECO_OUTAGES = {outages_json_str};
"""

    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(new_data_js_content)

    # 翻訳キャッシュの保存
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(translation_cache, f, ensure_ascii=False, indent=2)
        print(f"💾 翻訳ディスクキャッシュを保存しました（計 {len(translation_cache)} 件の履歴）")
    except Exception as e:
        print(f"⚠️ キャッシュの保存に失敗しました: {e}")

    print("\n--- 【すべてのパイプライン処理が正常に完了しました】 ---")
    print(f"   ✅ 電気（都市・時間・終了済マージ処理後）: {len(final_veco_outages)} 件")
    print(f"   ✅ 水道（MCWD計画断水情報）: {len(final_mcwd_outages)} 件")
    print(f"   💾 ファイル保存先: data.js")

if __name__ == "__main__":
    main()
