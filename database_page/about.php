<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>アニソンチェッカー　データベース About</title>
<link href="css/bootstrap.min.css" rel="stylesheet">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
</head>
<body>
<div class="container bg-light w-50">
<h1 class="p-4">Spotify アニソンデータベース</h1>
<a href="index.php">戻る</a>
<h2 class="p-4">About</h2>
<p class="p-4">Spotifyアニソンデータベースは，「<a href="../index.php">アニソンチェッカー</a>」の元となっているデータベースを公開しているものになっています．
    各アニメの曲が登録されているかどうか一目で分かるようになっています．</p>

<h2 class="p-4">注意</h2>
<p class="p-2">新しい情報は半自動で更新を行っている「アニソンチェッカー」となります．
    このデータベースは曖昧な情報も含んだままの状態で公開されています．
    未チェック状態のものは，検索して結果が得られたものですが正しい情報かどうかわからないものになります．
    詳しくは下の"登録状態について"を御覧ください．
</p>
<p class="p-2">Spotifyの検索APIの仕様上，その曲があるのに検索しても結果が返ってこないものがあります．
    例えば2018年秋のアニメ「RELEASE THE SPYCE」のオープニング曲「スパッと！スパイ＆スパイス」などがあります．原因不明で調査中です．
</p>
<p class="p-2">検索された曲が複数のアルバムに登録されていると別の曲とみなされ，登録の重複が発生することがあります．
</p>

<h3 class="pt-4 pl-4">登録状態について</h3>
<div class="row p-4">
    <div class="col-xl-4">
    <ul class="list-unstyled">
        <li><span class="badge badge-success">登録済み</span>
        <ul>
        <li>曲名とアーティストの完全一致</li>
        <li>「曲名＋アーティスト名」での一致</li>
        </ul>
        </li>
    </ul>
    </div>

    <div class="col-xl-4">
    <ul class="list-unstyled">
        <li><span class="badge badge-warning">未チェック</span>
        <ul>
        <li>同一の曲名がある時</li>
        <li>似たような曲がある時</li>
        <li>検索される曲がある時</li>
        <li>カバー曲がある時</li>
        <li>オルゴール曲がある時</li>
        </ul>
        </li>
    </ul>
    </div>

    <div class="col-xl-4">
    <ul class="list-unstyled">
        <li><span class="badge badge-danger">未登録</span>
        <ul>
        <li>検索結果が無い時</li>
        </ul>
        </li>
    </ul>
    </div>
</div>


</body>
<footer>
    <div class="text-center border border-primary p-5 m-5 bg-primary">
    <span class="p-5">Copyright(c) <?php echo date("Y"); ?> アニソンチェッカー All Rights Reserved.</span>
    </div>
</footer>
</html>