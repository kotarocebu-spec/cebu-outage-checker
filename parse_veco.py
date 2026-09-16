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
  # --- セブ市 (Cebu City) ---
  { "id": "cebu-itpark", "city": "cebu", "nameEn": "Cebu City (IT Park / Lahug)", "nameJa": "セブ市 (ITパーク / ラフグ)" },
  { "id": "cebu-ayala", "city": "cebu", "nameEn": "Cebu City (Ayala / Business Park / Luz)", "nameJa": "セブ市 (アヤラ / ビジネスパーク / ルズ)" },
  { "id": "cebu-mabolo", "city": "cebu", "nameEn": "Cebu City (Mabolo / Kasambagan)", "nameJa": "セブ市 (マボロ / カスンバガン)" },
  { "id": "cebu-banilad", "city": "cebu", "nameEn": "Cebu City (Banilad / AS Fortuna)", "nameJa": "セブ市 (バニラッド / ASフォーチュナ)" },
  { "id": "cebu-talamban", "city": "cebu", "nameEn": "Cebu City (Talamban / Pit-os / Bacayan)", "nameJa": "セブ市 (タランバン / ピットオス / バカヤン)" },
  { "id": "cebu-guadalupe", "city": "cebu", "nameEn": "Cebu City (Guadalupe / Capitol / Kalunasan)", "nameJa": "セブ市 (グアダルーペ / キャピトル / カルナサン)" },
  { "id": "cebu-apas", "city": "cebu", "nameEn": "Cebu City (Apas)", "nameJa": "セブ市 (アパス)" },
  { "id": "cebu-fuente", "city": "cebu", "nameEn": "Cebu City (Fuente / Ramos / Zapatera / Kamputhaw)", "nameJa": "セブ市 (フエンテ / ラモス / サパテラ / カンプタウ)" },
  { "id": "cebu-downtown", "city": "cebu", "nameEn": "Cebu City (Downtown / Colon / Pahina / Pari-an)", "nameJa": "セブ市 (ダウンタウン / コロン / パヒナ / パリアン)" },
  { "id": "cebu-mambaling", "city": "cebu", "nameEn": "Cebu City (Mambaling / Duljo / Basak)", "nameJa": "セブ市 (マンバリン / ドゥルホ / バサック)" },
  { "id": "cebu-punta", "city": "cebu", "nameEn": "Cebu City (Punta Princesa / Tisa / Labangon)", "nameJa": "セブ市 (プンタ・プリンセサ / ティサ / ラバンゴン)" },
  { "id": "cebu-pardo", "city": "cebu", "nameEn": "Cebu City (Pardo / Bulacao / Inayawan)", "nameJa": "セブ市 (パルド / ブラカオ / イナヤワン)" },
  { "id": "cebu-busay", "city": "cebu", "nameEn": "Cebu City (Busay / Mountain Areas)", "nameJa": "セブ市 (ブサイ / 山間部)" },
  { "id": "cebu-other", "city": "cebu", "nameEn": "Cebu City (Other Areas)", "nameJa": "セブ市 (その他エリア)" },

  # --- マンダウエ市 (Mandaue City) ---
  { "id": "mandaue-asfortuna", "city": "mandaue", "nameEn": "Mandaue City (AS Fortuna / Banilad)", "nameJa": "マンダウエ市 (ASフォーチュナ / バニラッド)" },
  { "id": "mandaue-tipolo", "city": "mandaue", "nameEn": "Mandaue City (Tipolo / Subangdaku / Guizo)", "nameJa": "マンダウエ市 (ティポロ / スバングダク / ギゾ)" },
  { "id": "mandaue-basak", "city": "mandaue", "nameEn": "Mandaue City (Basak / Jagobiao / Canduman)", "nameJa": "マンダウエ市 (バサック / ハゴビヤオ / カンドゥマン)" },
  { "id": "mandaue-centro", "city": "mandaue", "nameEn": "Mandaue City (Centro / Looc / Reclamation)", "nameJa": "マンダウエ市 (セントロ / ルック / 埋立地)" },
  { "id": "mandaue-cabancalan", "city": "mandaue", "nameEn": "Mandaue City (Cabancalan / Maguikay / Casuntingan)", "nameJa": "マンダウエ市 (カバンカラン / マグイカイ / カスンティンガン)" },
  { "id": "mandaue-other", "city": "mandaue", "nameEn": "Mandaue City (Other Areas)", "nameJa": "マンダウエ市 (その他エリア)" },

  # --- ラプラプ市 / マクタン島 (Lapu-Lapu City / Mactan) ---
  { "id": "lapulapu-mactan", "city": "lapulapu", "nameEn": "Lapu-Lapu City (Mactan / Newtown / Airport / Pusok)", "nameJa": "ラプラプ市 (マクタン / ニュータウン / 空港 / プソック)" },
  { "id": "lapulapu-maribago", "city": "lapulapu", "nameEn": "Lapu-Lapu City (Maribago / Agus / Resort Area)", "nameJa": "ラプラプ市 (マリバゴ / アグス / リゾートホテル街)" },
  { "id": "lapulapu-puntaengano", "city": "lapulapu", "nameEn": "Lapu-Lapu City (Punta Engaño)", "nameJa": "ラプラプ市 (プンタ・エンガーニョ)" },
  { "id": "lapulapu-basak", "city": "lapulapu", "nameEn": "Lapu-Lapu City (Basak / Pajac / Gun-ob)", "nameJa": "ラプラプ市 (バサック / パハック / グンオブ)" },
  { "id": "lapulapu-other", "city": "lapulapu", "nameEn": "Lapu-Lapu City (Other Areas)", "nameJa": "ラプラプ市 (その他エリア)" },

  # --- 近隣都市・自治体 ---
  { "id": "talisay", "city": "other_cities", "nameEn": "Talisay City", "nameJa": "タリサイ市" },
  { "id": "consolacion", "city": "other_cities", "nameEn": "Consolacion", "nameJa": "コンソラシオン" },
  { "id": "liloan", "city": "other_cities", "nameEn": "Liloan", "nameJa": "リロアン" },
  { "id": "minglanilla", "city": "other_cities", "nameEn": "Minglanilla", "nameJa": "ミングラニラ" },
  { "id": "cordova", "city": "other_cities", "nameEn": "Cordova", "nameJa": "コルドバ" },
  { "id": "naga", "city": "other_cities", "nameEn": "City of Naga", "nameJa": "ナガ市" },
  { "id": "other", "city": "other_cities", "nameEn": "Other (Manual Input)", "nameJa": "その他（手書き入力）" }
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
    "Cebu City": "セブ市", "Mandaue City": "マンダウエ市", "Lapu-Lapu City": "ラプラプ市",
    "Talisay City": "タリサイ市", "Liloan": "リロアン", "Minglanilla": "ミングラニラ",
    "Consolacion": "コンソラシオン", "Cordova": "コルドバ",
    "City of Naga": "ナガ市", "Naga City": "ナガ市", "Naga": "ナガ市"
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

def has_japanese(text):
    if not text:
        return False
    return bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", text))

def rule_based_translate_veco(text):
    res = text
    actions = [
        (r"Hotspot Correction", "異常発熱箇所（ホットスポット）の補修点検"),
        (r"installation of automatic reclosing device \(recloser\)", "自動再閉鎖装置（リクローザー）の設置"),
        (r"automatic reclosing device \(recloser\)", "自動再閉鎖装置（リクローザー）"),
        (r"secondary line maintenance", "低圧配電線（二次側）の保守点検"),
        (r"primary line maintenance", "高圧配電線（一次側）の保守点検"),
        (r"primary line upgrading", "高圧配電線の増容量・改修"),
        (r"reconstruction of primary lines?", "高圧配電幹線（一次回線）の改修・建て替え"),
        (r"replacement of primary pole", "高圧電柱の交換"),
        (r"replacement of rotten pole", "老朽電柱の交換"),
        (r"installation of distribution transformer", "配電変圧器（トランス）の設置"),
        (r"upgrading of distribution transformer", "配電変圧器（トランス）の増容量・更新"),
        (r"tapping of service entrance wire", "引き込み線の分岐接続（タップ）"),
        (r"tapping of primary line", "高圧配電線の分岐接続（タップ）"),
        (r"shutdown request from a customer", "顧客の要請に基づく送電停止（シャットダウン）"),
        (r"installation of line device hardware \(DS/FCO/LBS\)", "線路機器ハードウェア（DS/FCO/LBS）の設置"),
        (r"guying correction", "支線（ガイワイヤー）の補強"),
        (r"extension of primary lines \(line stringing\)", "高圧配電線の延伸・架線"),
        (r"line stringing", "配電線の架線・張り替え"),
        (r"installation of secondary lines?", "低圧配電線（二次回線）の設置"),
        (r"installation of primary pole", "高圧電柱の設置"),
    ]

    # 定型構文1: To prevent unnecessary s...
    m1 = re.search(r"To prevent unnecessary\s*[sｓ]?\s*due to anticipated system fault/damage\s*(?:Brgy\.\s*)?([^\s]+(?:\s+[^\s]+)?)\s*by facilitating\s*(.+)", res, re.IGNORECASE)
    if m1:
        area, act = m1.groups()
        act_ja = act.strip().rstrip(".")
        for pat, rep in actions:
            act_ja = re.sub(pat, rep, act_ja, flags=re.IGNORECASE)
        return f"突発的な停電事故を防止するため、{area.strip()}地区にて{act_ja}工事を実施するためです。"

    # 定型構文2: To improve the reliability...
    m2 = re.search(r"To improve the reliability of the distribution system serving\s*(?:Brgy\.\s*)?([^b]+?)\s*by facilitating\s*(.+)", res, re.IGNORECASE)
    if m2:
        area, act = m2.groups()
        act_ja = act.strip().rstrip(".")
        for pat, rep in actions:
            act_ja = re.sub(pat, rep, act_ja, flags=re.IGNORECASE)
        return f"周辺地域（{area.strip()}）へ電力を供給する配電システムの信頼性向上のため、{act_ja}工事を実施するためです。"

    # 定型構文3: To increase the capacity...
    m3 = re.search(r"To increase the capacity of the distribution system serving\s*(?:Brgy\.\s*)?([^b]+?)\s*by facilitating\s*(.+)", res, re.IGNORECASE)
    if m3:
        area, act = m3.groups()
        act_ja = act.strip().rstrip(".")
        for pat, rep in actions:
            act_ja = re.sub(pat, rep, act_ja, flags=re.IGNORECASE)
        return f"周辺地域（{area.strip()}）へ電力を供給する配電システムの容量増設のため、{act_ja}工事を実施するためです。"

    # エリア表現: Portion of X, along portion of Y
    m_aff = re.search(r"Portion of\s+([^,]+),\s*([^,]+),\s*along portion of\s+(.+)", res, re.IGNORECASE)
    if m_aff:
        brgy, city, st = m_aff.groups()
        st_clean = re.sub(r"Street", "通り", st, flags=re.IGNORECASE)
        st_clean = re.sub(r"Avenue|Ave", "通り", st_clean, flags=re.IGNORECASE)
        city_ja = cities_map_ja.get(city.strip(), city.strip())
        return f"{city_ja} {brgy.strip()}の一部、{st_clean.strip()}沿いの一部"

    m_aff2 = re.search(r"Portion of\s+([^,:]+)[:,]\s*(.+)", res, re.IGNORECASE)
    if m_aff2:
        c, b = m_aff2.groups()
        c_ja = cities_map_ja.get(c.strip(), c.strip())
        return f"{c_ja}の一部エリア: {b.strip()}"

    # 定型構文にマッチしなかった場合の単語置換
    for pat, rep in actions:
        res = re.sub(pat, rep, res, flags=re.IGNORECASE)
    return res

def cached_translate(text):
    if not text:
        return ""
    text_clean = text.strip()
    if text_clean in translation_cache:
        cached_val = translation_cache[text_clean]
        if has_japanese(cached_val):
            return cached_val
    
    if len(text_clean) > 1000:
        return text_clean
        
    # 1. 通常の GoogleTranslator
    try:
        translated = translator.translate(text_clean)
        if has_japanese(translated):
            translation_cache[text_clean] = translated
            return translated
    except Exception as e:
        pass

    # 2. 予備エンドポイント (ブラウザ偽装User-Agent付き Google Translate API)
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "ja",
            "dt": "t",
            "q": text_clean
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                translated = "".join([part[0] for part in data[0] if part and len(part) > 0 and part[0]])
                if has_japanese(translated):
                    translation_cache[text_clean] = translated
                    return translated
    except Exception as e:
        pass

    # 3. 緊急セーフティネット（ルールベース変換）
    rule_translated = rule_based_translate_veco(text_clean)
    if has_japanese(rule_translated):
        translation_cache[text_clean] = rule_translated
        return rule_translated

    return text_clean

# ==========================================
# 🛠️ 変換用ヘルパー関数群
# ==========================================
def parse_date(date_str):
    if not date_str:
        return None, None
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
    return None, None

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

def extract_date_range(text):
    months_pattern = "|".join(list(months_map.keys()) + list(months_abbrev.keys()))
    m_range = re.search(
        rf"\b({months_pattern})\s*(\d{{1,2}})\s*(?:-|to|–|—)\s*(\d{{1,2}})(?:,\s*(\d{{4}}))?\b",
        text,
        re.IGNORECASE
    )
    if m_range:
        m_en, start_d, end_d, y_str = m_range.groups()
        year = y_str if y_str else str(CURRENT_YEAR)
        m_num = months_abbrev.get(m_en.capitalize()[:3], "01")
        start_day = int(start_d)
        end_day = int(end_d)
        if start_day <= end_day and (end_day - start_day) <= 14:
            dates = []
            for d in range(start_day, end_day + 1):
                dates.append(f"{year}/{m_num}/{d:02d}")
            return dates
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
    
    # Overnightパターン (toまたはハイフンの両方に対応)
    pattern_overnight = r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*of\s*(\w+)\s*(\d+)\s*(?:to|-)\s*(\d{1,2}):(\d{2})\s*(AM|PM)\s*of\s*(\w+)\s*(\d+)"
    match_overnight = re.search(pattern_overnight, time_str_clean, re.IGNORECASE)
    if match_overnight:
        sh, sm, sampm, smonth, sday, eh, em, eampm, emonth, eday = match_overnight.groups()
        start_24 = to_24h(sh, sm, sampm)
        end_24 = to_24h(eh, em, eampm)
        return f"{start_24} - {end_24} (+1d)"

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
            
        # 両方とも AM/PM がない場合（22:00 - 06:00 など）
        if not sampm and not eampm:
            s_min = int(sh) * 60 + int(sm)
            e_min = int(eh) * 60 + int(em)
            plus_1d = " (+1d)" if e_min < s_min else ""
            return f"{int(sh):02d}:{int(sm):02d} - {int(eh):02d}:{int(em):02d}{plus_1d}"
            
        start_24 = to_24h(sh, sm, sampm)
        end_24 = to_24h(eh, em, eampm)
        s_h, s_m = map(int, start_24.split(":"))
        e_h, e_m = map(int, end_24.split(":"))
        s_min = s_h * 60 + s_m
        e_min = e_h * 60 + e_m
        plus_1d = " (+1d)" if e_min < s_min else ""
        return f"{start_24} - {end_24}{plus_1d}"
        
    return time_str_clean

def clean_translated_japanese(text):
    if not text:
        return ""
        
    # 1. 地名・通り・専門用語の表記ゆれ補正
    term_replacements = {
        r"リローン": "リロアン",
        r"タクド": "タユド",
        r"M\.C\.\s*の一部沿いブリオネス通り": "M.C.ブリオネス通り沿いの一部",
        r"配信システム": "配電システム",
        r"配信系統": "配電系統",
        r"一次回線の盗聴": "高圧配電線（一次回線）の分岐接続（タップ）",
        r"引込み線の盗聴": "引き込み線の分岐接続（タップ）",
        r"盗聴工事": "分岐接続（タップ）工事",
        r"盗聴": "分岐接続（タップ）",
        r"主要路線": "高圧配電幹線（一次回線）",
        r"主要電線": "高圧配電線",
        r"主極": "高圧電柱",
        r"一次電柱": "高圧電柱",
        r"一次極": "高圧電柱",
        r"一次ライン": "高圧配電線",
        r"プライマリ\s*ライン": "高圧配電線",
        r"自動再閉鎖装置\s*（リクローザー）": "自動再閉鎖装置（リクローザー）",
    }
    for pat, rep in term_replacements.items():
        text = re.sub(pat, rep, text)

    # バランガイやサービス提供の表現をインフラ用語として自然に
    text = re.sub(r"Brgy\s*にサービスを提供する", "周辺地域へ電力を供給する", text, flags=re.IGNORECASE)
    text = re.sub(r"Brgy\s*に電力を供給する", "周辺地域へ電力を供給する", text, flags=re.IGNORECASE)

    # 2. 突発停電・不要なs の補正
    text = re.sub(r"不要な\s*[sｓ]\s*を(?:防止するため|防ぐため|防止する|防ぐ)", "突発的な停電事故を防止するため", text, flags=re.IGNORECASE)
    text = re.sub(r"不要な(?:電力供給|停電|中断)を(?:防止|防ぐ)", "突発的な停電を防止", text)

    # 3. ホットスポット補正
    text = re.sub(r"([\w\s・-]+?)(?:による)?ホットスポット(?:修正|補修)の促進[。.]?", r"\1地区における異常発熱箇所（ホットスポット）の補修点検工事を実施するためです。", text)

    # 4. 文末に「、[地名]。」が取り残される語順崩れの補正
    text = re.sub(
        r"(?:を(?:促進することにより|促進することで|容易にすることにより|容易にすることで|促進することによって|行うことで|行うことにより|行うことによって)[、,\s]+)([\w\s・-]+)。?$",
        r"工事を実施するためです（対象地区: \1）。",
        text
    )
    text = re.sub(
        r"([\w・（）]+)の(アップグレード|設置|移設|再建|改修|タップ|交換|整備)を(?:促進することにより|促進することで|容易にすることにより|容易にすることで|促進することによって|行うことで|行うことにより|行うことによって)[、,\s]+([\w\s・-]+)。?$",
        r"\1の\2工事を実施するためです（対象地区: \3）。",
        text
    )

    # 5. 「〜を促進する」「〜を容易にする」直訳の補正
    text = re.sub(r"(?:を)?(?:再建|改修)を促進する[。.]?", "の改修・建て替え工事を実施するためです。", text)
    text = re.sub(r"(?:を)?設置を容易にする(?:ことにより|ことで|ことによって)?[、,.]?", "の設置工事を実施するため、", text)
    text = re.sub(r"(?:を)?交換を容易にする(?:ことにより|ことで|ことによって)?[、,.]?", "の交換工事を実施するため、", text)
    text = re.sub(r"(?:を)?メンテナンスを容易にする(?:ことにより|ことで|ことによって)?[、,.]?", "の保守点検工事を実施するため、", text)
    text = re.sub(r"を容易にすることによって", "を行うことによって", text)
    text = re.sub(r"容易になります", "行うためです", text)
    text = re.sub(r"容易にします", "行います", text)
    text = re.sub(r"容易にすることで", "行うことで", text)
    text = re.sub(r"容易にするため", "行うため", text)

    # 顧客の要請に基づくシャットダウン要求
    text = re.sub(
        r"([\w\s・]+)\s*は、顧客からの(?:シャットダウン要求|シャットダウン要請)を(?:容易にします|行います)。",
        r"顧客の要請に基づく送電停止（シャットダウン）工事を行うためです（対象エリア: \1）。",
        text
    )

    # 6. 「一部エリア:」が連続している箇所の整形（改行挿入）
    text = re.sub(r"([^\n]+の一部エリア:[^\n]+?)\s+([^\n]+の一部エリア:)", r"\1\n\2", text)

    # 7. 句読点・通りの整頓
    text = re.sub(r"の信頼性を向上させるため[。.]\s*", "の信頼性を向上させるため、", text)
    text = re.sub(r"([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+)の一部沿い([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+通り)", r"\1\2沿いの一部", text)
    text = re.sub(r"（対象エリア:\s*([\w\s・-]+)を実現します）", r"（対象エリア: \1）", text)
    text = re.sub(r"([\w\s・-]+)を実現します", r"\1", text)
    text = re.sub(r"、+", "、", text)
    text = re.sub(r"([。]+)", "。", text)

    return text.strip()

# ==========================================
# 🗺️ エリア・バランガイ判定マッピング辞書
# ==========================================
AREA_KEYWORDS = [
    # --- セブ市 ---
    {
        "en": "Cebu City (IT Park / Lahug)", "ja": "セブ市 (ITパーク / ラフグ)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["it park", "lahug", "salinas drive", "jy square", "gorordo"]
    },
    {
        "en": "Cebu City (Ayala / Business Park / Luz)", "ja": "セブ市 (アヤラ / ビジネスパーク / ルズ)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["ayala", "cebu business park", "cbp", "brgy. luz", "barangay luz", " luz,", "hipodromo", "cardinal rosales"]
    },
    {
        "en": "Cebu City (Mabolo / Kasambagan)", "ja": "セブ市 (マボロ / カスンバガン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["mabolo", "kasambagan", "tres borces", "sykes", "mj cuenco", "m.j. cuenco", "villa aurora", "sarrosa"]
    },
    {
        "en": "Cebu City (Banilad / AS Fortuna)", "ja": "セブ市 (バニラッド / ASフォーチュナ)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["banilad", "gov. cuenco", "governor cuenco", "country mall", "montebello", "maria luisa"]
    },
    {
        "en": "Cebu City (Talamban / Pit-os / Bacayan)", "ja": "セブ市 (タランバン / ピットオス / バカヤン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["talamban", "pit-os", "pitos", "bacayan", "binaliw", "pulangbato", "pulang bato", "nasipit", "san jose", "tigbao", "miñoza", "minoza"]
    },
    {
        "en": "Cebu City (Guadalupe / Capitol / Kalunasan)", "ja": "セブ市 (グアダルーペ / キャピトル / カルナサン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["guadalupe", "capitol site", "capitol", "kalunasan", "v. rama", "v rama", "englis", "oppra"]
    },
    {
        "en": "Cebu City (Apas)", "ja": "セブ市 (アパス)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["apas", "camp lapu-lapu", "camp lapulapu", "san antonio village"]
    },
    {
        "en": "Cebu City (Fuente / Ramos / Zapatera / Kamputhaw)", "ja": "セブ市 (フエンテ / ラモス / サパテラ / カンプタウ)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["fuente", "osmeña", "osmena", "ramos", "cogon ramos", "zapatera", "kamputhaw", "camputhaw", "lorega", "lorega san miguel", "santa cruz", "sta. cruz", "sikatuna", "sepulveda", "general maxilom", "mango avenue"]
    },
    {
        "en": "Cebu City (Downtown / Colon / Pahina / Pari-an)", "ja": "セブ市 (ダウンタウン / コロン / パヒナ / パリアン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["downtown", "colon", "pari-an", "parian", "sto. niño", "sto nino", "san roque", "ermita", "pahina central", "pahina san nicolas", "kalubihan", "kamagayan", "t. padilla", "t padilla", "tejero", "tinago", "sanciangko", "borromeo", "carbon", "sawang calero"]
    },
    {
        "en": "Cebu City (Mambaling / Duljo / Basak)", "ja": "セブ市 (マンバリン / ドゥルホ / バサック)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["mambaling", "duljo", "duljo fatima", "basak san nicolas", "basak pardo", "kinasang-an", "quiot", "n. bacalso", "natalio b. bacalso"]
    },
    {
        "en": "Cebu City (Punta Princesa / Tisa / Labangon)", "ja": "セブ市 (プンタ・プリンセサ / ティサ / ラバンゴン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["punta princesa", "tisa", "labangon", "buhisan", "calamba", "san nicolas proper", "tres de abril", "katipunan"]
    },
    {
        "en": "Cebu City (Pardo / Bulacao / Inayawan)", "ja": "セブ市 (パルド / ブラカオ / イナヤワン)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["pardo", "bulacao", "inayawan", "cogon pardo", "poblacion pardo", "toong", "south road properties", "srp"]
    },
    {
        "en": "Cebu City (Busay / Mountain Areas)", "ja": "セブ市 (ブサイ / 山間部)",
        "city_match": ["Cebu City", "Cebu"],
        "keywords": ["busay", "malubog", "babag", "sirao", "pung-ol", "taptap", "adlaon", "guba", "budlaan", "mabini", "transcentral", "tops"]
    },

    # --- マンダウエ市 ---
    {
        "en": "Mandaue City (AS Fortuna / Banilad)", "ja": "マンダウエ市 (ASフォーチュナ / バニラッド)",
        "city_match": ["Mandaue City", "Mandaue"],
        "keywords": ["a.s. fortuna", "as fortuna", "banilad", "oakridge", "j centre", "hernan cortes"]
    },
    {
        "en": "Mandaue City (Tipolo / Subangdaku / Guizo)", "ja": "マンダウエ市 (ティポロ / スバングダク / ギゾ)",
        "city_match": ["Mandaue City", "Mandaue"],
        "keywords": ["tipolo", "subangdaku", "subang daku", "bakilid", "guizo", "mantuyong", "lopez jaena"]
    },
    {
        "en": "Mandaue City (Basak / Jagobiao / Canduman)", "ja": "マンダウエ市 (バサック / ハゴビヤオ / カンドゥマン)",
        "city_match": ["Mandaue City", "Mandaue"],
        "keywords": ["basak", "jagobiao", "canduman", "tingub", "pagsabungan", "insulares"]
    },
    {
        "en": "Mandaue City (Centro / Looc / Reclamation)", "ja": "マンダウエ市 (セントロ / ルック / 埋立地)",
        "city_match": ["Mandaue City", "Mandaue"],
        "keywords": ["centro", "looc", "alang-alang", "alang alang", "ibabao", "ibabao-estancia", "opao", "umapad", "reclamation", "cdu", "parkmall"]
    },
    {
        "en": "Mandaue City (Cabancalan / Maguikay / Casuntingan)", "ja": "マンダウエ市 (カバンカラン / マグイカイ / カスンティンガン)",
        "city_match": ["Mandaue City", "Mandaue"],
        "keywords": ["cabancalan", "maguikay", "casuntingan", "tabok", "paknaan", "m. ceniza", "b.c. albano"]
    },

    # --- ラプラプ市 / マクタン島 ---
    {
        "en": "Lapu-Lapu City (Mactan / Newtown / Airport / Pusok)", "ja": "ラプラプ市 (マクタン / ニュータウン / 空港 / プソック)",
        "city_match": ["Lapu-Lapu City", "Lapu-Lapu", "Lapulapu", "Mactan"],
        "keywords": ["newtown", "mactan", "airport", "pusok", "ibo", "buaya", "bankal", "mactan-cebu"]
    },
    {
        "en": "Lapu-Lapu City (Maribago / Agus / Resort Area)", "ja": "ラプラプ市 (マリバゴ / アグス / リゾートホテル街)",
        "city_match": ["Lapu-Lapu City", "Lapu-Lapu", "Lapulapu", "Mactan"],
        "keywords": ["maribago", "agus", "marigondon", "subabasbas", "jpark", "solea", "plantation bay"]
    },
    {
        "en": "Lapu-Lapu City (Punta Engaño)", "ja": "ラプラプ市 (プンタ・エンガーニョ)",
        "city_match": ["Lapu-Lapu City", "Lapu-Lapu", "Lapulapu", "Mactan"],
        "keywords": ["punta engaño", "punta engano", "shangri-la", "shangrila", "mactan shrine", "mactan reef"]
    },
    {
        "en": "Lapu-Lapu City (Basak / Pajac / Gun-ob)", "ja": "ラプラプ市 (バサック / パハック / グンオブ)",
        "city_match": ["Lapu-Lapu City", "Lapu-Lapu", "Lapulapu", "Mactan"],
        "keywords": ["basak", "pajac", "gun-ob", "gun ob", "canjulao", "calawisan", "babag", "gaisano grand"]
    },

    # --- 近隣都市・自治体 ---
    {
        "en": "Talisay City", "ja": "タリサイ市",
        "city_match": ["Talisay City", "Talisay"],
        "keywords": ["talisay", "lagtang", "tabunok", "pooc", "dumlog", "mohon", "lawaan", "jaclupan", "bulacao, talisay"]
    },
    {
        "en": "Consolacion", "ja": "コンソラシオン",
        "city_match": ["Consolacion"],
        "keywords": ["consolacion", "casili", "garing", "panas", "panoypoy", "tayud", "jugan", "pitogo", "cansaga", "nangka", "pulpogan", "tolotolo"]
    },
    {
        "en": "Liloan", "ja": "リロアン",
        "city_match": ["Liloan"],
        "keywords": ["liloan", "jubay", "san vicente", "yati", "cotcot", "catarman", "calero", "cabadiangan", "lataban"]
    },
    {
        "en": "Minglanilla", "ja": "ミングラニラ",
        "city_match": ["Minglanilla"],
        "keywords": ["minglanilla", "tunghaan", "calajo-an", "pakigne", "tubod", "vito", "tulay", "linao"]
    },
    {
        "en": "Cordova", "ja": "コルドバ",
        "city_match": ["Cordova"],
        "keywords": ["cordova", "alegria", "bangbang", "buagsong", "gabi", "pilipog", "cclex"]
    },
    {
        "en": "City of Naga", "ja": "ナガ市",
        "city_match": ["City of Naga", "Naga City", "Naga"],
        "keywords": ["naga", "tuyan", "west poblacion", "east poblacion", "inoburan", "langtad", "tinaan", "colon, naga"]
    }
]

def parse_area_summary(affected_en, affected_ja=None):
    if not affected_en:
        return "Cebu", "セブ"

    # 1. 計画停電パターン: "Portion of [Brgy], [City], along ..."
    m_single = re.search(r'Portion[s]? of\s+([A-Za-z0-9\s\.\-]+?),\s*(Cebu City|Mandaue City|Lapu-Lapu City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova|City of Naga|Naga City)', affected_en, re.IGNORECASE)
    if m_single:
        brgy_en = m_single.group(1).replace("Brgy. ", "").replace("Brgys. ", "").strip()
        city_en = m_single.group(2).strip()
        city_ja = cities_map_ja.get(city_en, city_en)
        brgy_ja = clean_translated_japanese(cached_translate(brgy_en)).rstrip('。').rstrip('.')
        return f"{city_en} ({brgy_en})", f"{city_ja} ({brgy_ja})"

    # 2. 輪番停電等で "Portion of [City]: [Brgys...]" のパターン
    city_blocks = re.findall(r'Portion[s]? of\s+(Cebu City|Mandaue City|Lapu-Lapu City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova|City of Naga|Naga City)\s*[:：]\s*(.*?)(?=(?:Portion[s]? of\s+(?:Cebu City|Mandaue City|Lapu-Lapu City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova|City of Naga|Naga City)\s*[:：])|$)', affected_en, re.IGNORECASE | re.DOTALL)
    
    if city_blocks:
        first_city_en, raw_brgys = city_blocks[0]
        first_city_en = first_city_en.strip()
        city_ja = cities_map_ja.get(first_city_en, first_city_en)
        
        cleaned = re.sub(r'\s*&\s*', ', ', raw_brgys)
        cleaned = re.sub(r'\s+and\s+', ', ', cleaned, flags=re.IGNORECASE)
        brgys_en = [b.strip() for b in cleaned.split(',') if b.strip() and len(b.strip()) > 1]
        
        top_en = brgys_en[:3]
        
        # 日本語側の先頭地名を取得
        brgys_ja = []
        if affected_ja:
            m_ja = re.search(r'.*?の一部[:：]\s*(.*)', affected_ja)
            if m_ja:
                raw_ja = m_ja.group(1).strip()
                raw_ja = re.sub(r'\s*&\s*', '、', raw_ja)
                raw_ja = re.sub(r'\s*および\s*', '、', raw_ja)
                brgys_ja = [p.strip() for p in re.split(r'[,、]', raw_ja) if p.strip()]
        
        if not brgys_ja:
            top_ja = [clean_translated_japanese(cached_translate(b)).rstrip('。').rstrip('.') for b in top_en]
        else:
            top_ja = brgys_ja[:len(top_en)]
        
        suffix_en = "..." if len(brgys_en) > 3 or len(city_blocks) > 1 else ""
        suffix_ja = "..." if len(brgys_en) > 3 or len(city_blocks) > 1 else ""
        
        tag_en = f"{first_city_en} ({' / '.join(top_en)}{suffix_en})"
        tag_ja = f"{city_ja} ({' / '.join(top_ja)}{suffix_ja})"
        return tag_en, tag_ja

    # 3. カッコパターン: "Portion of [City] ([Brgy])"
    m_paren = re.search(r'Portion[s]? of\s+(Cebu City|Mandaue City|Lapu-Lapu City|Talisay City|Liloan|Minglanilla|Consolacion|Cordova|City of Naga|Naga City)\s*\((.*?)\)', affected_en, re.IGNORECASE)
    if m_paren:
        city_en = m_paren.group(1).strip()
        brgys = m_paren.group(2).strip()
        city_ja = cities_map_ja.get(city_en, city_en)
        cleaned = re.sub(r'\s*&\s*', ', ', brgys)
        parts_en = [p.strip().replace("Brgy. ", "") for p in cleaned.split(',') if p.strip()]
        top_en = parts_en[:3]
        top_ja = [clean_translated_japanese(cached_translate(b)).rstrip('。').rstrip('.') for b in top_en]
        suffix = "..." if len(parts_en) > 3 else ""
        return f"{city_en} ({' / '.join(top_en)}{suffix})", f"{city_ja} ({' / '.join(top_ja)}{suffix})"

    # 4. 都市名のみマッチした場合
    for city, city_ja in cities_map_ja.items():
        if city.lower() in affected_en.lower():
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
        
    if "flexible" in item_time.lower() or "tbd" in item_time.lower() or "as of" in item_time.lower():
        return False

    is_overnight = "(+1d)" in item_time or "overnight" in item_time.lower()

    # 終了時刻の抽出
    match = re.search(r'-\s*(\d{2}):(\d{2})', item_time)
    end_h, end_m = (int(match.group(1)), int(match.group(2))) if match else (None, None)

    # 1. 翌日またぎ（+1d）の場合の厳密な判定
    if is_overnight and end_h is not None:
        # 開始日が今日の場合: 終了は明日朝なので、今日中は絶対に未終了
        if item_dt_obj == today_pht:
            return False
        # 開始日が昨日（今日が終了日）の場合: 翌朝の終了時刻と現在時刻を比較
        elif item_dt_obj == today_pht - datetime.timedelta(days=1):
            current_h, current_m = current_dt_pht.hour, current_dt_pht.minute
            return (current_h > end_h) or (current_h == end_h and current_m >= end_m)
        # 開始日がそれより過去の場合: 終了済み
        elif item_dt_obj < today_pht - datetime.timedelta(days=1):
            return True
        # 開始日が未来の場合: 未終了
        else:
            return False

    # 2. 通常イベント（同日終了）の判定
    if item_dt_obj < today_pht:
        return True
    if item_dt_obj > today_pht:
        return False
        
    # 当日の場合: 終了時刻と比較
    if end_h is not None:
        current_h, current_m = current_dt_pht.hour, current_dt_pht.minute
        if (current_h > end_h) or (current_h == end_h and current_m >= end_m):
            return True
            
    return False

# ==========================================
# 輪番停電(Rotational Brownouts)専用 高度分解パーサー
# ==========================================
def parse_rotational_brownout_complex(text, date_formatted, today_str):
    text = unicodedata.normalize('NFKC', text)
    text_lower = text.lower()
    if "rotational brownout" not in text_lower and "possible rotational" not in text_lower:
        return []
        
    entries = []
    
    # セクション分割（Ongoing速報またはRestored区分）
    if "ongoing rotational brownout" in text_lower:
        m = re.search(r"(?:ongoing\s+rotational\s+brownout)(.*?)(?:restored\s+areas|\Z)", text, re.DOTALL | re.IGNORECASE)
        target_section = m.group(1) if m else text
    else:
        target_section = re.split(r"restored\s+areas", text, flags=re.IGNORECASE)[0]

    # スロット分割（時計アイコンまたは時間パターンで分割）
    # 時計アイコンがある場合はそれで分割、なければ時間パターンで分割
    if "⏰" in target_section:
        slots = target_section.split("⏰")
    else:
        # 改定スケジュール形式などの時間分割
        slots = re.split(r"(?=\b\d{1,2}:\d{2}\s*(?:AM|PM)\s*(?:-|to|–|—)\s*\d{1,2}:\d{2}\s*(?:AM|PM))", target_section, flags=re.IGNORECASE)

    for slot in slots:
        slot = slot.strip()
        if not slot:
            continue
            
        tm = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM)?\s*(?:-|to|–|—)\s*\d{1,2}:\d{2}\s*(?:AM|PM))", slot, re.IGNORECASE)
        if not tm:
            tm = re.search(r"(\d{1,2}:\d{2}[AP]M\s*-\s*\d{1,2}:\d{2}[AP]M)", slot, re.IGNORECASE)
        if not tm:
            continue
            
        raw_time = tm.group(1)
        time_formatted = parse_time(raw_time)
        
        # スロット内に日付（例: SEPTEMBER 6, 2026）があれば優先抽出
        slot_date = extract_mcwd_date(slot)
        item_date = slot_date if slot_date else date_formatted
        
        areas_part = slot[tm.end():]
        areas_part = re.sub(r"^\s*\|\s*[A-Za-z]+\s+\d{1,2}(?:-\s*\d{1,2})?,\s*\d{4}\s*", "", areas_part)
        
        # エリアブロックごとに分割 (各ブロックが都市・バランガイとマップURLを持つ)
        blocks = re.split(r"(?=📍|•|Portion[s]? of)", areas_part)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
                
            # マップURLの抽出
            map_match = re.search(r"(https?://(?:tinyurl\.com|maps\.google\.com|goo\.gl)/[^\s]+)", block)
            map_url = map_match.group(1) if map_match else ""
            if map_url:
                map_url = map_url.rstrip(").,;")
                
            # エリア名部分の抽出
            block_clean = re.sub(r"View the map.*", "", block, flags=re.IGNORECASE).strip()
            block_clean = re.sub(r"^[📍•\s]+", "", block_clean).strip()
            block_clean = clean_text_pipeline(block_clean)
            if not block_clean:
                continue
                
            city = ""
            brgys = []
            m = re.match(r"Portion[s]? of\s+([^,:]+)[:,]\s*(.*)", block_clean, re.IGNORECASE)
            if m:
                city = m.group(1).strip()
                brgys = [b.strip().rstrip('.') for b in re.split(r",|\band\b|&", m.group(2)) if b.strip()]
            else:
                for kc in ["Cebu City", "Mandaue City", "Talisay City", "Liloan", "Minglanilla", "Consolacion", "Cordova", "City of Naga", "Naga City"]:
                    if kc.lower() in block_clean.lower():
                        city = kc
                        rest = re.sub(rf".*?{kc}\s*[:,-]?\s*", "", block_clean, flags=re.IGNORECASE).strip()
                        brgys = [b.strip().rstrip('.') for b in re.split(r",|\band\b|&", rest) if b.strip()]
                        break
                        
            brgys = sorted(list(set([b for b in brgys if len(b) > 1 and "view the map" not in b.lower() and "http" not in b.lower()])))
            if not city or not brgys:
                continue
                
            city_ja = cities_map_ja.get(city, city)
            translated_brgys = [clean_translated_japanese(cached_translate(b)) for b in brgys]
            
            affected_en = f"Portion of {city}: {', '.join(brgys)}"
            affected_ja = f"{city_ja}の一部エリア: {', '.join(translated_brgys)}"
            
            try:
                dt_obj = datetime.datetime.strptime(item_date, "%Y/%m/%d")
                day_abbrev = dt_obj.strftime("%a")
            except:
                day_abbrev = "Sun"
                
            status_tag_en = "[ROTATIONAL BROWNOUT]"
            status_tag_ja = "【計画輪番停電】"
            
            entries.append({
                "id": 0,
                "type": "electricity",
                "date": item_date,
                "day": day_abbrev,
                "time": time_formatted,
                "areaEn": f"{city} ({', '.join(brgys[:2])}...)" if len(brgys) > 2 else f"{city} ({', '.join(brgys)})",
                "areaJa": f"{city_ja} ({', '.join(translated_brgys[:2])}...)" if len(translated_brgys) > 2 else f"{city_ja} ({', '.join(translated_brgys)})",
                "affectedEn": affected_en,
                "affectedJa": affected_ja,
                "detailsEn": f"{status_tag_en} Rotational brownout implemented due to power grid demand management.",
                "detailsJa": f"{status_tag_ja} 送電容量不足に伴う計画的な供給制限（輪番停電）です。",
                "mapUrl": map_url
            })
            
    return entries

# ==========================================
# 統合マージプロセッサ (完全重複のみ排除し、独立した回路・行データは保持)
# ==========================================
def merge_duplicate_outages(outages):
    """
    同一日時・同一対象地域の完全重複のみを排除し、
    回路（フィーダー）ごとに分かれた独立した行データは合体させずそのまま保持する。
    """
    seen = set()
    deduped = []
    for item in outages:
        # 重複判定キー：日付、時間、対象エリア（先頭60文字）、mapUrl
        key = (
            item.get("date", ""),
            item.get("time", ""),
            item.get("affectedEn", "")[:60].strip().lower(),
            item.get("mapUrl", "").strip()
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped

def remove_tbd_duplicates(outages):
    has_concrete_time = {}
    for item in outages:
        t = item["time"].lower()
        is_tbd = "tbd" in t or "flexible" in t or "as of" in t
        if not is_tbd:
            area_key = clean_text_pipeline(item["areaEn"]).lower()
            key = (item["date"], area_key)
            has_concrete_time[key] = True
            
    filtered = []
    for item in outages:
        t = item["time"].lower()
        is_tbd = "tbd" in t or "flexible" in t or "as of" in t
        if is_tbd:
            area_key = clean_text_pipeline(item["areaEn"]).lower()
            key = (item["date"], area_key)
            if key in has_concrete_time:
                print(f"⏰ 重複するTBD予定を除外しました: {item['date']} {item['areaEn']} (確定時間データが存在するため)")
                continue
        filtered.append(item)
    return filtered

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
            # 計画停電の個別記事リンク（hrefに "/post/" を含むaタグ）が描画されるまで待つ
            page.wait_for_selector('a[href*="/post/"]', timeout=15000)
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
            
            page.goto(base_url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            
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

    # 防災啓発（洪水、避難、台風、地震など）、オフィス閉鎖や採用情報の投稿を除外
    ignore_keywords = [
        "flood", "evacuate", "weather", "safety reminder", "typhoon", "storm", 
        "earthquake", "christmas", "holiday", "office closed", "advisory on office closure",
        "career", "job", "hiring"
    ]
    if any(k in text_lower for k in ignore_keywords):
        return None

    date_formatted = extract_mcwd_date(text)
    
    # 緊急アラート判定の厳格化（単なるemergencyやupdateを避け、輪番停電関連キーワードに限定）
    is_urgent_alert = any(k in text_lower for k in ["rotational brownout", "rotational load", "load shedding", "grid alert", "possible rotational"])
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
# 既存 data.js の未来スケジュール読み込み
# ==========================================
def load_existing_veco_outages(today_str):
    existing_outages = []
    if not os.path.exists("data.js"):
        return existing_outages
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r"export\s+const\s+VECO_OUTAGES\s*=\s*(\[.*?\]);", content, re.DOTALL)
        if m:
            raw_list = json.loads(m.group(1))
            for item in raw_list:
                # 電気かつ、日付が今日以降のデータのみ保持
                if item.get("type") == "electricity" and item.get("date", "") >= today_str:
                    existing_outages.append(item)
            print(f"📁 既存の data.js から未終了の未来スケジュール {len(existing_outages)} 件をロードしました。")
    except Exception as e:
        print(f"⚠️ 既存 data.js のロード中にエラーが発生しました: {e}")
    return existing_outages

def parse_gviz_date(val):
    if not val:
        return ""
    m = re.search(r'Date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)', str(val))
    if m:
        y = int(m.group(1))
        month = int(m.group(2)) + 1
        d = int(m.group(3))
        return f"{y:04d}/{month:02d}/{d:02d}"
    return str(val)

def fetch_veco_from_spreadsheet(today_str):
    sheet_id = "1rRq3A_2gFf0n68THzBVf6IYkHiSrhl1ZA6yOe50bp8o"
    main_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"
    updates_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?sheet=Updates&tqx=out:json"
    
    # 1. Updates シートの取得（スケジュール改定情報のマッピング作成）
    updates_map = {}
    try:
        r_up = requests.get(updates_url, timeout=15)
        if r_up.status_code == 200:
            m_up = re.search(r'setResponse\((.*)\);', r_up.text, re.DOTALL)
            if m_up:
                up_data = json.loads(m_up.group(1))
                up_table = up_data.get('table', {})
                for r in up_table.get('rows', []):
                    c = r.get('c', [])
                    def get_up_val(i):
                        if i < len(c) and c[i] and 'v' in c[i]:
                            return str(c[i]['v']).strip()
                        return ""
                    up_date = parse_gviz_date(get_up_val(0))
                    up_tag = get_up_val(2)
                    up_loc = get_up_val(3)
                    up_old = get_up_val(4)
                    up_new = get_up_val(5)
                    up_reason = get_up_val(6)
                    if up_date and up_loc and up_new:
                        key = (up_date, up_loc[:30].lower())
                        updates_map[key] = {
                            "tag": up_tag,
                            "old": up_old,
                            "new": up_new,
                            "reason": up_reason
                        }
    except Exception as e:
        print(f"⚠️ Updatesシートの取得警告: {e}")

    # 2. MainData シートの取得
    outages = []
    try:
        r_main = requests.get(main_url, timeout=15)
        if r_main.status_code != 200:
            print(f"⚠️ GoogleスプレッドシートAPIエラー: HTTP {r_main.status_code}")
            return []
        m_main = re.search(r'setResponse\((.*)\);', r_main.text, re.DOTALL)
        if not m_main:
            return []
        main_data = json.loads(m_main.group(1))
        main_table = main_data.get('table', {})
        rows = main_table.get('rows', [])
        
        for idx, r in enumerate(rows):
            c = r.get('c', [])
            def get_val(i):
                if i < len(c) and c[i] and 'v' in c[i]:
                    return str(c[i]['v']).strip()
                return ""
                
            exact_date = parse_gviz_date(get_val(1))
            category = get_val(2).lower()
            title = get_val(3)
            time_info = get_val(4)
            locations = get_val(5)
            status = get_val(6)
            map_url = get_val(7)
            
            if not exact_date or not time_info or not locations:
                continue
                
            if exact_date < today_str:
                continue
                
            # スケジュール改定（Updates）の適用
            loc_key = (exact_date, locations[:30].lower())
            if loc_key in updates_map:
                up_info = updates_map[loc_key]
                time_info = up_info["new"]
                title = f"{title} (改定: 旧{up_info['old']}から変更 - {up_info['reason']})"

            formatted_time = parse_time(time_info)
            area_en, area_ja = parse_area_summary(locations)
            
            try:
                dt_obj = datetime.datetime.strptime(exact_date, "%Y/%m/%d")
                day_abbrev = dt_obj.strftime("%a")
            except:
                day_abbrev = "Sun"
                
            is_rotational = "rotational" in category
            is_emergency = "emergency" in category
            
            if is_rotational:
                details_en = f"[ROTATIONAL BROWNOUT] {title}" if title else "[ROTATIONAL BROWNOUT] Rotational brownout implemented due to power grid demand management."
                details_ja = f"【計画輪番停電】 {cached_translate(title)}" if title else "【計画輪番停電】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
            elif is_emergency:
                details_en = f"[EMERGENCY OUTAGE] {title}" if title else "[EMERGENCY OUTAGE] Emergency power interruption."
                details_ja = f"【緊急停電】 {cached_translate(title)}" if title else "【緊急停電】 突発的な緊急停電情報です。"
            else:
                details_en = title if title else "Scheduled maintenance outage."
                details_ja = clean_translated_japanese(cached_translate(details_en))
            loc_lines = [l.strip() for l in locations.split('\n') if l.strip()]
            status_lines = [s.strip() for s in status.split('\n') if s.strip()]
            map_lines = [m.strip() for m in map_url.split('\n') if m.strip()]
            
            num_sub_entries = max(len(loc_lines), 1)
            for sub_idx in range(num_sub_entries):
                sub_loc = loc_lines[sub_idx] if sub_idx < len(loc_lines) else locations
                sub_status = status_lines[sub_idx].upper() if sub_idx < len(status_lines) else (status.strip().upper() if status else "UPCOMING")
                sub_map = map_lines[sub_idx] if sub_idx < len(map_lines) else map_url
                
                sub_affected_ja = clean_translated_japanese(cached_translate(sub_loc))
                sub_area_en, sub_area_ja = parse_area_summary(sub_loc, sub_affected_ja)
                
                sub_details_en = details_en
                sub_details_ja = details_ja
                if sub_status == "RESTORED":
                    if "（復旧済み" not in sub_details_ja:
                        sub_details_ja += "（復旧済み / 送電再開）"
                    if "(Restored)" not in sub_details_en:
                        sub_details_en += " (Restored)"

                outages.append({
                    "id": 0,
                    "type": "electricity",
                    "date": exact_date,
                    "day": day_abbrev,
                    "time": formatted_time,
                    "areaEn": sub_area_en,
                    "areaJa": sub_area_ja,
                    "affectedEn": sub_loc,
                    "affectedJa": sub_affected_ja,
                    "detailsEn": sub_details_en,
                    "detailsJa": sub_details_ja,
                    "mapUrl": sub_map,
                    "status": sub_status
                })
            
        print(f"📊 Googleスプレッドシートから {len(outages)} 件の有効な停電データを取得しました。")
    except Exception as e:
        print(f"⚠️ Googleスプレッドシートからの取得処理でエラー: {e}")
        
    return outages

def fetch_veco_facebook_advisories(today_str):
    """
    Apify経由でVECO公式Facebookの最新投稿（直近3件）を取得し、
    緊急停電や輪番停電、中止告知などの速報をパースして返す。
    Apifyトークン未設定やエラー時は安全に空リストを返すフェイルセーフ仕様。
    """
    if not APIFY_TOKEN:
        print("ℹ️ APIFY_TOKEN が未設定のため、Facebook速報チェックをスキップします。")
        return []
    
    print("\n👥 2. VECO公式Facebook（Apify）から最新速報をチェック中...")
    fb_outages = []
    try:
        veco_fb_raw = scrape_facebook_posts_via_apify("https://www.facebook.com/visayanelectriccompany/")
        if not veco_fb_raw:
            print("ℹ️ 新しいFacebook速報投稿はありませんでした。")
            return []
            
        for post in veco_fb_raw:
            post_lower = post.lower()
            
            unplanned_keywords = ["safety device to help protect", "automatically switched off", "unplanned power outage"]
            if any(k in post_lower for k in unplanned_keywords):
                print("⏭️ 計画外の自動遮断アナウンスをスキップしました。")
                continue
                
            portal_advisory_keywords = [
                "stay updated on service",
                "available on our official website",
                "access the service portal",
                "scan our qr code"
            ]
            if any(k in post_lower for k in portal_advisory_keywords) and not re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)", post, re.IGNORECASE):
                print("⏭️ 公式ウェブサイト誘導ポータル案内をスキップしました。")
                continue
                
            if "rotational brownout" in post_lower or "possible rotational" in post_lower:
                date_range = extract_date_range(post)
                if date_range:
                    valid_dates = [d for d in date_range if d >= today_str]
                    if not valid_dates:
                        continue
                    for target_date in valid_dates:
                        parsed_entries = parse_rotational_brownout_complex(post, target_date, today_str)
                        fb_outages.extend(parsed_entries)
                    continue
                    
                date_formatted = extract_mcwd_date(post)
                if not date_formatted:
                    date_formatted = today_str
                if date_formatted >= today_str:
                    parsed_entries = parse_rotational_brownout_complex(post, date_formatted, today_str)
                    fb_outages.extend(parsed_entries)
            else:
                parsed_post = parse_facebook_post_prose(post, is_water=False, today_str=today_str)
                if parsed_post:
                    fb_outages.append(parsed_post)
                    
        print(f"👥 Facebookから {len(fb_outages)} 件の速報情報を抽出しました。")
    except Exception as e:
        print(f"⚠️ Facebook速報の取得・解析中にエラーが発生しました（スプレッドシートデータで継続します）: {e}")
        
    return fb_outages

def merge_spreadsheet_and_facebook(spreadsheet_outages, fb_outages):
    """
    スプレッドシートの停電データとFacebook速報を安全に統合する。
    ・既にスプレッドシートにある計画停電は二重登録せずスキップ
    ・Facebook側で中止告知（CANCELLED）が出ている場合は反映
    ・スプレッドシートにない突発的な緊急停電・速報は新規追加
    """
    if not fb_outages:
        return spreadsheet_outages
        
    merged = list(spreadsheet_outages)
    
    for fb_item in fb_outages:
        fb_date = fb_item.get("date", "")
        fb_time = fb_item.get("time", "").strip()
        fb_area_en = fb_item.get("areaEn", "").strip().lower()
        fb_aff_en = fb_item.get("affectedEn", "").strip().lower()
        is_cancelled = "cancelled" in fb_item.get("detailsEn", "").lower() or "中止" in fb_item.get("detailsJa", "")
        
        matched_idx = -1
        for idx, sp_item in enumerate(merged):
            if sp_item.get("date") != fb_date:
                continue
            
            sp_area_en = sp_item.get("areaEn", "").strip().lower()
            sp_aff_en = sp_item.get("affectedEn", "").strip().lower()
            
            same_city = False
            for city in ["cebu city", "mandaue", "talisay", "liloan", "minglanilla", "consolacion", "cordova", "naga"]:
                if city in fb_area_en and city in sp_area_en:
                    same_city = True
                    break
            
            time_match = (fb_time != "TBD / Flexible" and sp_item.get("time") == fb_time)
            aff_words = [w for w in fb_aff_en.replace(",", " ").split() if len(w) > 4]
            aff_overlap = any(w in sp_aff_en for w in aff_words) if aff_words else False
            
            if (same_city and time_match) or (time_match and aff_overlap):
                matched_idx = idx
                break
                
        if matched_idx >= 0:
            if is_cancelled:
                print(f"📢 Facebookからの中止告知をスプレッドシートデータに反映しました: {fb_date} {merged[matched_idx]['areaJa']}")
                if "【中止】" not in merged[matched_idx]["detailsJa"]:
                    merged[matched_idx]["detailsJa"] = f"【中止】{merged[matched_idx]['detailsJa']}"
                    merged[matched_idx]["detailsEn"] = f"【CANCELLED】{merged[matched_idx]['detailsEn']}"
            else:
                print(f"ℹ️ Facebook投稿（{fb_date} {fb_item['areaJa']}）は既にスプレッドシートに含まれているため統合しました。")
        else:
            print(f"🔥 Facebook限定の速報・緊急停電を追加します: {fb_date} {fb_item['areaJa']}")
            if "【速報" not in fb_item["detailsJa"]:
                fb_item["detailsJa"] = f"【速報・FB公式】{fb_item['detailsJa']}"
                fb_item["detailsEn"] = f"[FB Advisory] {fb_item['detailsEn']}"
            merged.append(fb_item)
            
    return merged

# ==========================================
# ⚙️ メインパイプライン処理
# ==========================================
def fetch_veco_legacy_scraping(today_str):
    final_veco_outages = []
    veco_raw_articles = scrape_veco_raw_content()
    if APIFY_TOKEN:
        veco_fb_raw = scrape_facebook_posts_via_apify("https://www.facebook.com/visayanelectriccompany/")
    else:
        veco_fb_raw = []
    if veco_raw_articles:
        print("\n⚡ 3. VECO停電スケジュールデータの解析処理中...")
        for veco_raw in veco_raw_articles:
            article_text = "\n".join(veco_raw)
            article_text_lower = article_text.lower()

        
            # 記事全体に輪番停電キーワードが含まれる場合は、輪番停電パーサー専用で一括処理
            if "rotational brownout" in article_text_lower or "possible rotational" in article_text_lower:
                print("📝 輪番停電の大規模情報を検出しました。専用分解パーサーを実行します...")
                date_range = extract_date_range(article_text)
                if date_range:
                    valid_dates = [d for d in date_range if d >= today_str]
                    for target_date in valid_dates:
                        parsed_entries = parse_rotational_brownout_complex(article_text, target_date, today_str)
                        final_veco_outages.extend(parsed_entries)
                    continue

                date_formatted = extract_mcwd_date(article_text)
                if not date_formatted:
                    date_formatted = today_str
            
                parsed_entries = parse_rotational_brownout_complex(article_text, date_formatted, today_str)
                final_veco_outages.extend(parsed_entries)
                continue  # 通常の状態マシン（行ループ）へは流さず除外！

            current_date = None
            current_time = None
            month_names = list(months_map.keys())
        
            # --- [改善②: 状態マシン（State Machine）によるパース処理] ---
            active_item = None
            veco_outages = [] # この記事内でパースされた一時レコードを格納

            for line in veco_raw:

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
                if not date_formatted or date_formatted < today_str:
                    if not date_formatted:
                        print(f"⚠️ 日付の解析に失敗したためスキップしました: {raw.get('date_raw')}")
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

            # 2. 公式WEBサイト誘導ポータル案内のスキップ（具体的な時間表記がない広報文）
            portal_advisory_keywords = [
                "stay updated on service",
                "available on our official website",
                "access the service portal",
                "scan our qr code"
            ]
            if any(k in post_lower for k in portal_advisory_keywords) and not re.search(r"\d{1,2}:\d{2}\s*(?:AM|PM)", post, re.IGNORECASE):
                print("⏭️ 公式ウェブサイト誘導ポータル案内をスキップしました。")
                continue

            if "rotational brownout" in post_lower or "possible rotational" in post_lower:
                # 期間・日付範囲（例: DAILY | SEPTEMBER 9-13, 2026）の検出
                date_range = extract_date_range(post)
                if date_range:
                    valid_dates = [d for d in date_range if d >= today_str]
                    if not valid_dates:
                        print(f"⏭️ 過去の輪番停電期間（{date_range[0]}〜{date_range[-1]}）をスキップしました。")
                        continue
                    for target_date in valid_dates:
                        parsed_entries = parse_rotational_brownout_complex(post, target_date, today_str)
                        final_veco_outages.extend(parsed_entries)
                    continue

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


    # 既存 data.js の未終了未来スケジュールを読み込んで合体
    existing_future_outages = load_existing_veco_outages(today_str)
    all_veco = existing_future_outages + final_veco_outages

    print("\n⚡ 3-C. 重複する停電スケジュールの統合マージ処理を実行中...")
    final_veco_outages = merge_duplicate_outages(all_veco)
    final_veco_outages = remove_tbd_duplicates(final_veco_outages)

    # ------------------------------------------
    return final_veco_outages


# 60グループ全件精密ピン＆半径マスターデータ
DEFAULT_MASTER_GROUPS = [
  {
    "groupId": "grp-01",
    "timeSlot": "15:00 - 17:00",
    "areaJa": "セブ市 (カンピュソー / セブ ビジネス パーク / ラハグ...)",
    "affectedJa": "セブ市の一部: カンピュソー、セブ ビジネス パーク、ラハグ、ルズ",
    "affectedEn": "Portion of Cebu City: Camputhaw, Cebu Business Park, Lahug, & Luz",
    "mapUrl": "https://lh3.googleusercontent.com/d/1BFD_JP33E470Fgeqi0dm0r-Nl8ZLWSSK",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.32022,
        "lng": 123.90574,
        "radius": 250
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-02",
    "timeSlot": "15:00 - 17:00",
    "areaJa": "セブ市 (カンピュソー / コゴン・ラモス / ロレガ...)",
    "affectedJa": "セブ市の一部: カンピュソー、コゴン・ラモス、ロレガ、サパテラ",
    "affectedEn": "Portion of Cebu City: Camputhaw, Cogon Ramos, Lorega, & Zapatera",
    "mapUrl": "https://lh3.googleusercontent.com/d/1FoX9tiprhfBDfHTbb5I7I_Hu1jldtIrD",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.30952,
        "lng": 123.90588,
        "radius": 100
      },
      {
        "name": "Point 2",
        "lat": 10.31082,
        "lng": 123.90342,
        "radius": 200
      },
      {
        "name": "Point 3",
        "lat": 10.31133,
        "lng": 123.90089,
        "radius": 100
      },
      {
        "name": "Point 4",
        "lat": 10.31137,
        "lng": 123.89947,
        "radius": 100
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-03",
    "timeSlot": "15:00 - 17:00",
    "areaJa": "セブ市 (バカヤン / タランバン...)",
    "affectedJa": "セブ市の部分: バカヤンとタランバン、マンダウエ市の部分: バサック、カバンカラン、カンドゥマン、キューバク、ジャゴビアオ、ラボゴン、パグサブンガン、タボク、タワソン、コンソラシオンの部分: カシリ",
    "affectedEn": "Portion of Cebu City: Bacayan & Talamban, Portion of Mandaue City: Basak, Cabancalan, Canduman, Cubacub, Jagobiao, Labogon, Pagsabungan, Tabok, & Tawason, Portion of Consolacion: Casili",
    "mapUrl": "https://lh3.googleusercontent.com/d/1drKLIRxdXoL5t-9aufdjw9ZPXat2d5Y2",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.36791,
        "lng": 123.94913,
        "radius": 400
      },
      {
        "name": "Point 2",
        "lat": 10.36145,
        "lng": 123.94691,
        "radius": 400
      },
      {
        "name": "Point 3",
        "lat": 10.35486,
        "lng": 123.94647,
        "radius": 400
      },
      {
        "name": "Point 4",
        "lat": 10.34929,
        "lng": 123.94604,
        "radius": 300
      },
      {
        "name": "Point 5",
        "lat": 10.36203,
        "lng": 123.94123,
        "radius": 450
      },
      {
        "name": "Point 6",
        "lat": 10.36575,
        "lng": 123.93728,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.36778,
        "lng": 123.93514,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.366,
        "lng": 123.93042,
        "radius": 350
      },
      {
        "name": "Point 9",
        "lat": 10.36205,
        "lng": 123.9277,
        "radius": 350
      },
      {
        "name": "Point 10",
        "lat": 10.37166,
        "lng": 123.93376,
        "radius": 400
      },
      {
        "name": "Point 11",
        "lat": 10.37555,
        "lng": 123.92707,
        "radius": 650
      }
    ],
    "pinCount": 10
  },
  {
    "groupId": "grp-04",
    "timeSlot": "15:00 - 17:00",
    "areaJa": "セブ市 (バニラッド...)",
    "affectedJa": "セブ市の一部: バニラッド、マンダウエ市の一部: バキリッド、バニラッド、カバンカラン、カスンティンガン、マグイカイ",
    "affectedEn": "Portion of Cebu City: Banilad, Portion of Mandaue City: Bakilid, Banilad, Cabancalan, Casuntingan, & Maguikay",
    "mapUrl": "https://lh3.googleusercontent.com/d/1zattr9cxcXBe4F-PKPXXIxuwOxfEgP8c",
    "pins": [
      {
        "name": "Banilad",
        "lat": 10.34152,
        "lng": 123.92527,
        "radius": 400
      },
      {
        "name": "Cabancalan",
        "lat": 10.34371,
        "lng": 123.92655,
        "radius": 400
      },
      {
        "name": "Casuntingan",
        "lat": 10.33974,
        "lng": 123.93016,
        "radius": 400
      },
      {
        "name": "Maguikay",
        "lat": 10.33396,
        "lng": 123.93393,
        "radius": 500
      },
      {
        "name": "Point 5",
        "lat": 10.34287,
        "lng": 123.91849,
        "radius": 500
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-05",
    "timeSlot": "15:00 - 17:00",
    "areaJa": "セブ市 (デイアズ / カルビハン / カマガヤン...)",
    "affectedJa": "セブ市の一部: デイアズ、カルビハン、カマガヤン、ロレガ、パリアン、サンバグ 1、サン アントニオ、サン ロケ、セント。ニーニョ、T. パディラ、サパテラ",
    "affectedEn": "Portion of Cebu City: Day-as, Kalubihan, Kamagayan, Lorega, Pari-an, Sambag 1, San Antonio, San Roque, Sto. Niño, T. Padilla, & Zapatera",
    "mapUrl": "https://lh3.googleusercontent.com/d/1yKF8O44B9YROdtGZa_QcKbIR0PcPPbRD",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.30837,
        "lng": 123.90505,
        "radius": 200
      },
      {
        "name": "Point 2",
        "lat": 10.30647,
        "lng": 123.90377,
        "radius": 150
      },
      {
        "name": "Point 3",
        "lat": 10.30677,
        "lng": 123.90119,
        "radius": 150
      },
      {
        "name": "Point 4",
        "lat": 10.30428,
        "lng": 123.90226,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.30171,
        "lng": 123.90198,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.30183,
        "lng": 123.90514,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.3001,
        "lng": 123.89853,
        "radius": 350
      },
      {
        "name": "Point 8",
        "lat": 10.29626,
        "lng": 123.8982,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.29714,
        "lng": 123.90295,
        "radius": 300
      },
      {
        "name": "Point 10",
        "lat": 10.2941,
        "lng": 123.90123,
        "radius": 100
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-06",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "ミングラニラ (カドゥラワン / カラホアン / クアノス...)",
    "affectedJa": "ミングラニーラの一部: カドゥラワン、カラホアン、クアノス、リナオ、マンドゥアン、パキニ、トゥボッド、トゥンハーン、ヴィト、第 1 区、第 3 区、第 4 区、タリサイ市の部分: キャンプ 7、キャンプ 8、ラワーン I、ラワーン II、ラワーン III、リパタ",
    "affectedEn": "Portion of Minglanilla: Cadulawan, Calajo-an, Cuanos, Linao, Manduang, Pakigne, Tubod, Tunghaan, Vito, Ward 1, Ward 3, & Ward 4, Portion of Talisay City: Camp 7, Camp 8, Lawaan I, Lawaan II, Lawaan III, & Lipata",
    "mapUrl": "https://lh3.googleusercontent.com/d/1FBEouKi0fHoH2uZKTggpzGKsPtlMpNFS",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.24144,
        "lng": 123.78125,
        "radius": 200
      },
      {
        "name": "Point 2",
        "lat": 10.24626,
        "lng": 123.78545,
        "radius": 500
      },
      {
        "name": "Point 3",
        "lat": 10.24905,
        "lng": 123.7936,
        "radius": 500
      },
      {
        "name": "Point 4",
        "lat": 10.25302,
        "lng": 123.80057,
        "radius": 500
      },
      {
        "name": "Point 5",
        "lat": 10.25775,
        "lng": 123.80733,
        "radius": 500
      },
      {
        "name": "Point 6",
        "lat": 10.26121,
        "lng": 123.81369,
        "radius": 500
      },
      {
        "name": "Point 7",
        "lat": 10.26222,
        "lng": 123.82038,
        "radius": 500
      },
      {
        "name": "Point 8",
        "lat": 10.26915,
        "lng": 123.8106,
        "radius": 500
      },
      {
        "name": "Point 9",
        "lat": 10.26535,
        "lng": 123.80364,
        "radius": 500
      },
      {
        "name": "Point 10",
        "lat": 10.26089,
        "lng": 123.79689,
        "radius": 500
      },
      {
        "name": "Point 11",
        "lat": 10.25624,
        "lng": 123.78933,
        "radius": 500
      },
      {
        "name": "Point 12",
        "lat": 10.25192,
        "lng": 123.78201,
        "radius": 500
      },
      {
        "name": "Point 13",
        "lat": 10.24627,
        "lng": 123.77877,
        "radius": 300
      },
      {
        "name": "Point 14",
        "lat": 10.26055,
        "lng": 123.77766,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.26391,
        "lng": 123.78605,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.2683,
        "lng": 123.79334,
        "radius": 500
      },
      {
        "name": "Point 17",
        "lat": 10.27204,
        "lng": 123.80024,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.27635,
        "lng": 123.80745,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.26906,
        "lng": 123.77489,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.27229,
        "lng": 123.78238,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.27616,
        "lng": 123.78965,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.28024,
        "lng": 123.79775,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.28359,
        "lng": 123.80364,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.28997,
        "lng": 123.79606,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.28165,
        "lng": 123.78159,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.28693,
        "lng": 123.77425,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.29842,
        "lng": 123.79331,
        "radius": 500
      }
    ],
    "pinCount": 7
  },
  {
    "groupId": "grp-07",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "リロアン (カバディアンガン / コットコット / ジュベイ...)",
    "affectedJa": "リロアンの一部: カバディアンガン、コットコット、ジュベイ、ムラオ",
    "affectedEn": "Portion of Liloan: Cabadiangan, Cotcot, Jubay, & Mulao",
    "mapUrl": "https://lh3.googleusercontent.com/d/1_6wbx584Jj6GxHyPeh8a9JoZgV-pqVtH",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.41092,
        "lng": 123.99681,
        "radius": 100
      },
      {
        "name": "Point 2",
        "lat": 10.41299,
        "lng": 123.99579,
        "radius": 150
      },
      {
        "name": "Point 3",
        "lat": 10.41489,
        "lng": 123.99412,
        "radius": 150
      },
      {
        "name": "Point 4",
        "lat": 10.41759,
        "lng": 123.99403,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.42,
        "lng": 123.99334,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.423,
        "lng": 123.99141,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.42194,
        "lng": 123.99579,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.4238,
        "lng": 123.98454,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.42148,
        "lng": 123.98738,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.41523,
        "lng": 123.98802,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.41519,
        "lng": 123.99128,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.41345,
        "lng": 123.98476,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.42726,
        "lng": 123.9902,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.4303,
        "lng": 123.98969,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.43317,
        "lng": 123.98763,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.43655,
        "lng": 123.98402,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.43993,
        "lng": 123.98368,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.43486,
        "lng": 123.98505,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.4428,
        "lng": 123.98127,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.44517,
        "lng": 123.98059,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.44652,
        "lng": 123.97732,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.44707,
        "lng": 123.97404,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.4464,
        "lng": 123.97103,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.44276,
        "lng": 123.97069,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.44114,
        "lng": 123.96775,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.44597,
        "lng": 123.96709,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.44842,
        "lng": 123.96485,
        "radius": 200
      },
      {
        "name": "Point 28",
        "lat": 10.45158,
        "lng": 123.96358,
        "radius": 200
      },
      {
        "name": "Point 29",
        "lat": 10.45259,
        "lng": 123.96067,
        "radius": 200
      },
      {
        "name": "Point 30",
        "lat": 10.45614,
        "lng": 123.96032,
        "radius": 200
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-08",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "リロアン (コットコットとジュベイ)",
    "affectedJa": "リロアンの一部: コットコットとジュベイ",
    "affectedEn": "Portion of Liloan: Cotcot & Jubay",
    "mapUrl": "https://lh3.googleusercontent.com/d/1bKnP1cWQqd9khoUnkQA-gU0R4XmHsdqp",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.42529,
        "lng": 123.99404,
        "radius": 150
      },
      {
        "name": "Point 2",
        "lat": 10.42644,
        "lng": 123.99175,
        "radius": 150
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-09",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (カレタ / セブ ビジネス パーク / ヒポドロモ...)",
    "affectedJa": "セブ市の一部: カレタ、セブ ビジネス パーク、ヒポドロモ、マボロ、サン アントニオ、サン ロケ",
    "affectedEn": "Portion of Cebu City: Carreta, Cebu Business Park, Hipodromo, Mabolo, San Antonio, & San Roque",
    "mapUrl": "https://lh3.googleusercontent.com/d/1hghnWP3dXlgslR6Up-w7P6xWVOhCfORs",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.31348,
        "lng": 123.90713,
        "radius": 200
      },
      {
        "name": "Point 2",
        "lat": 10.31165,
        "lng": 123.90879,
        "radius": 100
      },
      {
        "name": "Point 3",
        "lat": 10.30996,
        "lng": 123.90802,
        "radius": 150
      },
      {
        "name": "Point 4",
        "lat": 10.31234,
        "lng": 123.91083,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.31355,
        "lng": 123.91319,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.31511,
        "lng": 123.91027,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.31614,
        "lng": 123.91222,
        "radius": 150
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-10",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "ミングラニラ (リパタ / パキーニ / ポブラシオン...)",
    "affectedJa": "ミングラニーラの一部: リパタ、パキーニ、ポブラシオン、トゥンキル、タリサイ市の一部: ビアソン、カンソジョン、ドゥムログ、リナオ、モホン、プーク、サン イシドロ",
    "affectedEn": "Portion of Minglanilla: Lipata, Pakigne, Poblacion, & Tungkil, Portion of Talisay City: Biasong, Cansojong, Dumlog, Linao, Mohon, Pooc, & San Isidro",
    "mapUrl": "https://lh3.googleusercontent.com/d/1TEQtLaAwL4_5fHxG9JgrjAIJOb__yQf6",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.24805,
        "lng": 123.8356,
        "radius": 200
      },
      {
        "name": "Point 2",
        "lat": 10.25008,
        "lng": 123.85483,
        "radius": 200
      },
      {
        "name": "Point 3",
        "lat": 10.25014,
        "lng": 123.8578,
        "radius": 200
      },
      {
        "name": "Point 4",
        "lat": 10.24719,
        "lng": 123.85025,
        "radius": 500
      },
      {
        "name": "Point 5",
        "lat": 10.2472,
        "lng": 123.84153,
        "radius": 500
      },
      {
        "name": "Point 6",
        "lat": 10.23951,
        "lng": 123.83843,
        "radius": 500
      },
      {
        "name": "Point 7",
        "lat": 10.24171,
        "lng": 123.84573,
        "radius": 400
      },
      {
        "name": "Point 8",
        "lat": 10.239,
        "lng": 123.83042,
        "radius": 500
      },
      {
        "name": "Point 9",
        "lat": 10.24516,
        "lng": 123.83454,
        "radius": 350
      },
      {
        "name": "Point 10",
        "lat": 10.24847,
        "lng": 123.82752,
        "radius": 500
      },
      {
        "name": "Point 11",
        "lat": 10.24938,
        "lng": 123.83265,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.24085,
        "lng": 123.81047,
        "radius": 500
      },
      {
        "name": "Point 13",
        "lat": 10.24081,
        "lng": 123.81789,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.24183,
        "lng": 123.82443,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.24652,
        "lng": 123.8128,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.24757,
        "lng": 123.82021,
        "radius": 300
      },
      {
        "name": "Point 17",
        "lat": 10.25242,
        "lng": 123.8106,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.25356,
        "lng": 123.81497,
        "radius": 400
      },
      {
        "name": "Point 19",
        "lat": 10.25487,
        "lng": 123.81849,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.25399,
        "lng": 123.82133,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.25259,
        "lng": 123.82424,
        "radius": 200
      }
    ],
    "pinCount": 9
  },
  {
    "groupId": "grp-11",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (カランバ / 国会議事堂跡 / グアダルーペ...)",
    "affectedJa": "セブ市の一部: カランバ、国会議事堂跡、グアダルーペ、ラバンゴン、サンバッグ 1、サンバッグ 2",
    "affectedEn": "Portion of Cebu City: Calamba, Capitol Site, Guadalupe, Labangon, Sambag 1, & Sambag 2",
    "mapUrl": "https://lh3.googleusercontent.com/d/1fmlWU3Dd5x8Xz6PCixYGx0SpNJq05bz9",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.308,
        "lng": 123.89231,
        "radius": 150
      },
      {
        "name": "Point 2",
        "lat": 10.30647,
        "lng": 123.89338,
        "radius": 100
      },
      {
        "name": "Point 3",
        "lat": 10.30635,
        "lng": 123.89166,
        "radius": 100
      },
      {
        "name": "Point 4",
        "lat": 10.30659,
        "lng": 123.89004,
        "radius": 100
      },
      {
        "name": "Point 5",
        "lat": 10.30626,
        "lng": 123.88817,
        "radius": 100
      },
      {
        "name": "Point 6",
        "lat": 10.30791,
        "lng": 123.89029,
        "radius": 100
      },
      {
        "name": "Point 7",
        "lat": 10.30797,
        "lng": 123.88819,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.3106,
        "lng": 123.88783,
        "radius": 150
      },
      {
        "name": "Point 9",
        "lat": 10.31207,
        "lng": 123.88836,
        "radius": 100
      },
      {
        "name": "Point 10",
        "lat": 10.30664,
        "lng": 123.88568,
        "radius": 100
      },
      {
        "name": "Point 11",
        "lat": 10.30597,
        "lng": 123.884,
        "radius": 100
      },
      {
        "name": "Point 12",
        "lat": 10.30909,
        "lng": 123.88995,
        "radius": 100
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-12",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (ブラカオとトン / タリサイ市の一部: ブラカオ...)",
    "affectedJa": "セブ市の一部: ブラカオとトン、タリサイ市の一部: ブラカオ、キャンプ 4、カンドゥラワン、ジャクルパン、ラグタン、ラワーン 1、ラワーン 2、ラワーン 3、リナオ、マガウェイ、モホン、タブノク",
    "affectedEn": "Portion of Cebu City: Bulacao & Toong, Portion of Talisay City: Bulacao, Camp 4, Candulawan, Jaclupan, Lagtang, Lawaan 1, Lawaan 2, Lawaan 3, Linao, Maghaway, Mohon, & Tabunok",
    "mapUrl": "https://lh3.googleusercontent.com/d/1q2UG_Y-9oBQW57bEZN9_1-_4tTSWD-f8",
    "pins": [
      {
        "name": "Bulacao",
        "lat": 10.27354,
        "lng": 123.84518,
        "radius": 250
      },
      {
        "name": "Bulacao",
        "lat": 10.26669,
        "lng": 123.84596,
        "radius": 300
      },
      {
        "name": "Camp 4",
        "lat": 10.31788,
        "lng": 123.81833,
        "radius": 500
      },
      {
        "name": "Candulawan",
        "lat": 10.28097,
        "lng": 123.83163,
        "radius": 500
      },
      {
        "name": "Jaclupan",
        "lat": 10.29229,
        "lng": 123.8148,
        "radius": 500
      },
      {
        "name": "Lagtang",
        "lat": 10.27261,
        "lng": 123.83042,
        "radius": 500
      },
      {
        "name": "Lawaan 1",
        "lat": 10.25884,
        "lng": 123.83248,
        "radius": 350
      },
      {
        "name": "Lawaan 2",
        "lat": 10.26467,
        "lng": 123.83369,
        "radius": 500
      },
      {
        "name": "Lawaan 3",
        "lat": 10.268,
        "lng": 123.822,
        "radius": 500
      },
      {
        "name": "Linao",
        "lat": 10.2607,
        "lng": 123.82553,
        "radius": 500
      },
      {
        "name": "Maghaway",
        "lat": 10.28367,
        "lng": 123.81584,
        "radius": 500
      },
      {
        "name": "Mohon",
        "lat": 10.25488,
        "lng": 123.82931,
        "radius": 500
      },
      {
        "name": "Tabunok",
        "lat": 10.26957,
        "lng": 123.83961,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.27449,
        "lng": 123.81671,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.27666,
        "lng": 123.83952,
        "radius": 500
      },
      {
        "name": "Point 17",
        "lat": 10.28817,
        "lng": 123.82607,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.30167,
        "lng": 123.81634,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.31003,
        "lng": 123.81635,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.32488,
        "lng": 123.81781,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.27162,
        "lng": 123.85182,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.27753,
        "lng": 123.84589,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-13",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (バニラッド / タランバン...)",
    "affectedJa": "セブ市の一部: バニラッド & タランバン、マンダウエ市の一部: カバンカラン",
    "affectedEn": "Portion of Cebu City: Banilad & Talamban, Portion of Mandaue City: Cabancalan",
    "mapUrl": "https://lh3.googleusercontent.com/d/1ede4D2oKiveec5ig-dqnm6zj5nSUkZos",
    "pins": [
      {
        "name": "Banilad",
        "lat": 10.3481,
        "lng": 123.92458,
        "radius": 300
      },
      {
        "name": "Talamban",
        "lat": 10.35975,
        "lng": 123.92098,
        "radius": 350
      },
      {
        "name": "Cabancalan",
        "lat": 10.3519,
        "lng": 123.92707
      },
      {
        "name": "Point 4",
        "lat": 10.34567,
        "lng": 123.92237,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.35393,
        "lng": 123.92303,
        "radius": 350
      },
      {
        "name": "Point 6",
        "lat": 10.35597,
        "lng": 123.91997,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.35857,
        "lng": 123.92535,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.3553,
        "lng": 123.92692,
        "radius": 200
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-14",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (アグスンゴット / アパス / ババグ...)",
    "affectedJa": "セブ市の一部: アグスンゴット、アパス、ババグ、ビナリウ、ボンボン、ブオ、ブサイ、カンプソー、グバ、ラフグ、マルボグ、プランバト、プンオル・シブガイ、サンロケ、シラオ、タブナン、タグバオ、タプタップ",
    "affectedEn": "Portion of Cebu City: Agsungot, Apas, Babag, Binaliw, Bonbon, Buot, Busay, Camputhaw, Guba, Lahug, Malubog, Pulangbato, Pung-ol Sibugay, San Roque, Sirao, Tabunan, Tagba-o, & Taptap",
    "mapUrl": "https://lh3.googleusercontent.com/d/1-a9ANwYKu3VZkU6fJ2MPtwQdgwaw6UKo",
    "pins": [
      {
        "name": "Apas",
        "lat": 10.33569,
        "lng": 123.89608
      },
      {
        "name": "Babag",
        "lat": 10.37378,
        "lng": 123.84785,
        "radius": 500
      },
      {
        "name": "Binaliw",
        "lat": 10.40788,
        "lng": 123.86793,
        "radius": 500
      },
      {
        "name": "Bonbon",
        "lat": 10.37065,
        "lng": 123.83961,
        "radius": 500
      },
      {
        "name": "Buot",
        "lat": 10.36728,
        "lng": 123.8306,
        "radius": 500
      },
      {
        "name": "Busay",
        "lat": 10.36727,
        "lng": 123.87961,
        "radius": 500
      },
      {
        "name": "Camputhaw",
        "lat": 10.32096,
        "lng": 123.8993
      },
      {
        "name": "Lahug",
        "lat": 10.33594,
        "lng": 123.89849
      },
      {
        "name": "Malubog",
        "lat": 10.37943,
        "lng": 123.87051,
        "radius": 500
      },
      {
        "name": "Pulangbato",
        "lat": 10.42183,
        "lng": 123.8614,
        "radius": 500
      },
      {
        "name": "Sirao",
        "lat": 10.42273,
        "lng": 123.87325,
        "radius": 500
      },
      {
        "name": "Point 12",
        "lat": 10.32353,
        "lng": 123.89694,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.32439,
        "lng": 123.9,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.32733,
        "lng": 123.89896,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.32697,
        "lng": 123.89618,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.32973,
        "lng": 123.89662,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.33032,
        "lng": 123.89945,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.33243,
        "lng": 123.89662,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.33344,
        "lng": 123.89859,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.33959,
        "lng": 123.89681,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.34601,
        "lng": 123.89406,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.35243,
        "lng": 123.88908,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.35936,
        "lng": 123.8841,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.36558,
        "lng": 123.86965,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.37322,
        "lng": 123.8745,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.37288,
        "lng": 123.86454,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.37977,
        "lng": 123.86175,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.41393,
        "lng": 123.87347,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.37276,
        "lng": 123.85695,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.38078,
        "lng": 123.8537,
        "radius": 500
      },
      {
        "name": "Point 31",
        "lat": 10.38956,
        "lng": 123.85686,
        "radius": 500
      },
      {
        "name": "Point 32",
        "lat": 10.39555,
        "lng": 123.85094,
        "radius": 500
      },
      {
        "name": "Point 33",
        "lat": 10.39684,
        "lng": 123.85903,
        "radius": 500
      },
      {
        "name": "Point 34",
        "lat": 10.40191,
        "lng": 123.86375,
        "radius": 500
      },
      {
        "name": "Point 35",
        "lat": 10.40385,
        "lng": 123.85328,
        "radius": 500
      },
      {
        "name": "Point 36",
        "lat": 10.41212,
        "lng": 123.84907,
        "radius": 500
      },
      {
        "name": "Point 37",
        "lat": 10.42124,
        "lng": 123.84186,
        "radius": 500
      },
      {
        "name": "Point 38",
        "lat": 10.42791,
        "lng": 123.84615,
        "radius": 500
      },
      {
        "name": "Point 39",
        "lat": 10.43467,
        "lng": 123.85122,
        "radius": 500
      },
      {
        "name": "Point 40",
        "lat": 10.43988,
        "lng": 123.8566,
        "radius": 500
      },
      {
        "name": "Point 41",
        "lat": 10.42097,
        "lng": 123.85157,
        "radius": 500
      },
      {
        "name": "Point 42",
        "lat": 10.42959,
        "lng": 123.87792,
        "radius": 500
      },
      {
        "name": "Point 43",
        "lat": 10.43474,
        "lng": 123.87054,
        "radius": 500
      },
      {
        "name": "Point 44",
        "lat": 10.43694,
        "lng": 123.86315,
        "radius": 500
      },
      {
        "name": "Point 45",
        "lat": 10.43135,
        "lng": 123.88638,
        "radius": 500
      },
      {
        "name": "Point 46",
        "lat": 10.4132,
        "lng": 123.858,
        "radius": 500
      },
      {
        "name": "Point 47",
        "lat": 10.41683,
        "lng": 123.83454,
        "radius": 500
      },
      {
        "name": "Point 48",
        "lat": 10.41252,
        "lng": 123.82819,
        "radius": 500
      },
      {
        "name": "Point 49",
        "lat": 10.42459,
        "lng": 123.83334,
        "radius": 500
      },
      {
        "name": "Point 50",
        "lat": 10.36052,
        "lng": 123.82415,
        "radius": 500
      }
    ],
    "pinCount": 7
  },
  {
    "groupId": "grp-15",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (カンピュソーと国会議事堂跡)",
    "affectedJa": "セブ市の一部: カンピュソーと国会議事堂跡",
    "affectedEn": "Portion of Cebu City: Camputhaw & Capitol Site",
    "mapUrl": "https://lh3.googleusercontent.com/d/1YpzmIx7_EzriXBI5zLtXiUSuD1ldbfcw",
    "pins": [
      {
        "name": "Camputhaw",
        "lat": 10.31901,
        "lng": 123.89338
      },
      {
        "name": "Capitol Site",
        "lat": 10.31099,
        "lng": 123.89085
      },
      {
        "name": "Point 3",
        "lat": 10.31417,
        "lng": 123.89065,
        "radius": 200
      },
      {
        "name": "Point 4",
        "lat": 10.31977,
        "lng": 123.89634,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.32182,
        "lng": 123.89248,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.32163,
        "lng": 123.89512,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.31914,
        "lng": 123.89866,
        "radius": 100
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-16",
    "timeSlot": "16:00 - 18:00",
    "areaJa": "セブ市 (アドロン / アグスンゴット / バカヤン...)",
    "affectedJa": "セブ市の部分: アドラン、アグスンゴット、バカヤン、ビナリウ、ブドラーン、カンビノコット、グバ、カルビハン、ラニプガ、ルサラン、マビニ、パリル、ピオス、プランバト、サンノゼ、タランバン、マンダウエ市の部分: カバンカラン、カンドゥマン、コンソラシオンの部分: カバンガハン、パナス",
    "affectedEn": "Portion of Cebu City: Adlaon, Agsungot, Bacayan, Binaliw, Budlaan, Cambinocot, Guba, Kalubihan, Lanipga, Lusaran, Mabini, Paril, Pit-os, Pulangbato, San Jose, & Talamban, Portion of Mandaue City: Cabancalan & Canduman, Portion of Consolacion: Cabangahan & Panas",
    "mapUrl": "https://lh3.googleusercontent.com/d/1xplSAwqgJGBIiG_WKHMHIQPEBxHU2d-S",
    "pins": [
      {
        "name": "Bacayan",
        "lat": 10.37191,
        "lng": 123.90874,
        "radius": 500
      },
      {
        "name": "Binaliw",
        "lat": 10.40239,
        "lng": 123.90664,
        "radius": 500
      },
      {
        "name": "Budlaan",
        "lat": 10.37,
        "lng": 123.9,
        "radius": 500
      },
      {
        "name": "Kalubihan",
        "lat": 10.37584,
        "lng": 123.91428,
        "radius": 500
      },
      {
        "name": "Pit-Os",
        "lat": 10.39766,
        "lng": 123.91334,
        "radius": 500
      },
      {
        "name": "Pulangbato",
        "lat": 10.37554,
        "lng": 123.92106,
        "radius": 500
      },
      {
        "name": "Talamban",
        "lat": 10.36123,
        "lng": 123.91248,
        "radius": 400
      },
      {
        "name": "Canduman",
        "lat": 10.37074,
        "lng": 123.92672,
        "radius": 500
      },
      {
        "name": "Point 10",
        "lat": 10.36736,
        "lng": 123.92196,
        "radius": 500
      },
      {
        "name": "Point 11",
        "lat": 10.36892,
        "lng": 123.91552,
        "radius": 500
      },
      {
        "name": "Point 12",
        "lat": 10.3835,
        "lng": 123.91645,
        "radius": 500
      },
      {
        "name": "Point 13",
        "lat": 10.39066,
        "lng": 123.91514,
        "radius": 500
      },
      {
        "name": "Point 14",
        "lat": 10.40503,
        "lng": 123.91645,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.39927,
        "lng": 123.91934,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.39591,
        "lng": 123.91963,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.39251,
        "lng": 123.92046,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.38888,
        "lng": 123.9196,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.40824,
        "lng": 123.91199,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.41261,
        "lng": 123.91565,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.39979,
        "lng": 123.89808,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.40467,
        "lng": 123.89179,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.40486,
        "lng": 123.88246,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.37563,
        "lng": 123.89445,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.3796,
        "lng": 123.88759,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.37386,
        "lng": 123.88168,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.42062,
        "lng": 123.91548,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.42847,
        "lng": 123.91299,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.43548,
        "lng": 123.90879,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.43945,
        "lng": 123.90312,
        "radius": 500
      },
      {
        "name": "Point 31",
        "lat": 10.44789,
        "lng": 123.90458,
        "radius": 500
      },
      {
        "name": "Point 32",
        "lat": 10.45603,
        "lng": 123.90329,
        "radius": 500
      },
      {
        "name": "Point 33",
        "lat": 10.46453,
        "lng": 123.90206,
        "radius": 500
      },
      {
        "name": "Point 34",
        "lat": 10.44714,
        "lng": 123.91388,
        "radius": 500
      },
      {
        "name": "Point 35",
        "lat": 10.45288,
        "lng": 123.9198,
        "radius": 500
      },
      {
        "name": "Point 36",
        "lat": 10.462,
        "lng": 123.92083,
        "radius": 500
      },
      {
        "name": "Point 37",
        "lat": 10.45371,
        "lng": 123.92818,
        "radius": 500
      },
      {
        "name": "Point 38",
        "lat": 10.45482,
        "lng": 123.93723,
        "radius": 500
      },
      {
        "name": "Point 39",
        "lat": 10.4484,
        "lng": 123.93359,
        "radius": 450
      },
      {
        "name": "Point 40",
        "lat": 10.463,
        "lng": 123.93728,
        "radius": 500
      }
    ],
    "pinCount": 10
  },
  {
    "groupId": "grp-17",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "ナガ市 (アルパコ / バリロン / カンタオアン...)",
    "affectedJa": "ナガ市の一部: アルパコ、バリロン、カンタオアン、コゴン、コロン、ギンダルハン、イナヤガン、ジャギミット、ラナス、ルタック、マヤナ、北ポブラシオン、パンダン、南ポブラシオン、タグジャギミット、タンケ、ティナーン、トゥヤン、ウリン、ミングラニラの一部: キャンプ 8、ラタバン、パナス、トゥンハーン、トゥンコップ",
    "affectedEn": "Portion of City of Naga: Alpaco, Balirong, Cantao-an, Cogon, Colon, Guindaruhan, Inayagan, Jaguimit, Lanas, Lutac, Mayana, North Poblacion, Pangdan, South Poblacion, Tagjaguimit, Tangke, Tinaan, Tuyan, & Uling, Portion of Minglanilla: Camp 8, Lataban, Panas, Tunghaan, & Tungkop",
    "mapUrl": "https://lh3.googleusercontent.com/d/1HLSvs5uVLSx6uuOGCcxR8d_RNe4DzktU",
    "pins": [
      {
        "name": "Alpaco",
        "lat": 10.21678,
        "lng": 123.73773,
        "radius": 500
      },
      {
        "name": "Balirong",
        "lat": 10.24001,
        "lng": 123.74537,
        "radius": 500
      },
      {
        "name": "Cantao-An",
        "lat": 10.22929,
        "lng": 123.74468,
        "radius": 500
      },
      {
        "name": "Cogon",
        "lat": 10.23562,
        "lng": 123.75,
        "radius": 500
      },
      {
        "name": "Colon",
        "lat": 10.23148,
        "lng": 123.73172,
        "radius": 500
      },
      {
        "name": "Inayagan",
        "lat": 10.23123,
        "lng": 123.76605,
        "radius": 500
      },
      {
        "name": "Jaguimit",
        "lat": 10.26021,
        "lng": 123.71018,
        "radius": 500
      },
      {
        "name": "Lutac",
        "lat": 10.23925,
        "lng": 123.76468,
        "radius": 500
      },
      {
        "name": "North Poblacion",
        "lat": 10.23579,
        "lng": 123.73876,
        "radius": 500
      },
      {
        "name": "South Poblacion",
        "lat": 10.21062,
        "lng": 123.74442,
        "radius": 500
      },
      {
        "name": "Tangke",
        "lat": 10.21475,
        "lng": 123.75369,
        "radius": 400
      },
      {
        "name": "Tinaan",
        "lat": 10.21155,
        "lng": 123.75824,
        "radius": 500
      },
      {
        "name": "Tuyan",
        "lat": 10.22506,
        "lng": 123.76133,
        "radius": 350
      },
      {
        "name": "Uling",
        "lat": 10.25158,
        "lng": 123.7246,
        "radius": 500
      },
      {
        "name": "Lataban",
        "lat": 10.435,
        "lng": 123.978
      },
      {
        "name": "Tunghaan",
        "lat": 10.23604,
        "lng": 123.77231,
        "radius": 500
      },
      {
        "name": "Point 17",
        "lat": 10.24214,
        "lng": 123.77654,
        "radius": 400
      },
      {
        "name": "Point 18",
        "lat": 10.21915,
        "lng": 123.75987,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.2074,
        "lng": 123.75274,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.22414,
        "lng": 123.73385,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.22161,
        "lng": 123.74264,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.24407,
        "lng": 123.75189,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.24035,
        "lng": 123.75798,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.24879,
        "lng": 123.77232,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.25643,
        "lng": 123.76737,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.26036,
        "lng": 123.75927,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.25285,
        "lng": 123.75463,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.23522,
        "lng": 123.72309,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.24465,
        "lng": 123.72339,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.25918,
        "lng": 123.72648,
        "radius": 400
      },
      {
        "name": "Point 31",
        "lat": 10.26425,
        "lng": 123.73129,
        "radius": 400
      },
      {
        "name": "Point 32",
        "lat": 10.26796,
        "lng": 123.73609,
        "radius": 350
      },
      {
        "name": "Point 33",
        "lat": 10.26767,
        "lng": 123.7425,
        "radius": 350
      },
      {
        "name": "Point 34",
        "lat": 10.26852,
        "lng": 123.74919,
        "radius": 400
      },
      {
        "name": "Point 35",
        "lat": 10.26717,
        "lng": 123.75555,
        "radius": 350
      },
      {
        "name": "Point 36",
        "lat": 10.2746,
        "lng": 123.75297,
        "radius": 500
      },
      {
        "name": "Point 37",
        "lat": 10.25259,
        "lng": 123.71567,
        "radius": 500
      },
      {
        "name": "Point 38",
        "lat": 10.25276,
        "lng": 123.70606,
        "radius": 500
      },
      {
        "name": "Point 39",
        "lat": 10.24727,
        "lng": 123.69928,
        "radius": 500
      },
      {
        "name": "Point 40",
        "lat": 10.24423,
        "lng": 123.69086,
        "radius": 500
      },
      {
        "name": "Point 41",
        "lat": 10.26801,
        "lng": 123.71451,
        "radius": 500
      },
      {
        "name": "Point 42",
        "lat": 10.27646,
        "lng": 123.71246,
        "radius": 500
      },
      {
        "name": "Point 43",
        "lat": 10.28519,
        "lng": 123.71395,
        "radius": 500
      },
      {
        "name": "Point 44",
        "lat": 10.29229,
        "lng": 123.71944,
        "radius": 500
      },
      {
        "name": "Point 45",
        "lat": 10.24702,
        "lng": 123.68305,
        "radius": 500
      },
      {
        "name": "Point 46",
        "lat": 10.25378,
        "lng": 123.67945,
        "radius": 500
      },
      {
        "name": "Point 47",
        "lat": 10.26344,
        "lng": 123.68087,
        "radius": 500
      },
      {
        "name": "Point 48",
        "lat": 10.26976,
        "lng": 123.68668,
        "radius": 500
      },
      {
        "name": "Point 49",
        "lat": 10.27711,
        "lng": 123.69141,
        "radius": 500
      },
      {
        "name": "Point 50",
        "lat": 10.28609,
        "lng": 123.69221,
        "radius": 500
      },
      {
        "name": "Point 51",
        "lat": 10.29171,
        "lng": 123.698,
        "radius": 500
      },
      {
        "name": "Point 52",
        "lat": 10.26104,
        "lng": 123.70108,
        "radius": 500
      },
      {
        "name": "Point 53",
        "lat": 10.26226,
        "lng": 123.69185,
        "radius": 500
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-18",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "マンダウエ市 (カバンカラン / カンドゥマン / カスンティンガン...)",
    "affectedJa": "マンダウエ市の一部: カバンカラン、カンドゥマン、カスンティンガン、マグイカイ、パグサブンガン、ティンガブ",
    "affectedEn": "Portion of Mandaue City: Cabancalan, Canduman, Casuntingan, Maguikay, Pagsabungan, & Tingub",
    "mapUrl": "https://lh3.googleusercontent.com/d/1BEOzsuueTARjnxvVJYgHCv6sju17WaAm",
    "pins": [
      {
        "name": "Cabancalan",
        "lat": 10.33898,
        "lng": 123.93681
      },
      {
        "name": "Canduman",
        "lat": 10.36263,
        "lng": 123.93711
      },
      {
        "name": "Casuntingan",
        "lat": 10.33852,
        "lng": 123.94012,
        "radius": 300
      },
      {
        "name": "Maguikay",
        "lat": 10.33607,
        "lng": 123.93703
      },
      {
        "name": "Pagsabungan",
        "lat": 10.3595,
        "lng": 123.93514
      },
      {
        "name": "Tingub",
        "lat": 10.35713,
        "lng": 123.93101
      },
      {
        "name": "Point 7",
        "lat": 10.34329,
        "lng": 123.93441,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.34549,
        "lng": 123.93205,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.34659,
        "lng": 123.93389,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.3482,
        "lng": 123.93579,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.34544,
        "lng": 123.93694,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.34785,
        "lng": 123.92926,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.34933,
        "lng": 123.93252,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.35141,
        "lng": 123.93008,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.3541,
        "lng": 123.92728,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.35427,
        "lng": 123.9302,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.35272,
        "lng": 123.93334,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.35619,
        "lng": 123.93399,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.36043,
        "lng": 123.93196,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.36354,
        "lng": 123.93364,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.36351,
        "lng": 123.93977,
        "radius": 100
      },
      {
        "name": "Point 22",
        "lat": 10.36204,
        "lng": 123.93964,
        "radius": 100
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-19",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "セブ市 (アパス / カサンバガン / ラフグ...)",
    "affectedJa": "セブ市の一部: アパス、カサンバガン、ラフグ、サンアントニオ、マンダウエ市の一部: バニラッド",
    "affectedEn": "Portion of Cebu City: Apas, Kasambagan, Lahug, & San Antonio, Portion of Mandaue City: Banilad",
    "mapUrl": "https://lh3.googleusercontent.com/d/1aWJPXcMJVKuBQP-BtPrhiYw4zkUD7X79",
    "pins": [
      {
        "name": "Apas",
        "lat": 10.34357,
        "lng": 123.91387,
        "radius": 150
      },
      {
        "name": "Kasambagan",
        "lat": 10.34207,
        "lng": 123.91462,
        "radius": 200
      },
      {
        "name": "Lahug",
        "lat": 10.33673,
        "lng": 123.90229
      },
      {
        "name": "San Antonio",
        "lat": 10.308,
        "lng": 123.896
      },
      {
        "name": "Point 5",
        "lat": 10.34228,
        "lng": 123.91304,
        "radius": 100
      },
      {
        "name": "Point 6",
        "lat": 10.33962,
        "lng": 123.91237,
        "radius": 100
      },
      {
        "name": "Point 7",
        "lat": 10.33953,
        "lng": 123.91379,
        "radius": 100
      },
      {
        "name": "Point 8",
        "lat": 10.33972,
        "lng": 123.91007,
        "radius": 150
      },
      {
        "name": "Point 9",
        "lat": 10.34124,
        "lng": 123.90804,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.34321,
        "lng": 123.90559,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.33979,
        "lng": 123.90469,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.34205,
        "lng": 123.90235,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.33675,
        "lng": 123.90587,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.33381,
        "lng": 123.90706,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.33713,
        "lng": 123.90851,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.33899,
        "lng": 123.90706,
        "radius": 150
      },
      {
        "name": "Point 18",
        "lat": 10.33373,
        "lng": 123.90381,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.34103,
        "lng": 123.90023,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.34299,
        "lng": 123.89834,
        "radius": 150
      },
      {
        "name": "Point 20",
        "lat": 10.34895,
        "lng": 123.90205,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.34525,
        "lng": 123.9043,
        "radius": 100
      },
      {
        "name": "Point 22",
        "lat": 10.34639,
        "lng": 123.90312,
        "radius": 100
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-20",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "セブ市 (バサク / バサク パルド / バサク サン ニコラス...)",
    "affectedJa": "セブ市の一部: バサク、バサク パルド、バサク サン ニコラス、ブヒサン、ブラカオ、キナサンアン パルド、パルド、ポブラシオン パルド、プンタ プリンセサ、キオット、サン ロケ",
    "affectedEn": "Portion of Cebu City: Basak, Basak Pardo, Basak San Nicolas, Buhisan, Bulacao, Kinasang-an Pardo, Pardo, Poblacion Pardo, Punta Princesa, Quiot, & San Roque",
    "mapUrl": "https://lh3.googleusercontent.com/d/1H-sYmRu2bt0LImhX7DsIT4qiFQ4TesmP",
    "pins": [
      {
        "name": "Basak",
        "lat": 10.29077,
        "lng": 123.86364,
        "radius": 300
      },
      {
        "name": "Basak San Nicolas",
        "lat": 10.29431,
        "lng": 123.86561
      },
      {
        "name": "Bulacao",
        "lat": 10.27548,
        "lng": 123.84883
      },
      {
        "name": "Kinasang-An Pardo",
        "lat": 10.28038,
        "lng": 123.85368
      },
      {
        "name": "Pardo",
        "lat": 10.28321,
        "lng": 123.85175
      },
      {
        "name": "Punta Princesa",
        "lat": 10.29465,
        "lng": 123.86089,
        "radius": 300
      },
      {
        "name": "Quiot",
        "lat": 10.298,
        "lng": 123.86
      },
      {
        "name": "San Roque",
        "lat": 10.283,
        "lng": 123.856
      },
      {
        "name": "Point 10",
        "lat": 10.27828,
        "lng": 123.84682,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.27777,
        "lng": 123.85133,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.28034,
        "lng": 123.84948,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.28549,
        "lng": 123.84905,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.28815,
        "lng": 123.84677,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.28947,
        "lng": 123.84434,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.2887,
        "lng": 123.83935,
        "radius": 350
      },
      {
        "name": "Point 17",
        "lat": 10.29385,
        "lng": 123.83613,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.29233,
        "lng": 123.84253,
        "radius": 300
      },
      {
        "name": "Point 19",
        "lat": 10.28857,
        "lng": 123.85755,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.29562,
        "lng": 123.85467,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.29389,
        "lng": 123.86832,
        "radius": 100
      }
    ],
    "pinCount": 7
  },
  {
    "groupId": "grp-21",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "セブ市 (カンピュトー / 国会議事堂跡 / グアダルーペ...)",
    "affectedJa": "セブ市の一部: カンピュトー、国会議事堂跡、グアダルーペ、カルナサン、サパンダク",
    "affectedEn": "Portion of Cebu City: Camputhaw, Capitol Site, Guadalupe, Kalunasan, & Sapangdaku",
    "mapUrl": "https://lh3.googleusercontent.com/d/1r99ihqUwHMAoBJagvLqMwrQRA6ic3h9p",
    "pins": [
      {
        "name": "Camputhaw",
        "lat": 10.31825,
        "lng": 123.89844,
        "radius": 150
      },
      {
        "name": "Capitol Site",
        "lat": 10.31716,
        "lng": 123.89347,
        "radius": 150
      },
      {
        "name": "Guadalupe",
        "lat": 10.32311,
        "lng": 123.87574,
        "radius": 500
      },
      {
        "name": "Kalunasan",
        "lat": 10.33046,
        "lng": 123.88008,
        "radius": 500
      },
      {
        "name": "Sapangdaku",
        "lat": 10.3359,
        "lng": 123.86725,
        "radius": 500
      },
      {
        "name": "Point 6",
        "lat": 10.31781,
        "lng": 123.89593,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.3172,
        "lng": 123.89158,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.31988,
        "lng": 123.89145,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.31853,
        "lng": 123.88786,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.31467,
        "lng": 123.88722,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.31239,
        "lng": 123.88662,
        "radius": 100
      },
      {
        "name": "Point 12",
        "lat": 10.31076,
        "lng": 123.88677,
        "radius": 100
      },
      {
        "name": "Point 13",
        "lat": 10.30943,
        "lng": 123.88711,
        "radius": 100
      },
      {
        "name": "Point 14",
        "lat": 10.31747,
        "lng": 123.88484,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.31792,
        "lng": 123.88119,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.32349,
        "lng": 123.88347,
        "radius": 500
      },
      {
        "name": "Point 17",
        "lat": 10.32818,
        "lng": 123.87089,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.33625,
        "lng": 123.87511,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.33687,
        "lng": 123.88059,
        "radius": 300
      },
      {
        "name": "Point 20",
        "lat": 10.34249,
        "lng": 123.87566,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.34453,
        "lng": 123.87279,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.3481,
        "lng": 123.87338,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.34169,
        "lng": 123.8648,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.34555,
        "lng": 123.86455,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.34766,
        "lng": 123.86713,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.34981,
        "lng": 123.87,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.32945,
        "lng": 123.85854,
        "radius": 200
      },
      {
        "name": "Point 28",
        "lat": 10.33355,
        "lng": 123.85764,
        "radius": 200
      },
      {
        "name": "Point 29",
        "lat": 10.33629,
        "lng": 123.85348,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-22",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "セブ市 (エルミタ / ロレガ / サンロケ...)",
    "affectedJa": "セブ市の一部: エルミタ、ロレガ、サンロケ、T. パディラ、テヘロ、ティナゴ",
    "affectedEn": "Portion of Cebu City: Ermita, Lorega, San Roque, T. Padilla, Tejero, & Tinago",
    "mapUrl": "https://lh3.googleusercontent.com/d/1jS6bbQ-gS_jWO6AN_c3E-CgiK5oI1D0F",
    "pins": [
      {
        "name": "Ermita",
        "lat": 10.29212,
        "lng": 123.89887
      },
      {
        "name": "Lorega",
        "lat": 10.30597,
        "lng": 123.9075
      },
      {
        "name": "San Roque",
        "lat": 10.29317,
        "lng": 123.90243
      },
      {
        "name": "Tejero",
        "lat": 10.29925,
        "lng": 123.90613
      },
      {
        "name": "Tinago",
        "lat": 10.29567,
        "lng": 123.9051
      },
      {
        "name": "Point 6",
        "lat": 10.29533,
        "lng": 123.90016,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.30305,
        "lng": 123.90583,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.302,
        "lng": 123.9084,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.29575,
        "lng": 123.90274,
        "radius": 200
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-23",
    "timeSlot": "17:00 - 19:00",
    "areaJa": "セブ市 (アパス / ラフグ / ルズ)",
    "affectedJa": "セブ市の一部: アパス、ラフグ、ルズ",
    "affectedEn": "Portion of Cebu City: Apas, Lahug, & Luz",
    "mapUrl": "https://lh3.googleusercontent.com/d/1mn2dsVk8GZayCda96j0JSMHE30bHIGYc",
    "pins": [
      {
        "name": "Apas",
        "lat": 10.32453,
        "lng": 123.90651
      },
      {
        "name": "Lahug",
        "lat": 10.32906,
        "lng": 123.90372,
        "radius": 350
      },
      {
        "name": "Point 3",
        "lat": 10.32163,
        "lng": 123.90531,
        "radius": 200
      },
      {
        "name": "Point 4",
        "lat": 10.32071,
        "lng": 123.90794,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.31961,
        "lng": 123.90394,
        "radius": 100
      },
      {
        "name": "Point 6",
        "lat": 10.31821,
        "lng": 123.90312,
        "radius": 100
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-24",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (バサック サン ニコラス / カサンバガン / マボロ...)",
    "affectedJa": "セブ市の一部: バサック サン ニコラス、カサンバガン、マボロ、サンノゼ、マンダウエ市の一部: スバンダク",
    "affectedEn": "Portion of Cebu City: Basak San Nicolas, Kasambagan, Mabolo, & San Jose, Portion of Mandaue City: Subangdaku",
    "mapUrl": "https://lh3.googleusercontent.com/d/1Ny_gZWEYzYnmDPNZtq-YHUpwR3DrDVFr",
    "pins": [
      {
        "name": "Point 1",
        "lat": 10.31454,
        "lng": 123.91716,
        "radius": 200
      },
      {
        "name": "Point 2",
        "lat": 10.31636,
        "lng": 123.91986,
        "radius": 200
      },
      {
        "name": "Point 3",
        "lat": 10.31712,
        "lng": 123.91545,
        "radius": 200
      },
      {
        "name": "Point 4",
        "lat": 10.31918,
        "lng": 123.91711,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.32307,
        "lng": 123.91625,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.32015,
        "lng": 123.91372,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.32371,
        "lng": 123.91184,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.32611,
        "lng": 123.91149,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.32585,
        "lng": 123.91492,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.32822,
        "lng": 123.91711,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-25",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (マボロ...)",
    "affectedJa": "セブ市の一部: マボロ、マンダウエ市の一部: ギソ、スバンダク、ティポロ",
    "affectedEn": "Portion of Cebu City: Mabolo, Portion of Mandaue City: Guizo, Subangdaku, & Tipolo",
    "mapUrl": "https://lh3.googleusercontent.com/d/1ML2DSxx822TtKYMpQSNZMw3tQ6XMwPR7",
    "pins": [
      {
        "name": "Mabolo",
        "lat": 10.31855,
        "lng": 123.91866
      },
      {
        "name": "Guizo",
        "lat": 10.32438,
        "lng": 123.92595
      },
      {
        "name": "Subangdaku",
        "lat": 10.31813,
        "lng": 123.92243,
        "radius": 300
      },
      {
        "name": "Tipolo",
        "lat": 10.32691,
        "lng": 123.92861
      },
      {
        "name": "Point 5",
        "lat": 10.32195,
        "lng": 123.92315,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.32887,
        "lng": 123.93122,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.33124,
        "lng": 123.93371,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.33259,
        "lng": 123.93577,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.33158,
        "lng": 123.92967,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.3297,
        "lng": 123.92724,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.32775,
        "lng": 123.9257,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-26",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (バサク サン ニコラス / カランバ / エルミタ...)",
    "affectedJa": "セブ市の一部: バサク サン ニコラス、カランバ、エルミタ、カルビハン、カマガヤン、ラバンゴン、マンバリン、パヒナ セントラル、パヒナ サン ニコラス、プンタ プリンセサ、サンバッグ 1、サン ニコラス プロパー、サワン カレロ",
    "affectedEn": "Portion of Cebu City: Basak San Nicolas, Calamba, Ermita, Kalubihan, Kamagayan, Labangon, Mambaling, Pahina Central, Pahina San Nicolas, Punta Princesa, Sambag 1, San Nicolas Proper, & Sawang Calero",
    "mapUrl": "https://lh3.googleusercontent.com/d/13RwSuG5Oubha6MK3Ix7__8xvCUwO_r3S",
    "pins": [
      {
        "name": "Basak San Nicolas",
        "lat": 10.29182,
        "lng": 123.87252
      },
      {
        "name": "Calamba",
        "lat": 10.29511,
        "lng": 123.87973
      },
      {
        "name": "Ermita",
        "lat": 10.29412,
        "lng": 123.89692
      },
      {
        "name": "Kalubihan",
        "lat": 10.29803,
        "lng": 123.89778
      },
      {
        "name": "Kamagayan",
        "lat": 10.29712,
        "lng": 123.89454
      },
      {
        "name": "Labangon",
        "lat": 10.29363,
        "lng": 123.88875
      },
      {
        "name": "Mambaling",
        "lat": 10.29204,
        "lng": 123.87488
      },
      {
        "name": "Pahina Central",
        "lat": 10.29742,
        "lng": 123.88844,
        "radius": 150
      },
      {
        "name": "Pahina San Nicolas",
        "lat": 10.2979,
        "lng": 123.89158
      },
      {
        "name": "Punta Princesa",
        "lat": 10.29321,
        "lng": 123.87707
      },
      {
        "name": "Sambag 1",
        "lat": 10.29608,
        "lng": 123.88235,
        "radius": 150
      },
      {
        "name": "San Nicolas Proper",
        "lat": 10.2963,
        "lng": 123.88557
      },
      {
        "name": "Sawang Calero",
        "lat": 10.29402,
        "lng": 123.8924
      },
      {
        "name": "Point 14",
        "lat": 10.29493,
        "lng": 123.89987,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.296,
        "lng": 123.89085,
        "radius": 200
      }
    ],
    "pinCount": 10
  },
  {
    "groupId": "grp-27",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "マンダウエ市 (バサック / セントロ / ジャゴビアオ...)",
    "affectedJa": "マンダウエ市の部分: バサック、セントロ、ジャゴビアオ、ラボゴン、パクナン、タボク、コンソラシオンの部分: ポブラシオン オリエンタル",
    "affectedEn": "Portion of Mandaue City: Basak, Centro, Jagobiao, Labogon, Paknaan, & Tabok, Portion of Consolacion: Poblacion Oriental",
    "mapUrl": "https://lh3.googleusercontent.com/d/1ufxNM7x8U7Ti6K7Fhsw6-ilsfPGihttl",
    "pins": [
      {
        "name": "Basak",
        "lat": 10.35098,
        "lng": 123.95209,
        "radius": 300
      },
      {
        "name": "Centro",
        "lat": 10.34736,
        "lng": 123.9505
      },
      {
        "name": "Jagobiao",
        "lat": 10.36351,
        "lng": 123.95312,
        "radius": 300
      },
      {
        "name": "Labogon",
        "lat": 10.35178,
        "lng": 123.95938,
        "radius": 500
      },
      {
        "name": "Paknaan",
        "lat": 10.3595,
        "lng": 123.95337,
        "radius": 350
      },
      {
        "name": "Tabok",
        "lat": 10.35537,
        "lng": 123.95295,
        "radius": 300
      },
      {
        "name": "Point 8",
        "lat": 10.34764,
        "lng": 123.95446,
        "radius": 300
      },
      {
        "name": "Point 9",
        "lat": 10.36731,
        "lng": 123.95514,
        "radius": 300
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-28",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (アパス / カサンバガン / ラハグ...)",
    "affectedJa": "セブ市の一部: アパス、カサンバガン、ラハグ、マンダウエ市の一部: バニラッド",
    "affectedEn": "Portion of Cebu City: Apas, Kasambagan, & Lahug, Portion of Mandaue City: Banilad",
    "mapUrl": "https://lh3.googleusercontent.com/d/1Qu-n8NG3AU81vi83jAVGAFwcPY96xNhb",
    "pins": [
      {
        "name": "Apas",
        "lat": 10.33713,
        "lng": 123.91529
      },
      {
        "name": "Kasambagan",
        "lat": 10.3352,
        "lng": 123.9175
      },
      {
        "name": "Point 4",
        "lat": 10.33447,
        "lng": 123.91392,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.3385,
        "lng": 123.91301,
        "radius": 150
      },
      {
        "name": "Point 6",
        "lat": 10.33609,
        "lng": 123.91258,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.33755,
        "lng": 123.91113,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.33453,
        "lng": 123.91055,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.32877,
        "lng": 123.90724,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.32851,
        "lng": 123.91117,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.33111,
        "lng": 123.90984,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-29",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "コンソラシオン (カンサガ / ジュガン / ラマック...)",
    "affectedJa": "コンソラシオンの部分: カンサガ、ジュガン、ラマック、ピトゴ、ポブラシオン オリエンタル、リロアンの部分: ヤティ",
    "affectedEn": "Portion of Consolacion: Cansaga, Jugan, Lamac, Pitogo, & Poblacion Oriental, Portion of Liloan: Yati",
    "mapUrl": "https://lh3.googleusercontent.com/d/1mI1hWBqTUmvOPt-BlXnB7D-GNb9lOT5g",
    "pins": [
      {
        "name": "Cansaga",
        "lat": 10.37377,
        "lng": 123.95501,
        "radius": 150
      },
      {
        "name": "Jugan",
        "lat": 10.37749,
        "lng": 123.962,
        "radius": 150
      },
      {
        "name": "Lamac",
        "lat": 10.37179,
        "lng": 123.95329,
        "radius": 150
      },
      {
        "name": "Pitogo",
        "lat": 10.37585,
        "lng": 123.95664,
        "radius": 150
      },
      {
        "name": "Poblacion Oriental",
        "lat": 10.37672,
        "lng": 123.95921,
        "radius": 150
      },
      {
        "name": "Yati",
        "lat": 10.38576,
        "lng": 123.9766,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.37792,
        "lng": 123.9642,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.37607,
        "lng": 123.96579,
        "radius": 150
      },
      {
        "name": "Point 9",
        "lat": 10.37404,
        "lng": 123.96721,
        "radius": 150
      },
      {
        "name": "Point 10",
        "lat": 10.37166,
        "lng": 123.96887,
        "radius": 150
      },
      {
        "name": "Point 11",
        "lat": 10.36993,
        "lng": 123.97223,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.3782,
        "lng": 123.96737,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.37564,
        "lng": 123.96996,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.37284,
        "lng": 123.9744,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.37576,
        "lng": 123.97661,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.37766,
        "lng": 123.97403,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.37889,
        "lng": 123.9709,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.3812,
        "lng": 123.97316,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.38383,
        "lng": 123.97408,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.38746,
        "lng": 123.97877,
        "radius": 150
      },
      {
        "name": "Point 21",
        "lat": 10.39146,
        "lng": 123.97054,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.39361,
        "lng": 123.97166,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.39154,
        "lng": 123.97325,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.39142,
        "lng": 123.97678,
        "radius": 150
      },
      {
        "name": "Point 25",
        "lat": 10.39058,
        "lng": 123.97918,
        "radius": 150
      },
      {
        "name": "Point 26",
        "lat": 10.38935,
        "lng": 123.98086,
        "radius": 150
      },
      {
        "name": "Point 27",
        "lat": 10.39096,
        "lng": 123.98201,
        "radius": 150
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-30",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (カンピュソー / 国会議事堂跡 / グアダルーペ...)",
    "affectedJa": "セブ市の一部: カンピュソー、国会議事堂跡、グアダルーペ、カルビハン、カルナサン、ラハグ",
    "affectedEn": "Portion of Cebu City: Camputhaw, Capitol Site, Guadalupe, Kalubihan, Kalunasan, & Lahug",
    "mapUrl": "https://lh3.googleusercontent.com/d/10C5JnwgING8bf2XE_1TSjYqZPKGxkZWQ",
    "pins": [
      {
        "name": "Camputhaw",
        "lat": 10.32531,
        "lng": 123.896
      },
      {
        "name": "Capitol Site",
        "lat": 10.33012,
        "lng": 123.89222,
        "radius": 300
      },
      {
        "name": "Guadalupe",
        "lat": 10.32378,
        "lng": 123.88548
      },
      {
        "name": "Kalunasan",
        "lat": 10.33599,
        "lng": 123.88407
      },
      {
        "name": "Lahug",
        "lat": 10.32784,
        "lng": 123.89591
      },
      {
        "name": "Point 7",
        "lat": 10.32581,
        "lng": 123.89904,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.32493,
        "lng": 123.90231,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.32299,
        "lng": 123.90017,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.32015,
        "lng": 123.90132,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.318,
        "lng": 123.89827,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.33341,
        "lng": 123.89025,
        "radius": 300
      },
      {
        "name": "Point 13",
        "lat": 10.32974,
        "lng": 123.88827,
        "radius": 300
      },
      {
        "name": "Point 14",
        "lat": 10.32505,
        "lng": 123.88887,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.32547,
        "lng": 123.89248,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.33376,
        "lng": 123.8864,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.33616,
        "lng": 123.88754,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.33856,
        "lng": 123.88664,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.34039,
        "lng": 123.88408,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.34331,
        "lng": 123.88447,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.34559,
        "lng": 123.88253,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.34702,
        "lng": 123.88468,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.34865,
        "lng": 123.88188,
        "radius": 200
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-31",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "コンソラシオン (カバンガハン / キューバク / カンサガ...)",
    "affectedJa": "慰めの一部: カバンガハン、キューバク、カンサガ、カシリ、ダンラグ、ガリング、パノイポイ、ポブラシオン オクシデンタル、ポブラシオン オリエンタル、ポログ、プルポガン、サクサク、ティルハオン、トロトロ",
    "affectedEn": "Portion of Consolacion: Cabangahan, Cubacub, Cansaga, Casili, Danglag, Garing, Panoypoy, Poblacion Occidental, Poblacion Oriental, Polog, Pulpogan, Sacsac, Tilhaong, & Tolo-tolo",
    "mapUrl": "https://lh3.googleusercontent.com/d/1QrWIN-BU9_TlRfNHTtwCV3Ekkox757UG",
    "pins": [
      {
        "name": "Cubacub",
        "lat": 10.36993,
        "lng": 123.94188
      },
      {
        "name": "Cansaga",
        "lat": 10.37998,
        "lng": 123.95312
      },
      {
        "name": "Casili",
        "lat": 10.38373,
        "lng": 123.9414,
        "radius": 350
      },
      {
        "name": "Danglag",
        "lat": 10.39716,
        "lng": 123.9463
      },
      {
        "name": "Garing",
        "lat": 10.395,
        "lng": 123.955
      },
      {
        "name": "Panoypoy",
        "lat": 10.40559,
        "lng": 123.94329
      },
      {
        "name": "Poblacion Occidental",
        "lat": 10.37563,
        "lng": 123.95428
      },
      {
        "name": "Poblacion Oriental",
        "lat": 10.37736,
        "lng": 123.95646
      },
      {
        "name": "Polog",
        "lat": 10.418,
        "lng": 123.925
      },
      {
        "name": "Pulpogan",
        "lat": 10.38137,
        "lng": 123.94973
      },
      {
        "name": "Sacsac",
        "lat": 10.4034,
        "lng": 123.95308
      },
      {
        "name": "Tilhaong",
        "lat": 10.3888,
        "lng": 123.94698
      },
      {
        "name": "Tolo-Tolo",
        "lat": 10.39141,
        "lng": 123.9408
      },
      {
        "name": "Point 14",
        "lat": 10.38058,
        "lng": 123.95678,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.38352,
        "lng": 123.95857,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.38481,
        "lng": 123.95571,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.38848,
        "lng": 123.95592,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.39192,
        "lng": 123.95625,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.37276,
        "lng": 123.94501,
        "radius": 350
      },
      {
        "name": "Point 20",
        "lat": 10.37343,
        "lng": 123.93999,
        "radius": 300
      },
      {
        "name": "Point 21",
        "lat": 10.37301,
        "lng": 123.94977,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.37272,
        "lng": 123.95252,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.37673,
        "lng": 123.93703,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.37716,
        "lng": 123.94967,
        "radius": 350
      },
      {
        "name": "Point 25",
        "lat": 10.37875,
        "lng": 123.94398,
        "radius": 350
      },
      {
        "name": "Point 26",
        "lat": 10.37911,
        "lng": 123.93911,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.39074,
        "lng": 123.94389,
        "radius": 200
      },
      {
        "name": "Point 28",
        "lat": 10.38815,
        "lng": 123.94177,
        "radius": 200
      },
      {
        "name": "Point 29",
        "lat": 10.39108,
        "lng": 123.95162,
        "radius": 350
      },
      {
        "name": "Point 30",
        "lat": 10.39505,
        "lng": 123.94896,
        "radius": 200
      },
      {
        "name": "Point 31",
        "lat": 10.40129,
        "lng": 123.94552,
        "radius": 300
      },
      {
        "name": "Point 32",
        "lat": 10.39794,
        "lng": 123.95293,
        "radius": 200
      },
      {
        "name": "Point 33",
        "lat": 10.40062,
        "lng": 123.95093,
        "radius": 200
      },
      {
        "name": "Point 34",
        "lat": 10.40267,
        "lng": 123.94873,
        "radius": 200
      },
      {
        "name": "Point 35",
        "lat": 10.40703,
        "lng": 123.9523,
        "radius": 200
      },
      {
        "name": "Point 36",
        "lat": 10.40965,
        "lng": 123.95016,
        "radius": 200
      },
      {
        "name": "Point 37",
        "lat": 10.41255,
        "lng": 123.94787,
        "radius": 200
      },
      {
        "name": "Point 38",
        "lat": 10.41564,
        "lng": 123.94629,
        "radius": 200
      },
      {
        "name": "Point 39",
        "lat": 10.41922,
        "lng": 123.94624,
        "radius": 200
      },
      {
        "name": "Point 40",
        "lat": 10.43139,
        "lng": 123.93267,
        "radius": 200
      },
      {
        "name": "Point 41",
        "lat": 10.43054,
        "lng": 123.93576,
        "radius": 200
      },
      {
        "name": "Point 42",
        "lat": 10.42869,
        "lng": 123.93885,
        "radius": 200
      },
      {
        "name": "Point 43",
        "lat": 10.4262,
        "lng": 123.94166,
        "radius": 200
      },
      {
        "name": "Point 44",
        "lat": 10.42252,
        "lng": 123.94177,
        "radius": 200
      },
      {
        "name": "Point 45",
        "lat": 10.41894,
        "lng": 123.94037,
        "radius": 200
      },
      {
        "name": "Point 46",
        "lat": 10.41644,
        "lng": 123.93825,
        "radius": 200
      },
      {
        "name": "Point 47",
        "lat": 10.42007,
        "lng": 123.93508,
        "radius": 200
      },
      {
        "name": "Point 48",
        "lat": 10.42024,
        "lng": 123.94375,
        "radius": 200
      },
      {
        "name": "Point 49",
        "lat": 10.40858,
        "lng": 123.94057,
        "radius": 200
      },
      {
        "name": "Point 50",
        "lat": 10.41044,
        "lng": 123.93842,
        "radius": 200
      },
      {
        "name": "Point 51",
        "lat": 10.41365,
        "lng": 123.9386,
        "radius": 200
      },
      {
        "name": "Point 52",
        "lat": 10.41171,
        "lng": 123.9349,
        "radius": 200
      },
      {
        "name": "Point 53",
        "lat": 10.41931,
        "lng": 123.92846,
        "radius": 200
      },
      {
        "name": "Point 54",
        "lat": 10.41534,
        "lng": 123.92907,
        "radius": 200
      },
      {
        "name": "Point 55",
        "lat": 10.42243,
        "lng": 123.92683,
        "radius": 200
      },
      {
        "name": "Point 56",
        "lat": 10.42607,
        "lng": 123.92683,
        "radius": 200
      },
      {
        "name": "Point 57",
        "lat": 10.41306,
        "lng": 123.93216,
        "radius": 200
      },
      {
        "name": "Point 58",
        "lat": 10.40132,
        "lng": 123.924,
        "radius": 200
      },
      {
        "name": "Point 59",
        "lat": 10.40478,
        "lng": 123.92451,
        "radius": 200
      },
      {
        "name": "Point 60",
        "lat": 10.40807,
        "lng": 123.92658,
        "radius": 200
      },
      {
        "name": "Point 61",
        "lat": 10.40875,
        "lng": 123.92949,
        "radius": 200
      },
      {
        "name": "Point 62",
        "lat": 10.41044,
        "lng": 123.93233,
        "radius": 200
      },
      {
        "name": "Point 63",
        "lat": 10.39961,
        "lng": 123.92698,
        "radius": 200
      },
      {
        "name": "Point 64",
        "lat": 10.39743,
        "lng": 123.92967,
        "radius": 200
      },
      {
        "name": "Point 65",
        "lat": 10.39413,
        "lng": 123.93044,
        "radius": 200
      },
      {
        "name": "Point 66",
        "lat": 10.39075,
        "lng": 123.92975,
        "radius": 200
      },
      {
        "name": "Point 67",
        "lat": 10.39075,
        "lng": 123.92641,
        "radius": 200
      },
      {
        "name": "Point 68",
        "lat": 10.38771,
        "lng": 123.92744,
        "radius": 200
      },
      {
        "name": "Point 69",
        "lat": 10.38517,
        "lng": 123.93076,
        "radius": 350
      },
      {
        "name": "Point 70",
        "lat": 10.38095,
        "lng": 123.93491,
        "radius": 300
      },
      {
        "name": "Point 71",
        "lat": 10.39572,
        "lng": 123.93891,
        "radius": 500
      },
      {
        "name": "Point 72",
        "lat": 10.40267,
        "lng": 123.93302,
        "radius": 500
      },
      {
        "name": "Point 73",
        "lat": 10.40537,
        "lng": 123.93903,
        "radius": 300
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-32",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "マンダウエ市 (ギゾ / スバンダク / ティポロ)",
    "affectedJa": "マンダウエ市の一部: ギゾ、スバンダク、ティポロ",
    "affectedEn": "Portion of Mandaue City: Guizo, Subangdaku, & Tipolo",
    "mapUrl": "https://lh3.googleusercontent.com/d/1Ev6rEckCVOmPmyxYOkhAGcl-DSI1nB4W",
    "pins": [
      {
        "name": "Guizo",
        "lat": 10.32598,
        "lng": 123.93617
      },
      {
        "name": "Subangdaku",
        "lat": 10.31982,
        "lng": 123.9281
      },
      {
        "name": "Tipolo",
        "lat": 10.32818,
        "lng": 123.93325
      },
      {
        "name": "Point 4",
        "lat": 10.32367,
        "lng": 123.9364,
        "radius": 200
      },
      {
        "name": "Point 5",
        "lat": 10.32146,
        "lng": 123.93299,
        "radius": 300
      },
      {
        "name": "Point 6",
        "lat": 10.32278,
        "lng": 123.92936,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.32493,
        "lng": 123.93891,
        "radius": 100
      },
      {
        "name": "Point 8",
        "lat": 10.32455,
        "lng": 123.94011,
        "radius": 100
      },
      {
        "name": "Point 9",
        "lat": 10.32499,
        "lng": 123.93345,
        "radius": 200
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-33",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (マボロ / 北部埋立地...)",
    "affectedJa": "セブ市の一部: マボロおよび北部埋立地、マンダウエ市の一部: アランアラン、カンバロ、セントロ、ギゾ、ロオク、オパオ、スバンダク、ティポロ、ウマパッド",
    "affectedEn": "Portion of Cebu City: Mabolo & North Reclamation Area, Portion of Mandaue City: Alang-Alang, Cambaro, Centro, Guizo, Looc, Opao, Subangdaku, Tipolo, & Umapad",
    "mapUrl": "https://lh3.googleusercontent.com/d/18oXsQltuPb47WnfNyx7yS6UuAR_t4cJE",
    "pins": [
      {
        "name": "Mabolo",
        "lat": 10.32573,
        "lng": 123.95772
      },
      {
        "name": "Cambaro",
        "lat": 10.32155,
        "lng": 123.94329
      },
      {
        "name": "Centro",
        "lat": 10.32568,
        "lng": 123.93938
      },
      {
        "name": "Guizo",
        "lat": 10.31931,
        "lng": 123.93599
      },
      {
        "name": "Looc",
        "lat": 10.32455,
        "lng": 123.94805
      },
      {
        "name": "Opao",
        "lat": 10.3232,
        "lng": 123.95157
      },
      {
        "name": "Subangdaku",
        "lat": 10.3308,
        "lng": 123.94793
      },
      {
        "name": "Tipolo",
        "lat": 10.33092,
        "lng": 123.95256
      },
      {
        "name": "Umapad",
        "lat": 10.32864,
        "lng": 123.95544
      },
      {
        "name": "Point 10",
        "lat": 10.32168,
        "lng": 123.93837,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.32433,
        "lng": 123.94205,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.32439,
        "lng": 123.94506,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.3216,
        "lng": 123.94893,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.32737,
        "lng": 123.93642,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.3275,
        "lng": 123.94617,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.33359,
        "lng": 123.94674,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.33532,
        "lng": 123.93953,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.33274,
        "lng": 123.95017,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.33224,
        "lng": 123.95506,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.33389,
        "lng": 123.95803,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.33008,
        "lng": 123.95841,
        "radius": 200
      }
    ],
    "pinCount": 8
  },
  {
    "groupId": "grp-34",
    "timeSlot": "18:00 - 20:00",
    "areaJa": "セブ市 (カサンバガンとマボロ / マンダウエ市の一部: バニラッド...)",
    "affectedJa": "セブ市の一部: カサンバガンとマボロ、マンダウエ市の一部: バニラッド、スバンダク、ティポロ",
    "affectedEn": "Portion of Cebu City: Kasambagan & Mabolo, Portion of Mandaue City: Banilad, Subangdaku, & Tipolo",
    "mapUrl": "https://lh3.googleusercontent.com/d/1lmjhEM2Ns7E08GGoToYPHd6Rr7GlLnus",
    "pins": [
      {
        "name": "Kasambagan",
        "lat": 10.32615,
        "lng": 123.91673
      },
      {
        "name": "Mabolo",
        "lat": 10.32582,
        "lng": 123.91982
      },
      {
        "name": "Subangdaku",
        "lat": 10.31416,
        "lng": 123.92248
      },
      {
        "name": "Tipolo",
        "lat": 10.32323,
        "lng": 123.92436
      },
      {
        "name": "Point 5",
        "lat": 10.32007,
        "lng": 123.92574,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.32623,
        "lng": 123.92261,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.32898,
        "lng": 123.92119,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.32958,
        "lng": 123.91884,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.32937,
        "lng": 123.92416,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.33195,
        "lng": 123.92172,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.33478,
        "lng": 123.92395,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.33322,
        "lng": 123.92687,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.33561,
        "lng": 123.92921,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.3374,
        "lng": 123.9264,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.33789,
        "lng": 123.92308,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.33898,
        "lng": 123.92037,
        "radius": 200
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-35",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "セブ市 (カンピュソー / 国会議事堂跡 / ロレガ)",
    "affectedJa": "セブ市の一部: カンピュソー、国会議事堂跡、ロレガ",
    "affectedEn": "Portion of Cebu City: Camputhaw, Capitol Site, & Lorega",
    "mapUrl": "https://lh3.googleusercontent.com/d/1iE-JE13mMidRxdyhQK-_riZ940YjnWFP",
    "pins": [
      {
        "name": "Camputhaw",
        "lat": 10.31597,
        "lng": 123.89716
      },
      {
        "name": "Capitol Site",
        "lat": 10.31513,
        "lng": 123.89368
      },
      {
        "name": "Lorega",
        "lat": 10.3099,
        "lng": 123.90531
      },
      {
        "name": "Point 4",
        "lat": 10.31244,
        "lng": 123.90339,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.31462,
        "lng": 123.90201,
        "radius": 150
      },
      {
        "name": "Point 6",
        "lat": 10.31302,
        "lng": 123.8999,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.31327,
        "lng": 123.89724,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.31222,
        "lng": 123.89475,
        "radius": 200
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-36",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "ナガ市 (コロン / イナヤガン / タンケ...)",
    "affectedJa": "ナガ市の一部: コロン、イナヤガン、タンケ、トゥヤン、ウリン、ミングラニラの一部: カラジョアン、リナオ、パキニ、トゥーレイ、トゥンハーン、トゥンキル、トゥンコップ、第 1 区、第 2 区、第 4 区",
    "affectedEn": "Portion of City of Naga: Colon, Inayagan, Tangke, Tuyan, & Uling, Portion of Minglanilla: Calajoan, Linao, Pakigne, Tulay, Tunghaan, Tungkil, Tungkop, Ward 1, Ward 2, & Ward 4",
    "mapUrl": "https://lh3.googleusercontent.com/d/1ha5ijTFVNcTEb4njJakwexPciXOVmKMq",
    "pins": [
      {
        "name": "Colon",
        "lat": 10.23065,
        "lng": 123.7718
      },
      {
        "name": "Inayagan",
        "lat": 10.23588,
        "lng": 123.78382,
        "radius": 500
      },
      {
        "name": "Tangke",
        "lat": 10.22625,
        "lng": 123.76477,
        "radius": 100
      },
      {
        "name": "Tuyan",
        "lat": 10.23318,
        "lng": 123.77678,
        "radius": 500
      },
      {
        "name": "Uling",
        "lat": 10.23891,
        "lng": 123.7909,
        "radius": 500
      },
      {
        "name": "Pakigne",
        "lat": 10.24845,
        "lng": 123.80523
      },
      {
        "name": "Tunghaan",
        "lat": 10.24031,
        "lng": 123.78558
      },
      {
        "name": "Tungkil",
        "lat": 10.24626,
        "lng": 123.80249
      },
      {
        "name": "Ward 1",
        "lat": 10.24301,
        "lng": 123.79425
      },
      {
        "name": "Ward 2",
        "lat": 10.24157,
        "lng": 123.79927,
        "radius": 500
      },
      {
        "name": "Point 12",
        "lat": 10.23748,
        "lng": 123.77979,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.23946,
        "lng": 123.80579,
        "radius": 300
      },
      {
        "name": "Point 14",
        "lat": 10.24327,
        "lng": 123.80499,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.24606,
        "lng": 123.80671,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.23537,
        "lng": 123.79834,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.23393,
        "lng": 123.78949,
        "radius": 200
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-37",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "セブ市 (バニラド / ブドラーン / ブサイ...)",
    "affectedJa": "セブ市の一部: バニラド、ブドラーン、ブサイ、タランバン、マンダウエ市の一部: バニラド",
    "affectedEn": "Portion of Cebu City: Banilad, Budlaan, Busay, & Talamban, Portion of Mandaue City: Banilad",
    "mapUrl": "https://lh3.googleusercontent.com/d/1MDiNs9ofoIr_e_2T9Yh4reABt9K9xrse",
    "pins": [
      {
        "name": "Banilad",
        "lat": 10.35284,
        "lng": 123.91428,
        "radius": 300
      },
      {
        "name": "Budlaan",
        "lat": 10.34817,
        "lng": 123.91695,
        "radius": 300
      },
      {
        "name": "Talamban",
        "lat": 10.35831,
        "lng": 123.91874
      },
      {
        "name": "Point 5",
        "lat": 10.36011,
        "lng": 123.91585,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.35867,
        "lng": 123.91302,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.3568,
        "lng": 123.91522,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.34861,
        "lng": 123.91291,
        "radius": 300
      },
      {
        "name": "Point 9",
        "lat": 10.34363,
        "lng": 123.91188,
        "radius": 300
      },
      {
        "name": "Point 10",
        "lat": 10.34693,
        "lng": 123.90838,
        "radius": 300
      },
      {
        "name": "Point 11",
        "lat": 10.35072,
        "lng": 123.90535,
        "radius": 300
      },
      {
        "name": "Point 12",
        "lat": 10.35173,
        "lng": 123.91016,
        "radius": 300
      },
      {
        "name": "Point 13",
        "lat": 10.35428,
        "lng": 123.90272,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.35739,
        "lng": 123.90012,
        "radius": 300
      },
      {
        "name": "Point 15",
        "lat": 10.3607,
        "lng": 123.90366,
        "radius": 300
      },
      {
        "name": "Point 16",
        "lat": 10.36398,
        "lng": 123.90029,
        "radius": 300
      },
      {
        "name": "Point 17",
        "lat": 10.36119,
        "lng": 123.8966,
        "radius": 300
      },
      {
        "name": "Point 18",
        "lat": 10.35697,
        "lng": 123.89505,
        "radius": 300
      },
      {
        "name": "Point 19",
        "lat": 10.36111,
        "lng": 123.91265,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.35884,
        "lng": 123.90949,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-38",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "セブ市 (ドゥルジョ ファティマ / エルミタ / マンバリン...)",
    "affectedJa": "セブ市の一部: ドゥルジョ ファティマ、エルミタ、マンバリン、パヒナ セントラル、パシル、サン ニコラス プロパー、サン ロケ、サワン カレロ、スバ、ティサ",
    "affectedEn": "Portion of Cebu City: Duljo Fatima, Ermita, Mambaling, Pahina Central, Pasil, San Nicolas Proper, San Roque, Sawang Calero, Suba, & Tisa",
    "mapUrl": "https://lh3.googleusercontent.com/d/13huMVjGBXeEvLIJ6kLBm7CVp30QXj0Gu",
    "pins": [
      {
        "name": "Duljo Fatima",
        "lat": 10.29288,
        "lng": 123.88312
      },
      {
        "name": "Ermita",
        "lat": 10.29022,
        "lng": 123.89458
      },
      {
        "name": "Mambaling",
        "lat": 10.288,
        "lng": 123.875
      },
      {
        "name": "Pasil",
        "lat": 10.28937,
        "lng": 123.8887
      },
      {
        "name": "San Nicolas Proper",
        "lat": 10.29076,
        "lng": 123.89149
      },
      {
        "name": "Sawang Calero",
        "lat": 10.28401,
        "lng": 123.88362
      },
      {
        "name": "Suba",
        "lat": 10.28629,
        "lng": 123.88587
      },
      {
        "name": "Point 11",
        "lat": 10.29252,
        "lng": 123.89342,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.29176,
        "lng": 123.88915,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.29296,
        "lng": 123.89113,
        "radius": 100
      },
      {
        "name": "Point 14",
        "lat": 10.29279,
        "lng": 123.8866,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.29085,
        "lng": 123.87988,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.28792,
        "lng": 123.88143,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.28973,
        "lng": 123.88375,
        "radius": 200
      }
    ],
    "pinCount": 9
  },
  {
    "groupId": "grp-39",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "その他（手書き入力）",
    "affectedJa": "サンフェルナンドの一部: バルード、バサク、ブゴ、カバトバタン、ランタワン、リブロン、マグシコ、パナタラン、南ポブラシオン、タビオナン、タナナス、ティヌブダン",
    "affectedEn": "Portion of San Fernando: Balud, Basak, Bugho, Cabatbatan, Lantawan, Liburon, Magsico, Panadtaran, South Poblacion, Tabionan, Tananas, & Tinubdan",
    "mapUrl": "https://lh3.googleusercontent.com/d/1DmzD5O-pIkS3Vd0WPDiq5mS3Dr2xwR_e",
    "pins": [
      {
        "name": "Balud",
        "lat": 10.1577,
        "lng": 123.70451,
        "radius": 300
      },
      {
        "name": "Bugho",
        "lat": 10.17699,
        "lng": 123.67576,
        "radius": 500
      },
      {
        "name": "Liburon",
        "lat": 10.15452,
        "lng": 123.70151
      },
      {
        "name": "Magsico",
        "lat": 10.17074,
        "lng": 123.68168,
        "radius": 500
      },
      {
        "name": "South Poblacion",
        "lat": 10.16136,
        "lng": 123.7082,
        "radius": 350
      },
      {
        "name": "Tananas",
        "lat": 10.17188,
        "lng": 123.68923
      },
      {
        "name": "Tinubdan",
        "lat": 10.17438,
        "lng": 123.68674
      },
      {
        "name": "Point 9",
        "lat": 10.16153,
        "lng": 123.70361,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.16399,
        "lng": 123.70087,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.16552,
        "lng": 123.6977,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.168,
        "lng": 123.69515,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.1699,
        "lng": 123.69228,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.17978,
        "lng": 123.68443,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.18527,
        "lng": 123.67765,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.19291,
        "lng": 123.67183,
        "radius": 500
      },
      {
        "name": "Point 17",
        "lat": 10.18351,
        "lng": 123.6708,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.18798,
        "lng": 123.66451,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.18563,
        "lng": 123.65543,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.17674,
        "lng": 123.65593,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.16863,
        "lng": 123.65807,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.19003,
        "lng": 123.64806,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.19718,
        "lng": 123.64366,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.202,
        "lng": 123.63674,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.19813,
        "lng": 123.65252,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.20209,
        "lng": 123.66028,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.20174,
        "lng": 123.66777,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.20133,
        "lng": 123.6757,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.20871,
        "lng": 123.67387,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.21674,
        "lng": 123.67009,
        "radius": 500
      },
      {
        "name": "Point 31",
        "lat": 10.22421,
        "lng": 123.67267,
        "radius": 500
      },
      {
        "name": "Point 32",
        "lat": 10.23065,
        "lng": 123.66671,
        "radius": 500
      },
      {
        "name": "Point 33",
        "lat": 10.21044,
        "lng": 123.65756,
        "radius": 500
      },
      {
        "name": "Point 34",
        "lat": 10.21501,
        "lng": 123.6508,
        "radius": 500
      },
      {
        "name": "Point 35",
        "lat": 10.21864,
        "lng": 123.64254,
        "radius": 500
      },
      {
        "name": "Point 36",
        "lat": 10.21057,
        "lng": 123.63932,
        "radius": 500
      },
      {
        "name": "Point 37",
        "lat": 10.2069,
        "lng": 123.64809,
        "radius": 500
      },
      {
        "name": "Point 38",
        "lat": 10.23878,
        "lng": 123.66182,
        "radius": 500
      }
    ],
    "pinCount": 1
  },
  {
    "groupId": "grp-40",
    "timeSlot": "19:00 - 21:00",
    "areaJa": "セブ市 (イナヤワン / マンバリング...)",
    "affectedJa": "セブ市の一部: イナヤワン & マンバリング、タリサイ市の一部: サン イシドロ",
    "affectedEn": "Portion of Cebu City: Inayawan & Mambaling, Portion of Talisay City: San Isidro",
    "mapUrl": "https://lh3.googleusercontent.com/d/1jAwBDD-dlL3_1SBUA5xsEp4SAqvEwq3y",
    "pins": [
      {
        "name": "Inayawan",
        "lat": 10.26746,
        "lng": 123.8772,
        "radius": 300
      },
      {
        "name": "Mambaling",
        "lat": 10.27099,
        "lng": 123.87961,
        "radius": 300
      },
      {
        "name": "Point 3",
        "lat": 10.27067,
        "lng": 123.87402,
        "radius": 300
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-41",
    "timeSlot": "20:00 - 22:00",
    "areaJa": "セブ市 (アパス / カサンバガン / ラハグ)",
    "affectedJa": "セブ市の一部: アパス、カサンバガン、ラハグ",
    "affectedEn": "Portion of Cebu City: Apas, Kasambagan, & Lahug",
    "mapUrl": "https://lh3.googleusercontent.com/d/1gYY4rUapPtweTl2AWfwnu0I66kna-SBx",
    "pins": [
      {
        "name": "Apas",
        "lat": 10.33816,
        "lng": 123.91503,
        "radius": 100
      },
      {
        "name": "Kasambagan",
        "lat": 10.32725,
        "lng": 123.90731,
        "radius": 150
      },
      {
        "name": "Lahug",
        "lat": 10.33124,
        "lng": 123.90735,
        "radius": 150
      },
      {
        "name": "Point 4",
        "lat": 10.32934,
        "lng": 123.9078,
        "radius": 150
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-42",
    "timeSlot": "20:00 - 22:00",
    "areaJa": "セブ市 (バサック サン ニコラス / カランバ / ドゥルジョ (ドゥルジョ ファティマ)...)",
    "affectedJa": "セブ市の一部: バサック サン ニコラス、カランバ、ドゥルジョ (ドゥルジョ ファティマ)、グアダルーペ、マンバリン、パヒナ セントラル、サンバッグ 1、サンバッグ 2、サン アントニオ、サン ニコラス (サン ニコラス プロパー)、サン ロケ、サワン カレロ",
    "affectedEn": "Portion of Cebu City: Basak San Nicolas, Calamba, Duljo (Duljo Fatima), Guadalupe, Mambaling, Pahina Central, Sambag 1, Sambag 2, San Antonio, San Nicolas (San Nicolas Proper), San Roque, & Sawang Calero",
    "mapUrl": "https://lh3.googleusercontent.com/d/1WOHBweWiXJrHQZbf9Ghp2tCtMmRmSGwN",
    "pins": [
      {
        "name": "Basak San Nicolas",
        "lat": 10.29039,
        "lng": 123.87519,
        "radius": 150
      },
      {
        "name": "Calamba",
        "lat": 10.30339,
        "lng": 123.88784,
        "radius": 150
      },
      {
        "name": "Duljo",
        "lat": 10.29237,
        "lng": 123.87905,
        "radius": 150
      },
      {
        "name": "Mambaling",
        "lat": 10.29014,
        "lng": 123.87785,
        "radius": 150
      },
      {
        "name": "Pahina Central",
        "lat": 10.30077,
        "lng": 123.88969,
        "radius": 300
      },
      {
        "name": "San Antonio",
        "lat": 10.30373,
        "lng": 123.89329
      },
      {
        "name": "San Nicolas",
        "lat": 10.29376,
        "lng": 123.8884
      },
      {
        "name": "San Roque",
        "lat": 10.27797,
        "lng": 123.8796,
        "radius": 150
      },
      {
        "name": "Sawang Calero",
        "lat": 10.28806,
        "lng": 123.8793,
        "radius": 150
      },
      {
        "name": "Point 13",
        "lat": 10.28034,
        "lng": 123.87827,
        "radius": 150
      },
      {
        "name": "Point 14",
        "lat": 10.28309,
        "lng": 123.87755,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.28563,
        "lng": 123.87974,
        "radius": 150
      },
      {
        "name": "Point 16",
        "lat": 10.29403,
        "lng": 123.8812,
        "radius": 150
      },
      {
        "name": "Point 17",
        "lat": 10.29537,
        "lng": 123.88342,
        "radius": 150
      },
      {
        "name": "Point 18",
        "lat": 10.29567,
        "lng": 123.88608,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.29491,
        "lng": 123.89132,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.29685,
        "lng": 123.88926,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.30065,
        "lng": 123.89424,
        "radius": 250
      },
      {
        "name": "Point 20",
        "lat": 10.30597,
        "lng": 123.88686,
        "radius": 150
      },
      {
        "name": "Point 21",
        "lat": 10.30369,
        "lng": 123.89038,
        "radius": 200
      }
    ],
    "pinCount": 9
  },
  {
    "groupId": "grp-43",
    "timeSlot": "20:00 - 22:00",
    "areaJa": "コンソラシオン (カレロ / カンサガ / ジュガン...)",
    "affectedJa": "コンソラシオンの部分: カレロ、カンサガ、ジュガン、ナンカ、ピトゴ、ポブラシオン オクシデンタル、ポブラシオン オリエンタル、タユド、トゥグブンガン、リロアンの部分: カレロ、ジュガン、タユド、ヤティ、マンダウエ市の部分: ヤゴビアオ",
    "affectedEn": "Portion of Consolacion: Calero, Cansaga, Jugan, Nangka, Pitogo, Poblacion Occidental, Poblacion Oriental, Tayud, & Tugbungan, Portion of Liloan: Calero, Jugan, Tayud, & Yati, Portion of Mandaue City: Jagobiao",
    "mapUrl": "https://lh3.googleusercontent.com/d/1xPvbfk6lDvwS2ur8PYoKGcS7YQTkOMZ9",
    "pins": [
      {
        "name": "Calero",
        "lat": 10.3701,
        "lng": 123.96857
      },
      {
        "name": "Cansaga",
        "lat": 10.37504,
        "lng": 123.96089
      },
      {
        "name": "Jugan",
        "lat": 10.368,
        "lng": 123.965
      },
      {
        "name": "Nangka",
        "lat": 10.37044,
        "lng": 123.95531
      },
      {
        "name": "Pitogo",
        "lat": 10.365,
        "lng": 123.958
      },
      {
        "name": "Poblacion Occidental",
        "lat": 10.37272,
        "lng": 123.95617,
        "radius": 150
      },
      {
        "name": "Poblacion Oriental",
        "lat": 10.37419,
        "lng": 123.95784
      },
      {
        "name": "Tayud",
        "lat": 10.36562,
        "lng": 123.97603
      },
      {
        "name": "Tugbungan",
        "lat": 10.37094,
        "lng": 123.96586
      },
      {
        "name": "Tayud",
        "lat": 10.36722,
        "lng": 123.99076
      },
      {
        "name": "Yati",
        "lat": 10.37305,
        "lng": 123.9632
      },
      {
        "name": "Jagobiao",
        "lat": 10.36909,
        "lng": 123.96029,
        "radius": 500
      },
      {
        "name": "Point 14",
        "lat": 10.3636,
        "lng": 123.96466,
        "radius": 350
      },
      {
        "name": "Point 15",
        "lat": 10.36808,
        "lng": 123.97123,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.37247,
        "lng": 123.97051,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.35253,
        "lng": 123.97356,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.3541,
        "lng": 123.9817,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.35933,
        "lng": 123.97725,
        "radius": 500
      },
      {
        "name": "Point 20",
        "lat": 10.35866,
        "lng": 123.98676,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.36466,
        "lng": 123.98281,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.3601,
        "lng": 123.99189,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.37107,
        "lng": 123.98603,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.36483,
        "lng": 123.99326,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.36208,
        "lng": 123.99489,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.35997,
        "lng": 123.99732,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.35912,
        "lng": 124.00041,
        "radius": 200
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-44",
    "timeSlot": "20:00 - 22:00",
    "areaJa": "コンソラシオン (カレロ / カンサガ / ジュガン...)",
    "affectedJa": "慰めの部分: カレロ、カンサガ、ジュガン、ラマック、ピトゴ、ポブラシオン オクシデンタル、ポブラシオン オリエンタル、サン ビセンテ、タユド、ティルハオン、リロアンの部分: カタルマン、ペピト、サン ロケ、タユド、ヤティ",
    "affectedEn": "Portion of Consolacion: Calero, Cansaga, Jugan, Lamac, Pitogo, Poblacion Occidental, Poblacion Oriental, San Vicente, Tayud, & Tilhaong, Portion of Liloan: Catarman, Pepito, San Roque, Tayud, & Yati",
    "mapUrl": "https://lh3.googleusercontent.com/d/17SImNMStIjg-SH2XsrH4R67F6VCSzy_B",
    "pins": [
      {
        "name": "Calero",
        "lat": 10.38324,
        "lng": 123.97024
      },
      {
        "name": "Cansaga",
        "lat": 10.37867,
        "lng": 123.9614
      },
      {
        "name": "Jugan",
        "lat": 10.3818,
        "lng": 123.96741
      },
      {
        "name": "Lamac",
        "lat": 10.37495,
        "lng": 123.95359
      },
      {
        "name": "Pitogo",
        "lat": 10.37758,
        "lng": 123.95814
      },
      {
        "name": "Poblacion Occidental",
        "lat": 10.37706,
        "lng": 123.95496
      },
      {
        "name": "Poblacion Oriental",
        "lat": 10.38053,
        "lng": 123.96423
      },
      {
        "name": "San Vicente",
        "lat": 10.38492,
        "lng": 123.96226,
        "radius": 500
      },
      {
        "name": "Tayud",
        "lat": 10.38399,
        "lng": 123.97393
      },
      {
        "name": "Catarman",
        "lat": 10.36288,
        "lng": 123.99925,
        "radius": 500
      },
      {
        "name": "Tayud",
        "lat": 10.37757,
        "lng": 123.98904,
        "radius": 500
      },
      {
        "name": "Yati",
        "lat": 10.38863,
        "lng": 123.97307,
        "radius": 500
      },
      {
        "name": "Point 15",
        "lat": 10.36931,
        "lng": 124.00503,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.36828,
        "lng": 123.99539,
        "radius": 300
      },
      {
        "name": "Point 17",
        "lat": 10.37225,
        "lng": 123.99196,
        "radius": 300
      },
      {
        "name": "Point 18",
        "lat": 10.38103,
        "lng": 123.99385,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.38306,
        "lng": 123.99067,
        "radius": 300
      },
      {
        "name": "Point 20",
        "lat": 10.38399,
        "lng": 123.98526,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.38418,
        "lng": 123.97825,
        "radius": 300
      },
      {
        "name": "Point 22",
        "lat": 10.38036,
        "lng": 123.97882,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.38855,
        "lng": 123.96792,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.38981,
        "lng": 123.96329,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.39599,
        "lng": 123.95773,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.39446,
        "lng": 123.96106,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.39234,
        "lng": 123.96295,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.39792,
        "lng": 123.96123,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.39631,
        "lng": 123.96389,
        "radius": 200
      },
      {
        "name": "Point 28",
        "lat": 10.39371,
        "lng": 123.96555,
        "radius": 200
      }
    ],
    "pinCount": 4
  },
  {
    "groupId": "grp-45",
    "timeSlot": "20:00 - 22:00",
    "areaJa": "セブ市 (カレタ / 北干拓地 / テヘロ)",
    "affectedJa": "セブ市の一部: カレタ、北干拓地、テヘロ",
    "affectedEn": "Portion of Cebu City: Carreta, North Reclamation Area, & Tejero",
    "mapUrl": "https://lh3.googleusercontent.com/d/1zbnlSY8YIilWGGaDfpbKaIoYmV7THYqh",
    "pins": [
      {
        "name": "Carreta",
        "lat": 10.30605,
        "lng": 123.90939,
        "radius": 150
      },
      {
        "name": "Tejero",
        "lat": 10.30335,
        "lng": 123.90977,
        "radius": 150
      },
      {
        "name": "Point 3",
        "lat": 10.30854,
        "lng": 123.90754,
        "radius": 200
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-46",
    "timeSlot": "21:00 - 23:00",
    "areaJa": "セブ市 (カレタ / マボロ / 北埋立地...)",
    "affectedJa": "セブ市の一部: カレタ、マボロ、北埋立地、サンロケ、テジェロ、ティナゴ、マンダウエ市の一部: スバンダク",
    "affectedEn": "Portion of Cebu City: Carreta, Mabolo, North Reclamation Area, San Roque, Tejero, & Tinago, Portion of Mandaue City: Subangdaku",
    "mapUrl": "https://lh3.googleusercontent.com/d/1hYw3_sHoM9zPWe552Eo0zNIy99em_N85",
    "pins": [
      {
        "name": "Carreta",
        "lat": 10.30432,
        "lng": 123.91505
      },
      {
        "name": "Mabolo",
        "lat": 10.31314,
        "lng": 123.92463
      },
      {
        "name": "San Roque",
        "lat": 10.29385,
        "lng": 123.90767
      },
      {
        "name": "Tejero",
        "lat": 10.29997,
        "lng": 123.9102
      },
      {
        "name": "Tinago",
        "lat": 10.29697,
        "lng": 123.90887
      },
      {
        "name": "Subangdaku",
        "lat": 10.315,
        "lng": 123.92788
      },
      {
        "name": "Point 7",
        "lat": 10.30208,
        "lng": 123.91256,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.30441,
        "lng": 123.91239,
        "radius": 100
      },
      {
        "name": "Point 9",
        "lat": 10.30602,
        "lng": 123.9173,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.30784,
        "lng": 123.91953,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.31367,
        "lng": 123.91936,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.3112,
        "lng": 123.92149,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.31737,
        "lng": 123.93067,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.31775,
        "lng": 123.92801,
        "radius": 200
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-47",
    "timeSlot": "21:00 - 23:00",
    "areaJa": "タリサイ市 (カンソジョン / ラワーン I / リナオ...)",
    "affectedJa": "タリサイ市の一部: カンソジョン、ラワーン I、リナオ、モホン、サン イシドロ、サン ロケ、タブノク、タンケ",
    "affectedEn": "Portion of Talisay City: Cansojong, Lawaan I, Linao, Mohon, San Isidro, San Roque, Tabunok, & Tangke",
    "mapUrl": "https://lh3.googleusercontent.com/d/18gvik3F-4XaDM-w4GF4KcmlKhcXlEFLH",
    "pins": [
      {
        "name": "Cansojong",
        "lat": 10.25521,
        "lng": 123.82931
      },
      {
        "name": "Lawaan I",
        "lat": 10.26172,
        "lng": 123.84064
      },
      {
        "name": "Linao",
        "lat": 10.25445,
        "lng": 123.8239
      },
      {
        "name": "Mohon",
        "lat": 10.25369,
        "lng": 123.82708
      },
      {
        "name": "San Isidro",
        "lat": 10.25326,
        "lng": 123.81961
      },
      {
        "name": "San Roque",
        "lat": 10.25867,
        "lng": 123.84021
      },
      {
        "name": "Tabunok",
        "lat": 10.26467,
        "lng": 123.84072
      },
      {
        "name": "Tangke",
        "lat": 10.25428,
        "lng": 123.86442,
        "radius": 500
      },
      {
        "name": "Point 9",
        "lat": 10.25061,
        "lng": 123.86188,
        "radius": 300
      },
      {
        "name": "Point 10",
        "lat": 10.25445,
        "lng": 123.85948,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.2542,
        "lng": 123.85338,
        "radius": 350
      },
      {
        "name": "Point 12",
        "lat": 10.25369,
        "lng": 123.84845,
        "radius": 300
      },
      {
        "name": "Point 13",
        "lat": 10.25749,
        "lng": 123.84991,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.25898,
        "lng": 123.84722,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.25631,
        "lng": 123.84338,
        "radius": 500
      },
      {
        "name": "Point 16",
        "lat": 10.26159,
        "lng": 123.84926,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.26473,
        "lng": 123.85022,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.26304,
        "lng": 123.84687,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.26274,
        "lng": 123.84357,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.25593,
        "lng": 123.83665,
        "radius": 300
      },
      {
        "name": "Point 21",
        "lat": 10.25572,
        "lng": 123.83231,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.25357,
        "lng": 123.83896,
        "radius": 100
      },
      {
        "name": "Point 23",
        "lat": 10.25255,
        "lng": 123.85823,
        "radius": 200
      }
    ],
    "pinCount": 8
  },
  {
    "groupId": "grp-48",
    "timeSlot": "12:00 - 14:00",
    "areaJa": "リロアン (カタルマン / コットコット / ジュベイ...)",
    "affectedJa": "リロアンの一部: カタルマン、コットコット、ジュベイ、ポブラシオン、タユド",
    "affectedEn": "Portion of Liloan: Catarman, Cotcot, Jubay, Poblacion, & Tayud",
    "mapUrl": "https://lh3.googleusercontent.com/d/16WZM5ql6Ic2lusPpTFb75rSsu0O6AYGL",
    "pins": [
      {
        "name": "Catarman",
        "lat": 10.38314,
        "lng": 124.01642,
        "radius": 500
      },
      {
        "name": "Cotcot",
        "lat": 10.42113,
        "lng": 124.00251,
        "radius": 500
      },
      {
        "name": "Jubay",
        "lat": 10.40716,
        "lng": 123.99835
      },
      {
        "name": "Poblacion",
        "lat": 10.40408,
        "lng": 124.00002
      },
      {
        "name": "Tayud",
        "lat": 10.40072,
        "lng": 124.00046
      },
      {
        "name": "Point 6",
        "lat": 10.38534,
        "lng": 124.00869,
        "radius": 500
      },
      {
        "name": "Point 7",
        "lat": 10.39074,
        "lng": 124.00457,
        "radius": 350
      },
      {
        "name": "Point 8",
        "lat": 10.42536,
        "lng": 124.00543,
        "radius": 300
      },
      {
        "name": "Point 9",
        "lat": 10.42747,
        "lng": 124.00201,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.43227,
        "lng": 124.00063,
        "radius": 300
      },
      {
        "name": "Point 11",
        "lat": 10.43621,
        "lng": 123.99905,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.4333,
        "lng": 123.99665,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.42835,
        "lng": 123.99869,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.42992,
        "lng": 123.99647,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.4173,
        "lng": 123.99759,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.41391,
        "lng": 123.99728,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.41028,
        "lng": 123.99762,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.39784,
        "lng": 123.99742,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.3972,
        "lng": 124.0008,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.3945,
        "lng": 124.00146,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.39125,
        "lng": 124.00033,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.38589,
        "lng": 124.00004,
        "radius": 450
      },
      {
        "name": "Point 23",
        "lat": 10.37516,
        "lng": 123.99925,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.37955,
        "lng": 124.00337,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.37871,
        "lng": 124.01054,
        "radius": 300
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-49",
    "timeSlot": "12:00 - 14:00",
    "areaJa": "マンダウエ市 (イババオ・エスタンシア / マグイカ / パクナン...)",
    "affectedJa": "マンダウエ市の一部: イババオ・エスタンシア、マグイカ、パクナン、タボク",
    "affectedEn": "Portion of Mandaue City: Ibabao-Estancia, Maguikay, Paknaan, & Tabok",
    "mapUrl": "https://lh3.googleusercontent.com/d/1KL6llY3_pm4RXJvrxYCXIXOwJPaxRm5v",
    "pins": [
      {
        "name": "Ibabao-Estancia",
        "lat": 10.34114,
        "lng": 123.9452
      },
      {
        "name": "Maguikay",
        "lat": 10.34164,
        "lng": 123.9423,
        "radius": 150
      },
      {
        "name": "Paknaan",
        "lat": 10.34328,
        "lng": 123.94852
      },
      {
        "name": "Tabok",
        "lat": 10.34658,
        "lng": 123.94887
      },
      {
        "name": "Point 5",
        "lat": 10.33884,
        "lng": 123.94374,
        "radius": 100
      },
      {
        "name": "Point 6",
        "lat": 10.34323,
        "lng": 123.94042,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.34471,
        "lng": 123.93872,
        "radius": 100
      },
      {
        "name": "Point 8",
        "lat": 10.34424,
        "lng": 123.95159,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.34283,
        "lng": 123.95383,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.3458,
        "lng": 123.95406,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.3476,
        "lng": 123.95628,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.34551,
        "lng": 123.95859,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.34878,
        "lng": 123.95365,
        "radius": 200
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-50",
    "timeSlot": "13:00 - 15:00",
    "areaJa": "セブ市 (カランバ / グアダルーペ / ラバンゴン)",
    "affectedJa": "セブ市の一部: カランバ、グアダルーペ、ラバンゴン",
    "affectedEn": "Portion of Cebu City: Calamba, Guadalupe, & Labangon",
    "mapUrl": "https://lh3.googleusercontent.com/d/1ftUq137xfHn5_9ocK2NNZzNpB6CawPXu",
    "pins": [
      {
        "name": "Salvador St (Banawa/Guadalupe)",
        "lat": 10.31403,
        "lng": 123.88029
      },
      {
        "name": "Katipunan St (Labangon)",
        "lat": 10.30833,
        "lng": 123.88257
      },
      {
        "name": "V. Rama Ave (Calamba)",
        "lat": 10.3115,
        "lng": 123.88754,
        "radius": 150
      },
      {
        "name": "M. Velez St (Capitol Site)",
        "lat": 10.31509,
        "lng": 123.88364
      },
      {
        "name": "Horseshoe Hills (Banawa)",
        "lat": 10.31555,
        "lng": 123.87553
      },
      {
        "name": "Point 6",
        "lat": 10.30956,
        "lng": 123.88548,
        "radius": 150
      },
      {
        "name": "Point 7",
        "lat": 10.31175,
        "lng": 123.8845,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.31657,
        "lng": 123.8787,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.31323,
        "lng": 123.87724,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.31707,
        "lng": 123.87287,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.31784,
        "lng": 123.8703,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.31096,
        "lng": 123.88095,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.30965,
        "lng": 123.87786,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.30673,
        "lng": 123.87773,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.30749,
        "lng": 123.88,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.30639,
        "lng": 123.8752,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.30407,
        "lng": 123.87708,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.30217,
        "lng": 123.87803,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.31197,
        "lng": 123.87884,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.31298,
        "lng": 123.88202,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.30969,
        "lng": 123.87455,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.30926,
        "lng": 123.87167,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.30956,
        "lng": 123.86806,
        "radius": 300
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-51",
    "timeSlot": "13:00 - 15:00",
    "areaJa": "セブ市 (カンプソーとヒポドロモ)",
    "affectedJa": "セブ市の一部: カンプソーとヒポドロモ",
    "affectedEn": "Portion of Cebu City: Camputhaw & Hipodromo",
    "mapUrl": "https://lh3.googleusercontent.com/d/16o7Tu20W6ueIGARzpScJbheO59X_7CTx",
    "pins": [
      {
        "name": "Camputhaw",
        "lat": 10.31551,
        "lng": 123.90355
      },
      {
        "name": "Point 2",
        "lat": 10.31673,
        "lng": 123.90162,
        "radius": 150
      },
      {
        "name": "Point 3",
        "lat": 10.31821,
        "lng": 123.90321,
        "radius": 100
      },
      {
        "name": "Point 4",
        "lat": 10.31281,
        "lng": 123.90432,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.31116,
        "lng": 123.90505,
        "radius": 100
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-52",
    "timeSlot": "13:00 - 15:00",
    "areaJa": "セブ市 (マンバリンとサンロケ / タリサイ市の一部: サンロケとタンケ...)",
    "affectedJa": "セブ市の一部: マンバリンとサンロケ、タリサイ市の一部: サンロケとタンケ",
    "affectedEn": "Portion of Cebu City: Mambaling & San Roque, Portion of Talisay City: San Roque & Tangke",
    "mapUrl": "https://lh3.googleusercontent.com/d/1WiVuO2PzeSi_1dMw00u5LcRneHN5MOib",
    "pins": [
      {
        "name": "San Roque (Talisay / CSCR)",
        "lat": 10.25834,
        "lng": 123.86132
      },
      {
        "name": "Tangke (Talisay / CSCR)",
        "lat": 10.25631,
        "lng": 123.85884
      },
      {
        "name": "Inayawan (Cebu City)",
        "lat": 10.2694,
        "lng": 123.873
      },
      {
        "name": "Mambaling / SRP (Cebu City)",
        "lat": 10.27201,
        "lng": 123.88149
      },
      {
        "name": "Point 5",
        "lat": 10.26839,
        "lng": 123.88106,
        "radius": 200
      },
      {
        "name": "Point 6",
        "lat": 10.26568,
        "lng": 123.87909,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.26611,
        "lng": 123.87471,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.26291,
        "lng": 123.87191,
        "radius": 300
      },
      {
        "name": "Point 9",
        "lat": 10.2591,
        "lng": 123.86441,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.25935,
        "lng": 123.86853,
        "radius": 300
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-53",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "セブ市 (カレタ / セブ ビジネス パーク / ヒポドロモ...)",
    "affectedJa": "セブ市の一部: カレタ、セブ ビジネス パーク、ヒポドロモ、カサンバガン、ルス、マボロ、北開拓地",
    "affectedEn": "Portion of Cebu City: Carreta, Cebu Business Park, Hipodromo, Kasambagan, Luz, Mabolo, & North Reclamation Area",
    "mapUrl": "https://lh3.googleusercontent.com/d/1Wd1B3-hSrGHPzoiW9sgQZy6uAg3xN82P",
    "pins": [
      {
        "name": "Carreta",
        "lat": 10.30694,
        "lng": 123.91265,
        "radius": 250
      },
      {
        "name": "Kasambagan",
        "lat": 10.32573,
        "lng": 123.90909,
        "radius": 150
      },
      {
        "name": "Mabolo",
        "lat": 10.31661,
        "lng": 123.90801,
        "radius": 150
      },
      {
        "name": "Point 4",
        "lat": 10.32357,
        "lng": 123.91024,
        "radius": 150
      },
      {
        "name": "Point 5",
        "lat": 10.32167,
        "lng": 123.91128,
        "radius": 150
      },
      {
        "name": "Point 6",
        "lat": 10.31855,
        "lng": 123.91042,
        "radius": 200
      },
      {
        "name": "Point 7",
        "lat": 10.31737,
        "lng": 123.91329,
        "radius": 150
      },
      {
        "name": "Point 8",
        "lat": 10.3153,
        "lng": 123.91488,
        "radius": 150
      },
      {
        "name": "Point 9",
        "lat": 10.30926,
        "lng": 123.91582,
        "radius": 250
      },
      {
        "name": "Point 10",
        "lat": 10.31256,
        "lng": 123.91618,
        "radius": 200
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-54",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "セブ市 (バサク パルド / バサク サン ニコラス / ブラカオ...)",
    "affectedJa": "セブ市の一部: バサク パルド、バサク サン ニコラス、ブラカオ、コゴン パルド、イナヤワン、キナサンアン、マンバリン、ポブラシオン パルド、サン ロケ、タリサイ市の一部: ブラカオ、サン ロケ",
    "affectedEn": "Portion of Cebu City: Basak Pardo, Basak San Nicolas, Bulacao, Cogon Pardo, Inayawan, Kinasang-an, Mambaling, Poblacion Pardo, & San Roque, Portion of Talisay City: Bulacao & San Roque",
    "mapUrl": "https://lh3.googleusercontent.com/d/1y5VPZNSEp7fPIeKZmrSLPK-bY6MZUP6I",
    "pins": [
      {
        "name": "Basak Pardo",
        "lat": 10.28904,
        "lng": 123.87326,
        "radius": 150
      },
      {
        "name": "Basak San Nicolas",
        "lat": 10.28527,
        "lng": 123.87235,
        "radius": 300
      },
      {
        "name": "Bulacao",
        "lat": 10.27573,
        "lng": 123.85484,
        "radius": 300
      },
      {
        "name": "Cogon Pardo",
        "lat": 10.28274,
        "lng": 123.86068,
        "radius": 300
      },
      {
        "name": "Inayawan",
        "lat": 10.26999,
        "lng": 123.84862,
        "radius": 300
      },
      {
        "name": "Kinasang-An",
        "lat": 10.28532,
        "lng": 123.86373,
        "radius": 300
      },
      {
        "name": "Mambaling",
        "lat": 10.28781,
        "lng": 123.87647,
        "radius": 300
      },
      {
        "name": "Poblacion Pardo",
        "lat": 10.27915,
        "lng": 123.85789,
        "radius": 300
      },
      {
        "name": "San Roque",
        "lat": 10.28832,
        "lng": 123.87051
      },
      {
        "name": "Bulacao",
        "lat": 10.27278,
        "lng": 123.85184,
        "radius": 300
      },
      {
        "name": "San Roque",
        "lat": 10.26104,
        "lng": 123.85673
      },
      {
        "name": "Point 12",
        "lat": 10.28309,
        "lng": 123.86854,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.28663,
        "lng": 123.86755,
        "radius": 300
      },
      {
        "name": "Point 14",
        "lat": 10.28153,
        "lng": 123.86528,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.27886,
        "lng": 123.86317,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.27519,
        "lng": 123.86089,
        "radius": 300
      },
      {
        "name": "Point 17",
        "lat": 10.26974,
        "lng": 123.85755,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.26578,
        "lng": 123.86258,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.26645,
        "lng": 123.86707,
        "radius": 300
      },
      {
        "name": "Point 20",
        "lat": 10.26375,
        "lng": 123.85575,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.26273,
        "lng": 123.853,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.25914,
        "lng": 123.85866,
        "radius": 200
      }
    ],
    "pinCount": 8
  },
  {
    "groupId": "grp-55",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "マンダウエ市 (バキリド / カスンティンガン / マグカイ)",
    "affectedJa": "マンダウエ市の一部: バキリド、カスンティンガン、マグカイ",
    "affectedEn": "Portion of Mandaue City: Bakilid, Casuntingan, & Maguikay",
    "mapUrl": "https://lh3.googleusercontent.com/d/1LkDpfbMoie8-5OB4M004Qyp0kRWU0__Q",
    "pins": [
      {
        "name": "Bakilid",
        "lat": 10.34085,
        "lng": 123.93647,
        "radius": 150
      },
      {
        "name": "Casuntingan",
        "lat": 10.34093,
        "lng": 123.93454,
        "radius": 150
      },
      {
        "name": "Maguikay",
        "lat": 10.338,
        "lng": 123.935
      },
      {
        "name": "Point 4",
        "lat": 10.3433,
        "lng": 123.93146,
        "radius": 100
      },
      {
        "name": "Point 5",
        "lat": 10.34584,
        "lng": 123.92884,
        "radius": 100
      }
    ],
    "pinCount": 3
  },
  {
    "groupId": "grp-56",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "リロアン (ラタバン / ポブラシオン / サンロケ...)",
    "affectedJa": "リロアンの一部: ラタバン、ポブラシオン、サンロケ、サンビセンテ、スタ。クルーズ、タブラ、ヤティ",
    "affectedEn": "Portion of Liloan: Lataban, Poblacion, San Roque, San Vicente, Sta. Cruz, Tabla, & Yati",
    "mapUrl": "https://lh3.googleusercontent.com/d/1GZLOpLALJI8D2k29z2R7EryufAL_r6hF",
    "pins": [
      {
        "name": "Lataban",
        "lat": 10.42577,
        "lng": 123.99663,
        "radius": 300
      },
      {
        "name": "Poblacion",
        "lat": 10.40484,
        "lng": 123.99844,
        "radius": 500
      },
      {
        "name": "San Roque",
        "lat": 10.40286,
        "lng": 123.99333
      },
      {
        "name": "San Vicente",
        "lat": 10.40738,
        "lng": 123.98029,
        "radius": 500
      },
      {
        "name": "Sta. Cruz",
        "lat": 10.40518,
        "lng": 123.98548
      },
      {
        "name": "Tabla",
        "lat": 10.42796,
        "lng": 123.95943,
        "radius": 500
      },
      {
        "name": "Yati",
        "lat": 10.39821,
        "lng": 123.98822,
        "radius": 300
      },
      {
        "name": "Point 8",
        "lat": 10.40682,
        "lng": 123.99256,
        "radius": 300
      },
      {
        "name": "Point 9",
        "lat": 10.4032,
        "lng": 123.98914,
        "radius": 300
      },
      {
        "name": "Point 10",
        "lat": 10.40827,
        "lng": 123.9866,
        "radius": 200
      },
      {
        "name": "Point 11",
        "lat": 10.39397,
        "lng": 123.98513,
        "radius": 300
      },
      {
        "name": "Point 12",
        "lat": 10.39241,
        "lng": 123.98016,
        "radius": 300
      },
      {
        "name": "Point 13",
        "lat": 10.39636,
        "lng": 123.97851,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.39621,
        "lng": 123.98119,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.4007,
        "lng": 123.97968,
        "radius": 400
      },
      {
        "name": "Point 16",
        "lat": 10.39758,
        "lng": 123.97453,
        "radius": 300
      },
      {
        "name": "Point 17",
        "lat": 10.39749,
        "lng": 123.96981,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.40172,
        "lng": 123.97144,
        "radius": 300
      },
      {
        "name": "Point 19",
        "lat": 10.40368,
        "lng": 123.97533,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.40079,
        "lng": 123.96578,
        "radius": 400
      },
      {
        "name": "Point 21",
        "lat": 10.40522,
        "lng": 123.96037,
        "radius": 400
      },
      {
        "name": "Point 22",
        "lat": 10.40543,
        "lng": 123.96591,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.41134,
        "lng": 123.96363,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.40775,
        "lng": 123.97179,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.4132,
        "lng": 123.97788,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.41636,
        "lng": 123.97612,
        "radius": 200
      },
      {
        "name": "Point 27",
        "lat": 10.427,
        "lng": 123.96767,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.41902,
        "lng": 123.95951,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.42134,
        "lng": 123.97222,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.43616,
        "lng": 123.95754,
        "radius": 500
      },
      {
        "name": "Point 31",
        "lat": 10.4419,
        "lng": 123.95084,
        "radius": 500
      },
      {
        "name": "Point 32",
        "lat": 10.44426,
        "lng": 123.9596,
        "radius": 500
      },
      {
        "name": "Point 33",
        "lat": 10.45186,
        "lng": 123.95634,
        "radius": 500
      },
      {
        "name": "Point 34",
        "lat": 10.44679,
        "lng": 123.94312,
        "radius": 500
      },
      {
        "name": "Point 35",
        "lat": 10.45405,
        "lng": 123.94758,
        "radius": 500
      },
      {
        "name": "Point 36",
        "lat": 10.45388,
        "lng": 123.93831,
        "radius": 500
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-57",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "セブ市 (バサック サン ニコラス / ブヒサン / カランバ...)",
    "affectedJa": "セブ市の一部: バサック サン ニコラス、ブヒサン、カランバ、カルビハン、ラバンゴン、パムタン、プンタ プリンセサ、サンバッグ 1、サン ホセ、ティサ、トン",
    "affectedEn": "Portion of Cebu City: Basak San Nicolas, Buhisan, Calamba, Kalubihan, Labangon, Pamutan, Punta Princesa, Sambag 1, San Jose, Tisa, & Toong",
    "mapUrl": "https://lh3.googleusercontent.com/d/1RoshZeayPcNMNh6LB39av8J1bGUPPUFB",
    "pins": [
      {
        "name": "Basak San Nicolas",
        "lat": 10.29837,
        "lng": 123.87214,
        "radius": 300
      },
      {
        "name": "Buhisan",
        "lat": 10.2943,
        "lng": 123.86699,
        "radius": 500
      },
      {
        "name": "Calamba",
        "lat": 10.30136,
        "lng": 123.8851
      },
      {
        "name": "Kalubihan",
        "lat": 10.3042,
        "lng": 123.88506
      },
      {
        "name": "Labangon",
        "lat": 10.3069,
        "lng": 123.88548,
        "radius": 150
      },
      {
        "name": "Pamutan",
        "lat": 10.32843,
        "lng": 123.83961,
        "radius": 300
      },
      {
        "name": "Punta Princesa",
        "lat": 10.30568,
        "lng": 123.88313
      },
      {
        "name": "Sambag 1",
        "lat": 10.29832,
        "lng": 123.88552
      },
      {
        "name": "Tisa",
        "lat": 10.29959,
        "lng": 123.88222
      },
      {
        "name": "Toong",
        "lat": 10.30689,
        "lng": 123.85952,
        "radius": 500
      },
      {
        "name": "Point 11",
        "lat": 10.30285,
        "lng": 123.88219,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.3058,
        "lng": 123.88008,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.30039,
        "lng": 123.87948,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.30336,
        "lng": 123.87884,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.29773,
        "lng": 123.87965,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.29841,
        "lng": 123.8763,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.30166,
        "lng": 123.86613,
        "radius": 500
      },
      {
        "name": "Point 18",
        "lat": 10.29845,
        "lng": 123.85986,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.30667,
        "lng": 123.86512,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.30766,
        "lng": 123.85368,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.30985,
        "lng": 123.85128,
        "radius": 200
      },
      {
        "name": "Point 22",
        "lat": 10.31148,
        "lng": 123.84855,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.30884,
        "lng": 123.84553,
        "radius": 300
      },
      {
        "name": "Point 24",
        "lat": 10.3076,
        "lng": 123.84134,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.30945,
        "lng": 123.83825,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.31374,
        "lng": 123.83978,
        "radius": 300
      },
      {
        "name": "Point 27",
        "lat": 10.31917,
        "lng": 123.8404,
        "radius": 300
      },
      {
        "name": "Point 28",
        "lat": 10.32455,
        "lng": 123.84124,
        "radius": 300
      }
    ],
    "pinCount": 5
  },
  {
    "groupId": "grp-58",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "ナガ市 (バイラン / カブンガハン / 中央ポブラシオン...)",
    "affectedJa": "ナガ市の一部: バイラン、カブンガハン、中央ポブラシオン、コロン、東ポブラシオン、イノブラン、ジャギミット、ラングタッド、ルタック、メイント、北ポブラシオン、パタグ、南ポブラシオン、タンケ、ティナン、西ポブラシオン、サンフェルナンドの一部: バルド、ブゴ、グリーンヒルズ、イラヤ、ランタワン、パナタラン、ピタロ、サンイシドロ、サンガット、タナナス、トンゴ",
    "affectedEn": "Portion of City of Naga: Bairan, Cabungahan, Central Poblacion, Colon, East Poblacion, Inoburan, Jaguimit, Langtad, Lutac, Mainit, North Poblacion, Patag, South Poblacion, Tangke, Tinaan, & West Poblacion, Portion of San Fernando: Balud, Bugho, Greenhills, Ilaya, Lantawan, Panadtaran, Pitalo, San Isidro, Sangat, Tananas, & Tonggo",
    "mapUrl": "https://lh3.googleusercontent.com/d/1qd6d_PWRzSPnanQrC7eHzox69D4j9Owv",
    "pins": [
      {
        "name": "Central Poblacion",
        "lat": 10.20859,
        "lng": 123.7585,
        "radius": 300
      },
      {
        "name": "Colon",
        "lat": 10.19473,
        "lng": 123.73481,
        "radius": 500
      },
      {
        "name": "Inoburan",
        "lat": 10.20394,
        "lng": 123.75601,
        "radius": 300
      },
      {
        "name": "Langtad",
        "lat": 10.19609,
        "lng": 123.74734,
        "radius": 450
      },
      {
        "name": "Lutac",
        "lat": 10.2232,
        "lng": 123.71446,
        "radius": 500
      },
      {
        "name": "Mainit",
        "lat": 10.2102,
        "lng": 123.7258,
        "radius": 500
      },
      {
        "name": "North Poblacion",
        "lat": 10.21636,
        "lng": 123.76021
      },
      {
        "name": "South Poblacion",
        "lat": 10.2003,
        "lng": 123.75206,
        "radius": 300
      },
      {
        "name": "Tangke",
        "lat": 10.20267,
        "lng": 123.73069,
        "radius": 500
      },
      {
        "name": "Tinaan",
        "lat": 10.1856,
        "lng": 123.73532,
        "radius": 500
      },
      {
        "name": "West Poblacion",
        "lat": 10.21298,
        "lng": 123.75927
      },
      {
        "name": "Bugho",
        "lat": 10.18688,
        "lng": 123.70897,
        "radius": 500
      },
      {
        "name": "Panadtaran",
        "lat": 10.17581,
        "lng": 123.72099,
        "radius": 500
      },
      {
        "name": "Pitalo",
        "lat": 10.18096,
        "lng": 123.72811,
        "radius": 500
      },
      {
        "name": "San Isidro",
        "lat": 10.19135,
        "lng": 123.74202,
        "radius": 500
      },
      {
        "name": "Sangat",
        "lat": 10.16357,
        "lng": 123.70829,
        "radius": 500
      },
      {
        "name": "Tananas",
        "lat": 10.15655,
        "lng": 123.70254,
        "radius": 500
      },
      {
        "name": "Point 19",
        "lat": 10.20396,
        "lng": 123.7514,
        "radius": 200
      },
      {
        "name": "Point 20",
        "lat": 10.17015,
        "lng": 123.71421,
        "radius": 500
      },
      {
        "name": "Point 21",
        "lat": 10.15021,
        "lng": 123.6967,
        "radius": 500
      },
      {
        "name": "Point 22",
        "lat": 10.21553,
        "lng": 123.71859,
        "radius": 500
      },
      {
        "name": "Point 23",
        "lat": 10.19034,
        "lng": 123.72811,
        "radius": 500
      },
      {
        "name": "Point 24",
        "lat": 10.19668,
        "lng": 123.72142,
        "radius": 500
      },
      {
        "name": "Point 25",
        "lat": 10.20259,
        "lng": 123.71494,
        "radius": 500
      },
      {
        "name": "Point 26",
        "lat": 10.21002,
        "lng": 123.71103,
        "radius": 500
      },
      {
        "name": "Point 27",
        "lat": 10.17928,
        "lng": 123.71383,
        "radius": 500
      },
      {
        "name": "Point 28",
        "lat": 10.19414,
        "lng": 123.70348,
        "radius": 500
      },
      {
        "name": "Point 29",
        "lat": 10.1999,
        "lng": 123.69655,
        "radius": 500
      },
      {
        "name": "Point 30",
        "lat": 10.20705,
        "lng": 123.69161,
        "radius": 500
      },
      {
        "name": "Point 31",
        "lat": 10.17353,
        "lng": 123.70584,
        "radius": 500
      },
      {
        "name": "Point 32",
        "lat": 10.18109,
        "lng": 123.7011,
        "radius": 500
      },
      {
        "name": "Point 33",
        "lat": 10.18766,
        "lng": 123.69563,
        "radius": 500
      },
      {
        "name": "Point 34",
        "lat": 10.1944,
        "lng": 123.68992,
        "radius": 500
      },
      {
        "name": "Point 35",
        "lat": 10.20176,
        "lng": 123.68512,
        "radius": 500
      },
      {
        "name": "Point 36",
        "lat": 10.20973,
        "lng": 123.68473,
        "radius": 500
      },
      {
        "name": "Point 37",
        "lat": 10.20379,
        "lng": 123.67797,
        "radius": 500
      },
      {
        "name": "Point 38",
        "lat": 10.165,
        "lng": 123.69923,
        "radius": 500
      },
      {
        "name": "Point 39",
        "lat": 10.17057,
        "lng": 123.69181,
        "radius": 500
      },
      {
        "name": "Point 40",
        "lat": 10.17522,
        "lng": 123.68442,
        "radius": 500
      },
      {
        "name": "Point 41",
        "lat": 10.18172,
        "lng": 123.67902,
        "radius": 500
      },
      {
        "name": "Point 42",
        "lat": 10.18907,
        "lng": 123.67361,
        "radius": 500
      },
      {
        "name": "Point 43",
        "lat": 10.15687,
        "lng": 123.69344,
        "radius": 500
      },
      {
        "name": "Point 44",
        "lat": 10.16297,
        "lng": 123.68713,
        "radius": 500
      },
      {
        "name": "Point 45",
        "lat": 10.16694,
        "lng": 123.67989,
        "radius": 500
      },
      {
        "name": "Point 46",
        "lat": 10.17475,
        "lng": 123.67563,
        "radius": 500
      },
      {
        "name": "Point 47",
        "lat": 10.18134,
        "lng": 123.67258,
        "radius": 350
      }
    ],
    "pinCount": 2
  },
  {
    "groupId": "grp-59",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "マンダウエ市 (アラン アラン / カンバロ / イババオ エスタンシア...)",
    "affectedJa": "マンダウエ市の一部: アラン アラン、カンバロ、イババオ エスタンシア、オパオ、パクナン、タボク、ティポロ、ウマパッド",
    "affectedEn": "Portion of Mandaue City: Alang-Alang, Cambaro, Ibabao-Estancia, Opao, Paknaan, Tabok, Tipolo, & Umapad",
    "mapUrl": "https://lh3.googleusercontent.com/d/1W68EXJJs0kr5oZGo9m0qMmeV8iHUUv96",
    "pins": [
      {
        "name": "Cambaro",
        "lat": 10.33845,
        "lng": 123.95188
      },
      {
        "name": "Ibabao-Estancia",
        "lat": 10.33713,
        "lng": 123.95849
      },
      {
        "name": "Opao",
        "lat": 10.33988,
        "lng": 123.94891
      },
      {
        "name": "Paknaan",
        "lat": 10.34582,
        "lng": 123.96363
      },
      {
        "name": "Tabok",
        "lat": 10.34739,
        "lng": 123.94634
      },
      {
        "name": "Tipolo",
        "lat": 10.33624,
        "lng": 123.94904
      },
      {
        "name": "Umapad",
        "lat": 10.34376,
        "lng": 123.96063
      },
      {
        "name": "Point 8",
        "lat": 10.34135,
        "lng": 123.95792,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.33903,
        "lng": 123.95522,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.34095,
        "lng": 123.96737,
        "radius": 500
      },
      {
        "name": "Point 11",
        "lat": 10.34105,
        "lng": 123.96183,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.33464,
        "lng": 123.96827,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.33451,
        "lng": 123.96077,
        "radius": 200
      },
      {
        "name": "Point 14",
        "lat": 10.33168,
        "lng": 123.96261,
        "radius": 200
      },
      {
        "name": "Point 15",
        "lat": 10.33143,
        "lng": 123.95415,
        "radius": 200
      },
      {
        "name": "Point 16",
        "lat": 10.33371,
        "lng": 123.95728,
        "radius": 200
      },
      {
        "name": "Point 17",
        "lat": 10.33523,
        "lng": 123.95385,
        "radius": 200
      },
      {
        "name": "Point 18",
        "lat": 10.33781,
        "lng": 123.94626,
        "radius": 200
      },
      {
        "name": "Point 19",
        "lat": 10.33527,
        "lng": 123.94488,
        "radius": 150
      },
      {
        "name": "Point 20",
        "lat": 10.34554,
        "lng": 123.94364,
        "radius": 200
      },
      {
        "name": "Point 21",
        "lat": 10.34958,
        "lng": 123.94501,
        "radius": 150
      },
      {
        "name": "Point 22",
        "lat": 10.34799,
        "lng": 123.94244,
        "radius": 200
      },
      {
        "name": "Point 23",
        "lat": 10.34942,
        "lng": 123.93961,
        "radius": 200
      },
      {
        "name": "Point 24",
        "lat": 10.35073,
        "lng": 123.9369,
        "radius": 200
      },
      {
        "name": "Point 25",
        "lat": 10.35306,
        "lng": 123.93767,
        "radius": 200
      },
      {
        "name": "Point 26",
        "lat": 10.34199,
        "lng": 123.94759,
        "radius": 200
      }
    ],
    "pinCount": 6
  },
  {
    "groupId": "grp-60",
    "timeSlot": "14:00 - 16:00",
    "areaJa": "マンダウエ市 (アラン アラン / カンバロ / セントロ...)",
    "affectedJa": "マンダウエ市の一部: アラン アラン、カンバロ、セントロ、ギゾ、イババオ エスタンシア、ロオク、マントゥヨン",
    "affectedEn": "Portion of Mandaue City: Alang-Alang, Cambaro, Centro, Guizo, Ibabao-Estancia, Looc, & Mantuyong",
    "mapUrl": "https://lh3.googleusercontent.com/d/1YPhVsi4-8BbD-oQAsWdFLY4NaeIjhDeU",
    "pins": [
      {
        "name": "Cambaro",
        "lat": 10.32974,
        "lng": 123.93904
      },
      {
        "name": "Centro",
        "lat": 10.33456,
        "lng": 123.94136
      },
      {
        "name": "Guizo",
        "lat": 10.33101,
        "lng": 123.93608,
        "radius": 150
      },
      {
        "name": "Ibabao-Estancia",
        "lat": 10.33679,
        "lng": 123.94325,
        "radius": 150
      },
      {
        "name": "Looc",
        "lat": 10.32683,
        "lng": 123.95192,
        "radius": 150
      },
      {
        "name": "Mantuyong",
        "lat": 10.3327,
        "lng": 123.93861
      },
      {
        "name": "Point 7",
        "lat": 10.32602,
        "lng": 123.94286,
        "radius": 200
      },
      {
        "name": "Point 8",
        "lat": 10.33215,
        "lng": 123.94389,
        "radius": 200
      },
      {
        "name": "Point 9",
        "lat": 10.33033,
        "lng": 123.9472,
        "radius": 200
      },
      {
        "name": "Point 10",
        "lat": 10.3289,
        "lng": 123.95013,
        "radius": 150
      },
      {
        "name": "Point 11",
        "lat": 10.32854,
        "lng": 123.94471,
        "radius": 200
      },
      {
        "name": "Point 12",
        "lat": 10.32936,
        "lng": 123.94175,
        "radius": 200
      },
      {
        "name": "Point 13",
        "lat": 10.33186,
        "lng": 123.94081,
        "radius": 200
      }
    ],
    "pinCount": 5
  }
]

def main():
    today_str = datetime.datetime.now(pht_tz).strftime("%Y/%m/%d")
    print(f"=== Cebu Outage Auto Update Pipeline (セブ現地時間: {today_str}) ===")

    final_veco_outages = []

    # ------------------------------------------
    # ⚡ 1. VECO公式カレンダー（Googleスプレッドシート）直接取得
    # ------------------------------------------
    print("\n⚡ 1. VECO公式サービス停止カレンダー（Googleスプレッドシート）からデータ取得中...")
    veco_spreadsheet_outages = fetch_veco_from_spreadsheet(today_str)
    
    if veco_spreadsheet_outages:
        final_veco_outages.extend(veco_spreadsheet_outages)
    else:
        print("⚠️ スプレッドシートからデータが取得できなかったため、従来のWEB/Facebookスクレイピングを試みます...")
        final_veco_outages = fetch_veco_legacy_scraping(today_str)

    # ------------------------------------------
    # 👥 2. VECO公式Facebook速報（Apify）並行チェック & マージ
    # ------------------------------------------
    if APIFY_TOKEN:
        fb_advisories = fetch_veco_facebook_advisories(today_str)
        if fb_advisories:
            final_veco_outages = merge_spreadsheet_and_facebook(final_veco_outages, fb_advisories)
    else:
        print("ℹ️ APIFY_TOKEN が未設定のため、Facebook速報チェックをスキップします。")

    # 停電データの重複整理
    final_veco_outages = merge_duplicate_outages(final_veco_outages)
    final_veco_outages = remove_tbd_duplicates(final_veco_outages)

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
    
    # MAPリンクをGoogleアカウント不要の直接画像URLに自動変換（内蔵辞書＋自動解決）
    builtin_map_cache = {
    "https://tinyurl.com/2h9zdv3n": "https://lh3.googleusercontent.com/d/1hT5Tf0SAx1lR9fGAziRkAmJsIzyV3Hi_",
    "https://tinyurl.com/6hr4wtma": "https://lh3.googleusercontent.com/d/1SgYrQVF8sEnUWGUXjnUdUWF-mKikEqT2",
    "https://tinyurl.com/3833mbj5": "https://lh3.googleusercontent.com/d/1BFD_JP33E470Fgeqi0dm0r-Nl8ZLWSSK",
    "https://tinyurl.com/a9j5pdjv": "https://lh3.googleusercontent.com/d/1FoX9tiprhfBDfHTbb5I7I_Hu1jldtIrD",
    "https://tinyurl.com/5arys842": "https://lh3.googleusercontent.com/d/1drKLIRxdXoL5t-9aufdjw9ZPXat2d5Y2",
    "https://tinyurl.com/mu59y6ys": "https://lh3.googleusercontent.com/d/1zattr9cxcXBe4F-PKPXXIxuwOxfEgP8c",
    "https://tinyurl.com/2r47cvf4": "https://lh3.googleusercontent.com/d/1yKF8O44B9YROdtGZa_QcKbIR0PcPPbRD",
    "https://tinyurl.com/ysn397nj": "https://lh3.googleusercontent.com/d/1FBEouKi0fHoH2uZKTggpzGKsPtlMpNFS",
    "https://tinyurl.com/mpw5kmxe": "https://lh3.googleusercontent.com/d/1_6wbx584Jj6GxHyPeh8a9JoZgV-pqVtH",
    "https://tinyurl.com/3x6jcs62": "https://lh3.googleusercontent.com/d/1bKnP1cWQqd9khoUnkQA-gU0R4XmHsdqp",
    "https://tinyurl.com/457wkkt6": "https://lh3.googleusercontent.com/d/1hghnWP3dXlgslR6Up-w7P6xWVOhCfORs",
    "https://tinyurl.com/2tp8fm8u": "https://lh3.googleusercontent.com/d/1TEQtLaAwL4_5fHxG9JgrjAIJOb__yQf6",
    "https://tinyurl.com/4t5zrpan": "https://lh3.googleusercontent.com/d/1fmlWU3Dd5x8Xz6PCixYGx0SpNJq05bz9",
    "https://tinyurl.com/y3xj8z4r": "https://lh3.googleusercontent.com/d/1q2UG_Y-9oBQW57bEZN9_1-_4tTSWD-f8",
    "https://tinyurl.com/mr275pb4": "https://lh3.googleusercontent.com/d/1ede4D2oKiveec5ig-dqnm6zj5nSUkZos",
    "https://tinyurl.com/yhhuwjj7": "https://lh3.googleusercontent.com/d/1-a9ANwYKu3VZkU6fJ2MPtwQdgwaw6UKo",
    "https://tinyurl.com/hm74tnrp": "https://lh3.googleusercontent.com/d/1YpzmIx7_EzriXBI5zLtXiUSuD1ldbfcw",
    "https://tinyurl.com/54jf6auy": "https://lh3.googleusercontent.com/d/1xplSAwqgJGBIiG_WKHMHIQPEBxHU2d-S",
    "https://tinyurl.com/yms77n8b": "https://lh3.googleusercontent.com/d/1HLSvs5uVLSx6uuOGCcxR8d_RNe4DzktU",
    "https://tinyurl.com/35ny3vde": "https://lh3.googleusercontent.com/d/1BEOzsuueTARjnxvVJYgHCv6sju17WaAm",
    "https://tinyurl.com/3vh7wtzw": "https://lh3.googleusercontent.com/d/1aWJPXcMJVKuBQP-BtPrhiYw4zkUD7X79",
    "https://tinyurl.com/muyt5s8b": "https://lh3.googleusercontent.com/d/1H-sYmRu2bt0LImhX7DsIT4qiFQ4TesmP",
    "https://tinyurl.com/584ru7wa": "https://lh3.googleusercontent.com/d/1r99ihqUwHMAoBJagvLqMwrQRA6ic3h9p",
    "https://tinyurl.com/nzzrwphh": "https://lh3.googleusercontent.com/d/1jS6bbQ-gS_jWO6AN_c3E-CgiK5oI1D0F",
    "https://tinyurl.com/bdsszbkt": "https://lh3.googleusercontent.com/d/1mn2dsVk8GZayCda96j0JSMHE30bHIGYc",
    "https://tinyurl.com/2d4frvdr": "https://lh3.googleusercontent.com/d/1Ny_gZWEYzYnmDPNZtq-YHUpwR3DrDVFr",
    "https://tinyurl.com/mrxkm8by": "https://lh3.googleusercontent.com/d/1ML2DSxx822TtKYMpQSNZMw3tQ6XMwPR7",
    "https://tinyurl.com/2p9v3vk5": "https://lh3.googleusercontent.com/d/13RwSuG5Oubha6MK3Ix7__8xvCUwO_r3S",
    "https://tinyurl.com/52jv2m27": "https://lh3.googleusercontent.com/d/1ufxNM7x8U7Ti6K7Fhsw6-ilsfPGihttl",
    "https://tinyurl.com/344kfaa7": "https://lh3.googleusercontent.com/d/1Qu-n8NG3AU81vi83jAVGAFwcPY96xNhb",
    "https://tinyurl.com/4c7c2e8b": "https://lh3.googleusercontent.com/d/1mI1hWBqTUmvOPt-BlXnB7D-GNb9lOT5g",
    "https://tinyurl.com/4b48h74n": "https://lh3.googleusercontent.com/d/10C5JnwgING8bf2XE_1TSjYqZPKGxkZWQ",
    "https://tinyurl.com/4bhdmd92": "https://lh3.googleusercontent.com/d/1QrWIN-BU9_TlRfNHTtwCV3Ekkox757UG",
    "https://tinyurl.com/esfbch7k": "https://lh3.googleusercontent.com/d/1Ev6rEckCVOmPmyxYOkhAGcl-DSI1nB4W",
    "https://tinyurl.com/2jkrafp6": "https://lh3.googleusercontent.com/d/18oXsQltuPb47WnfNyx7yS6UuAR_t4cJE",
    "https://tinyurl.com/bdhdd25w": "https://lh3.googleusercontent.com/d/1lmjhEM2Ns7E08GGoToYPHd6Rr7GlLnus",
    "https://tinyurl.com/3pc9d37k": "https://lh3.googleusercontent.com/d/1iE-JE13mMidRxdyhQK-_riZ940YjnWFP",
    "https://tinyurl.com/3k4trbmd": "https://lh3.googleusercontent.com/d/1ha5ijTFVNcTEb4njJakwexPciXOVmKMq",
    "https://tinyurl.com/ms2s5zav": "https://lh3.googleusercontent.com/d/1MDiNs9ofoIr_e_2T9Yh4reABt9K9xrse",
    "https://tinyurl.com/yc2539pt": "https://lh3.googleusercontent.com/d/13huMVjGBXeEvLIJ6kLBm7CVp30QXj0Gu",
    "https://tinyurl.com/3xm7tjej": "https://lh3.googleusercontent.com/d/1DmzD5O-pIkS3Vd0WPDiq5mS3Dr2xwR_e",
    "https://tinyurl.com/44e2cbxz": "https://lh3.googleusercontent.com/d/1jAwBDD-dlL3_1SBUA5xsEp4SAqvEwq3y",
    "https://tinyurl.com/4rwhrjkc": "https://lh3.googleusercontent.com/d/1gYY4rUapPtweTl2AWfwnu0I66kna-SBx",
    "https://tinyurl.com/5n6k78xd": "https://lh3.googleusercontent.com/d/1WOHBweWiXJrHQZbf9Ghp2tCtMmRmSGwN",
    "https://tinyurl.com/2jy2uu78": "https://lh3.googleusercontent.com/d/1xPvbfk6lDvwS2ur8PYoKGcS7YQTkOMZ9",
    "https://tinyurl.com/eu8pjz5t": "https://lh3.googleusercontent.com/d/17SImNMStIjg-SH2XsrH4R67F6VCSzy_B",
    "https://tinyurl.com/ufvxw7ne": "https://lh3.googleusercontent.com/d/1zbnlSY8YIilWGGaDfpbKaIoYmV7THYqh",
    "https://tinyurl.com/39zahuan": "https://lh3.googleusercontent.com/d/1hYw3_sHoM9zPWe552Eo0zNIy99em_N85",
    "https://tinyurl.com/pcdb6e3a": "https://lh3.googleusercontent.com/d/18gvik3F-4XaDM-w4GF4KcmlKhcXlEFLH",
    "https://tinyurl.com/mr2a8azt": "https://lh3.googleusercontent.com/d/1aYo22VL8TY50uOLWBRhRiMbe41Lmmuev",
    "https://tinyurl.com/2z6tybjx": "https://lh3.googleusercontent.com/d/1bDYXTj20V6seKfU-PFxM4uo3wcDzUFU1",
    "https://tinyurl.com/yt69wpfe": "https://lh3.googleusercontent.com/d/1yjvtv5wDvkuy9LLMZcSCRkkOVX1wfcHy",
    "https://tinyurl.com/6s8cmp24": "https://lh3.googleusercontent.com/d/1klKvqC9w4nbXJ2cQ9jcOLTWG2Y6A3Ui5",
    "https://tinyurl.com/fn7v2ppx": "https://lh3.googleusercontent.com/d/16WZM5ql6Ic2lusPpTFb75rSsu0O6AYGL",
    "https://tinyurl.com/bv4panyr": "https://lh3.googleusercontent.com/d/1KL6llY3_pm4RXJvrxYCXIXOwJPaxRm5v",
    "https://tinyurl.com/mr73r47r": "https://lh3.googleusercontent.com/d/1bawkjYo4n5U4q4oul7m6CFYGk5nTDcy3",
    "https://tinyurl.com/bdew4nrz": "https://lh3.googleusercontent.com/d/1ftUq137xfHn5_9ocK2NNZzNpB6CawPXu",
    "https://tinyurl.com/ns3fb4zu": "https://lh3.googleusercontent.com/d/16o7Tu20W6ueIGARzpScJbheO59X_7CTx",
    "https://tinyurl.com/mryfdv22": "https://lh3.googleusercontent.com/d/1WiVuO2PzeSi_1dMw00u5LcRneHN5MOib",
    "https://tinyurl.com/2p8wt7t": "https://lh3.googleusercontent.com/d/1Wd1B3-hSrGHPzoiW9sgQZy6uAg3xN82P",
    "https://tinyurl.com/48um3ve7": "https://lh3.googleusercontent.com/d/1y5VPZNSEp7fPIeKZmrSLPK-bY6MZUP6I",
    "https://tinyurl.com/42ct5fy4": "https://lh3.googleusercontent.com/d/1LkDpfbMoie8-5OB4M004Qyp0kRWU0__Q",
    "https://tinyurl.com/wn6cb5t3": "https://lh3.googleusercontent.com/d/1GZLOpLALJI8D2k29z2R7EryufAL_r6hF",
    "https://tinyurl.com/3mbf7dnx": "https://lh3.googleusercontent.com/d/1RoshZeayPcNMNh6LB39av8J1bGUPPUFB",
    "https://tinyurl.com/3wefpxxz": "https://lh3.googleusercontent.com/d/1qd6d_PWRzSPnanQrC7eHzox69D4j9Owv",
    "https://tinyurl.com/3df7bsy2": "https://lh3.googleusercontent.com/d/1W68EXJJs0kr5oZGo9m0qMmeV8iHUUv96",
    "https://tinyurl.com/tz6wx679": "https://lh3.googleusercontent.com/d/1YPhVsi4-8BbD-oQAsWdFLY4NaeIjhDeU",
    "https://tinyurl.com/55bmvnz4": "https://lh3.googleusercontent.com/d/1Wr44lH5KGu6zHMDMiRL0R9H0vhCfIaHE",
    "https://tinyurl.com/3vtvdehy": "https://lh3.googleusercontent.com/d/1y9PP_ANb_LyV_-pAl6rGjV2ODt5nhTx7",
    "https://tinyurl.com/4d59vxkw": "https://lh3.googleusercontent.com/d/1bkOrEIhqt6eE-wxCYtYeBeeFt7c7qP8A",
    "https://tinyurl.com/bddh2uhe": "https://lh3.googleusercontent.com/d/1HNQSg0yXmDlBELemL_dI6ArNBx8OOyfm",
    "https://tinyurl.com/mvn3w4wd": "https://lh3.googleusercontent.com/d/1xZSEPeFQkGvfhWN6SmJDFnch0o88cVak",
    "https://tinyurl.com/mrxhmyzj": "https://lh3.googleusercontent.com/d/1Hv7sUtYAnL8CtngEswsnaw3kcwkSgmqK",
    "https://tinyurl.com/jwzunj94": "https://lh3.googleusercontent.com/d/1dJC7ipQosG6fvT6vCMcCbxgS7sWVxABK",
    "https://tinyurl.com/zrsynjkz": "https://lh3.googleusercontent.com/d/11HxDGqsTey_GFlsU15B8hMIiPfcUQZua",
    "https://tinyurl.com/2juf42jp": "https://lh3.googleusercontent.com/d/1Y_G-zehUK0EaYQVN7ZLis1cp2ky8VtSX",
    "https://tinyurl.com/yumy9kbz": "https://lh3.googleusercontent.com/d/1OyUUdRdLpyyYcuphzvxtlc_qBi22sT5N",
    "https://tinyurl.com/y44remc9": "https://lh3.googleusercontent.com/d/1figI5aBfDLVAfmoSQZbDUQ4WfU8Vsovj",
    "https://tinyurl.com/ymvw23zk": "https://lh3.googleusercontent.com/d/1FAhPtDWYaHDyT0ifyPT6s4tokjsYl2Hs",
    "https://tinyurl.com/38xxe3xh": "https://lh3.googleusercontent.com/d/1pf1mrh7v69_e7MmNT1YgJz2Fhz8OjbO9",
    "https://tinyurl.com/mvjshuy2": "https://lh3.googleusercontent.com/d/11zLKH72SWPNYr_w_eHd7bYBDAVMnaumL",
    "https://tinyurl.com/4mb9j7km": "https://lh3.googleusercontent.com/d/1lebHAjo5MqS8EKH0yGpZZsQQVL6wHsBI"
}

    for item in filtered_outages:
        m_url = item.get("mapUrl")
        if m_url and "tinyurl.com" in m_url:
            if m_url in builtin_map_cache:
                item["mapUrl"] = builtin_map_cache[m_url]
            else:
                try:
                    import urllib.request
                    req = urllib.request.Request(m_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        f_url = resp.geturl()
                        m = re.search(r'/d/([a-zA-Z0-9_-]+)', f_url) or re.search(r'id=([a-zA-Z0-9_-]+)', f_url)
                        if m:
                            item["mapUrl"] = f"https://lh3.googleusercontent.com/d/{m.group(1)}"
                        else:
                            item["mapUrl"] = f_url
                except Exception:
                    pass

    cebu_areas_str = json.dumps(CEBU_AREAS, ensure_ascii=False, indent=2)
    outages_json_str = json.dumps(filtered_outages, ensure_ascii=False, indent=2)
    
    # 60グループマスターの内蔵データ（外部JSONファイル不要の完全自己完結仕様）
    groups_master_str = json.dumps(DEFAULT_MASTER_GROUPS, ensure_ascii=False, indent=2)

    new_data_js_content = f"""/**
 * Cebu Infrastructure Checker - Integrated Data Source
 */
export const CEBU_AREAS = {cebu_areas_str};

export const VECO_OUTAGES = {outages_json_str};

export const VECO_GROUPS_MASTER = {groups_master_str};
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
