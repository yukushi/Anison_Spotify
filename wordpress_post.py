from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from datetime import datetime
import hiddenInfo

def wp_post(anime_title,track_name,track_id,artists,img_url,release_date,flag):

    wp = Client(hiddenInfo.wp_URL,hiddenInfo.wp_author,hiddenInfo.wp_pass)
    post = WordPressPost()

    #Title
    title = "「{}」が配信が開始".format(track_name)

    #Content
    img_source = "<img src=\"{}\" />".format(img_url)
    article_top = "アニメ「{}」の「 {}」 がSpotifyにて配信が開始されました！".format(anime_title,track_name)

    #Artists list to string
    artists_str = ','.join(artists)

    #Table
    table_template = "<table style=\"width: 100%; background-color: #fff5f5;\">\
                        <tbody>\
                            <tr>\
                            <td style=\"background-color: #ffd4d4;\"><span style=\"font-size: 8pt;\">アニメタイトル</span></td>\
                            </tr>\
                            <tr>\
                            <td><span style=\"font-size: 14pt;\"><strong>{}</strong></span></td>\
                            </tr>\
                            <tr>\
                            <td style=\"background-color: #ffd4d4;\"><span style=\"font-size: 8pt;\">トラック名</span></td>\
                            </tr>\
                            <tr>\
                            <td><span style=\"font-size: 14pt;\"><strong>{}</strong></span></td>\
                            </tr>\
                            <tr>\
                            <td style=\"background-color: #ffd4d4;\"><span style=\"font-size: 8pt;\">アーティスト</span></td>\
                            </tr>\
                            <tr>\
                            <td><span style=\"font-size: 14pt;\"><strong>{}</strong></span></td>\
                            </tr>\
                            <tr>\
                            <td style=\"background-color: #ffd4d4;\"><span style=\"font-size: 8pt;\">リリース日</span></td>\
                            </tr>\
                            <tr>\
                            <td><span style=\"font-size: 14pt;\"><strong>{}</strong></span></td>\
                            </tr>\
                        </tbody>\
                    </table>".format(anime_title,track_name,artists_str,release_date)

    #Spotify_HTML_Player
    player = "<h3>視聴</h3><iframe src=\"https://open.spotify.com/embed/track/{}\" width=\"100%\" height=\"80\" frameborder=\"0\"></iframe><br><br>".format(track_id)

    #URL
    link = "Spotify URL (Webプレイヤーが開きます)<br><a href=\"https://open.spotify.com/track/{}\">https://open.spotify.com/track/{}</a>".format(track_id,track_id)

    body = img_source + article_top + table_template + player + link

    #Post status
    if(flag == 1):
        post_status = 'draft'
    else:
        post_status = 'publish'

    #Tag and category
    tag = artists
    cat = []

    year = release_date.split('-')[0]
    month = int(release_date.split('-')[1])

    if(month >= 9):
        season = "秋アニメ"
    elif(month >= 7):
        season = "夏アニメ"
    elif(month >= 4):
        season = "春アニメ"
    elif(month >= 1):
        season = "冬アニメ"
    cat_set = year + season
    cat.append(cat_set)

    tag_cat = {'post_tag': tag,'category': cat}

    #Custom field
    # customFields = [{'key': 'fifu_image_url','value': img_url}]

    # set param----------
    post.title = title
    post.content = body
    post.terms_names = tag_cat
    datetime.now()
    post.post_status = post_status
    post.comment_status = 'open'
    # post.custom_fields = customFields
    #--------------------

    wp.call(NewPost(post))