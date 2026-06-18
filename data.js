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
    "type": "water",
    "date": "2026/06/18",
    "day": "Thu",
    "time": "TBD / Flexible",
    "areaEn": "Cebu City (Other Areas)",
    "areaJa": "セブ市 (その他エリア)",
    "affectedEn": "EWSI, All Canduman Pumps shut-off due to unscheduled VECO rotational power . 18June, 7:54 pm - (ETC) 9:00 pm, AA: Elevated and interior parts of Canduman, Riverside, Pagsabungan, Tawason, Cubacub, Jagobiao, Mandaue City, Casili, and Ylaya, Tintay, Talamban, Cebu CityJune 18, 2026",
    "affectedJa": "EWSI、予定外の VECO 回転力により、すべての Canduman ポンプが停止します。 6月18日、午後7時54分 - (ETC)午後9時、AA: カンドゥマン、リバーサイド、パグサブンガン、タワソン、キューバク、ジャゴビアオ、マンダウエ市、カシリ、およびイラヤ、ティンタイ、タランバン、セブ市の高架部分および内部部分2026年6月18日",
    "detailsEn": "Emergency water service interruption announced by MCWD. Please store water in advance.",
    "detailsJa": "水道局（MCWD）から発表された、突発的な緊急断水情報です。現在お住まいの方は貯水などの備えを行ってください。"
  },
  {
    "id": 101,
    "type": "water",
    "date": "2026/06/18",
    "day": "Thu",
    "time": "TBD / Flexible",
    "areaEn": "Cebu City (Other Areas)",
    "areaJa": "セブ市 (その他エリア)",
    "affectedEn": "EWSI, All Canduman Pumps shut-off due to unscheduled VECO rotational power . 18June, 7:54 pm - (ETC) 9:00 pm, AA: Elevated and interior parts of Canduman, Riverside, Pagsabungan, Tawason, Cubacub, Jagobiao, Mandaue City, Casili, and Ylaya, Tintay, Talamban, Cebu City",
    "affectedJa": "EWSI、予定外の VECO 回転力により、すべての Canduman ポンプが停止します。 6月18日、午後7時54分 - (ETC)午後9時、AA: カンドゥマン、リバーサイド、パグサブンガン、タワソン、キューバク、ジャゴビアオ、マンダウエ市、カシリ、およびイラヤ、ティンテイ、タランバン、セブ市の高台および内部部分",
    "detailsEn": "Scheduled water service interruption announced by MCWD. Please store water.",
    "detailsJa": "水道局（MCWD）から発表された、計画的な断水情報です。事前の貯水や備えを推奨します。"
  },
  {
    "id": 102,
    "type": "water",
    "date": "2026/06/18",
    "day": "Thu",
    "time": "TBD / Flexible",
    "areaEn": "Mandaue City (Other Areas)",
    "areaJa": "マンダウエ市 (その他エリア)",
    "affectedEn": "EWSI, Mainline Leak Repair of 6-inch diameter pipe in P. Remedios St, corner A.S. Fortuna, Mandaue City/18Jun, 11:40am-10pm(ETR)/AA:P. Remedios St., Mandaue CityJune 18, 2026",
    "affectedJa": "EWSI、P. Remedios St、A.S.コーナーの直径6インチパイプの幹線漏れ修理フォーチュナ、マンダウエ市/6 月 18 日、午前 11 時 40 分～午後 10 時 (ETR)/AA:P. Remedios St.、マンダウエ市2026 年 6 月 18 日",
    "detailsEn": "Emergency water service interruption announced by MCWD. Please store water in advance.",
    "detailsJa": "水道局（MCWD）から発表された、突発的な緊急断水情報です。現在お住まいの方は貯水などの備えを行ってください。"
  },
  {
    "id": 103,
    "type": "water",
    "date": "2026/06/18",
    "day": "Thu",
    "time": "TBD / Flexible",
    "areaEn": "Mandaue City (Other Areas)",
    "areaJa": "マンダウエ市 (その他エリア)",
    "affectedEn": "EWSI, Mainline Leak Repair of 6-inch diameter pipe in P. Remedios St, corner A.S. Fortuna, Mandaue City/18Jun, 11:40am-10pm(ETR)/AA:P. Remedios St., Mandaue City",
    "affectedJa": "EWSI、P. Remedios St、A.S.コーナーの直径6インチパイプの幹線漏れ修理フォーチュナ、マンダウエ市/6 月 18 日、午前 11 時 40 分～午後 10 時 (ETR)/AA:P.レメディオス ストリート、マンダウエ シティ",
    "detailsEn": "Emergency water service interruption announced by MCWD. Please store water in advance.",
    "detailsJa": "水道局（MCWD）から発表された、突発的な緊急断水情報です。現在お住まいの方は貯水などの備えを行ってください。"
  },
  {
    "id": 104,
    "type": "water",
    "date": "2026/06/18",
    "day": "Thu",
    "time": "TBD / Flexible",
    "areaEn": "Other (Manual Input)",
    "areaJa": "その他（手書き入力）",
    "affectedEn": "EWSI, JE Hydro Busay and Pit-os pumps shut off due to  leak repair in their system.17JUNE, 11:16 PM - 18JUNE, 3:00 AM ( ETC ), AA:Pit-os, Tapoko, Bacayan, Tigbao, Talamban, San Jose, Kalubihan, Nasipit, Busay, Lahug, Capitol, Sambag 1&2, V. Rama, Banawa, Ramos, Zapatera, Lorega San MiguelJune 18, 2026",
    "affectedJa": "EWSI、JE Hydro Busay、および Pit-os ポンプは、システムの漏れ修理のため停止しました。6 月 17 日、午後 11 時 16 分 - 6 月 18 日、午前 3 時 (ETC)、AA: ピッツオス、タポコ、バカヤン、ティグバオ、タランバン、サンノゼ、カルビハン、ナシピット、ブサイ、ラハグ、キャピトル、サンバッグ 1&2、 V. ラマ、バナワ、ラモス、サパテラ、ロレガ サン ミゲル 2026 年 6 月 18 日",
    "detailsEn": "Emergency water service interruption announced by MCWD. Please store water in advance.",
    "detailsJa": "水道局（MCWD）から発表された、突発的な緊急断水情報です。現在お住まいの方は貯水などの備えを行ってください。"
  },
  {
    "id": 105,
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
    "id": 106,
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
    "id": 107,
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
    "id": 108,
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
    "id": 109,
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
    "id": 110,
    "type": "electricity",
    "date": "2026/06/25",
    "day": "Thu",
    "time": "09:00 - 12:00",
    "areaEn": "Liloan (San Vicente)",
    "areaJa": "リロアン (サンビセンテ)",
    "affectedEn": "Portion of San Vicente, Liloan, along portions of Aguinaldo Street and the road leading to San Vicente Barangay Hall. Portion of West Poblacion, City of Naga, along portions of San Francisco Street, Mejia Street, and Gomez Street. Portion of Casuntingan & Maguikay, Mandaue City, along M. Ceniza St., M. Ceniza Ext., B.C. Albano St.",
    "affectedJa": "リローンのサン ビセンテの一部、アギナルド ストリートの一部とサン ビセンテ バランガイ ホールに通じる道路沿い。ナガ市西ポブラシオンの一部、サンフランシスコ通り、メヒア通り、ゴメス通りの一部沿い。マンダウエ市カスンティンガンとマグイカの一部、M. Ceniza St.、M. Ceniza Ext.、BC 沿いアルバーノ ストリート",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. San Vicente by facilitating installation of secondary lines. West Poblacion by facilitating reconstruction of primary lines. Casuntingan & Maguikay by facilitating installation of distribution transformer and installation of primary pole.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。サン ビセンテの二次回線の設置を容易にする。西ポブラシオンでは、主要路線の再建が促進されます。カスンティンガンとマグイカイでは、配電変圧器の設置と一次極の設置が容易になります。"
  },
  {
    "id": 111,
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
