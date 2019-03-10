<?php
    header('Content-Type: text/html; charset=UTF-8');
    require_once(dirname (__FILE__)."./info/config.php");
    // require_once(dirname (__FILE__)."/info/config.php");
    define('DB_HOST', $host);
    define('DB_NAME', $dbname);
    define('DB_USER', $username);
    define('DB_PASSWORD', $password);
    try{
        $dbh = new PDO('mysql:host='.$host.';charset=utf8;dbname='.DB_NAME,DB_USER,DB_PASSWORD);
    }catch(PDOException $e){
        echo $e->getMessage();
        exit;
    }
    $recently_flag = 0;
?>
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>アニソンチェッカー　データベース</title>
<link href="css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.css"/> 
<link href="css/main.css" rel="stylesheet">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<script type="text/javascript" src="./js/pop.js"></script>
<script src="https://cdn.datatables.net/t/bs-3.3.6/jqc-1.12.0,dt-1.10.11/datatables.min.js"></script>
<script>
jQuery(function($){
    $("#data-table").DataTable({
        order: [],
        lengthChange: false,
        searching: false,
        info: false,
        paging: false
    });
});
</script>
</head>
<body>
<div class="container">
<h1>Spotify アニソンデータベース</h1>

<form class="m-4" action="index.php" method="get">
<a href="../index.php" class="mr-3">アニソンチェッカーへ戻る</a>
<a href="about.php">About</a><br>
<button type="submit" class="btn btn-info m-3" name="anime_data" value="recently">最新曲</button>
<button type="submit" class="btn btn-info m-3" name="anime_data" value="2019-01-01">2019年冬アニメ登録状況</button>
<button type="submit" class="btn btn-info m-3" name="anime_data" value="2018-10-01">2018年秋アニメ登録状況</button>
</form>
<span class="label label-success">登録済み</span>　・・・間違いなく登録されているものです<br>
<span class="label label-warning">未チェック</span>・・・検索結果はありましたが，疑わしいものです<br>
<span class="label label-danger">未登録</span>　・・・検索しましたが，見つからなかったものです

<?php
    if(isset($_GET["anime_data"])){
        $anime_data_start = htmlspecialchars($_GET["anime_data"]);
        if($anime_data_start != "recently"){

            echo "<div class=\"table-responsive\">
                    <table id=\"data-table\" class=\"table\">
                    <thead>
                    <tr class=\"thead-dark\">
                        <th>アニメタイトル</th>
                        <th class=\"text-nowrap\">曲名</th>
                        <th>OP/ED</th>
                        <th class=\"text-nowrap\">状態</th>
                        <th class=\"text-nowrap\">視聴</th>
                    </tr>
                    </thead>
                    <tbody>";

            $anime_data_end   = date('Y-m-d', strtotime("$anime_data_start +3 month -1 day"));

            $query = "SELECT * FROM (
                        SELECT DISTINCT
                        song_list.song_no,
                        song_list.anime_title,
                        song_list.timing,
                        song_list.song_name,
                        song_list.artist,
                        program_list.release_year,
                        song_list.register_flag
                        FROM program_list
                        JOIN song_list
                        ON song_list.program_no=program_list.program_no
                        WHERE release_year >= :r_start AND release_year <= :r_end
                        ) AS aaaiii
                    LEFT OUTER JOIN spotify_all_info
                    ON aaaiii.song_name=spotify_all_info.track_name_csv";
                    
        }else{
                echo "<h3>最新登録25曲を表示しています</h3>";
                echo "<div class=\"table-responsive\">
                <table id=\"data-table\" class=\"table table-striped\">
                <thead>
                <tr class=\"thead-dark\">
                    <th>アニメタイトル</th>
                    <th class=\"text-nowrap\">曲名</th>
                    <th class=\"text-nowrap\">リリース日</th>
                    <th class=\"text-nowrap\">視聴</th>
                </tr>
                </thead>
                <tbody>";

                $query = "SELECT spotify_all_info.track_name, program_list.anime_title, spotify_all_info.release_date, spotify_all_info.regi_date ,preview_url FROM spotify_all_info JOIN program_list ON spotify_all_info.program_no=program_list.program_no ORDER BY release_date DESC LIMIT 25";
                $recently_flag = 1;
            }
        $stmt_query = $dbh->prepare($query);
        if($recently_flag != 1){
        $stmt_query->bindValue(":r_start",$anime_data_start);
        $stmt_query->bindValue(":r_end",$anime_data_end);
        }
        $stmt_query->execute();
    }

    if($recently_flag != 1){
    foreach($stmt_query->fetchAll(PDO::FETCH_ASSOC) as $track_info){
?>


<tr <?php if($track_info["register_flag"] == 1){echo "class=\"success\"";}elseif($track_info["need_to_confirm"] == 1){echo "class=\"warning\"";}?>>
<td><?php echo $track_info["anime_title"];?></td>
<td><?php if($track_info["register_flag"] == 1){echo $track_info["track_name"];}else{echo $track_info["song_name"];}?></td>
<td><?php echo $track_info["timing"];?></td>
<td ><?php if($track_info["register_flag"] == 1){echo "<span class=\"label label-success\">登録済み</span>";}elseif($track_info["need_to_confirm"] == 1){echo "<span class=\"label label-warning\">未チェック</span>";}else{echo "<span class=\"label label-danger\">未登録</span>";} ?></td>
<?php
if($track_info["register_flag"] == 1){
    echo "<td><a href=\"".$track_info["preview_url"]."\" class=\"popup\"><img src=\"img/link.png\" width=\"15px\"></a></td>";
}else{
    echo "<td>x</td>";
}
?>
</tr>

<?php } ?><!-- foreach-end -->
<?php }else{ foreach($stmt_query->fetchAll(PDO::FETCH_ASSOC) as $track_info){?><!-- recently_flag -->

<tr>
<td><?php echo $track_info["anime_title"];?></td>
<td><?php echo $track_info["track_name"];?></td>
<td><?php echo $track_info["release_date"];?></td>
<?php echo "<td><a href=\"".$track_info["preview_url"]."\" class=\"popup\"><img src=\"img/link.png\" width=\"15px\"></a></td>";?>
</tr>


<?php } ?><!-- foreach-recently-end -->
<?php } ?><!-- else-end -->
</tbody>
</table>
</div>

</div>
<footer>
<div class="text-center p-5 m-5">*視聴機能はポップアップ式ですので広告ブロック機能により利用できない場合があります。こちらのページには広告はありませんので，ブロック機能をOFFにしてご利用ください。</div>
<div class="text-center border border-primary p-5 m-5 bg-primary">
<span class="p-5">Copyright(c) <?php echo date("Y"); ?> アニソンチェッカー All Rights Reserved.</span>
</div>
</footer>
</body>
</html>