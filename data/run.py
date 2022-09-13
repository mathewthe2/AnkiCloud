# create db
import sqlite3
import json

sqlite3.dbapi2.converters['DATETIME'] = sqlite3.dbapi2.converters['TIMESTAMP']

con = sqlite3.connect("data.db")
# con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE cards(updated, added, deckName, modelName, fields, media, tags, options)")

data =[
    [
        "2022-01-02 23:45:00", # last updated, for reference only
        False, # added
        "Japanese",   # deck
        "Japanese Anime", # model
        json.dumps({
            'Word': '挑発',
            'Kana': 'ちょうはつ',
            'Meaning': 'provocation',
            'Sentence': '乗るつもりか　敵の挑発に',
            'Sentence Translation': 'Do you plan on accepting the enemy\'s challenge?'
         }), 
        json.dumps({
            "audio": [{
                "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=挑発&kana=ちょうはつ",
                "filename": "yomichan_ちょうはつ_挑発.mp3",
                "fields": [
                    "Picture"
                ]
            }],
            "picture": [{
                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/A_black_cat_named_Tilly.jpg/220px-A_black_cat_named_Tilly.jpg",
                "filename": "black_cat.jpg",
                "skipHash": "8d6e4646dfae812bf39651b59d7429ce",
                "fields": [
                    "Audio"
                ]
            }]
        }),
        json.dumps([]), # tags
        json.dumps([]) # options
    ],
    [
        "2022-01-03 23:45:00",  # last updated
        False, # added
        'Japanese', # deck
        'Japanese Anime', # model
        json.dumps({ 
            'Word': '一刀両断',
            'Kana': 'いっとうりょうだん',
            'Meaning': 'cutting in two, taking decisive action'
        }), 
        json.dumps({}), # media
        json.dumps([]), # tags
        json.dumps([]) # options
    ],
]
cur.executemany("INSERT INTO cards VALUES (?,?,?,?,?,?,?,?)", data)

con.commit()

for row in cur.execute("SELECT deckName, fields, tags FROM cards ORDER BY updated"):
    print(row)