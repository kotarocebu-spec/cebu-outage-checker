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
    "date": "2026/06/20",
    "day": "Sat",
    "time": "08:00 - 09:00",
    "areaEn": "Cebu City (Other Areas)",
    "areaJa": "セブ市 (その他エリア)",
    "affectedEn": "Portion of Adlaon, Sudlon II, Tabunan, Tagba-o & Taptap, Cebu City, along portions of Cebu Transcentral Highway and Sister Cities Drive.",
    "affectedJa": "セブ市のアドロン、スドロン II、タブナン、タグバオ、タプタップの一部、セブ横断高速道路と姉妹都市ドライブの一部に沿ったエリア。",
    "detailsEn": "To ensure the safety of personnel working on the line.",
    "detailsJa": "ラインで作業する人の安全を確保するため。"
  },
  {
    "id": 101,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "08:00 - 17:00",
    "areaEn": "Cebu City (Sister Cities Drive. Portion of Adlaon & Taptap)",
    "areaJa": "セブ市 (姉妹都市ドライブ。アドロン＆タプタップの一部)",
    "affectedEn": "Portion of Adlaon, Tagba-o & Taptap Cebu City, along portions of Sister Cities Drive. Portion of Adlaon & Taptap, Cebu City, along portions of Sister Cities Drive.",
    "affectedJa": "アドラオン、タグバオ、タプタップ セブ シティの一部、姉妹都市ドライブの一部沿い。セブ市のアドロンとタップタップの一部、姉妹都市ドライブの一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Adlaon, Tagba-o & Taptap by facilitating primary line maintenance. Adlaon & Taptap by facilitating primary line maintenance.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。 Adlaon、Tagba-o、Taptap の一次回線のメンテナンスを容易にします。 Adlaon と Taptap により、一次回線のメンテナンスが容易になります。"
  },
  {
    "id": 102,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "08:00 - 16:00",
    "areaEn": "Mandaue City (Subangdaku)",
    "areaJa": "マンダウエ市 (スバンダク)",
    "affectedEn": "Portion of Subangdaku, Mandaue City, along portion of M. Logarta Avenue.",
    "affectedJa": "マンダウエ市スバンダクの一部、M. ロガルタ アベニューの一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Subangdaku by facilitating installation of distribution transformer and extension of primary lines (line stringing).",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。配電変圧器の設置と一次線の延長（線引き）を容易にすることでスバンダクを実現します。"
  },
  {
    "id": 103,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "09:00 - 11:00",
    "areaEn": "Cebu City (Banilad and Busay)",
    "areaJa": "セブ市 (バニラッドとブサイ)",
    "affectedEn": "⏰ 9:00 AM to 11:00 AM (2 hours)\n• Portions of Banilad, Budlaan, and Busay along Paseo Don Sergio Road, Paseo Elizabeth Road, Paseo John-John, and Paseo Salud Road. ⏰ 1:00 PM to 2:00 PM (1 hour)\n• Portions of Banilad and Busay, Cebu City, along portions of Paseo Yvette. ⏰ 2:00 PM to 3:00 PM (1 hour)\n• Portions of Banilad and Busay, along portions of Paseo Rodolfo. ⏰ 3:00 PM to 4:00 PM (1 hour)\n• Portions of Banilad and Busay, along portions of Paseo Estefania. ⏰ 4:00 PM to 5:00 PM (1 hour)\n• Portions of Banilad and Busay, along portions of Paseo Anabelle. ⚠",
    "affectedJa": "⏰ 午前9時から午前11時まで（2時間）\n• パセオ・ドン・セルジオ・ロード、パセオ・エリザベス・ロード、パセオ・ジョン・ジョン、パセオ・サルード・ロード沿いのバニラッド、ブドラーン、ブサイの一部。 ⏰ 午後1時から午後2時まで（1時間）\n• セブ市バニラッドとブサイの一部、パセオ イベットの一部沿い。 ⏰ 午後 2 時から午後 3 時まで (1 時間)\n• バニラドとブサイの一部、パセオ ロドルフォの一部沿い。 ⏰ 午後 3 時から午後 4 時まで (1 時間)\n• バニラッドとブサイの一部、パセオ エステファニアの一部。 ⏰ 午後4時から午後5時まで（1時間）\n• バニラッドとブサイの一部、パセオ アナベルの一部沿い。 ⚠",
    "detailsEn": "Rotational Brownouts / Grid Alert",
    "detailsJa": "循環停電 / グリッドアラート"
  },
  {
    "id": 104,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "14:00 - 15:00",
    "areaEn": "Cebu City (Banilad, Kasambagan...) / Mandaue City (Subangdaku, Tipolo)",
    "areaJa": "セブ市 (バニラッド, カサンバガン...) / マンダウエ市 (スバンダク, ティポロ)",
    "affectedEn": "Portion of Cebu City: Banilad, Kasambagan, Mabolo \n Portion of Mandaue City: Subangdaku, Tipolo",
    "affectedJa": "セブ市の一部エリア: バニラッド, カサンバガン, マボロ \n マンダウエ市の一部エリア: スバンダク, ティポロ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 105,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "15:00 - 16:00",
    "areaEn": "Cebu City (Ermita, Mambaling...) / Liloan (Cabadiangan, Cotco...)",
    "areaJa": "セブ市 (エルミタ, マンバリング...) / リロアン (カバディアンガン, コットコ...)",
    "affectedEn": "Portion of Cebu City: Ermita, Mambaling, Pahina Central, Pasil, San Nicolas Proper, San Roque, Sawang Calero, Suba, Tisa \n Portion of Liloan: Cabadiangan, Cotco, Jubay, Lataban, Mulao, Poblacion, San Vicente, Sta. Cruz, Yati",
    "affectedJa": "セブ市の一部エリア: エルミタ, マンバリング, パヒナ セントラル, パシル, サン・ニコラス・プロパー, サンロケ, サワン・カレロ, スバ, ティサ \n リロアンの一部エリア: カバディアンガン, コットコ, ジュベイ, ラタバン, ムラオ, ポブラシオン, サンビセンテ, 駅クルーズ, ヤティ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 106,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "16:00 - 17:00",
    "areaEn": "Cebu City (Camputhaw, Capitol Site...) / Consolacion (Cansaga, Jugan...) / Liloan (Lataban, Pitogo...)",
    "areaJa": "セブ市 (カンピュソー, 国会議事堂跡...) / コンソラシオン (カンサガ, ジュガン...) / リロアン (ラタバン, ピトーゴ...)",
    "affectedEn": "Portion of Cebu City: Camputhaw, Capitol Site, Guadalupe, Kalunasan, Sapangdaku \n Portion of Consolacion: Cansaga, Jugan, Lamac, Poblacion Oriental, San Roque, San Vicente, Sta. Cruz \n Portion of Liloan: Lataban, Pitogo, Tilhaong, Yati",
    "affectedJa": "セブ市の一部エリア: カンピュソー, 国会議事堂跡, グアダルーペ, カルナサン, サパンダク \n コンソラシオンの一部エリア: カンサガ, ジュガン, ラマック, ポブラシオン オリエンタル, サンロケ, サンビセンテ, 駅クルーズ \n リロアンの一部エリア: ラタバン, ピトーゴ, ティルハオン, ヤティ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 107,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "17:00 - 18:00",
    "areaEn": "City of Naga (Alpaco, Balirong...) / Mandaue City (Cabancalan, Canduman...) / Minglanilla (Camp 8, Guindaruhan...) / Other (Balud, Greenhills...)",
    "areaJa": "ナガ市 (アルパコ, バリロン...) / マンダウエ市 (カバンカラン, カンドゥマン...) / ミングラニラ (キャンプ8, ギンダルハン...) / Other (バルド, グリーンヒルズ...)",
    "affectedEn": "Portion of City of Naga: Alpaco, Balirong, Cantao-An, Cogon, Colon, Inayagan, Jaguimit, Lutac, North Poblacion, South Poblacion, Tangke, Tinaan, Uling \n Portion of Mandaue City: Cabancalan, Canduman, Casuntingan, Maguikay, Pagsabungan, Tingub, Tingug \n Portion of Minglanilla: Camp 8, Guindaruhan, Lanas, Lataban, Mayana, Panas, Pangdan, Tagjaguimit, Tunghaan, Tungkop, Tuyan \n Portion of Other: Balud, Greenhills, Lantawan, Panadtaran, Sangat, Tonggo",
    "affectedJa": "ナガ市の一部エリア: アルパコ, バリロン, カンタオアン, コゴン, 結腸, イナヤガン, ジャギミット, ルタック, 北ポブラシオン, 南ポブラシオン, タンケ, ティナーン, ウリン \n マンダウエ市の一部エリア: カバンカラン, カンドゥマン, カサンティンガン, マグカイ, パグサブンガン, ティンガブ, ティンググ \n ミングラニラの一部エリア: キャンプ8, ギンダルハン, ラナス, ラタバン, マヤナ, パナス, パンダン, タジャギミット, トゥンハーン, トゥンコップ, トゥヤン \n Otherの一部エリア: バルド, グリーンヒルズ, ランタワン, パナタラン, サンガット, トンゴ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 108,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "18:00 - 19:00",
    "areaEn": "Cebu City (Banilad, Talamban) / Mandaue City (Bakilid, Cabancalan...) / Minglanilla (Biasong, Cansojong...) / Talisay City (Dumlog, Mohon...)",
    "areaJa": "セブ市 (バニラッド, タランバン) / マンダウエ市 (ベイキリッド, カバンカラン...) / ミングラニラ (ビアソン, カンソジョン...) / タリサイ市 (ダムログ, モホン...)",
    "affectedEn": "Portion of Cebu City: Banilad, Talamban \n Portion of Mandaue City: Bakilid, Cabancalan, Casuntingan, Ibabao-Estancia, Maguikay, Paknaan, Tabok \n Portion of Minglanilla: Biasong, Cansojong, Linao, Lipata, Pakigne, Poblacion, Tungkil \n Portion of Talisay City: Dumlog, Mohon, Pooc, San Isidro",
    "affectedJa": "セブ市の一部エリア: バニラッド, タランバン \n マンダウエ市の一部エリア: ベイキリッド, カバンカラン, カサンティンガン, イババオ-エスタンシア, マグカイ, パクナン, タボク \n ミングラニラの一部エリア: ビアソン, カンソジョン, リナオ, リパタ, パキーニ, ポブラシオン, トゥンキル \n タリサイ市の一部エリア: ダムログ, モホン, プーク, サン・イシドロ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 109,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "19:00 - 20:00",
    "areaEn": "Cebu City (Apas, Banilad...) / Minglanilla (Cadulawan, Calajo-an...) / Talisay City (Lawaan I, Lawaan II...)",
    "areaJa": "セブ市 (アパス, バニラッド...) / ミングラニラ (カドゥラワン, カラジョアン...) / タリサイ市 (ラワーン I, ラワーン II...)",
    "affectedEn": "Portion of Cebu City: Apas, Banilad, Basak Pardo, Basak San Nicolas, Buhisan, Bulacao, Kasambagan, Kinasang-an Pardo, Lahug, Pardo, Poblacion Pardo, Punta Princesa, Quiot, Quiot Pardo, San Roque \n Portion of Minglanilla: Cadulawan, Calajo-an, Camp 7, Camp 8, Cuanos, Linao, Lipata, Manduang, Pakigne, Tubod, Tunghaan, Vito \n Portion of Talisay City: Lawaan I, Lawaan II, Lawaan III, Ward 1, Ward 3, Ward 4",
    "affectedJa": "セブ市の一部エリア: アパス, バニラッド, バサック・パルド, バサク・サン・ニコラス, ぶひさん, ブラカオ, カサンバガン, キナサンアン パルド, ラハグ, パルド, ポブラシオン・パルド, プンタ プリンセサ, クイオット, クイオット・パルド, サンロケ \n ミングラニラの一部エリア: カドゥラワン, カラジョアン, キャンプ 7, キャンプ8, クアノス, リナオ, リパタ, マンドゥアン, パキーニ, トゥボッド, トゥンハーン, ヴィト \n タリサイ市の一部エリア: ラワーン I, ラワーン II, ラワーンⅢ, 1区, 3区, 4区",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 110,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "20:00 - 21:00",
    "areaEn": "Cebu City (Camputhaw, Capitol Site...) / Talisay City (San Roque, Tangke)",
    "areaJa": "セブ市 (カンピュソー, 国会議事堂跡...) / タリサイ市 (サンロケ, タンケ)",
    "affectedEn": "Portion of Cebu City: Camputhaw, Capitol Site, Cogon Ramos, Guadalupe, Kalubihan, Kalunasan, Lahug, Lorega, Mambaling, Zapatera \n Portion of Talisay City: San Roque, Tangke",
    "affectedJa": "セブ市の一部エリア: カンピュソー, 国会議事堂跡, コゴン・ラモス, グアダルーペ, カルビハン, カルナサン, ラハグ, ロレガ, マンバリング, サパテラ \n タリサイ市の一部エリア: サンロケ, タンケ",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 111,
    "type": "electricity",
    "date": "2026/06/20",
    "day": "Sat",
    "time": "21:00 - 22:00",
    "areaEn": "Cebu City (Calamba, Kalubihan...)",
    "areaJa": "セブ市 (カランバ, カルビハン...)",
    "affectedEn": "Portion of Cebu City: Calamba, Kalubihan, Labangon, Punta Princesa, Sambag 1, San Jose, Tisa. Please note that schedules may change depending on actual grid conditions, cooperation as we work to support grid stability, further directives from NGCP. We continue to monitor the situation, will provide updates should there be any changes to the schedule. We appreciate your patience",
    "affectedJa": "セブ市の一部エリア: カランバ, カルビハン, ラバンゴン, プンタ プリンセサ, サンバッグ 1, サンノゼ, ティサ。実際のグリッド状況によりスケジュールが変更される場合がありますのでご了承ください, 送電網の安定性をサポートするために協力してください, NGCP からのさらなる指示。引き続き状況を監視していきます, スケジュールに変更があった場合は更新情報を提供します。ご理解のほどよろしくお願いいたします",
    "detailsEn": "⚠️ [CONDITIONAL - RED ALERT] Scheduled power reduction due to limited grid generation capacity.",
    "detailsJa": "⚠️ 【赤アラート時のみ実施（可能性あり）】 送電容量不足に伴う計画的な供給制限（輪番停電）です。"
  },
  {
    "id": 112,
    "type": "electricity",
    "date": "2026/06/21",
    "day": "Sun",
    "time": "08:00 - 17:00",
    "areaEn": "Cebu City (Other Areas)",
    "areaJa": "セブ市 (その他エリア)",
    "affectedEn": "Portion of Binaliw, Pit-os & Pulangbato, Cebu City, along portions of A. Minoza Street, Miramonte–Riverdale Road, Tapuko Road, and Binaliw Road, as well as the subdivisions of Camella Miramonte and Camella Riverdale.",
    "affectedJa": "セブ市ビナリウ、ピオス、プランバトの一部、A. ミノザ ストリート、ミラモンテ - リバーデール ロード、タプコ ロード、ビナリウ ロードの一部、およびカメラ ミラモンテとカメラ リバーデールの分譲地。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Binaliw, Pit-os & Pulangbato by facilitating primary line maintenance and primary line upgrading.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。プライマリ ラインのメンテナンスとプライマリ ラインのアップグレードを容易にすることで、ビナリウ、ピオス、プランバトを実現します。"
  },
  {
    "id": 113,
    "type": "electricity",
    "date": "2026/06/23",
    "day": "Tue",
    "time": "09:00 - 13:00",
    "areaEn": "Cebu City (the road leading to Dagongdong Basketball Court. Portion of Mambaling)",
    "areaJa": "セブ市 (大公洞バスケットボール場に続く道。マンバリングの一部)",
    "affectedEn": "Portion of Garing, Panas & Panoypoy, Consolacion, along portions of the road leading to Dagongdong Basketball Court. Portion of Mambaling, Cebu City, along portions of Natalio B. Bacalso Avenue. Portion of Pahina Central, along portions of Sanciangko Street and A. Borromeo Street. Portion of San Jose, along portions of San Jose Road and Fresia Road.",
    "affectedJa": "ガリング、パナス、パノイポイ、コンソラシオンの一部、大公洞バスケットボールコートに通じる道路の一部沿い。セブ市マンバリングの一部、ナタリオ B. バカルソ アベニューの一部沿い。パヒナ セントラルの一部、サンチャンコ ストリートと A. ボロメオ ストリートの一部沿い。サンノゼの一部、サンノゼ ロードとフレシア ロードの一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Garing, Panas & Panoypoy by facilitating primary line maintenance. Mambaling by facilitating replacement of rotten pole. Pahina Central by facilitating tapping of service entrance wire. San Jose by facilitating reconstruction of primary lines.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。一次回線のメンテナンスを容易にすることで、Garing、Panas、Panoypoy を実現します。腐ったポールの交換を容易にすることでマンバリングを防止します。引き込み線の盗聴を容易にするパヒナ・セントラル。サンノゼの幹線鉄道の再建を促進する。"
  },
  {
    "id": 114,
    "type": "electricity",
    "date": "2026/06/23",
    "day": "Tue",
    "time": "09:00 - 14:00",
    "areaEn": "City of Naga (Other Areas)",
    "areaJa": "ナガ市 (その他エリア)",
    "affectedEn": "Portion of Tuyan, City of Naga, along portions of Cebu South Road near Judge A. Larumbre Street.",
    "affectedJa": "ナガ市トゥヤンの一部、ジャッジ A. ラランブル ストリート近くのセブ サウス ロード沿いの一部。",
    "detailsEn": "To increase the capacity of the distribution system serving Brgy. Tuyan by facilitating upgrading of distribution transformer.",
    "detailsJa": "Brgy にサービスを提供する配電システムの容量を増やすため。 Tuyan は配電変圧器のアップグレードを促進します。"
  },
  {
    "id": 115,
    "type": "electricity",
    "date": "2026/06/23",
    "day": "Tue",
    "time": "09:00 - 17:00",
    "areaEn": "Consolacion (Casili)",
    "areaJa": "コンソラシオン (カシリ)",
    "affectedEn": "Portion of Casili, Consolacion, along portion of Upper Casili Street. Portion of Lagtang, Talisay City, along portion of Molave Ext Street.",
    "affectedJa": "コンソラシオンのカシーリの一部、アッパー カシーリ ストリートの一部沿い。タリサイ市ラグタンの一部、モラベ エクスト ストリートの一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Casili by facilitating installation of distribution transformer and installation of primary pole. Lagtang by facilitating replacement of primary pole.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。配電変圧器の設置と一次極の設置を容易にすることでCasiliを実現します。ラグタンにより一次ポールの交換が容易になります。"
  },
  {
    "id": 116,
    "type": "electricity",
    "date": "2026/06/23",
    "day": "Tue",
    "time": "09:00 - 15:00",
    "areaEn": "Liloan (Jubay)",
    "areaJa": "リロアン (ジュベイ)",
    "affectedEn": "Portion of Jubay, Liloan, along portions of the road leading to Cloud of Glory Prayer Mountain.",
    "affectedJa": "リローンのジュベイの一部、クラウド オブ グローリー プレイヤー マウンテンに通じる道路の一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Jubay by facilitating installation of primary pole.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。主柱の設置を容易にすることで Jubay を実現します。"
  },
  {
    "id": 117,
    "type": "electricity",
    "date": "2026/06/25",
    "day": "Thu",
    "time": "09:00 - 12:00",
    "areaEn": "Liloan (San Vicente)",
    "areaJa": "リロアン (サンビセンテ)",
    "affectedEn": "Portion of San Vicente, Liloan, along portions of Aguinaldo Street and the road leading to San Vicente Barangay Hall. Portion of West Poblacion, City of Naga, along portions of San Francisco Street, Mejia Street, and Gomez Street. Portion of Casuntingan & Maguikay, Mandaue City, along M. Ceniza St., M. Ceniza Ext., B.C. Albano St.",
    "affectedJa": "リローンのサン ビセンテの一部、アギナルド ストリートの一部とサン ビセンテ バランガイ ホールに通じる道路沿い。ナガ市西ポブラシオンの一部、サンフランシスコ通り、メヒア通り、ゴメス通りの一部沿い。マンダウエ市カスンティンガンとマグイカの一部、M. Ceniza St.、M. Ceniza Ext.、BC 沿いアルバーノ ストリート",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. San Vicente by facilitating installation of secondary lines. West Poblacion by facilitating reconstruction of primary lines. Casuntingan & Maguikay by facilitating installation of distribution transformer and installation of primary pole.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。サン ビセンテの二次回線の設置を容易にする。西ポブラシオンの主要路線の再建を促進する。カスンティンガンとマグイカイでは、配電変圧器の設置と一次極の設置が容易になります。"
  },
  {
    "id": 118,
    "type": "electricity",
    "date": "2026/06/27",
    "day": "Sat",
    "time": "08:00 - 16:00",
    "areaEn": "Cebu City (Zapatera)",
    "areaJa": "セブ市 (サパテラ)",
    "affectedEn": "Portion of Zapatera, Cebu City, along portions of Sikatuna Street, Alcohol Street, Creekside Street, General and Sepulveda Street.",
    "affectedJa": "セブ市ザパテラの一部、シカトゥナ ストリート、アルコール ストリート、クリークサイド ストリート、ジェネラル ストリート、セプルベダ ストリートの一部に沿ったエリア。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Zapatera by by facilitating extension of primary lines (line stringing).",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。 Zapatera は、プライマリ ラインの拡張 (ライン ストリング) を容易にすることによって行います。"
  }
];
