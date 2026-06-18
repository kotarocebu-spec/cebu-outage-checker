/**
 * Cebu Infrastructure Checker - Integrated Data Source
 */
export const CEBU_AREAS = [
  {
    "id": "cebu-itpark",
    "nameEn": "Cebu City (IT Park / Lahug)",
    "nameJa": "セブ市 (ITパーク / ラフグ)"
  },
  {
    "id": "cebu-banilad",
    "nameEn": "Cebu City (Banilad / AS Fortuna)",
    "nameJa": "セブ市 (バニラッド / ASフォーチュナ)"
  },
  {
    "id": "cebu-talamban",
    "nameEn": "Cebu City (Talamban)",
    "nameJa": "セブ市 (タランバン)"
  },
  {
    "id": "cebu-guadalupe",
    "nameEn": "Cebu City (Guadalupe)",
    "nameJa": "セブ市 (グアダルーペ)"
  },
  {
    "id": "cebu-downtown",
    "nameEn": "Cebu City (Downtown / Colon)",
    "nameJa": "セブ市 (ダウンタウン / コロン)"
  },
  {
    "id": "cebu-other",
    "nameEn": "Cebu City (Other Areas)",
    "nameJa": "セブ市 (その他エリア)"
  },
  {
    "id": "mandaue-basak",
    "nameEn": "Mandaue City (Basak / Jagobiao)",
    "nameJa": "マンダウエ市 (バサック / ハゴビヤオ)"
  },
  {
    "id": "mandaue-centro",
    "nameEn": "Mandaue City (Centro / Looc)",
    "nameJa": "マンダウエ市 (セントロ / ルック)"
  },
  {
    "id": "mandaue-other",
    "nameEn": "Mandaue City (Other Areas)",
    "nameJa": "マンダウエ市 (その他エリア)"
  },
  {
    "id": "lapulapu-mactan",
    "nameEn": "Lapu-Lapu City (Mactan / Newtown)",
    "nameJa": "ラプラプ市 (マクタン / ニュータウン)"
  },
  {
    "id": "lapulapu-other",
    "nameEn": "Lapu-Lapu City (Other Areas)",
    "nameJa": "ラプラプ市 (その他エリア)"
  },
  {
    "id": "talisay",
    "nameEn": "Talisay City",
    "nameJa": "タリサイ市"
  },
  {
    "id": "consolacion",
    "nameEn": "Consolacion",
    "nameJa": "コンソラシオン"
  },
  {
    "id": "liloan",
    "nameEn": "Liloan",
    "nameJa": "リロアン"
  },
  {
    "id": "minglanilla",
    "nameEn": "Minglanilla",
    "nameJa": "ミングラニラ"
  },
  {
    "id": "cordova",
    "nameEn": "Cordova",
    "nameJa": "コルドバ"
  },
  {
    "id": "other",
    "nameEn": "Other (Manual Input)",
    "nameJa": "その他（手書き入力）"
  }
];

export const VECO_OUTAGES = [
  {
    "id": 100,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "15:00 - 16:00",
    "areaEn": "Cebu City (Mambaling) / Talisay City (San Roque, Tangke)",
    "areaJa": "セブ市 (マンバリング) / タリサイ市 (サンロケ, タンケ)",
    "affectedEn": "Portion of Cebu City: Mambaling \n Portion of Talisay City: San Roque, Tangke",
    "affectedJa": "セブ市の一部エリア: マンバリング \n タリサイ市の一部エリア: サンロケ, タンケ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 101,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "16:00 - 17:00",
    "areaEn": "Cebu City (Adlaon, Agsungot...) / Mandaue City (Cabancalan, Canduman)",
    "areaJa": "セブ市 (アドロン, アグスンゴット...) / マンダウエ市 (カバンカラン, カンドゥマン)",
    "affectedEn": "Portion of Cebu City: Adlaon, Agsungot, Apas, Bacayan, Binaliw, Budlaan, Cambinocot, Day-as, Guba, Kalubihan, Kamagayan, Lahug, Lanipga, Lusaran, Luz, Mabini, Pahina Central, Panas, Pari-an, Paril, Pit-os, Pulangbato, Sambag 1, San Jose, Sto. Nino, T. Padilla, Talamban \n Portion of Mandaue City: Cabancalan, Canduman",
    "affectedJa": "セブ市の一部エリア: アドロン, アグスンゴット, アパス, バカヤン, ビナリウ, ブドラーン, カンビノコット, デイアズ, グバ, カルビハン, カマガヤン, ラハグ, ラニプガ, ルサラン, ルス, マビニ, パヒナ セントラル, パナス, パリアン, パリル, ピオス, プランバト, サンバッグ 1, サンノゼ, スト。ニノ, T. パディラ, タランバン \n マンダウエ市の一部エリア: カバンカラン, カンドゥマン",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 102,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "17:00 - 18:00",
    "areaEn": "Cebu City (Calamba, Camputhaw...)",
    "areaJa": "セブ市 (カランバ, カンピュソー...)",
    "affectedEn": "Portion of Cebu City: Calamba, Camputhaw, Capitol Site, Cogon Ramos, Day-as, Guadalupe, Hipodromo, Labangon, Lorega, Sta. Cruz, T.Padilla, Zapatera",
    "affectedJa": "セブ市の一部エリア: カランバ, カンピュソー, 国会議事堂跡, コゴン・ラモス, デイアズ, グアダルーペ, ヒポドロモ, ラバンゴン, ロレガ, 駅クルーズ, T.パディラ, サパテラ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 103,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "18:00 - 19:00",
    "areaEn": "Cebu City (Basak San Nicolas, Bulacao...) / Liloan (Catarman, Cotcot...) / Mandaue City (Subangdaku) / Talisay City (Kinasang-an, San Roque)",
    "areaJa": "セブ市 (バサク・サン・ニコラス, ブラカオ...) / リロアン (カタルマン, コットコット...) / マンダウエ市 (スバンダク) / タリサイ市 (鬼南山庵, サンロケ)",
    "affectedEn": "Portion of Cebu City: Basak San Nicolas, Bulacao, Carreta, Cebu Business Park, Cogon Pardo, Hipodromo, Inayawan, Kasambagan, Mabolo, Mambaling, North Reclamation Area, Poblacion Pardo, Reclamation Area, San Antonio, San Jose, San Roque, Subangdaku, Tejero, Tinago \n Portion of Liloan: Catarman, Cotcot, Jubay, Poblacion, Tayud \n Portion of Mandaue City: Subangdaku \n Portion of Talisay City: Kinasang-an, San Roque",
    "affectedJa": "セブ市の一部エリア: バサク・サン・ニコラス, ブラカオ, カレタ, セブ ビジネス パーク, コゴン・パルド, ヒポドロモ, 伊那谷湾, カサンバガン, マボロ, マンバリング, 北干拓地, ポブラシオン・パルド, 埋立地域, サンアントニオ, サンノゼ, サンロケ, スバンダク, テヘロ, ティナゴ \n リロアンの一部エリア: カタルマン, コットコット, ジュベイ, ポブラシオン, タユド \n マンダウエ市の一部エリア: スバンダク \n タリサイ市の一部エリア: 鬼南山庵, サンロケ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 104,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "19:00 - 20:00",
    "areaEn": "Cebu City (Bacayan, Camputhaw...) / City of Naga (Alpaco, Balirong...) / Consolacion (Cansaga, Casili...) / Liloan (Calero) / Mandaue City (Basak, Cabancalan...) / Minglanilla (Biasong: Cansojong, Camp 8...) / Talisay City (Dumlog, Mohon...)",
    "areaJa": "セブ市 (バカヤン, カンピュソー...) / ナガ市 (アルパコ, バリロン...) / コンソラシオン (カンサガ, カシリ...) / リロアン (カレロ) / マンダウエ市 (バサック, カバンカラン...) / ミングラニラ (カンソジョン, キャンプ8...) / タリサイ市 (ダムログ, モホン...)",
    "affectedEn": "Portion of Cebu City: Bacayan, Camputhaw, Capitol Site, Guadalupe, Kalunasan, Sapangdaku, Talamban \n Portion of City of Naga: Alpaco, Balirong, Cantao-An, Cogon, Colon, Inayagan, Jaguimit, Lutac, North Poblacion, South Poblacion, Tangke, Tinaan, Uling \n Portion of Consolacion: Cansaga, Casili, Jugan, Nangka, Pagsabungan, Pitogo, Poblacion Occidental, Poblacion Oriental, Tawason, Tayud, Tugbungan \n Portion of Liloan: Calero \n Portion of Mandaue City: Basak, Cabancalan, Canduman, Cubacub, Jagobiao, Labogon, Tabok \n Portion of Minglanilla: Biasong: Cansojong, Camp 8, Guindaruhan, Lanas, Lataban, Linao, Lipata, Mayana, Pakigne, Panas, Pangdan, Poblacion, Tagjaguimit, Tunghaan, Tungkil, Tungkop, Tuyan \n Portion of Talisay City: Dumlog, Mohon, Pooc, San Isidro",
    "affectedJa": "セブ市の一部エリア: バカヤン, カンピュソー, 国会議事堂跡, グアダルーペ, カルナサン, サパンダク, タランバン \n ナガ市の一部エリア: アルパコ, バリロン, カンタオアン, コゴン, 結腸, イナヤガン, ジャギミット, ルタック, 北ポブラシオン, 南ポブラシオン, タンケ, ティナーン, ウリン \n コンソラシオンの一部エリア: カンサガ, カシリ, ジュガン, ナンカ, パグサブンガン, ピトーゴ, ポブラシオン オクシデンタル, ポブラシオン オリエンタル, タワソン, タユド, トゥグブンガン \n リロアンの一部エリア: カレロ \n マンダウエ市の一部エリア: バサック, カバンカラン, カンドゥマン, キュバキュブ, ジャゴビアオ, ラボゴン, タボク \n ミングラニラの一部エリア: カンソジョン, キャンプ8, ギンダルハン, ラナス, ラタバン, リナオ, リパタ, マヤナ, パキーニ, パナス, パンダン, ポブラシオン, タジャギミット, トゥンハーン, トゥンキル, トゥンコップ, トゥヤン \n タリサイ市の一部エリア: ダムログ, モホン, プーク, サン・イシドロ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 105,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "20:00 - 21:00",
    "areaEn": "Cebu City (Apas, Banilad...)",
    "areaJa": "セブ市 (アパス, バニラッド...)",
    "affectedEn": "Portion of Cebu City: Apas, Banilad, Kasambagan, Lahug, San Antonio. EARLIER ADVISORY:",
    "affectedJa": "セブ市の一部エリア: アパス, バニラッド, カサンバガン, ラハグ, サンアントニオ。以前のアドバイス:",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 106,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "21:00 - 22:00",
    "areaEn": "Cebu City (Duljo Fatima, Ermita...)",
    "areaJa": "セブ市 (ドゥルジョ ファティマ, エルミタ...)",
    "affectedEn": "Portion of Cebu City: Duljo Fatima, Ermita, Mambaling, Pahina Central, Pasil, San Nicolas Proper, San Roque, Sawang Calero, Suba, Tisa. Please note that schedules may change depending on actual grid conditions, cooperation as we work to support grid stability, further directives from NGCP. We continue to monitor the situation, will provide updates should there be any changes to the schedule. We appreciate your patience",
    "affectedJa": "セブ市の一部エリア: ドゥルジョ ファティマ, エルミタ, マンバリング, パヒナ セントラル, パシル, サン・ニコラス・プロパー, サンロケ, サワン・カレロ, スバ, ティサ。実際のグリッド状況によりスケジュールが変更される場合がありますのでご了承ください, 送電網の安定性をサポートするために協力してください, NGCP からのさらなる指示。引き続き状況を監視していきます, スケジュールに変更があった場合は更新情報を提供します。ご理解のほどよろしくお願いいたします",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  }
];
