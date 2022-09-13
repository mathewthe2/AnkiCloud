# create db
import sqlite3
import json

sqlite3.dbapi2.converters['DATETIME'] = sqlite3.dbapi2.converters['TIMESTAMP']

con = sqlite3.connect("data.db")
# con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS note;")
cur.execute("CREATE TABLE note(updated, added, deckName, modelName, fields, media, tags, options)")

data =[
    [
        "2022-01-02 23:45:00", # last updated, for reference only
        False, # added
        "Japanese",   # deck
        "Japanese Anime", # model
        json.dumps({
            'Word': '寝かす',
            'Kana': 'ねかす',
            'Meaning': 'to put to sleep',
            'Sentence': '泣く赤ちゃん寝かす よい方法とは',
            'Sentence Translation': 'Good ways to put an infant to sleep'
         }), 
        json.dumps({
            "audio": [{
                "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=寝かす&kana=ねかす",
                "filename": "yomichan_ねかす_寝かす.mp3",
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
        json.dumps({
            "allowDuplicate": True
        }) # options
    ],
    [
        "2022-01-03 23:45:00",  # last updated
        False, # added
        'Japanese', # deck
        'Japanese Anime', # model
        json.dumps({ 
            'Word': '共演',
            'Kana': 'きょうえん',
            'Meaning': 'co-starring'
        }), 
        json.dumps({}), # media
        json.dumps([]), # tags
        json.dumps({
                "allowDuplicate": True
            }) # options
    ],
]
cur.executemany("INSERT INTO note VALUES (?,?,?,?,?,?,?,?)", data)

con.commit()

for row in cur.execute("SELECT deckName, fields, tags FROM note ORDER BY updated"):
    print(row)