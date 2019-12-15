save-up-coin
============================

Lambdaの定期実行にてbitFlyer上で積立する。

## 事前準備

### bitFlyer アカウント登録

トレードクラスが必要。
現金をいくらか入金しておく。

### bitFlyer APIキーを発行

bitFlyer LightningからAPIキーを取得する

* 必要な権限
    - 資産残高を取得
    - 新規注文を出す

### AWS SES

必要であれば、実行時にメールを送ることも可能。
AWSのSESにて送信元と送信先をVerifyしておく。

### AWS Lambda へ pybitflyer を登録

```
cd ~/Desktop
mkdir ~/Desktop/python
pip install -t ~/Desktop/python/ pybitflyer
zip -r pybitflyer.zip python/
```

* https://github.com/yagays/pybitflyer からリポジトリをzipでダウンロード
* 解凍し、中のpybitflyerフォルダの名前を`python`に変更し、フォルダを圧縮。

* Lambda -> レイヤーの作成
    - 名前
        - pybitflyer
    - アップロード
        - pybitflyer.zip
    - ランタイム
        - Python 3.6, 3.7, 3.8

## AWS Lambda 関数作成

* Lambda -> 関数の作成 -> 一から作成
    - 関数名
        - save-up-coin
    - ランタイム
        - Python 3.8
    - 実行ロール
        - save-up-coin
            - AmazonSESFullAccess をアタッチしたもの
    - ハンドラ
        - main.main
    - タイムアウト
        - 10秒
    - リトライ
        - 0回
    - 環境変数
        - SAVE_UP_COIN_API_KEY
        - SAVE_UP_COIN_API_SECRET
        - SAVE_UP_COIN_SES_REGION
        - SAVE_UP_COIN_MAIL_FROM
        - SAVE_UP_COIN_MAIL_TO
    - トリガーを追加
        - CloudWatch Events
            - 新規ルールの作成
            - ルール名: 9am-every-day
            - cron(0 0 ? * * *)
    - レイヤーの追加
        - pybitflyer
    - このリポジトリのzipをアップロード
        - そのうちgithubと連動させてもいい


## 開発環境メモ

aws_cliのプロファイルを作っておく。

```
pyenv local 3.8.0
pip install pybitflyer
echo export SAVE_UP_COIN_AWS_PROFILE=***** >> ~/.bash_profile # デフォルトプロファイルじゃない場合のみ
echo export SAVE_UP_COIN_SES_REGION=us-west-2
echo export SAVE_UP_COIN_MAIL_FROM=***@gmail.com
echo export SAVE_UP_COIN_MAIL_TO=***@gmail.com,***@gmail.com
echo export SAVE_UP_COIN_API_KEY=*********** >> ~/.bash_profile
echo export SAVE_UP_COIN_API_SECRET=******** >> ~/.bash_profile
source ~/.bash_profile
```

## 連絡先

* [twitter: @m_cre](https://twitter.com/m_cre)

## License

* MIT
  + see LICENSE