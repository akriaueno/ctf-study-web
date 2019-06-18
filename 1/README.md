# CTF 勉強会 Web 第1回

## 概要
CTFのWebというジャンルについて簡単な講義&実戦形式で問題を解いていきます．自分はCTF初心者なので，内容は初歩的です．

## Webというジャンルについて
Web上に公開されているサービスの脆弱性をついてflagを取得します．脆弱性の原因は様々で，WebフレームワークやDBの使用方法の誤りやそれらのバグ，入力値チェック(バリデーションといいます)のミスなどに起因します．
今回はWebの基盤よくCTFに出る基本的な脆弱性をいくつか解説します．

## HTTP
脆弱性の解説の前にHTTPについて説明します．Web上ではHTTPリクエストというものをクライアント側(ブラウザやアプリ)からサーバ側へ飛ばし、レスポンスをサーバが返すことでサービスを動作させています．

![](https://i.imgur.com/R2vfuov.png)

例えばGoogleで検索する際にはどのようなリクエストを投げているのでしょうか．実際に確認してみましょう．
### Google Web Developer Tools
HTTPリクエストを見てみる為にGoogle Web Developer Toolsを使ってみましょう．Web Developer ToolsはGoogleが開発者向けに公開しているツールの1つで，Google Chrome上に載せられています．
Chromeを開いて，画面上で右クリックすると「検証」という項目があるのでクリックしてください．
(Macを使っている人はCommand+Option+I，Windowsを使っている人はCtrl+Shift+Iでもできます．)

![](https://i.imgur.com/GfHGQBx.png)

こんな画面になるはずです．ここで**Network**というタブを開いてみましょう．

![](https://i.imgur.com/dUQw7JY.png)

今はまだ何もリクエストを送っていないので何も表示されていません．

次に検索窓に何か文字を打って検索してみましょう．今回はtomatoを検索してみました．

![](https://i.imgur.com/a4RQA7t.png)

そうすると何やらかたくさん表示されました．実はこれらが検索して画面を表示する為にブラウザが送ったHTTPリクエストです．
この一番上の`search?q=<検索文字列>...`と表示されているHTTPリクエストをクリックしてみましょう．

![](https://i.imgur.com/0rG9PYM.png)

この**Headers**というタブの**General**という項目ではHTTPリクエストの概要を見ることができます．
この場合ではリクエストしたURLとメソッド、レスポンスのステータスコードなどが表示されています．
#### Request URL
**Request URL**を見ると
`https://www.google.com/search?q=tomato&oq=tomato&aqs=chrome..69i57.7637j0j1&sourceid=chrome&ie=UTF-8`
となっています．
これは`https://www.google.com/search`というURLにクエリと値
`q=tomato`
`oq=tomato`
`aqs=chrome..69i57.7637j0j1`
`sourceid=chrome`
`ie=UTF-8`
が追加されてリクエストが投げらていることが分かります．`q`というクエリの値が検索文字列になっています．
一般にリクエストURLは`URL?query_1=value_1&query_2=value_2&...&query_n=value_n`という形式で投げられます．

#### Request Method
**Request Method**はGETになっています．
リクエストメソッドにはGET, POST，PATCH, PUT, DELETE, OPTIONSなど様々なメソッドがありますが主に使われるのがGETとPOSTです．GETはリソースの取得，POSTはリソースの作成や更新によく使われます．
今回はtomatoを検索(リソースの取得)したのでGETリクエストが投げられています．

#### Status Code
**Status Code**は200になっています．
これはサーバ上で正常に処理が行われたことを表しています．これも200番だけではなく様々ありますがおおまかに説明すると、
200番台: 正常に動作
300番台: リダイレクト
400番台: クライアント側のエラー
500番台: サーバ側のエラー
を表しています．

スクロールすると**Response Headers**や**Request Headers**, **Query String Parameters**などリクエストとレスポンスについて詳しく見ることができます．
HTTPリクエスト・レスポンスはHeaderとBodyに分かれていて，概要がHeaderに内容がBodyに書かれています．GETリクエストの場合Bodyは付けず、クエリに書くことが一般的なので、今回**Request Body**という項目はありません．
一方でレスポンスについてはBodyを見ることができます．そのBodyは**Response**タブをクリックすることで見ることができます.

![](https://i.imgur.com/TL1g76X.png)

文字がぎっしり詰まっていますが，これはブラウザ上で画面を表示させるためのHTMLです．このHTMLはDeveloper Tools上部の**Elements**タブから整形されたものを見ることもできます．

![](https://i.imgur.com/4rBc0G6.png)

以上のようにGoogleで検索する際にはHTTPを利用していることが実感できたかと思います．
