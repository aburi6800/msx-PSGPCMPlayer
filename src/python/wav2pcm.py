# -*- coding: utf-8 -*-

#
# wav2asm.py
#
# 11Khz8bitモノラルのPCMデータを格納したwavファイルを、.asmソースに変換する。
# なお、wavコンテナの各情報は以下。
#
# RIFFチャンク（アドレス固定）
# - +0x0000〜+0x0003 4byte  0x52, 0x49, 0x46, 0x46 ('RIFF')
# - +0x0004〜+0x0007 4byte  +0x0008以降のデータサイズ
# - +0x0008〜+0x000B 4vyte  0x57, 0x41, 0x56, 0x45 ('WAVE')
# fmtチャンク（RIFFチャンクの後で固定）
# - +0x000c〜+0x000f 4byte  0x66, 0x6d, 0x74, 0x20 ('fmt ')
# - +0x0010〜+0x0013 4byte  fmtチャンクバイト数
# - +0x0014〜+0x0015 2byte  フォーマットコード (0x0001=PCM)
# - +0x0016〜+0x0017 2byte  チャンネル数
# - +0x0018〜+0x001B 4byte  サンプリングレート 0x2b11=11025(11KHz),0x1f40=8000(8KHz) 
# - +0x001C〜+0x001F 4byte  データ速度 ステレオだとサンプリングレートx2となる
# - +0x0020〜+0x0021 2byte  ブロックサイズ
# - +0x0022〜+0x0023 2byte  サンプルあたりのビット数 0x0008=8bit,0x0010=16bit
# - +0x0024〜+0x0025 2byte  拡張部分のサイズ、リニアPCMは存在しない
# - +0x0026〜               拡張部分
# dataチャンク（開始アドレスは任意）
# - +0x0000〜+0x0003 4byte  0x64, 0x61, 0x74, 0x61 ('data')
# - +0x0004〜+0x0007 4byte  波形データのバイト数
# - +0x0008〜               波形データ
# LISTチャンク（ない場合もある）
# - +0x0000〜+0x0003 4byte  0x4c, 0x49, 0x53, 0x54 ('LIST')
# - +0x0004〜+0x0007 4byte  +0x0008以降のデータサイズ
# - +0x0008〜               データ

import binascii
import os

data = ""
pos = 0x0000

def execute(filename):
    global data
    global pos

    if '/' in filename:
        path = filename
    else:
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), filename))

    with open(path, mode="rb") as f:
        data = f.read().hex()
        f.close()

    # 取得したデータの長さ分処理する
    print("data size:" + str(len(data)/2) + "bytes.")
    while pos < len(data)/2:

        # Chank名取得
        chankName = getStringData()
        if chankName == "RIFF":
            checkRIFFChank()
        elif chankName == "fmt ":
            checkFmtChank()
        elif chankName == "data":
            checkDataChank()
        elif chankName == "LIST":
            checkListChank()
        

#    datasize = int.from_bytes(binascii.a2b_hex(data[0x0028*2:0x002A*2]), "little")
#    print("Data size : " + str(datasize) + "bytes")

#    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "sample.pcm"))
#    with open(path, mode="wb") as f:
#        data = f.write( bytes.fromhex( data[0x002c*2:(0x002c+datasize)*2] ) )
#        f.close()


def checkRIFFChank():
    '''
    RIFFチャンクの処理\n
    '''
    global data
    global pos

    # 全体のデータサイズ取得
    size = getInt4byteData()
    print("データサイズ : " + str(size))
    pos += 4
    return     


def checkFmtChank():
    '''
    fmtチャンクの処理\n
    '''
    global data
    global pos

    # fmtチャンクバイト数取得
    size = getInt4byteData()
    print("fmtチャンクサイズ : " + str(size))
    pos_sv = pos

    # フォーマットコードチェック
    if getInt2byteData() != 0x0001:
        # PCMでなければエラー
        raise("PCMデータではありません。")

    # チャンネル数はスキップ
    pos += 2

    # サンプリングレートチェック
    v = getInt4byteData()
    if v != 0x2b11 and v != 0x1f40:
        # 11025,8000以外であればエラー
        raise("サンプリングレートが11KHz/8KHzではありません。")

    # データ速度はスキップ
    pos += 4

    # ブロックサイズはスキップ
    pos += 2

    # サンプルあたりのビット数はスキップ
    pos += 2

    
    pos = pos_sv + size
    return     


def checkDataChank():
    '''
    dataチャンクの処理\n
    '''
    global data
    global pos

    size = getInt4byteData()
    print("dataチャンクサイズ : " + str(size))
    pos_sv = pos

    # 波形データのサイズを取得
    datasize = getInt4byteData()

    # 波形データをバイトデータとしてファイルに出力
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "sample.pcm"))
    with open(path, mode="wb") as f:
        f.write( bytes.fromhex( data[pos*2:(pos+datasize)*2] ) )
        f.close()

    pos = pos_sv + size
    return     


def checkListChank():
    '''
    LISTチャンクの処理\n
    '''
    global data
    global pos

    size = getInt4byteData()
    print("LISTチャンクサイズ : " + str(size))

    # 全てスキップ
    pos += size

    return     


def getStringData():
    '''
    データを文字列として取得して返却します。\n
    この関数を実行すると、現在の処理対象位置が+4されます。\n
    '''
    global data
    global pos

    result = ""
    for i in range(0, 4):
        result += chr(int(data[(pos)*2:(pos+1)*2], 16))
        pos += 1
    return result


def getInt2byteData():
    '''
    2byteのデータを取得して数値として返却します。\n
    この関数を実行すると、現在の処理対象位置が+2されます。\n
    '''
    global data
    global pos

    result = getIntValue(pos, pos+1)
    pos += 2
    return result


def getInt4byteData():
    '''
    4byteのデータを取得して数値として返却します。\n
    この関数を実行すると、現在の処理対象位置が+4されます。\n
    '''
    global data
    global pos

    result = getIntValue(pos, pos+3)
    pos += 4
    return result


def getIntValue(startPos, endPos):
    '''
    dataに格納された16進数文字列の指定位置の値をint型の数値に変換して返却します。\n
    data : バイナリを16進文字列化して格納したデータ(例:01A0FF)\n
    startPos : 開始位置\n
    endPos : 終了位置\n
    '''
    global data

    return int.from_bytes(binascii.a2b_hex(data[startPos*2:(endPos+1)*2]), "little")


if __name__ == "__main__":
    execute("test_8.wav")
