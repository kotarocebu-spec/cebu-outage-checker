import json
import re
import time
import datetime
import os
import sys
import io
import unicodedata  # 特殊ユニコード太字を標準英字に直すために追加
from urllib.parse import urljoin
import urllib.request
import subprocess
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
# 🗺️ VECO輪番停電マスターデータ & 地図URLキャッシュ
# ==========================================
MASTER_FILE = os.path.join(os.path.dirname(__file__), 'veco_groups_master.json')
DEFAULT_MASTER_GROUPS = []
if os.path.exists(MASTER_FILE):
    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as _mf:
            DEFAULT_MASTER_GROUPS = json.load(_mf)
    except Exception as e:
        print(f"⚠️ veco_groups_master.json 読み込みエラー: {e}")

MECO_MASTER_FILE = os.path.join(os.path.dirname(__file__), 'meco_groups_master.json')
DEFAULT_MECO_GROUPS = []
if os.path.exists(MECO_MASTER_FILE):
    try:
        with open(MECO_MASTER_FILE, 'r', encoding='utf-8') as _mf:
            DEFAULT_MECO_GROUPS = json.load(_mf)
    except Exception as e:
        print(f"⚠️ meco_groups_master.json 読み込みエラー: {e}")

MAP_URL_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'map_url_cache.json')
builtin_map_cache = {}
if os.path.exists(MAP_URL_CACHE_FILE):
    try:
        with open(MAP_URL_CACHE_FILE, 'r', encoding='utf-8') as _mcf:
            builtin_map_cache = json.load(_mcf)
    except Exception as e:
        print(f"⚠️ map_url_cache.json 読み込みエラー: {e}")

if os.path.exists(MAP_URL_CACHE_FILE):
    try:
        with open(MAP_URL_CACHE_FILE, 'r', encoding='utf-8') as _mcf:
            _loaded = json.load(_mcf)
            builtin_map_cache.update(_loaded)
    except Exception as e:
        print(f"⚠️ map_url_cache.json 読み込みエラー: {e}")

def resolve_map_link(u):
    if not u:
        return u
    if u in builtin_map_cache:
        return builtin_map_cache[u]
    try:
        resp = requests.head(u, allow_redirects=True, timeout=5)
        final_url = resp.url
        m = re.search(r'/d/([a-zA-Z0-9_-]+)', final_url) or re.search(r'id=([a-zA-Z0-9_-]+)', final_url)
        if m:
            lh3_url = f"https://lh3.googleusercontent.com/d/{m.group(1)}"
            builtin_map_cache[u] = lh3_url
            try:
                with open(MAP_URL_CACHE_FILE, 'w', encoding='utf-8') as _mcf:
                    json.dump(builtin_map_cache, _mcf, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return lh3_url
        if "google" in final_url:
            builtin_map_cache[u] = final_url
            try:
                with open(MAP_URL_CACHE_FILE, 'w', encoding='utf-8') as _mcf:
                    json.dump(builtin_map_cache, _mcf, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return final_url
    except Exception:
        pass
    return u
    if u in builtin_map_cache:
        return builtin_map_cache[u]
    try:
        resp = requests.head(u, allow_redirects=True, timeout=5)
        final_url = resp.url
        if "google" in final_url:
            builtin_map_cache[u] = final_url
            try:
                with open(MAP_URL_CACHE_FILE, 'w', encoding='utf-8') as _mcf:
                    json.dump(builtin_map_cache, _mcf, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return final_url
    except Exception:
        pass
    return u

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


def fetch_veco_calendar_outages(today_str):
    """
    VECO公式 Service Interruption Calendar のバックエンドデータ（Googleスプレッドシート）から
    リアルタイムに全日程の停電スケジュール（輪番停電＋計画保守）を直接取得します。
    """
    print("\n⚡ 1. VECO公式カレンダー（GoogleスプレッドシートAPI）から最新スケジュールを取得中...")
    spreadsheet_id = '1rRq3A_2gFf0n68THzBVf6IYkHiSrhl1ZA6yOe50bp8o'
    url_main = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:json"
    url_updates = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:json&sheet=updates"

    def fetch_gviz(url):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode('utf-8')
            m = re.search(r'google\.visualization\.Query\.setResponse\(([\s\S]*)\);?', text)
            if not m:
                return []
            data = json.loads(m.group(1))
            cols = [c.get('label') or f"col_{i}" for i, c in enumerate(data['table']['cols'])]
            rows = []
            for r in data['table']['rows']:
                row_vals = []
                for c in r['c']:
                    if c is None:
                        row_vals.append(None)
                    else:
                        row_vals.append(c.get('f') or c.get('v'))
                rows.append(dict(zip(cols, row_vals)))
            return rows
        except Exception as e:
            print(f"⚠️ スプレッドシート取得エラー ({url}): {e}")
            return []

    main_rows = fetch_gviz(url_main)
    print(f"📊 カレンダーメインデータ取得成功: {len(main_rows)} 件")

    if not main_rows:
        print("⚠️ カレンダー取得失敗のため、フォールバックで従来スクレイピングを実行します...")
        return fetch_veco_legacy_scraping(today_str)

    # マスターデータの高速検索用マップ（Google Drive URL -> グループ情報）
    master_by_map_url = {g.get('mapUrl'): g for g in DEFAULT_MASTER_GROUPS if g.get('mapUrl')}

    calendar_outages = []
    for idx, r in enumerate(main_rows):
        exact_date = r.get('exactDate')
        if not exact_date:
            continue
        
        date_formatted = exact_date.replace('-', '/')
        if date_formatted < today_str:
            # 過去の日程はスキップ
            continue
            
        category = (r.get('category') or '').strip().lower()
        time_info = r.get('timeInfo') or ''
        parsed_time = parse_time(time_info)
        locations = r.get('locations') or ''
        title = r.get('title') or ''
        status = (r.get('status') or '').strip()
        map_link = r.get('mapLinks') or ''
        
        try:
            dt = datetime.datetime.strptime(date_formatted, "%Y/%m/%d")
            day_str = dt.strftime("%a")
        except Exception:
            day_str = ""

        clean_status = "SCHEDULED"
        if "NOT IMPLEMENTED" in status.upper() or "REMAINED ON" in status.upper() or "GRID CONDITIONS" in status.upper():
            clean_status = "AVOIDED"
        elif "RESTORED" in status.upper():
            clean_status = "RESTORED"
        elif "ONGOING" in status.upper() or "ACTIVE" in status.upper():
            clean_status = "ONGOING"
        elif "UPCOMING" in status.upper():
            clean_status = "UPCOMING"
        elif "CANCELLED" in status.upper():
            clean_status = "CANCELLED"

        # mapLinks に含まれるURLを抽出
        found_urls = re.findall(r'https?://[^\s,]+', map_link)
        loc_lines = [line.strip() for line in locations.splitlines() if line.strip()]

        # 輪番停電で複数の地域・図面URLが含まれている場合は、1地域/1グループ＝1件として個別に完全展開
        if "rotational" in category and (len(found_urls) > 1 or len(loc_lines) > 1):
            count_items = max(len(found_urls), len(loc_lines))
            for u_idx in range(count_items):
                u = found_urls[u_idx] if u_idx < len(found_urls) else (found_urls[0] if found_urls else map_link)
                this_loc = loc_lines[u_idx] if u_idx < len(loc_lines) else (loc_lines[0] if loc_lines else locations)

                drive_url = resolve_map_link(u)
                matched_grp = master_by_map_url.get(drive_url)

                if matched_grp:
                    sub_area_en = matched_grp.get('areaEn') or matched_grp.get('areaJa') or ''
                    sub_area_ja = matched_grp.get('areaJa') or sub_area_en
                    sub_aff_en = matched_grp.get('affectedEn') or ''
                    sub_aff_ja = matched_grp.get('affectedJa') or sub_aff_en
                else:
                    sub_area_en, sub_area_ja = parse_area_summary(this_loc)
                    sub_aff_en = this_loc
                    sub_aff_ja = clean_translated_japanese(cached_translate(this_loc))

                calendar_outages.append({
                    "id": 1000 + len(calendar_outages),
                    "type": "electricity",
                    "date": date_formatted,
                    "day": day_str,
                    "time": parsed_time,
                    "areaEn": sub_area_en,
                    "areaJa": sub_area_ja,
                    "affectedEn": sub_aff_en,
                    "affectedJa": sub_aff_ja,
                    "detailsEn": "Rotational Brownouts / Grid Alert",
                    "detailsJa": "計画的な供給制限（輪番停電）です。",
                    "mapUrl": drive_url,
                    "status": clean_status
                })
        else:
            drive_url = resolve_map_link(found_urls[0]) if found_urls else map_link
            matched_grp = master_by_map_url.get(drive_url) if drive_url else None

            if matched_grp and "rotational" in category:
                area_en = matched_grp.get('areaEn') or matched_grp.get('areaJa') or ''
                area_ja = matched_grp.get('areaJa') or area_en
                affected_en = matched_grp.get('affectedEn') or ''
                affected_ja = matched_grp.get('affectedJa') or affected_en
            else:
                area_en, area_ja = parse_area_summary(locations)
                affected_en = locations
                affected_ja = clean_translated_japanese(cached_translate(locations))

            if "rotational" in category:
                details_en = "Rotational Brownouts / Grid Alert"
                details_ja = "計画的な供給制限（輪番停電）です。"
            else:
                details_en = title if title else "Scheduled Distribution System Maintenance"
                details_ja = clean_translated_japanese(cached_translate(details_en))

            calendar_outages.append({
                "id": 1000 + len(calendar_outages),
                "type": "electricity",
                "date": date_formatted,
                "day": day_str,
                "time": parsed_time,
                "areaEn": area_en,
                "areaJa": area_ja,
                "affectedEn": affected_en,
                "affectedJa": affected_ja,
                "detailsEn": details_en,
                "detailsJa": details_ja,
                "mapUrl": drive_url,
                "status": clean_status
            })

    print(f"✅ カレンダーから本日および未来の停電スケジュール {len(calendar_outages)} 件を生成しました。")
    return calendar_outages

# ==========================================
# ⚡ MECO（マクタン島：ラプラプ市・コルドバ）公式停電告知スクレイピング & OCR解析
# ==========================================
MECO_OCR_CACHE_FILE = os.path.join(os.path.dirname(__file__), "meco_ocr_cache.json")
meco_ocr_cache = {}
if os.path.exists(MECO_OCR_CACHE_FILE):
    try:
        with open(MECO_OCR_CACHE_FILE, "r", encoding="utf-8") as f:
            meco_ocr_cache = json.load(f)
    except Exception:
        pass

MECO_LANDMARK_TO_FEEDER = {
    "RENDEZVOUS": "meco-f06",
    "CUSTOM": "meco-f07",
    "CUSTOMS": "meco-f07",
    "BLISS": "meco-f17",
    "COAST PACIFIC": "meco-f17",
    "MALINAO": "meco-f12",
    "AGUS": "meco-f12",
    "PUNTA ENGANO": "meco-f19",
    "SHANGRI-LA": "meco-f19",
    "NEWTOWN": "meco-f19",
    "JPARK": "meco-f14",
    "MARIBAGO": "meco-f14",
    "BUYONG": "meco-f14",
    "PLANTATION": "meco-f06",
    "AIRPORT": "meco-f08",
    "PUSOK": "meco-f08",
    "MARINA MALL": "meco-f08",
    "MEPZ 1": "meco-mez1",
    "MEPZ 2": "meco-acoland",
    "PUEBLO VERDE": "meco-f10a",
    "CLIP": "meco-f01",
    "TANGKE": "meco-f01",
    "SUDTUNGGAN": "meco-f01",
    "BASAK": "meco-f01",
    "PAJO": "meco-f02",
    "CAGUDOY": "meco-f03",
    "BANKAL": "meco-f04",
    "HOOPS DOME": "meco-f07",
    "CANJULAO": "meco-f07",
    "BABAG": "meco-f16",
    "CALAWISAN": "meco-f16",
    "CORDOVA": "meco-f17",
    "GABI": "meco-f17",
    "BUAYA": "meco-f13",
    "MACTAN SHRINE": "meco-f18"
}

def ocr_meco_image(img_url, local_filename):
    if img_url in meco_ocr_cache and meco_ocr_cache[img_url]:
        return meco_ocr_cache[img_url]

    local_path = os.path.abspath(local_filename)
    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp, open(local_path, "wb") as out:
            out.write(resp.read())
    except Exception as e:
        print(f"⚠️ MECO画像ダウンロードエラー ({img_url}): {e}")
        return ""

    ps_script_path = os.path.join(os.path.dirname(__file__), "meco_ocr.ps1")
    if not os.path.exists(ps_script_path):
        return ""

    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_script_path, "-ImagePath", local_path]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25, encoding="utf-8", errors="replace")
        text = res.stdout.strip()
        if text:
            meco_ocr_cache[img_url] = text
            try:
                with open(MECO_OCR_CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(meco_ocr_cache, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return text
    except Exception as e:
        print(f"⚠️ MECO OCR実行エラー: {e}")
        return ""

def fetch_meco_outages_from_facebook():
    """
    Facebook（Playwright）からMECO公式ページの最新停電情報をスクレイピングして返す。
    fb_auth.json が存在しない場合やエラー時は安全に空リストを返すフェイルセーフ仕様。
    """
    auth_file = os.path.join(os.path.dirname(__file__), "fb_auth.json")
    if not os.path.exists(auth_file):
        print("ℹ️ [MECO_FB] fb_auth.json が存在しないため、Facebookスクレイピングをスキップします。")
        return []

    print("📡 [MECO_FB] MECO公式Facebookから最新停電告知を取得中...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️ [MECO_FB] playwright が未インストールのためスキップします。")
        return []

    pht_tz = datetime.timezone(datetime.timedelta(hours=8))
    today_dt = datetime.datetime.now(pht_tz)
    today_str = today_dt.strftime("%Y/%m/%d")

    target_url = "https://www.facebook.com/mecomactan"
    all_outages = []

    # フィーダーマスター辞書作成
    feeder_dict = {}
    for g in DEFAULT_MECO_GROUPS:
        f_num = str(g.get("feederNumber", "")).strip().upper()
        if f_num:
            feeder_dict[f_num] = g

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                storage_state=auth_file,
                viewport={"width": 1280, "height": 1000},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)

            # ログイン状態および画面の検証ログ
            page_title = page.title()
            current_url = page.url
            print(f"📄 [MECO_FB] ページタイトル: {page_title}")
            print(f"🔗 [MECO_FB] アクセス先URL: {current_url}")

            # 証拠用スクリーンショットの保存
            screenshot_file = os.path.join(os.path.dirname(__file__), "github_meco_check.png")
            page.screenshot(path=screenshot_file)
            print(f"📸 [MECO_FB] 画面キャプチャを保存しました: {screenshot_file}")

            # 投稿をスクロール読み込み
            for _ in range(5):
                page.mouse.wheel(0, 1000)
                time.sleep(1.2)

            expand_buttons = page.locator("div[role='button']:has-text('さらに表示'), div[role='button']:has-text('See more')").all()
            for btn in expand_buttons:
                try:
                    if btn.is_visible():
                        btn.click(timeout=800)
                        time.sleep(0.2)
                except Exception:
                    pass

            time.sleep(1.5)
            posts = page.locator("div[role='feed'] > div, div[role='article']").all()
            print(f"📊 [MECO_FB] 取得された投稿要素数: {len(posts)} 件")

            seen_ids = set()
            meco_posts_count = 0

            for post_idx, post in enumerate(posts):
                raw_text = post.inner_text().strip()
                if not raw_text or len(raw_text) < 30:
                    continue
                if "Mactan Electric Company" not in raw_text and "MECO" not in raw_text:
                    continue

                meco_posts_count += 1
                norm_text = unicodedata.normalize('NFKD', raw_text)
                upper_text = norm_text.upper()

                # 最新投稿の生テキストプレビューをログ出力（証拠記録）
                if meco_posts_count <= 3:
                    preview_lines = [l.strip() for l in norm_text.split('\n') if l.strip()]
                    print(f"📝 [MECO_FB 投稿#{meco_posts_count} 抜粋]: {' / '.join(preview_lines[:3])}")

                # 1. 輪番停電 (Manual Load Dropping / MLD)
                if "MANUAL LOAD DROPPING" in upper_text or "MLD" in upper_text:
                    date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(202\d)", norm_text)
                    if not date_match:
                        continue
                    m_str, d_str, y_str = date_match.groups()
                    try:
                        dt = datetime.datetime.strptime(f"{m_str} {d_str} {y_str}", "%B %d %Y")
                        date_formatted = dt.strftime("%Y/%m/%d")
                        day_abbrev = dt.strftime("%a")
                    except Exception:
                        continue

                    # 今日および未来の日付のみを対象（過去の停電は除外）
                    if date_formatted < today_str:
                        print(f"⏭️ [MECO_FB] 過去の輪番停電 ({date_formatted}) をスキップしました。")
                        continue

                    feeder_lines = re.findall(r"(?:Feeder|FEEDER)\s*([0-9]+[A-Za-z]?)[–\-\—\s]*(?:\((.*?)\))?", norm_text)
                    for f_num, time_str in feeder_lines:
                        f_num_clean = f_num.strip().upper()
                        master = feeder_dict.get(f_num_clean, {})
                        
                        area_ja = master.get("areaJa", f"ラプラプ市・コルドバ (フィーダー {f_num_clean})")
                        area_en = master.get("areaEn", f"Lapu-Lapu & Cordova (Feeder {f_num_clean})")
                        affected_ja = master.get("affectedJa", "")
                        affected_en = master.get("affectedEn", "")
                        formatted_time = time_str.strip() if time_str else "12:00PM - 09:00PM (予定枠)"
                        status = "FINISHED" if time_str and "-" in time_str else "SCHEDULED"

                        item_id = f"meco-mld-{date_formatted.replace('/', '')}-f{f_num_clean.lower()}"
                        if item_id not in seen_ids:
                            seen_ids.add(item_id)
                            all_outages.append({
                                "id": item_id,
                                "type": "electricity",
                                "company": "MECO",
                                "date": date_formatted,
                                "day": day_abbrev,
                                "time": formatted_time,
                                "status": status,
                                "title": f"MECO FEEDER {f_num_clean} 輪番停電 (MLD)",
                                "groupId": f"meco-f{f_num_clean.lower()}",
                                "feederNumber": f_num_clean,
                                "feederTitle": f"MECO FEEDER {f_num_clean}",
                                "areaJa": area_ja,
                                "areaEn": area_en,
                                "affectedJa": affected_ja,
                                "affectedEn": affected_en,
                                "detailsJa": "送電逼迫による系統運用者（NGCP）指示の輪番停電（MLD）",
                                "detailsEn": "Manual Load Dropping (MLD) directive due to NGCP grid power supply condition",
                                "pins": master.get("pins", [])
                            })

                # 2. 定期計画停電 (Scheduled Power Outage)
                elif "SCHEDULED POWER" in upper_text or "SCHEDULED" in upper_text:
                    date_match = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(202\d)", norm_text)
                    if not date_match:
                        continue
                    m_str, d_str, y_str = date_match.groups()
                    try:
                        dt = datetime.datetime.strptime(f"{m_str} {d_str} {y_str}", "%B %d %Y")
                        date_formatted = dt.strftime("%Y/%m/%d")
                        day_abbrev = dt.strftime("%a")
                    except Exception:
                        continue

                    # 今日および未来の日付のみを対象（過去の停電は除外）
                    if date_formatted < today_str:
                        print(f"⏭️ [MECO_FB] 過去の計画停電 ({date_formatted}) をスキップしました。")
                        continue

                    time_match = re.search(r"from\s+(\d{1,2}:\d{2}\s*[APMapm]+)\s+to\s+(\d{1,2}:\d{2}\s*[APMapm]+)", norm_text)
                    time_str = f"{time_match.group(1)} - {time_match.group(2)}" if time_match else "02:00PM - 07:00PM"

                    item_id = f"meco-sched-{date_formatted.replace('/', '')}"
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        all_outages.append({
                            "id": item_id,
                            "type": "electricity",
                            "company": "MECO",
                            "date": date_formatted,
                            "day": day_abbrev,
                            "time": time_str,
                            "status": "SCHEDULED",
                            "title": "MECO 定期計画停電",
                            "groupId": "meco-general",
                            "feederNumber": "ALL",
                            "feederTitle": "MECO Scheduled Outage",
                            "areaJa": "ラプラプ市・コルドバ 対象地域",
                            "areaEn": "Lapu-Lapu & Cordova Scheduled Areas",
                            "affectedJa": "詳細はMECO公式告知を参照",
                            "affectedEn": "Please check MECO official advisory",
                            "detailsJa": "MECO配電設備の定期保守・改良工事",
                            "detailsEn": "Scheduled maintenance and distribution line improvement",
                            "pins": []
                        })

            print(f"🏁 [MECO_FB] 有効な本日以降の停電データ抽出結果: {len(all_outages)} 件")
            browser.close()
    except Exception as e:
        print(f"⚠️ [MECO_FB] スクレイピング実行中エラー: {e}")

    return all_outages

def fetch_meco_outages():
    # 1. まずFacebook公式ページからの取得を実行
    fb_outages = fetch_meco_outages_from_facebook()
    if fb_outages:
        print(f"✅ MECO公式Facebookから {len(fb_outages)} 件の停電データを生成しました。")
        return fb_outages

    # 2. Facebookから取れなかった場合のみ、従来のWeb APIに安全にフォールバック
    print("ℹ️ Facebookからのデータがないため、Web APIをチェックします...")
    print("📡 MECO（マクタン島）公式告知APIから停電情報を取得中...")
    pht_tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(pht_tz)
    today_str = now.strftime("%Y/%m/%d")

    groups_by_id = {g['groupId']: g for g in DEFAULT_MECO_GROUPS}
    
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }

    posts_url = "https://mecomactan.com/wp-json/wp/v2/posts?per_page=10"
    try:
        req = urllib.request.Request(posts_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            posts = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"⚠️ MECO公式API接続エラー: {e}")
        return []

    outages = []
    idx = 0

    for post in posts:
        pid = post.get('id')
        post_date = post.get('date', '')[:10].replace('-', '/')
        content_html = post.get('content', {}).get('rendered', '')
        soup = BeautifulSoup(content_html, 'html.parser')
        img_urls = [img.get('src') for img in soup.find_all('img') if img.get('src')]

        for img_url in img_urls:
            idx += 1
            tmp_img = os.path.join(os.path.dirname(__file__), f"meco_tmp_{idx}.jpg")
            raw_text = ocr_meco_image(img_url, tmp_img)
            if not raw_text:
                continue

            clean = re.sub(r'\s+', ' ', raw_text)

            # 1. Date
            m_d = re.search(r'DATE\s*:?\s*([A-Za-z]+)?\s*(\d{1,2})\s*,?\s*([A-Za-z]+)\s*,?\s*(\d{4})', clean, re.I)
            date_str = ''
            day_str = ''
            if m_d:
                day, mon, yr = m_d.group(2), m_d.group(3), m_d.group(4)
                m_num = months.get(mon.lower(), '09')
                date_str = f"{yr}/{m_num}/{int(day):02d}"
                try:
                    dt_obj = datetime.date(int(yr), int(m_num), int(day))
                    day_str = dt_obj.strftime("%a")
                except Exception:
                    day_str = 'Wed'
            elif post_date:
                date_str = post_date
                try:
                    parts = date_str.split('/')
                    dt_obj = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                    day_str = dt_obj.strftime("%a")
                except Exception:
                    day_str = 'Wed'

            # 2. Time
            m_t = re.search(r'TIME\s*:?\s*(\d{1,2}\s*:\s*\d{2}\s*(?:AM|PM))\s*[^A-Za-z0-9]*\s*(\d{1,2}\s*:\s*\d{2}\s*(?:AM|PM))', clean, re.I)
            time_str = ''
            time_end_pos = -1
            start_dt = None
            end_dt = None
            if m_t:
                t1 = re.sub(r'\s+', '', m_t.group(1))
                t2 = re.sub(r'\s+', '', m_t.group(2))
                time_str = f"{t1} - {t2}"
                time_end_pos = m_t.end()
                if date_str:
                    try:
                        start_dt = datetime.datetime.strptime(f"{date_str} {t1}", "%Y/%m/%d %I:%M%p").replace(tzinfo=pht_tz)
                        end_dt = datetime.datetime.strptime(f"{date_str} {t2}", "%Y/%m/%d %I:%M%p").replace(tzinfo=pht_tz)
                    except Exception:
                        pass

            # 3. Affected Area (Between Time and Reason)
            reason_pos = clean.find('REASON:')
            affected_str = ''
            if time_end_pos != -1 and reason_pos != -1 and reason_pos > time_end_pos:
                raw_aff = clean[time_end_pos:reason_pos]
                affected_str = re.sub(r'^[^\w]+', '', raw_aff).strip()
                affected_str = re.sub(r'^[E\[\]\(\)]\s*', '', affected_str).strip()

            # 4. Reason
            reason_str = ''
            m_r = re.search(r'REASON:\s*(.+?)(?=TICKET|#|WWW|$)', clean, re.I)
            if m_r:
                reason_str = m_r.group(1).strip()
                if 'BLISS CORDOVA' in reason_str:
                    affected_str = (affected_str + ', BLISS CORDOVA').strip(', ')
                    reason_str = reason_str.replace('BLISS CORDOVA', '').strip()

            # 5. Feeder matching
            matched = None
            best_score = 0
            aff_upper = (affected_str + ' ' + reason_str).upper()

            for lm, gid in MECO_LANDMARK_TO_FEEDER.items():
                if lm in aff_upper:
                    matched = groups_by_id.get(gid)
                    best_score = 100
                    break

            if not matched:
                for g in DEFAULT_MECO_GROUPS:
                    score = 0
                    f_num = g.get('feederNumber', '')
                    if f"FEEDER {f_num}" in clean.upper() or f"F-{f_num}" in clean.upper():
                        score += 15
                    search_corpus = (g.get('affectedEn', '') + ' ' + g.get('areaEn', '') + ' ' + g.get('title', '') + ' ' + str(g.get('pins', ''))).upper()
                    tokens = [t.strip() for t in re.split(r'[,/ ]+', aff_upper) if len(t.strip()) >= 4]
                    for tok in tokens:
                        if tok not in ['NEAR', 'STREET', 'ROAD', 'BARANGAY', 'AREA', 'EMERGENCY', 'POWER', 'INTERRUPTION']:
                            if tok in search_corpus:
                                score += 5
                    if score > best_score:
                        best_score = score
                        matched = g

            # Status calculation
            status = "FINISHED"
            if start_dt and end_dt:
                if now < start_dt:
                    status = "SCHEDULED"
                elif start_dt <= now <= end_dt:
                    status = "ONGOING"
                else:
                    status = "FINISHED"
            elif date_str:
                if date_str > today_str:
                    status = "SCHEDULED"
                elif date_str == today_str:
                    status = "ONGOING"
                else:
                    status = "FINISHED"

            gid = matched.get('groupId') if matched else ''
            feeder_num = matched.get('feederNumber') if matched else ''
            feeder_title = matched.get('title') if matched else 'MECO 停電'
            area_ja = matched.get('areaJa') if matched else 'ラプラプ市 / マクタン島'
            area_en = matched.get('areaEn') if matched else 'Lapu-Lapu City / Mactan'

            outages.append({
                "id": f"meco-{pid}-{idx}",
                "type": "electricity",
                "company": "MECO",
                "date": date_str,
                "day": day_str,
                "time": time_str,
                "status": status,
                "title": f"{feeder_title} 停電告知",
                "groupId": gid,
                "feederNumber": feeder_num,
                "feederTitle": feeder_title,
                "areaJa": area_ja,
                "areaEn": area_en,
                "affectedJa": affected_str,
                "affectedEn": affected_str,
                "detailsJa": clean_translated_japanese(cached_translate(reason_str)) if reason_str else "設備メンテナンス・点検作業",
                "detailsEn": reason_str if reason_str else "Scheduled Distribution System Maintenance",
                "imageUrl": img_url,
                "mapUrl": img_url
            })

    print(f"✅ MECO公式告知から {len(outages)} 件の停電データを生成しました。")
    return outages

def main():
    pht_tz = datetime.timezone(datetime.timedelta(hours=8))
    today = datetime.datetime.now(pht_tz)
    today_str = today.strftime("%Y/%m/%d")

    # 1. 電気（VECO公式カレンダー）情報の取得
    final_veco_outages = fetch_veco_calendar_outages(today_str)

    # 2. 電気（MECOマクタン島公式告知）情報の取得
    try:
        final_meco_outages = fetch_meco_outages()
    except Exception as e:
        print(f"⚠️ MECO取得スキップ: {e}")
        final_meco_outages = []

    # 3. 水道（MCWD）情報の取得
    try:
        final_mcwd_outages = scrape_mcwd_water_interruptions(today_str) if 'scrape_mcwd_water_interruptions' in globals() else []
    except Exception as e:
        print(f"⚠️ MCWD取得スキップ: {e}")
        final_mcwd_outages = []

    # 3. イベントリストのマージ（VECO公式の発表ステータスをそのまま維持）
    filtered_outages = final_veco_outages + final_mcwd_outages

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
        if m_url:
            if m_url in builtin_map_cache:
                item["mapUrl"] = builtin_map_cache[m_url]
            else:
                m = re.search(r'/d/([a-zA-Z0-9_-]+)', m_url) or re.search(r'id=([a-zA-Z0-9_-]+)', m_url)
                if m:
                    item["mapUrl"] = f"https://lh3.googleusercontent.com/d/{m.group(1)}"
                elif "tinyurl.com" in m_url:
                    try:
                        import urllib.request
                        req = urllib.request.Request(m_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            f_url = resp.geturl()
                            m2 = re.search(r'/d/([a-zA-Z0-9_-]+)', f_url) or re.search(r'id=([a-zA-Z0-9_-]+)', f_url)
                            if m2:
                                item["mapUrl"] = f"https://lh3.googleusercontent.com/d/{m2.group(1)}"
                            else:
                                item["mapUrl"] = f_url
                    except Exception:
                        pass

    cebu_areas_str = json.dumps(CEBU_AREAS, ensure_ascii=False, indent=2)
    outages_json_str = json.dumps(filtered_outages, ensure_ascii=False, indent=2)
    meco_outages_str = json.dumps(final_meco_outages, ensure_ascii=False, indent=2)
    
    # 60グループマスターの内蔵データ（外部JSONファイル不要の完全自己完結仕様）
    groups_master_str = json.dumps(DEFAULT_MASTER_GROUPS, ensure_ascii=False, indent=2)
    meco_groups_master_str = json.dumps(DEFAULT_MECO_GROUPS, ensure_ascii=False, indent=2)

    new_data_js_content = f"""/**
 * Cebu Infrastructure Checker - Integrated Data Source
 */
export const CEBU_AREAS = {cebu_areas_str};

export const VECO_OUTAGES = {outages_json_str};

export const MECO_OUTAGES = {meco_outages_str};

export const VECO_GROUPS_MASTER = {groups_master_str};

export const MECO_GROUPS_MASTER = {meco_groups_master_str};
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
    print(f"   ✅ 電気（VECO公式カレンダー）: {len(final_veco_outages)} 件")
    print(f"   ✅ 電気（MECOマクタン島公式告知）: {len(final_meco_outages)} 件")
    print(f"   ✅ 水道（MCWD計画断水情報）: {len(final_mcwd_outages)} 件")
    print(f"   💾 ファイル保存先: data.js")

if __name__ == "__main__":
    main()
