# -*- coding: utf-8 -*-

import csv
import mysql.connector
import datetime
import ezslack
import hiddenInfo

#検索する日付をシーズンごとにする
def season_year():
    m = datetime.datetime.now().month
    if(m >= 9):
        return(datetime.datetime.now().strftime("%Y-10-01"))
    elif(m >= 7):
        return(datetime.datetime.now().strftime("%Y-07-01"))
    elif(m >= 4):
        return(datetime.datetime.now().strftime("%Y-04-01"))
    elif(m >= 1):
        return(datetime.datetime.now().strftime("%Y-01-01"))

target_year_query = season_year()
# TARGET_DATE = "2010-01-01"
new_song_count = 0

slack = ezslack.Slack(url=hiddenInfo.slack_hook,username="曲の抽出取得ジョブ")

try:
    conn = mysql.connector.connect(user=hiddenInfo.db_user, password=hiddenInfo.db_password, host=hiddenInfo.db_host, database=hiddenInfo.db_database)
    cur = conn.cursor(buffered=True)
except:
    print("データベース接続エラー")

#プログラムリストのテーブルから番組IDを取得する
get_program_id_query = "SELECT * FROM `program_list` WHERE release_year > %s;"
insert_date = (target_year_query,)
cur.execute(get_program_id_query,insert_date)

try:
    for program_row in cur.fetchall():
        with open(r"Q:\Program\spo\anison.csv","r",encoding="utf-8_sig") as f:
            song_data = csv.reader(f)
            header = next(song_data)

            for anison_csv in song_data:
                if(int(anison_csv[0]) == program_row[0]):
                    cur2 = conn.cursor(buffered=True)

                    #重複チェッククエリ
                    check_program_no_query = "SELECT EXISTS (SELECT * FROM song_list WHERE program_no = %s);"
                    check_song_name_query = "SELECT EXISTS (SELECT * FROM song_list WHERE song_name = %s);"
                    chk_no = (program_row[0],)
                    chk_song = (anison_csv[6],)
                    cur2.execute(check_program_no_query,chk_no)
                    cur2.execute(check_song_name_query,chk_song)
                    register_flag = cur2.fetchone()[0]

                    #登録されていない場合のみチェック
                    #プログラムNO+曲名がない場合のみ実行
                    if(register_flag != 1 and chk_song != 1):
                        new_song_count += 1
                        # print("---ID:{},{},{},{},{}".format(program_row[0],anison_csv[2],anison_csv[3],anison_csv[6],anison_csv[7]))
                        insert_anison_query = "INSERT INTO song_list (program_no,anime_title,timing,song_name,artist) VALUES (%s,%s,%s,%s,%s);"
                        insert_song_data = (int(program_row[0]),anison_csv[2],anison_csv[3],anison_csv[6],anison_csv[7],)
                        cur.execute(insert_anison_query,insert_song_data)
        cur2.close()
    cur.close()
    conn.commit()
    message_text = "曲の抽出ジョブが実行されました．\n```検索条件：{}\n新規登録数：{}```".format(target_year_query,new_song_count)
    slack.send(text=message_text,icon_emoji=":notes:")
except:
    error_message_text = "曲の抽出ジョブに失敗しました．\n```検索条件：{}\n新規登録数：{}```".format(target_year_query,new_song_count)
    slack.send(text=error_message_text,icon_emoji=":x:")