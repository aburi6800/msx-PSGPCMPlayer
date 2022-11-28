# PCMPlayer

## 概要

MSX用のPCMデータプレイヤーです。  
8KHz/11KHzの8bitモノラルPCMデータを再生します。
z88dkのz80asmでコンパイルできる形にしています。  

## ライセンス

MIT Lisence

## 実行サンプル

以下のURLでサンプルプログラムの動作確認ができます。  
（一度再生して止まりますので、再度再生させる場合はWebMSXでResetの操作をしてください）

https://webmsx.org/?MACHINE=MSX1J&ROM=https://github.com/aburi6800/msx-PSGPCMPlayer/raw/main/dist/sample.rom&FAST_BOOT

## 使用方法

- pcmplayer.asmを利用するプロジェクトのディレクトリにコピーします。
- 初期設定では8KHzの再生に対応しています。11KHzの再生を行う場合は、87行目のコメントを外し、88行目をコメントにしてください。
- 再生するデータを準備します。（次の「PCMデータの作成」を参照ください）
- プログラムソースの先頭で、以下の指定を行います。
```
EXTERN PCMPLAY
```
- HLレジスタにPCMデータの先頭アドレス、DEレジスタにデータ長(byte)を指定して、以下を実行します。
```
    CALL PCMPLAY
```
- 再生中は割り込み禁止となり、他の処理が停止します。再生が終わると制御を戻します。

## ビルド方法

### cmakeを利用する場合の手順：

このプロジェクトに含まれている`CMakeLists.txt`を編集し、このプレイヤーのソース(`psmplayer,asm`)と作成したソースを指定します。  
たとえば、サンプルプログラムの場合は以下の定義になっています。  
```
add_source_files(
    ./src/msx/pcmplayer.asm
    ./src/msx/sample.asm
)
```

そして、makeファイルを生成するため、プロジェクトのルートディレクトリで以下のコマンドを実行します。（初回のみ、２回目以降は不要）
```
$ mkdir build && cd build
$ cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/z88dk.cmake ..
```

ビルドは`build`ディレクトリで以下のコマンドを実行します。
```
$ make clean && make
```

`.rom`ファイルは`dist`ディレクトリに作成されます。

### zccコマンドを利用する場合の手順：

ソースディレクトリに入り、以下コマンドを実行します。（ソースファイル名は、適宜変更してください）  
コマンドは`zcc`ですが、アセンブラとCのどちらのソースでも同じです。  
includeファイルのパス指定など、他オプションの詳細については`zcc -h`で表示されるヘルプを参照ください。  
```
$ zcc +msx -create-app -subtype=rom pcmplayer.asm sample.asm -o=../../dist/build.rom 
```

## PCMデータの作成

使用できるPCMデータは、以下形式となります。  
- サンプリングレート11KHz or 8KMz
- ビットレート8bit
- モノラル

以下の手順で作成します。
1. 44.1KHz16bitステレオ（通常の設定）でwavファイルを作成する  
    なお、録音したデータの切り出しは各種ツールを使用しますが、以下サイトでも行えます。
    https://audiotrimmer.com/
1. ffmpegを使用して、11KHz or 8KHz 8bitモノラルのwavファイルに変換する
    ```
    11KHzの場合：
    $ ffmpeg -i <入力wavファイル名> -ac 1 -ar 11025 -acodec pcm_u8 <出力wavファイル名>
    8KHzの場合：
    $ ffmpeg -i <入力wavファイル名> -ac 1 -ar 8000 -acodec pcm_u8 <出力wavファイル名>
    ```
    > または、以下サイトを使用して変換できます。  
    > https://www.petitmonte.com/labo/wave-format/
1. `src/python/wav2pcm.py`を使用し、PCMデータを抽出する
    > 現在、入力ファイル名と出力ファイル名を指定できず、固定になっています、すみません。
1. 使用するプログラムでincludeする
    ```
    PCMDATA:
        INCBIN "assets/sample_8.pcm"
    PCMDATA_END:
        DB $7F
    ```
    > 上記の`PCMDATA`はPCMデータの開始アドレスを示すラベルになります。  
    > `PCMDATA_END`はPCMデータ長を計算するために設定したラベルです。  
    > こうすることで、DEレジスタには`PCMDATA_END - PCMDATA`でデータ長を指定できます。

## リリースノート

### pcmplayer.asm

- 2022/11/27  Version 0.2.0
    - PSGレジスタの保存/復元、初期化を追加
    - WebMSXで実行した際にCh1〜3のトーンが初期化されていない不具合に対応

- 2022/11/26  Version 0.1.0
    - 初版作成

### wav2pcm.py

- 2022/11/28  Version 0.3.0
    - 引数に対応。
    - 任意のパスのファイルの処理に対応。

- 2022/11/27  Version 0.2.0
    - wavコンテナのチャンクを正しく取得して処理するように修正

- 2022/11/26  Version 0.1.0
    - 初版作成

## Thanks
[h1romas4](https://github.com/h1romas4)  
[超人MSX](http://hp.vector.co.jp/authors/VA054130/pcm1dm.html)  
[MSX Assembly Page](http://map.grauw.nl/articles/psg_sample.php)  
