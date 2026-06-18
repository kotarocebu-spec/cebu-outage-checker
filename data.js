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
  },
  {
    "id": 107,
    "type": "electricity",
    "date": "2026/06/19",
    "day": "Fri",
    "time": "22:00 - 06/20 (Sat) 04:00",
    "areaEn": "Cebu City (Camputhaw)",
    "areaJa": "セブ市 (カンピュソー)",
    "affectedEn": "Portion of Basak, Centro, Paknaan & Tabok, Mandaue City, along portion of Labogon Road, including portions of Sitios Caimito, Canumay, Chicos, Cumpang, Kalabasa, Kamanggahan, Kasagingan, Lapyahan, Latasan, Law-O, Locus, Mabolo, Mahayahay, Pamilya, Sab-A, San Jose, Sta. Cruz, Tabay, Tuburan, & Valleriano, and Agbay Compound, Almers Compound, Baguio Compound, Deca Homes, Kimwa Compound, Ma. Antonia Village, Mafria Teresa Village, Marcelino Village, Palm Hills Subdivision, Sacred Heart Village, Sliding Hills, Tikay Compound, & Yy Compound. Portion of Camputhaw, Cebu City, along portion of N. Escario Street. Portion of Tipolo, along portions of A. Seno Extension.",
    "affectedJa": "マンダウエ市バサク、セントロ、パクナン、タボクの一部、ラボゴン通り沿いのシティオス・カイミト、カヌマイ、チコス、クンパン、カラバサ、カマンガハン、カサギンガン、ラピヤハン、ラタサン、ロー・オー、ローカス、マボロ、マハヤハイ、パミルヤ、サブ・A、サンノゼ、スタの一部を含む。クルーズ、タベイ、トゥブラン、バレリアーノ、アグベイ コンパウンド、アルマース コンパウンド、バギオ コンパウンド、デカ ホームズ、キムワ コンパウンド、マサチューセッツ州。アントニア ビレッジ、マフリア テレサ ビレッジ、マルセリーノ ビレッジ、パーム ヒルズ サブディビジョン、セイクリッド ハート ビレッジ、スライディング ヒルズ、ティカイ コンパウンド、Yy コンパウンド。セブ市カンピュソーの一部、N. エスカリオ ストリートの一部沿い。ティポロの一部、A. セノ延長の一部沿い。",
    "detailsEn": "To improve the reliability of the distribution system serving Brgy. Basak, Centro, Paknaan & Tabok by facilitating installation of primary lines and installation of primary pole and rerouting of primary lines. Camputhaw by facilitating reconstruction of primary lines. Tipolo by facilitating isolation of equipment due to safety concern.",
    "detailsJa": "Brgy にサービスを提供する配信システムの信頼性を向上させるため。バサク、セントロ、パクナン、タボクでは、主線の設置、主柱の設置、主線の配線変更が容易になります。主要ラインの再構築を促進することによるカンピューソー。 Tipolo は、安全上の懸念から機器の隔離を容易にします。"
  },
  {
    "id": 108,
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
    "id": 109,
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
    "id": 110,
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
    "id": 111,
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
    "id": 112,
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
    "id": 113,
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
    "id": 114,
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
    "id": 115,
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
    "id": 116,
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
    "id": 117,
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
