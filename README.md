Polls Application with Responder
======
[![python](https://img.shields.io/badge/Python-3.6%20|%203.7-blueviolet.svg?style=flat)](https://www.python.org/downloads/release/python-368/)
[![responder](https://img.shields.io/badge/Responder-1.3.1-lightgray.svg?style=flat)](https://python-responder.org/en/latest/)
[![license](https://img.shields.io/badge/LICENSE-MIT-informational.svg?style=flat)](https://python-responder.org/en/latest/)
  
(最終更新：2019.09.17)  
  
このアプリケーションは株式会社ライトコードで運営するブログにて連載している「Responderを使ってDjangoチュートリアルをやってみた」で作成したものです。
  
Responder(ver. 1.3.1)で作成したアプリケーションのため、バージョンが異なるとうまく動作しない場合があります。
  
本コードは下記に示す「[番外編 - さらなるアプリ改良](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-application-improvements)」
で作成された最終的なコードです。
    
## 開発
[株式会社ライトコード ー WEB・モバイル・ゲーム開発に強い会社](https://rightcode.co.jp)  


## 連載記事もくじ

[第0回 - 初期セットアップ編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-0)   
[第1回 - プロジェクト作成編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-1)   
[第2回 - データベース・モデル構築編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-2-1)   
[第3回 - データベース操作編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-3-1)   
[第4回 - 公開ビュー作成編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-4)   
[第5回 - 自動テスト導入編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-automated-test)   
[第6回 - 静的ファイル管理編](https://rightcode.co.jp/blog/information-technology/responder-django-static)   
[第7回 - adminページ改良編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-admin-page-improvement-1)   
  
[番外編 - さらなるアプリ改良](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-application-improvements)

## アプリケーションの起動(Localhost)
```bash
$ cd ResponderTutorial/polls
$ python run.py
```

## 注意
本アプリケーションはResponder(ver.**1.3.1**)で実装されています。
エラーハンドリングについては、お手持ちのデフィルトResponder環境では動作しません。
詳しくは[第4回 - 公開ビュー作成編](https://rightcode.co.jp/blog/information-technology/responder-django-tutorial-4)
をご覧ください。
  
また、記事とはディレクトリ構成が多少異なります。
記事中の「responder」ディレクトリは本ソースコードでいう「polls」にあたります。
  

## LICENSE
Copyright (c) 2019 RightCode Inc.  
Released under the MIT license  
[LICENSE.txt](LICENSE.txt)