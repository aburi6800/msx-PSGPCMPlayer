# -*- coding: utf-8 -*-

#
# wav2pcm.py
#
# 11Khz or 8KHzの8bitモノラルのwavファイルからPCMデータを抽出して保存する。
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

import os
import sys
import traceback
import argparse
import binascii

data = ""
pos = 0x0000

def main():
    '''
    メイン処理\n
    '''
    global data
    global pos

    # 引数パース
    argparser = argparse.ArgumentParser(description="Extract PCM data from a WAV file.\nWAV files must be 8-bit mono at 11 KHz or 8 KHz.")
    argparser.add_argument("infile", help="WAV file name to input.")
    argparser.add_argument("--outfile", "-o", help="PCM file name for output.", default="out.pcm")
    argparser.add_argument("--force", "-f", action="store_const", const="", help="Ignore output even if the file exists.")
    argparser.add_argument("--ver", "-v", action="version", version="%(prog)s 0.3.0")
    args = argparser.parse_args()

    # 入力ファイル取得
    getData(args.infile)

    # 取得したデータの長さ分処理する
    while pos < len(data)/2:

        # Chank名取得
        chankName = getStringData()
        if chankName == "RIFF":
            checkRIFFChank()
        elif chankName == "fmt ":
            checkFmtChank()
        elif chankName == "data":
            checkDataChank(args.outfile, args.force)
        elif chankName == "LIST":
            checkListChank()


def getData(inWAVFile:str):
    '''
    入力ファイル取得処理\n
    inWAVFile : 入力WAVファイル
    '''
    global data

    try:
        # 拡張子チェック
        if os.path.splitext(inWAVFile)[1] != ".wav":
            raise Exception("File extension is not .wav.")

        # 入力ファイルのフルパスを設定
        filepath = filePathUtil(inWAVFile)

        # 存在チェック
        if os.path.exists(filepath) == False:
            raise Exception("File not found.")

        # ファイル読み込み
        with open(filepath, mode="rb") as f:
            data = f.read().hex()
            f.close()

    except Exception as e:
        print(traceback.format_exception_only(type(e), e)[0])
        sys.exit()

    return


def checkRIFFChank():
    '''
    RIFFチャンクの処理\n
    '''
    global data
    global pos

    # 全体のデータサイズ取得
    size = getInt4byteData()
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
    pos_sv = pos

    try:
        # フォーマットコードチェック
        if getInt2byteData() != 0x0001:
            # PCMでなければエラー
            raise Exception("This is not PCM data.")

        # チャンネル数はスキップ
        pos += 2

        # サンプリングレートチェック
        v = getInt4byteData()
        if v != 0x2b11 and v != 0x1f40: # 2b11は11KHz、1f40は8KHz
            # 8000以外であればエラー
            raise Exception("Sampling rate is not 11Khz/8KHz.")

        # データ速度はスキップ
        pos += 4

        # ブロックサイズはスキップ
        pos += 2

        # サンプルあたりのビット数はスキップ
        pos += 2

        # 次のチャンクの先頭にセット
        pos = pos_sv + size

    except Exception as e:
        print(traceback.format_exception_only(type(e), e)[0])
        sys.exit()

    return     


def checkDataChank(outPCMFile:str, force:str):
    '''
    dataチャンクの処理\n
    '''
    global data
    global pos

    size = getInt4byteData()
    pos_sv = pos

    # 波形データのサイズを取得
    datasize = getInt4byteData()

    try:
        # 出力ファイルのフルパスを設定
        filepath = filePathUtil(outPCMFile)

        # 存在チェック
        # オプション --force(-f)が設定されている場合はエラーとしない
        if os.path.exists(filepath) and force == None:
            raise FileExistsError("Specified file already exists.")

        # 波形データをバイトデータとしてファイルに出力
        with open(filepath, mode="wb") as f:
            f.write( bytes.fromhex( data[pos*2:(pos+datasize)*2] ) )
            f.close()
            print("output data size " + str(size - 4) + "bytes.")

        # 次のチャンクの先頭にセット
        pos = pos_sv + size

    except Exception as e:
        print(traceback.format_exception_only(type(e), e)[0])
        sys.exit()

    return     


def checkListChank():
    '''
    LISTチャンクの処理\n
    '''
    global data
    global pos

    size = getInt4byteData()

    # 次のチャンクの先頭にセット
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


def filePathUtil(path:str):
    '''
    ファイルパスユーティリティ\n
    引数のパスにディレクトリを含んでいない場合、カレントディレクトリを付与したフルパスを生成して返却します。\n
    path : ファイルパス
    '''
    # 入力ファイルのフルパスからファイル名を取得
    filename = os.path.basename(path)

    # 入力ファイルのフルパスからファイルパスを取得
    filepath = os.path.dirname(path)
    if filepath == "" or filepath == None:
        # ファイルパスが取得できなかった場合（ファイル名のみ指定された場合）は現在のパスを設定
#        filepath = os.path.normpath(os.path.join(os.path.dirname(__file__), filename))
        filepath = os.path.dirname(__file__)

    return filepath + os.sep + filename


if __name__ == "__main__":
    main()
