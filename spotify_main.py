# -*- coding: utf-8 -*-

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import datetime
import re
import mysql.connector
import hiddenInfo
import ezslack
import wordpress_post

conn = mysql.connector.connect(user=hiddenInfo.db_user, password=hiddenInfo.db_password, host=hiddenInfo.db_host, database=hiddenInfo.db_database)

regi_date_now = datetime.datetime.now().strftime("%Y-%m-%d")

regi_count = 0
slack_nofication_message = "```"
slack = ezslack.Slack(url=hiddenInfo.slack_hook,username="最新曲登録ジョブ",icon_emoji=":white_check_mark:")
track_id_wp = []

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

def db_test():

    db_anison_list = ["song_no","program_no","anime_title","timing","song_name","artist","release_year","register_flag"]

    cur = conn.cursor(buffered=True,dictionary=True)
    #クエリ発行
    #登録されているリスト取得
    query = "SELECT \
                    song_list.song_no,\
                    song_list.program_no,\
                    song_list.anime_title,\
                    song_list.timing,\
                    song_list.song_name,\
                    song_list.artist,\
                    program_list.release_year,\
                    song_list.register_flag\
            FROM \
                song_list\
            JOIN \
                program_list\
            ON \
                song_list.program_no = program_list.program_no\
            WHERE \
                release_year >= %s AND register_flag = 0;"
    
    target_year_query = season_year()
    cur.execute(query,(target_year_query,))

    for db_row in cur.fetchall():
        print("----------------------------------------------")
        for db_record in range(0,len(db_row)):
            print(db_row[db_anison_list[db_record]],end=" - ")
        print()
        
        search_track_name = db_row["song_name"]
        search_artist     = db_row["artist"]
        search_year_lim   = str(db_row["release_year"])
        program_no        = db_row["program_no"]
        timing            = db_row["timing"]
        anime_title       = db_row["anime_title"]

        main(search_track_name,search_year_lim,search_artist,program_no,timing,anime_title)

    cur.close()
    #更新する場合はコミット
    # conn.commit()

    #Slackメッセージ(登録数と登録曲)
    message_text = "Spotifyから最新曲を検索しました．\n```新規登録数：{}```".format(regi_count)
    global slack_nofication_message
    slack_nofication_message += "```"
    slack.send(text=message_text)
    if(regi_count > 0):
        slack.send(text=slack_nofication_message)

def main(search_track_name,year_lim,search_artist,program_no,timing,anime_title):

    conn.ping(reconnect=True)

    #要再チェック項目フラグ初期化
    need_to_confirm = 0

    #OAuth2.0
    client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(hiddenInfo.client_id, hiddenInfo.client_secret)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    print("----------------------------------------------")

    #クエリ用に年を{20XX}に調整，秋の場合はクエリを年明けリリースを考慮して{20XX OR 20XX+1}に変更
    query_year_lim = year_lim[0:4]

    #検索上限の設定
    search_lim = "50" #50まで

    #検索
    #クエリ形式: https://api.spotify.com/v1/search?q=track:{}%20year:{}%20artist:{} ...
    results = spotify.search(q='track:' + search_track_name + " year:"+ query_year_lim + " artist:" + search_artist, limit=search_lim, type='track',market="JP")

    #検索結果数を取得
    total_track = results["tracks"]["total"] #int
    if(total_track > int(search_lim)):
        print("検索結果が多すぎます："+str(total_track)+"件")
        total_track = int(search_lim)
    elif(total_track == 0):
        #見つからない場合はアーティストを直接クエリに挿入する
        #例) 変更前 q='track:youthful beautiful artist:内田真礼 ...'
        #    変更後 q='track:youthful beautiful 内田真礼'
        print("該当なし トラック名＋アーティスト名の直接検索を行います")
        results = spotify.search(q='track:' + search_track_name + " " + search_artist + " year:"+ query_year_lim, limit=search_lim, type='track',market="JP")
        total_track = int(results["tracks"]["total"])
        #さらに見つからない場合はアーティスト情報を消して'TV'を付ける
        #例) 変更前 q='track:youthful beautiful 内田真礼'
        #    変更後 q='track:youthful beautiful TV'
        if(total_track == 0):
            print("該当なし トラック名+TVで検索します")
            results = spotify.search(q='track:' + search_track_name + " " + search_artist + " ?TV?" +" year:"+ query_year_lim, limit=search_lim, type='track',market="JP")
            if(total_track == 0):
                results = spotify.search(q='track:' + search_track_name + " year:"+ query_year_lim, limit=search_lim, type='track',market="JP")
                total_track = int(results["tracks"]["total"])
                if(total_track > 10):
                    print("該当なし トラック名のみで検索しましたが，多すぎます({})".format(total_track))
                    return()
                elif(total_track == 0):
                    print("該当なし 終了")
                    return()
                else:
                    #検索結果が疑わしいのでフラグを立てる
                    need_to_confirm = 1
                    print("トラック名のみの検索です")
        else:
            need_to_confirm = 1

    print(str(total_track)+"件")

    track_info = results["tracks"]["items"]

    #検索結果数に合わせて表示
    for total in range(0,total_track):

        release_date  = track_info[total]["album"]["release_date"] #リリース日
        #日付型に変換
        set_year = datetime.datetime.strptime(year_lim, "%Y-%m-%d") - datetime.timedelta(days=10)
        #YYYY-MM-DD表記ではない場合は無視
        year_flag = re.match(r"\d{4}-\d{2}-\d{2}",release_date)
        if(year_flag):
            target_year = datetime.datetime.strptime(release_date,"%Y-%m-%d")

            #基準となる日付以降のリリースの時に抽出
            #クエリでは日付で絞り込めないので検索結果から絞り込む
            #各種情報取得
            if(target_year >= set_year):

                artist_name = []
                artist_id   = []

                #アーティスト
                for artist_number in range(0,len(track_info[total]["album"]["artists"])):
                    artist_name.append(track_info[total]["album"]["artists"][artist_number]["name"])
                    artist_id.append(track_info[total]["album"]["artists"][artist_number]["id"])

                #アルバム
                album_id = track_info[total]["album"]["id"]

                #トラック
                track_id    = track_info[total]["id"]
                spotify_track_name  = track_info[total]["name"]

                img_url     = track_info[total]["album"]["images"][0]["url"] #カバー画像
                preview_url = track_info[total]["preview_url"]               #プレビュー再生URL
                popularity  = track_info[total]["popularity"]                #人気度(0~100)
                # lyrics      = track_info[total]["explicit"]                #歌詞表現の規制(False/True)

                print(spotify_track_name + " : " + artist_name[0] + " ---Release-> " + release_date)

                #登録が出来たらregister_flagをON
                if(need_to_confirm == 0):
                    flag_cur = conn.cursor(buffered=True)
                    flag_query = "UPDATE song_list SET register_flag = %s WHERE program_no = %s AND timing = %s;"
                    flag_cur.execute(flag_query,(b"1",program_no,timing,))
                    flag_cur.close()

                #登録済みはスキップ
                cur_regi_confirm = conn.cursor(buffered=True)
                regi_confirm_query = "SELECT * FROM spotify_all_info WHERE track_id = %s;"
                cur_regi_confirm.execute(regi_confirm_query,(track_id,))

                if(not cur_regi_confirm.fetchall()):
                    global regi_count
                    global slack_nofication_message
                    regi_count += 1

                    #追加された曲をSlackで通知する為，タイトル名とトラック名を追記
                    check_mark = " - "
                    if(need_to_confirm == 1):
                        check_mark = "(x)"
                    else:
                        track_id_wp.append(track_id)
                    slack_nofication_message += check_mark + anime_title + " - " + spotify_track_name + "\n"
                    

                    #一般情報の登録
                    cur_regi = conn.cursor(buffered=True)
                    query = "INSERT INTO spotify_all_info (program_no,track_id,track_name,track_name_csv,album_id,release_date,img_url,preview_url,popularity,need_to_confirm,regi_date)\
                                                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                    info = (program_no,track_id,spotify_track_name,search_track_name,album_id,release_date,img_url,preview_url,popularity,need_to_confirm,regi_date_now,)
                    cur_regi.execute(query,info)
                    cur_regi.close()
                    cur_regi_confirm.close()

                    #WordPressに投稿
                    wordpress_post.wp_post(anime_title,spotify_track_name,track_id,artist_name,img_url,release_date,need_to_confirm)

                for group in range(0,len(track_info[total]["album"]["artists"])):
                    #アーティストが登録済みか確認
                    cur_artist_confirm = conn.cursor(buffered=True)
                    artist_confirm_query = "SELECT * FROM artist_list WHERE artist_id = %s;"
                    cur_artist_confirm.execute(artist_confirm_query,(artist_id[group],))

                    #アーティストの登録(重複を除く)
                    if(not cur_artist_confirm.fetchall()):
                        cur_artist = conn.cursor(buffered=True)
                        artist_query = "INSERT INTO artist_list (artist_id,artist_name) VALUES (%s,%s);"
                        cur_artist.execute(artist_query,(artist_id[group],artist_name[group],))
                        cur_artist.close()
                        cur_artist_confirm.close()

                    #アーティストとトラックの組み合わせが登録済みか確認
                    cur_match_confirm = conn.cursor(buffered=True)
                    match_confirm_query = "SELECT * FROM artist_song WHERE artist_id = %s AND track_id = %s;"
                    cur_match_confirm.execute(match_confirm_query,(track_id,artist_id[group],))

                    #アーティストとトラックの組み合わせを登録
                    if(not cur_match_confirm.fetchall()):
                        cur_match = conn.cursor(buffered=True)
                        match_query = "INSERT INTO artist_song (track_id,artist_id,track_name,artist_name) VALUES (%s,%s,%s,%s);"
                        cur_match.execute(match_query,(track_id,artist_id[group],spotify_track_name,artist_name[group],))
                        cur_match.close()
                        cur_match_confirm.close()

    conn.commit()

if __name__ == '__main__':
    db_test()