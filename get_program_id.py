# -*- coding: utf-8 -*-

import csv
import datetime
import mysql.connector
import ezslack
import hiddenInfo

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

slack = ezslack.Slack(url=hiddenInfo.slack_hook,username="プログラム取得ジョブ")
new_program_count = 0

try:
    with open(r"Q:\Program\spo\program.csv","r",encoding="utf-8_sig") as f:
    # with open(r"program.csv","r",encoding="utf-8_sig") as f:
        program_data = csv.reader(f)

        for row in program_data:
            try:
                base_date = datetime.datetime.strptime(target_year_query,"%Y-%m-%d")
                target_date = datetime.datetime.strptime(row[9],"%Y-%m-%d")
            except:
                pass
            if(row[1] == "テレビアニメーション" and target_date >= base_date):
                #DB接続
                conn = mysql.connector.connect(user=hiddenInfo.db_user, password=hiddenInfo.db_password, host=hiddenInfo.db_host, database=hiddenInfo.db_database)
                cur = conn.cursor(buffered=True,dictionary=True)
                #そのIDがあれば1を返す
                check_list = "SELECT EXISTS (SELECT * FROM program_list WHERE program_no = %s);"
                chk_no = (row[0],)
                cur.execute(check_list,chk_no)
                register_flag = list(cur.fetchone().values())[0]

                #登録されていない場合に実行
                if(register_flag != 1):
                    new_program_count += 1
                    print(row[0] + "," + row[3] + "," + row[4] + "," + row[9])
                    query = "INSERT INTO program_list (program_no,anime_title,anime_title_kana,release_year) VALUES (%s,%s,%s,%s);"
                    data = (row[0],row[3],row[4],row[9],)
                    cur.execute(query, data)
                cur.close()
                conn.commit()
        message_text = "番組CSVの情報抽出ジョブが実行されました．\n```検索条件：{}\n新規登録数：{}```".format(target_year_query,new_program_count)
        slack.send(text=message_text,icon_emoji=":tv:")
except:
    error_message_text = "番組CSVの情報抽出に失敗しました"
    slack.send(text=error_message_text,icon_emoji=":x:")