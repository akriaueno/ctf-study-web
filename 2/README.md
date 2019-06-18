# CTF 勉強会 Web 第2回
今回はSQLインジェクションとCookieについて説明します。

## SQLインジェクション1
SQLはDBを操作する言語ですが、この利用方法がまずいとSQLインジェクションを引き起こしてしまいます．

### コード例
例えば次のようなログイン処理をするスクリプトを見てみましょう
``` python
import sqlite3

def login(user, password):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    sql = 'SELECT flag FROM user WHERE username="{0}" AND password="{1}"'
    c.execute(sql.format(user, password))
    res = c.fetchone()
    conn.close()
    if res is None:
        return 'Login failed'
    else:
        return 'Login succeeded, {0}'.format(res[0])
```
まずDBに接続しconnctionオブジェクトを作り、それからDBを操作するためのcursorオブジェクトを生成しています。
SQL文の詳細は後で書きますが、DBに登録されたusername、passwordが入力値と等しい行を探しflagというカラムを取り出します。今回はフラグを取り出すということがログインすることと同じ意味を持ちます。
c.execute()で引数のSQLを実行することができます。
c.fetchone()は結果をタプルで返しますが、結果がない場合は`None`を返します。
flagを取得できる場合はログイン成功、そうでない場合はログイン失敗なので、最後にif文で分岐しています。
自然なログイン処理ですが、これにはSQLインジェクションの脆弱性が含まれています。
DBMSにSQLiteを使っていますが、SQLインジェクションはどのDBMSを使った場合も生じ得ます。
### SQL文
次にSQL文をみてみましょう
``` sql
SELECT flag FROM user WHERE username="{0}" AND password="{1}"
```
SELCT句では取得するカラム名、FROM句には取得する対象のテーブル名、WHERE句には取得する際の条件を書きます。
userテーブルのusernameとpasswordが入力値と一致した場合、その行のflagを取り出すというSQLです。
{0}と{1}はのちに入力値として[str.format()で引数の値に置き換える](https://docs.python.org/ja/3/library/stdtypes.html?#str.format)ための文字列です(置換フィールドといいます)。


userテーブルは以下のようになっているとしましょう
| id | username | password | flag |
| -- | -- | -- | -- |
| 1 | admin | 11235 | flag{SQLINJECTI0N}|

### 普通にログインする
adminとしてログインするには`username=admin`, `password=11235`とすれば、ログインできます。
このときSQL文は次のようになっています。
``` sql
SELECT flag FROM user WHERE username="admin" AND password="11235"
```
userテーブルのusername、passwordと合致するので、flagを取得できてログイン成功です。

### SQLインジェクションを利用してログインする
しかしSQLインジェクションを利用すればpasswordを知らなくてもログインすることができます。
次のように値を設定します`username=admin`, `password=" OR 1=1 --`
このときSQL文は次のようになっています
``` sql
SELECT flag FROM user WHERE username="admin" AND password="" OR 1=1--"
```
`password`にパスワードの値ではなくSQLの一部を入力しています。(下記の網掛部分)

`SELECT flag FROM user WHERE username="akky" AND password="`==`" OR 1=1 --`==`"`
`passowrd=""`の部分は偽となりますが、`1=1`は常に真となるので
``` sql
password="" OR 1=1
```
も常に真になります。
`--`はその後に来る文字列をコメントにする文字列です。これがないと今回はダブルクオーテーションの対応が合わないので構文エラーになります。
以上のようにSQLインジェクションの脆弱性がある場合、パスワードを入力せずともログインできてしまいます。

### 対策
CTF勉強会なので詳しくは紹介しませんが、入力値のエスケープやバリデーション、プリペアードステートメント(置換するものをリテラルだけに制限する)などです。

### 問題
`username=admin`, `password=" OR 1=1 --` とする以外にもSQLインジェクションの方法は存在します。違う方法を考えてみましょう。

## CookieとWebシステム
Webシステムでは一度ログインすると、ある程度の期間は再ログインすることなく使うことができるように設計されている場合がほとんどです。毎度ログイン認証することなくシステム側はユーザをどのように識別しているのでしょうか？
実現する方法の1つにCookieとセッションIDを利用する方法があります。セッションIDとはユーザを一意に判別する文字列のことで、セッションIDをCookieに保存しシステムはリクエストが来るたびにセッションIDのCookieを見ればユーザを識別することができます。

### Cookieについて
CookieとはWebシステム側が自由に設定しユーザのブラウザに保存することができる情報のことです。この値はシステムのみならずユーザも見ることができます。
Chromeを使っている場合はWeb Developer Toolsを開いて Application>Storage>Cookies から見ることができます。
![](https://i.imgur.com/FcUJs5q.png)

### Cookieの書き換え
ユーザはCookieを書き換えることもできます。
[EditThisCookie](http://www.editthiscookie.com/)というツールが有名です。
またこの資料を作っている時に知ったのですが、ブラウザのコンソールでJavaScriptを動かせばツールを使わなくても簡単に書き換えることができます(https://t-shukujo.com/edit-cookie/)。
``` js
document.cookie='userid=foo'  // ブラウザで実行
```
ユーザー側はCookieを書き換えることができるので、Cookieをうまく設定することでシステムに認証情報を誤解させて脆弱性をつくことができます。

### Cookieを書き換えてなりすます
実際にはあり得ないですが、ユーザを識別する際にセッションIDとしてユーザ名を利用しているシステムを考えてみましょう。
1. ユーザがログインする
2. サーバがDBのユーザ名とパスワードを照会する
3. 入力値と等しい場合はCookieにuser:<ユーザー名>を設定する
4. 以後サーバはCookieのuserの値を見ることでユーザを識別する

このようなシステムだとユーザがログインしたのちにuserを別のユーザ名に書き換えることでなりすましができてしまいます。

世の中のシステムはこのような仕組みではなくセッションIDを推測困難な文字列に設定し、DBにセッションIDとユーザ名を1対1に対応づけるテーブルを用意して、セッションIDの値からユーザ名を判別しています。しかしセッションIDの値が盗まれたり、推測困難な文字列を生成するアルゴリズムが弱い(総当たり可能になってしまう(自分は暗号分野に詳しくないので具体的には知りません))という場合にはやはりCookieを書き換えてなりすましができてしまいます。
したがってセッションIDにCookieに保存してをユーザーの識別に使う場合には
1. 他人にCookieを盗まれないようにする
2. セッションIDは推測困難な十分な強度のアルゴリズムで生成する

ことが重要です。1の方はXSSという脆弱性でよく問題になります。

## 関連問題
今回紹介した脆弱性で解ける問題をいくつか選んでみたのでやってみてください
### picoCTF
https://2018game.picoctf.com
* Logon
  http://2018shell.picoctf.com:5477
* Irish Name Repo
  http://2018shell.picoctf.com:59464/
### akkyCTF
https://ctf.akky.me/
* Can you login?
  http://q02.ctf.akky.me/
* Do you like that?
  http://q06.ctf.akky.me/
### websec
http://websec.fr/#
* level01(少し難しめ)
  http://websec.fr/level01/index.php
### ksnctf
https://ksnctf.sweetduet.info/
* Login(少し難しめ)
  http://ctfq.sweetduet.info:10080/~q6/
  
## 参考文献
徳丸 浩 「安全なWebアプリケーションの作り方 第2版」
大垣 靖男 「[完全なSQLインジェクション対策](https://blog.ohgaki.net/complete-sql-injection-counter-measure)」
