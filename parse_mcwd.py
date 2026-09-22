import os
import sys
import io
import re
import json
import datetime
from playwright.sync_api import sync_playwright

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

pht_tz = datetime.timezone(datetime.timedelta(hours=8))

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

# セブ・マンダウエ・ラプラプの主要エリア判定用辞書
AREA_KEYWORDS = [
    # セブ市
    {"keywords": ["IT PARK", "LAHUG"], "ja": "セブ市 (ITパーク / ラフグ)", "en": "Cebu City (IT Park / Lahug)"},
    {"keywords": ["AYALA", "BUSINESS PARK", "LUZ", "HIPODROMO"], "ja": "セブ市 (アヤラ / ビジネスパーク / ルズ)", "en": "Cebu City (Ayala / Business Park / Luz)"},
    {"keywords": ["APAS", "FULTON"], "ja": "セブ市 (アパス)", "en": "Cebu City (Apas)"},
    {"keywords": ["MABOLO", "KASAMBAGAN", "CARRETA", "TEJERO", "NRA"], "ja": "セブ市 (マボロ / カスンバガン)", "en": "Cebu City (Mabolo / Kasambagan)"},
    {"keywords": ["BANILAD", "A.S. FORTUNA", "AS FORTUNA"], "ja": "セブ市・マンダウエ市 (バニラッド / ASフォーチュナ)", "en": "Cebu & Mandaue (Banilad / AS Fortuna)"},
    {"keywords": ["TALAMBAN", "PIT-OS", "PITOS", "BACAYAN", "TIGBAO", "NASIPIT", "PULANGBATO"], "ja": "セブ市 (タランバン / ピットオス / バカヤン)", "en": "Cebu City (Talamban / Pit-os / Bacayan)"},
    {"keywords": ["GUADALUPE", "CAPITOL", "KALUNASAN", "ESCARIO", "V. RAMA", "V.RAMA"], "ja": "セブ市 (グアダルーペ / キャピトル / カルナサン)", "en": "Cebu City (Guadalupe / Capitol / Kalunasan)"},
    {"keywords": ["FUENTE", "RAMOS", "ZAPATERA", "KAMPUTHAW", "CAMPUTHAW", "ECHAVEZ"], "ja": "セブ市 (フエンテ / ラモス / サパテラ / カンプタウ)", "en": "Cebu City (Fuente / Ramos / Zapatera / Kamputhaw)"},
    {"keywords": ["DOWNTOWN", "COLON", "PAHINA", "PARIAN", "SAMBAG", "CALAMBA", "LABANGON"], "ja": "セブ市 (ダウンタウン / コロン / サンバグ / ラバンゴン)", "en": "Cebu City (Downtown / Colon / Sambag / Labangon)"},
    {"keywords": ["BUSAY", "MOUNTAIN"], "ja": "セブ市 (ブサイ / 山間部)", "en": "Cebu City (Busay / Mountain)"},
    # マンダウエ市
    {"keywords": ["MANDAUE", "TIPOLO", "SUBANGDAKU", "CABANCALAN", "CASUNTINGAN", "MAGUIKAY", "HERNAN CORTES"], "ja": "マンダウエ市 (セントロ / カバンカラン / ティポロ)", "en": "Mandaue City (Centro / Cabancalan / Tipolo)"},
    # ラプラプ市
    {"keywords": ["LAPU-LAPU", "LAPULAPU", "LLC", "MACTAN", "CORDOVA"], "ja": "マクタン島 (ラプラプ市 / コルドバ)", "en": "Mactan Island (Lapu-Lapu / Cordova)"},
    # 北部近郊
    {"keywords": ["CONSOLACION", "LILOAN", "COMPOSTELA"], "ja": "セブ北部 (コンソラシオン / リロアン)", "en": "Northern Cebu (Consolacion / Liloan)"}
]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def detect_area(affected_text, reason_text):
    combined = (affected_text + " " + reason_text).upper()
    for item in AREA_KEYWORDS:
        for kw in item["keywords"]:
            if kw in combined:
                return item["ja"], item["en"]
    return "セブ水道区 (MCWD供給地域)", "Cebu Water District (MCWD Grid)"

def extract_time_and_etr(raw_str):
    # 1. 開始時間 - 復旧見込み時刻 (例: 12:00PM. - (ETR) 3:00PM や 8:04am-EST,5:00PM)
    m = re.search(r'(\d{1,2}(?::\d{2})?\s*[apAP][mM])(?:\.|\s)*[-–to]+(?:\s*\(?(?:ETR|EST)\)?\s*,?\s*)?(\d{1,2}(?::\d{2})?\s*[apAP][mM])', raw_str)
    if m:
        t1 = m.group(1).upper()
        t2 = m.group(2).upper()
        return f"{t1} - {t2} (復旧見込)"
    
    # 2. 翌日跨ぎ (例: 10:00pm-23Sept,5:00am)
    m2 = re.search(r'(\d{1,2}(?::\d{2})?\s*[apAP][mM])\s*[-–to]+\s*\d{1,2}[A-Za-z]+,?\s*(\d{1,2}(?::\d{2})?\s*[apAP][mM])', raw_str)
    if m2:
        return f"{m2.group(1).upper()} - 翌{m2.group(2).upper()}"

    # 3. 復旧作業中 (例: 4:30AM-ongoing や 8:04am-EST)
    m3 = re.search(r'(\d{1,2}(?::\d{2})?\s*[apAP][mM])\s*[-–to]+\s*([A-Za-z]+)?', raw_str)
    if m3:
        w = (m3.group(2) or '').lower()
        if 'ongoing' in w:
            return f"{m3.group(1).upper()} - 復旧作業中"
        return f"{m3.group(1).upper()}〜 (復旧作業中)"

    return "終日 / 復旧作業中"

def scrape_mcwd_water_interruptions(target_date_str=None, max_days_history=3):
    """
    MCWD公式サイトから直近の断水情報をスクレイピング・パースして返す
    """
    url = 'https://www.mcwd.gov.ph/ords/production/r/mcwd-website/news?p55_news_selected=interruption'
    print(f"💧 Connecting to MCWD: {url}...")

    raw_items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=45000, wait_until='domcontentloaded')
            page.wait_for_timeout(4000)

            cards = page.query_selector_all('.t-Cards-item, .t-Card, .a-CardView-item')
            if cards:
                for c in cards:
                    txt = c.inner_text()
                    if txt and ('EMERGENCY' in txt or 'SCHEDULED' in txt or 'EWSI' in txt or 'SWSI' in txt):
                        raw_items.append(txt)
            else:
                body = page.inner_text('body')
                chunks = re.split(r'\n(?=(?:EMERGENCY|SCHEDULED))', body)
                for chunk in chunks:
                    if 'EWSI' in chunk or 'SWSI' in chunk or 'AA:' in chunk:
                        raw_items.append(chunk)

        except Exception as e:
            print(f"⚠️ Error fetching MCWD: {e}")
        finally:
            browser.close()

    now = datetime.datetime.now(pht_tz)
    target_dt = now.date()
    min_date = target_dt - datetime.timedelta(days=max_days_history)

    parsed_outages = []
    seen_keys = set()

    for idx, raw in enumerate(raw_items):
        lines = [l.strip() for l in raw.split('\n') if l.strip()]
        if not lines:
            continue
        raw_str = " ".join(lines)

        # 1. 種類 (緊急断水 / 計画断水)
        is_emergency = "EMERGENCY" in raw_str.upper() or "EWSI" in raw_str.upper()
        outage_type_label = "緊急断水" if is_emergency else "計画断水"

        # 2. 日付の解析
        parsed_dt = None
        m_date = re.search(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', raw_str)
        if m_date:
            m_name, d_num, y_num = m_date.group(1).lower(), int(m_date.group(2)), int(m_date.group(3))
            m_val = MONTHS.get(m_name, now.month)
            try:
                parsed_dt = datetime.date(y_num, m_val, d_num)
            except Exception:
                pass
        else:
            m_date2 = re.search(r'(\d{1,2})\s*([A-Za-z]{3,9})', raw_str)
            if m_date2:
                d_num = int(m_date2.group(1))
                m_name = m_date2.group(2).lower()
                m_val = MONTHS.get(m_name, now.month)
                try:
                    parsed_dt = datetime.date(now.year, m_val, d_num)
                except Exception:
                    pass

        if not parsed_dt:
            parsed_dt = target_dt

        # 古すぎる過去データ（3日以上前）は除外して現在有効な断水に絞り込む
        if parsed_dt < min_date:
            continue

        date_str = parsed_dt.strftime("%Y/%m/%d")
        day_str = parsed_dt.strftime("%a")

        # 3. 対象エリア (AA: ...)
        affected_str = ""
        m_aa = re.search(r'(?:AA|Affected Areas?)\s*:\s*(.+?)(?=(?:September|August|July|June|May|EMERGENCY|SCHEDULED|$))', raw_str, re.I)
        if m_aa:
            affected_str = clean_text(m_aa.group(1)).rstrip('.,')
        else:
            affected_str = "セブ市内 MCWD管轄地域"

        # 重複排除キー (日付 + 対象エリア冒頭30文字)
        dup_key = f"{date_str}_{affected_str[:35]}"
        if dup_key in seen_keys:
            continue
        seen_keys.add(dup_key)

        # 4. 時間帯
        time_str = extract_time_and_etr(raw_str)

        # 5. 理由・工事内容
        reason_str = ""
        m_reason = re.search(r'(?:EWSI|SWSI)\s*,\s*(.+?)(?=\.\s*\d{1,2}[A-Za-z]+|\d{1,2}(?::\d{2})?\s*(?:am|pm)|AA:|$)', raw_str, re.I)
        if m_reason:
            reason_str = clean_text(m_reason.group(1)).rstrip('.,')
        else:
            reason_str = "配水管漏水修理・ポンプ点検整備"

        # 6. エリア自動判定
        area_ja, area_en = detect_area(affected_str, reason_str)
        title = f"MCWD {outage_type_label} ({area_ja.split(' ')[-1].strip('()')})"

        # 7. ステータス (本日実施中は ONGOING、未来日は SCHEDULED)
        if parsed_dt == target_dt:
            status = "ONGOING"
        elif parsed_dt > target_dt:
            status = "SCHEDULED"
        else:
            status = "RESTORED"

        item = {
            "id": f"mcwd-{date_str.replace('/', '')}-{len(parsed_outages)+1}",
            "type": "water",
            "company": "MCWD",
            "date": date_str,
            "day": day_str,
            "time": time_str,
            "status": status,
            "title": title,
            "areaJa": area_ja,
            "areaEn": area_en,
            "affectedJa": affected_str,
            "affectedEn": affected_str,
            "reasonJa": f"{outage_type_label}: {reason_str}",
            "reasonEn": f"{'Emergency' if is_emergency else 'Scheduled'}: {reason_str}",
            "detailsJa": f"{reason_str} (復旧予定: {time_str} / 対象: {affected_str})",
            "detailsEn": f"{reason_str} (ETR: {time_str} / Affected: {affected_str})",
            "sourceUrl": url,
            "registeredAt": now.isoformat()
        }
        parsed_outages.append(item)

    print(f"✅ Successfully prepared {len(parsed_outages)} active MCWD water outage records.")
    return parsed_outages

if __name__ == '__main__':
    res = scrape_mcwd_water_interruptions()
    for r in res:
        print(f"[{r['date']}] {r['title']} | {r['time']} | {r['areaJa']}")
