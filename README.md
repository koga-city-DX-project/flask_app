同一ネットワーク内で、http://192.168.0.○○:5000　にアクセス。○○はipconfigのipv4アドレスを参照
動作環境
・Google Chrome ver121.0.6167.187
・Microsoft Edge ver121.0.2277.128
・Mozilla Firefox ver123.0 (64bit)
・Apple Safari ver 604.1
上記バージョン以外は未検証。後方互換性があれば動くと思われる。
同時接続は２台のPCと３種のブラウザの計６接続での動作は確認済
iPhoneでも動作するが非推奨

仮サーバー用の変更点
・DockerfileにてEXPOSE ○○○○(〇はポート番号)をつかってポート開放
・devcontainer.jsonでは"appPort": ["5000:5000"],でポート指定と"image": "app-test"で
イメージ名を指定してあげた
・"workspaceMount"の"source="にローカルでの実行フォルダのパスを指定
・app.run_serverのdebugをFalseに
・その他不必要なページやメニュー項目の削除
