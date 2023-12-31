


## 480ティックのみ対応 一定テンポのみ対応　サンプリングレート44.1kのみ対応 4/4のみ確認している　ベロシティは１２７が最大　ファイル名は＿Rが混入してるののみ除外
# 学習用音声デ＾た音声ファイルは WAV形式で 16kHz, 16bit, PCM（無圧縮）形式である必要があり ます。テキストファイルはテキスト形式で、文字コードは UTF-8です。
############################### ファイルインポート ######################
import coreAI


import os
from socket import if_indextoname
from struct import pack
from types import DynamicClassAttribute
from xml.dom import InvalidStateErr
import torch
import tkinter
from tkinter import filedialog
import mido
import torchaudio
import matplotlib.pyplot as plt
import time
#import simpleaudio
import numpy
#from playsound import playsound
from PIL import Image,ImageDraw
from torch import nn
#import pyworld as pw
import scipy.io
from scipy.io.wavfile import read
from scipy.interpolate  import interp1d
#from pocketsphinx import LiveSpeech
import subprocess
import re
import shutil
#import librosa
import soundfile
#import pyopenjtalk
#from nnmnkwii.io import hts
#import ttslearn
import sounddevice as sd
import tkinter.font as ft
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle
from functools import partial

################################## 定数 #################################

# gui関連
WINDOW_WIDTH_PX = 1280  #横方向のデフォルトウィンドウサイズ
WINDOW_HEIGHT_PX = 800  #縦方向のデフォルトウィンドウサイズ
FONT_STYLE = "MSゴシック"
DEFAULT_PARAM_WIN_HEIGHT = 400
# 音楽関連
SAMPLE_RATE = 44100     # サンプリングレートを44.1kHzで固定して定義
DEFAULT_READ_LOCATION = r'C:\Users\yuto\Desktop\projectVOICE\voice\voice'# デフォルトの読み込み位置
DELTA_TIME = 1          # 微小な時間[ms]
S_PER_BEAT = 0.5        # テンポ120の時の１拍あたりの秒数[s]
QUARTER_NOTE_TICKS = 480#4分音符一つのティック数
STANDARD_TEMPOS_S = 0.0010416666#[s]120bpmの時の秒数 todo 1テンポの秒数？
MAX_VEROCITY = 127      # ０からカウントのベロシティーの最大値
INITIAL_DYNAMICS_VALUE = 0.7 #　ノートのダイナミクスのデフォルト初期値　０以上１以下であること
# midi関連
TIME_PER_BER = 1920     #１小節がmidiのtimeではどんな数値になるか
# ピアノロール関係
L=80
C = L*1.8
        
global PX_PER_BAR
PX_PER_BAR = 400                # 1小節を何ピクセルにするか定義[px]

# パラメーター部関連
PARM_TIME_RESOLUSION = 0.1      #[s]のパラメータの時間方向の分解能

# グリッド線関連
VERTICAL_LENGTH = 2000          #[px]垂直線のグリッドの長さ
VERTICAL_GRID_SPACE = 300       #[px]垂直線のグリッドの間隔

# gui
RATIO_MAIN_2_TOTAL_HEIGHT = 0.6 # ウィンドウの高さに対するメイン画面の割合
RATIO_MAIN_2_TOTAL_WIDTH = 0.2  # 全体のウィンドウの幅に対する右側のエリアの幅割合
INITIAL_LENGTH_PX = 1600        # [px]初期状態のＢＧの横幅兼パラメタ部の横方向の幅

#エンジン関連
SAMPLE_RATE_MIDI_2_FREQ = 100   # midiデータから周波数データに変換する時のサンプリングレート[ms]
DEFAOUT_MIDI_TEMPO = 500000.0
MIDI_TIME_RESOLUSION_S = 0.01   #[s]のmidiデータを元に音高の周波数に変換する時間分解能
TIME_2_TICK_RESOLUTION = 50      #何ティックで時間方向の分解能１とするか（パラメタとピッチの）         

# データ形式関連       #fullWavDataのデータ仕様　１行が一つのwavデータを表現
RAW_DATA = 0        # 生のwavファイル 2次元
MU_RAW_DATA = 1     # mulawで圧縮されたwavファイル　2次元
FILE_NAME = 2       # ファイル名（名前未加工）1次元
PHONE_ALIGMENT = 3  # 音素アライメント[2]
DETECTED_PHONE = 4  # openJtalkで検出された音素検出
LINGISH_CHARA = 5   # 言語特徴量５つ（ターゲットと前後2つの音素の種類データ）
ENCODED_CHARA=6       # 数値に変換された言語特徴量
EXPRESION = 7       # 将来的に使う声の種類（裏声とか）を表す特徴量　現在未使用０
WAV_SAMPLING_TIME = 0.001   #[s]wav１サンプルの時間todo

# その他
isClicking = False  #マウスが左クリックされるときTrue　それ以外Falseになるフラグ
cousolPosX = 0      # マウスカーソルの位置ｘ座標
cousolPosY = 0  # マウスカーソルの位置y座標

################################## イベント関数 ##########################

def close_disp():
    pass

# 上書き保存するイベント
def save_file(self,event):

    # 保存する拡張子の設定
    type = [('voice','*.voice')]

    # デフォルトのディレクトリを設定してダイアログ表示
    window.filename = filedialog.asksaveasfilename(filetypes = type,initialdir = DEFAULT_READ_LOCATION,title="save as")

# 名前を付けて保存するイベント

def import_wav():
   
    # wavファイルを読み込みの時のイベント関数

    # タイプの設定
    type = [('mp3','*.mp3')]
   
    # デフォルトのディレクトリを設定してダイアログ表示
    wavDataPath = filedialog.askopenfilename(filetypes = type,initialdir = DEFAULT_READ_LOCATION)
   
    #wav_obj = simpleaudio.WaveObject.from_wave_file(wavDataPath)
    #play_obj = wav_obj.play()
    #play_obj.wait_done()

    playsound(wavDataPath)

def export_wav(event):

    # 音声保存を実行するイベントハンドラ
    pass

def export_model(event):

    # モデルエクスポートを実行するイベントハンドラ
    pass

class applicationDataFormat():

    # 本ソフトのデータ形式を表現したクラス　作曲者、音源作成者共通のデータ構造とする ただしwavファイルは”動的”にアトリビュートに追加されるここの定義は最低限度のもの

    def __init__(self):
       
        self.totalWavAmount = 0

    '''
 class ttmkm():  
    # 畳み込みブロックを表現するクラス

    def test(

        # 初期化メソッド
        self,               #　pythonの言語使用にのっとりインスタンス参照用
        residualChannel,    # 残差接続のチャンネル数
        gateChanels,        # ゲートのチャンネル数
        kernelSize,         # カーネルサイズ 畳み込みは全て共通のカーネルサイズとする
        skipConnectChanel,  # スキップコネクションのチャンネル数
        dilation = 1,       # ディレーションファクターは１で固定
        charaChanels=80,    # 条件付き特徴量のチャンネル数　1x1畳み込みに入れる入力用
   
    ):  
    # アトリビュートの定義
   
        # 膨張畳み込みの場合パディング数は下記で定義される -1は過去方向への因果なのでディレーションは間隔なので
        self.padding = ( kernelSize -1 ) * dilation

        # 1次元膨張因果畳み込みを表現
        self.conv = nn.Conv1d(residualChannel,gateChanels,kernelSize,padding = self.padding,padding_mode='zeros')

        # アップサンプル済み条件付け特徴量に対して使われる1x1畳み込み用(local conditioning)
        self.localConditioning = nn.Conv1d(charaChanels,gateChanels,kernelSize,bias=False)

        # ゲートから出てきた時のチャンネル数 特徴量の1x1畳み込みからの出力は”２分のチャンネル”なのでゲートの出力は半分のチャンネル数
        gateOutputChanel = gateChanels // 2

        # スキップ接続で"ない"つまり本層の出力として出す直前の1x1畳み込み用
        self.residual1x1conv = nn.Conv1d1x1(gateOutputChanel,residualChannel,kernelSize)

        # スキップ接続用出力の直前に挟まれる1x1の畳み込み用
        self.skipConnection = nn.Conv1d1x1(gateOutputChanel,skipConnectChanel,kernelSize)

    # メソッドの定義
    def forward(self,layerInputOutput,charaAmountInput):

        # 残差接続で最終的に入力を加算する為に値を保持
        residual = layerInputOutput

        # 膨張畳み込みを実行
        self.conv(layerInputOutput)

        # 因果性を確保する為にトーチの出力をシフト　todo 理解がまだ
        layerInputOutput= layerInputOutput[:,:,: -self.padding]

        # tanh sigma用の2つにチャンネルを分割　todo 理解がまだ
        tanhInput,sigmaInput = layerInputOutput.split(layerInputOutput.size(1) // 2,dim=1)

        # ゲート付き活性化関数
        gateOutput = torch.tanh(tanhInput) * torch.sigmoid(sigmaInput)

        # ゲートからの出力のチャンネルを2分割
        gateOutput1,gateOutput2 = gateOutput.split(gateOutput.size(1) // 2,dim=1)

        # ローカルコンディショニングからの出力を得る
        #ca,
        # 畳み込み済み条件付き特徴量を加算
        #gateOutput1 = tanhInput +
        #gateOutput2 = sigmaInput +
        # 残差接続の加算を実行
        layerInputOutput = layerInputOutput + residual
'''

class recordAudio():

    # オーディオレコーディングするクラス
    pass

class midi():

    # midiデータに関係するクラス

    def countNotes(self,midiFile,trackNumber):

        # 与えられたトラック無いのノートの数をカウントするメソッド

        # カウンターの初期化
        count = 0
            
        for msg in midiFile.tracks[trackNumber]:
             if msg.type =="note_on" and msg.dict()["velocity"] !=0:
                 count +=1

        return count
    
    def load_Midis(self,midiData,composerData,MidiNumber2Freq):

        # 指定されたmidiファイルのトラックを元に画面にノートを表示するメソッド
       
        currentTime = 0             # ms単位での周波数をプロットする時刻を格納する変数を定義
        noteOnOffTotalAmount = 0    # ノートがオン、オフした回数を保存　偶数個なら正常なmidiデータで奇数個なら以上なmidiデータと判断する
        index = 0                   # リストの何番目を参照しているかのインデックス
        doubleAmount = 0            # 次のノートが１つタイミング的に食い込むごとに増えるカウント用変数
        noteFlag = 0                # note_on信号を読み込んだら１それに対応するoff信号を読み込んだら０に戻るフラグ
        loadedmMetaDataFlag = 0     #midiのメタデータを読み終わったら１になるフラグ
        firstNoteTimeFlag = 1
        metaDataRows=0              # メタデータに何行費やしたかカウントする
        noteOnAmount=0
        noteOffAmount = 0
        midiReadPosition=0#読み込んでるmidiの行
        endOverlappingFlag =0
        tmp=[]
        startPointWritten=0
        tickSum=0# はじめを０とした絶対ティック数の累計

        # トラックＩＤをウィジェット変数から取得
        midisTruckId = selectedTruck.get()

        # 対象トラック中のノートの数をカウント
        noteAmount = midi.countNotes(midiData,selectedTruck.get());

        # 再生時間の取得
        truckTime = midiData.length

        midisList = [[1,1,1]]# どの高さを　どこ（絶対ティック数）から　どこ（絶対ティック数）まで　を格納

        # midiデータを１行づつ総なめにする処理
        for targetMassage in midiData.tracks[selectedTruck.get()]:
            
            # テンポを取得
            if targetMassage.type =='set_tempo':

                #テンポを取得してウィジェット変数へ格納する
                midisBpm.set(targetMassage.tempo) 
                #print("テンポは",midisBpm.get())

            # メタデータ以外のみを取り出す
            if not targetMassage.is_meta:
           
                if firstNoteTimeFlag == 1:

                    index = 0
                    firstNoteTimeFlag = 0

                if targetMassage.type == 'note_on' and firstNoteTimeFlag == 0:

                    # リストを拡張
                    midisList.append([0,0,0])

                    #print("index",index,"index + metaDataRows",index + metaDataRows,"累計",tickSum,"オン数",noteOnAmount,"オフ数",noteOffAmount,"midi行",midiReadPosition)

                    # 重複を検出
                    if noteOnAmount - noteOffAmount >= 1:

                        # 重複や重なりがある時
                        #print("重複検出(on)")

                        tmp.append(midiData.tracks[selectedTruck.get()][midiReadPosition].time)

                        # ノート番号（高さ）を格納
                        midisList[index + len(tmp)][0] = midiData.tracks[selectedTruck.get()][midiReadPosition].note

                        # 現在の信号が示すティック数を計算
                        tickSum= tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time

                        #print("ｔｍｐの数",len(tmp))
                        # ノートの開始点を絶対ティック数で格納
                        midisList[index + len(tmp)][1] = tickSum


                        #
                        # ノートオンになった数を数えるためにインクリメント
                        noteOnAmount = noteOnAmount + 1

                    else:

                        # 重複や重なりがないとき
                        #print("重なりなし(on)")

                        # ノート番号（高さ）を格納
                        midisList[index][0] = midiData.tracks[selectedTruck.get()][midiReadPosition].note

                        # 現在の信号が示すティック数を計算
                        tickSum= tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time

                        # ノートの開始点を絶対ティック数で格納
                        midisList[index][1] = tickSum

                    
                        # ノートオンになった数を数えるためにインクリメント
                        noteOnAmount = noteOnAmount + 1


                elif targetMassage.type == 'note_off' and firstNoteTimeFlag == 0:

                    #print("index",index,"index + metaDataRows",index + metaDataRows,"累計",tickSum,"オン数",noteOnAmount,"オフ数",noteOffAmount,"midi行",midiReadPosition)
                    #print("tmpの数",len(tmp))
            

                    if len(tmp) == 0:
                    # ノートが互いに食い込んだり同時に存在しない場合
                    
                        # 重なりがない時の処理をする為に分岐
                        if endOverlappingFlag != 1:

                            #print("重複検出 ラスト")

                            # 現在の信号が示すティック数を計算
                            tickSum= tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time

                            midisList[index][2] = tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time 
                        
                        # 重なりが解消された時かどかチェック（つまりいままでノートに重なりがあったか）
                        if endOverlappingFlag == 1:
                        
                            # 重なりが解消された瞬間
                            #print("重複検出(off)ラスト")

                            # １つ前のノートの終わりに現在のtime値を加算してノート長さを計算
                            midisList[noteOffAmount][2] = midisList[noteOffAmount - 1][2] + midiData.tracks[selectedTruck.get()][midiReadPosition].time 

                            # リストの次の行に書き込む為にインデックスをインクリメントして更新
                            index = index + 1

                            # ノートを正常にオフしたのでカウンタ変数をインクリメント  
                            noteOffAmount = noteOffAmount + 1
                        else:

                            #print("その他")
                            # 重なりが解消された直後でない時（そもそも重なりがない場合はこっちに入る）
                            # ノートの終了時刻を絶対ティック数で格納
                            midisList[index][2] = tickSum

                            # リストの次の行に書き込む為にインデックスをインクリメントして更新 todo 検討
                            #index = index + 1

                    # 重複を検出 ノートが互いに食い込んだり同時に存在する場合
                    else :
                        #print("重複検出(off)")

                        #print("tmp",len(tmp),"ティック合計",tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time)
                        midisList[noteOnAmount - 1 - len(tmp)][2] = tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time 
                        
                        # 現在の信号が示すティック数を計算 todo いらないかも
                        tickSum= tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time
                        # midisList[noteOnAmount - 1 - len(tmp)][2] = tickSum + midiData.tracks[selectedTruck.get()][midiReadPosition].time 
                        
                        # tmpの一つ要素を削除
                        tmp.pop(len(tmp) - 1)

                        # 重なりが解消された直後の時だけ処理の流れが分岐するのでその判別のために重なりが解消された瞬間である事を示すフラグを立てる
                        if len(tmp) == 0:
                            endOverlappingFlag = 1

                        # ノートを一つ認識し終わったのでインデックスを更新
                        index = index + 1
                    
                    # ノートオフの数をカウントするためにインクリメント todo ここであってる？
                    noteOffAmount = noteOffAmount + 1
                    #print(tmp)

                ##print("check",midisList)
                #Qprint("=====================================")

                if noteOffAmount == noteOnAmount:
                    index = index + 1
            else:
                metaDataRows = metaDataRows + 1

            midiReadPosition = midiReadPosition + 1
        
        #最後の行のみ無意味なデータなので削除
        del midisList[- 1]

        #ノート番号
        #print(midisList)
        
        # midi読み込みフラグを立てる
        midiLoadFlag.set(True)

        # 最初のmidiノートが追加されたら内部処理メソッドを呼び出す
        midiLoadFlag.trace_add('write',midi.inner_procedure(midisList,composerData,MidiNumber2Freq))
        
        print("midi読み込みされました")

    def inner_procedure(self,midisList,composerData,MidiNumber2Freq):

        # midiが読み込まれたり最初のノートが作られたときの一連の処理
        
  
        # 抽出整理したmidiデータをコンポーザーインスタンス内のリストにデータを移す
        composerData.composerInnerData = midisList

        # ノートを描画する関数を呼び出し
        midi.drawNotes(midisList,composerData)
        
        # 各ノートの周波数データをリストに追加
        composerData.set_Frequency(MidiNumber2Freq,composerData.composerInnerData)
        
        #ダイナミクスの初期値を示すデータをリストに追加
        composerData.set_initial_Dynamics(composerData)

        # ダイナミクス制御点のキャンバス上の座標を求めて内部データリストに保存
        composerData.makeDynamicsCurve(composerData)

        # ダイナミクスカーブを描画
        application.drawDynamicsCurve(dynamicsTabCanvas,composerData)

        # ピッチカーブの初期値を設定
        composerData.set_initial_pitch_curve(composerData)

        # ピッチ制御点のキャンバス上の座標を求めて内部データリストに保存
        composerData.makePitchCurve(composerData,freq_2_ScreenPos_Table)

        #ピッチカーブの描画
        application.drawPitchCurve(pitchEditCanvas,freq_2_ScreenPos_Table,composerData)



   
    def drawNotes(self,midisList,composerData):

        #与えられたmidi（整理されているが重複を含みうる）を元にすべてのノートを描画する
        
        # デバッグ用確認表示
        #print(midisList)

        # ノート１つずつ総なめにする処理でノートを全て描画
        for index in midisList:
        
            # ノートを一つずつ描画
            midi.drawNote(pitchEditCanvas,index[0],index[1],index[2],composerData)

    def drawNote(self,pitchEditCanvas,noteNumber,startTicks,endTicks,composerData):

        # 音符そ１つ描画するメソッド

        # スケーリングに対応する為の変数　todo仮
        SCALEING_FACTOR = 2
        scalingFactorVertical = SCALEING_FACTOR

        # midiのtime=1（＝ティック数）が何ピクセルに相当するか係数を計算 x方向
        midiTimeToPxCoffecient = (1 /TIME_PER_BER) * PX_PER_BAR

        # ティック数からピクセルへ数値を変換
        startPosXPx = startTicks * midiTimeToPxCoffecient
        endPosXPx = endTicks * midiTimeToPxCoffecient

        # ノート番号とピクセルの関係を計算

        # 何オクターブ分移動したか計算　ＢＧの一部（１オクターブに一回）に１ｐｘだけ幅が異なる所があるので必要
        octaveAmount = int(noteNumber / 12)
        octaveAmount = 0#todo 仮

        # 119(C8 B)から半音何個分離れているか計算
        relativeNoteDistance = abs(noteNumber - 119)

        # ノート番号からピクセルを計算（縦方向）
        startPosYPx = relativeNoteDistance * 13 * SCALEING_FACTOR + octaveAmount
        endPosYPx  = (relativeNoteDistance + 1) * 13 * SCALEING_FACTOR + octaveAmount

        #print(octaveAmount," ",startPosXPx ," ",startPosYPx," ",endPosXPx," ",endPosYPx)

        # ノート配置
        idName = pitchEditCanvas.create_rectangle(startPosXPx, startPosYPx,endPosXPx,endPosYPx,fill="DeepSkyBlue2",tag=('disactivated','pitch'),width=0)
            
        # 描画した図形にイベント処理設定
        #クリックした時の処理を紐づけ (選択)
        #pitchEditCanvas.tag_bind(idName,"<ButtonPress-1>",partial(application.clickNote,pitchEditCanvas = pitchEditCanvas,color = 'red',idName = idName))
            
        pitchEditCanvas.tag_bind(idName,"<ButtonPress-1>",partial(application.clickNote,pitchEditCanvas = pitchEditCanvas,color = 'red',idName = idName))
        
        # ドラッグした時の処理を紐づけ（移動）
        pitchEditCanvas.tag_bind(idName,"<Button1-Motion>",partial(application.dragNoteVerticcle,pitchEditCanvas = pitchEditCanvas,scalingFactor = scalingFactorVertical,idName = idName),add = '+')

        # 右ダブルクリックした時の処理を紐づけ（削除）
        pitchEditCanvas.tag_bind(idName,"<ButtonPress-3>",partial(application.daleteNote,idName = idName),add = '+')
       
        # 下矢印で１つノートを移動させる紐づけ（移動）todo
        pitchEditCanvas.tag_bind(idName,"<KeyPress-Down>",partial(application.moveNoteDown,pitchEditCanvas = pitchEditCanvas,idName = idName,scaleingFactor = scalingFactorVertical),add = '+')
            
        # BGの色を変更する関数を紐付け
        pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'blue',idName = idName),add = '+')
          
        # BGの色を変更する関数を紐付け
        pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'DeepSkyBlue2',idName = idName),add = '+')

        # ノートの左端と右端にカーソルが来てるときにカーソルを変更する関数を紐付け
        pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.changeCousor,pitchEditCanvas = pitchEditCanvas,idName = idName),add = "+")
          
        # キャンバスを更新
        pitchEditCanvas.update()

    def kill_window(self,dlg_modal):
        
        #　ウィンドウを消す
        dlg_modal.destroy()
    
    def select_midi_track(self,composerData,MidiNumber2Freq):

        # 読み込んだを時間vs周波数と時間vs継続長のデータに変換するメソッド

        # グローバル変数としてウィジェット変数を使う
        global selectedTruck

        # タイプの設定
        type = [('MIDI','*.mid')]
   
        # デフォルトのディレクトリを設定してダイアログ表示
        readMidiData = filedialog.askopenfilename(filetypes = type,initialdir = DEFAULT_READ_LOCATION)
   
        # midiデータを読み込み変数に格納
        midiData = mido.MidiFile(readMidiData,clip=True)

        # midiの生データ確表示デバッグ用
        #print(midiData)

        # 複数のトラックからどのトラックを編集対象とするか選択させる為にダイアログを表示
        dlg_modal = tkinter.Toplevel()

        # ウィンドウの名前の指定
        dlg_modal.title("読み込むトラックを選択")

        # ダイアログのサイズの指定
        dlg_modal.geometry("200x300")

        # ウィンドウをモーダルにする
        dlg_modal.grab_set()

        # 新しく作ったダイアログにフォーカスを移す
        dlg_modal.focus_set()

        
        # ダイアログ中のトップフレームを作成
        dlgTop = tkinter.Frame(dlg_modal,width="300",height="300",bg="gray33")

        dlgTop.grid(row=0,column=0)

        # リストボックスの選択肢を作成
        trackList=[]
        

        # 各トラックのメッセージ数をカウントしてリストに追加
        for index in numpy.arange(0,len(midiData.tracks),1):
            addData = int(self.countNotes(midiData,index))
            # addData = index ,' :音符の総数',self.countNotes(midiData,index)
           
            trackList.append(addData)

        v1 = tkinter.StringVar(value = trackList)

        # リストボックスの作成
        listBox = tkinter.Listbox(dlgTop,width = 20,selectmode=tkinter.SINGLE,listvariable=v1)
        
        # リストボックスをバインド
        listBox.bind("<<ListboxSelect>>",midi.get_Truck_Index)
       
        # スクロールバーの作成
        scrollbar = ttk.Scrollbar(dlgTop,orient="vertical",command=listBox.yview)

        # スクロールバーの機能化
        listBox['yscrollcommand']= scrollbar.set

        # スクロールバーの配置
        scrollbar.grid(row=0,column=1,sticky=(tkinter.N, tkinter.S))

        # リストボックスを配置
        listBox.grid(row=0,column=0)



        # ボタンの作成
        okButton = ttk.Button(dlgTop ,text = "読み込み",command=lambda:[midi.load_Midis(midiData,composerData,MidiNumber2Freq),midi.kill_window(dlg_modal)])
        
        # ボタンの配置
        okButton.grid(row=1,column=0)

    def get_Truck_Index(self,event):

        # 選択したトラック番号をウィジェット変数に格納する

        # グローバル変数としてselectedTruckを作成
        global selectedTruck

        # イベントから現在選択されているインデックスのリストを取得
        test = event.widget.curselection()

        # リストの１番目にアクセス
        targetTruck = int(test[0])

        # 抽出した数字をウィジェット変数として保存
        selectedTruck.set(targetTruck)

class composer:

    #　作曲者モードで使用するデータと機能を定義するクラス

    ######################### アトリビュート #####################

    composerInnerData = [[]]

    ############################# メソッド ########################

    def __init___(self):

        self.composerData = [[]]  
    def paintCurve(self,dynamicsTabCanvas):

        # カーブるいをマウスで描画編集する時に呼び出されるメソッド

        pass
        #dynamicsTabCanvas.coods()
    def dragging(self,event):

        # ドラッグ中に呼び出されるイベント関数

        print("ドラッグ検出")
    def on_key_left(self,event):

        # 左マウスボタン押下の時に呼び出されるイベント関数

        print("左ボタン押下検出")
        #self.currentId = self.canvas.create_line(event.x,event.y,event.x,event.y,fill='black')
    def makeDynamicsCurve(self,composerData):

        # ダイナミクス点のキャンバス上での座標を求めるメソッド
        
        # スケーリングに対応する為の変数　todo仮


        # midiのtime=1（＝ティック数）が何ピクセルに相当するか係数を計算 x方向
        midiTimeToPxCoffecient = (1 /TIME_PER_BER) * PX_PER_BAR

        if len(composerData.composerInnerData) == 1:

            print("ダイナミクスカーブデータなし")

        else:

            # 描画対象のデータがある時

            print("ダイナミクスカーブデータを描画します")

            # デバッグ用確認表示 この時点では１.ノート番号 2.最初のティック　３。最後のティック　、４周波数の４つがデータに保存される
            #for row in composerData.composerInnerData:
                #print(row)


            for row in composerData.composerInnerData:
                
                # ダイナミクスの制御点の数を取得
                dynamicsCtlPointAmount = row[4]

                # 0除算を防ぐ
                if dynamicsCtlPointAmount != 0:
                
                    # ティック単位の制御点の間隔を計算
                    intervalTicks = (row[2] - row[1])/ dynamicsCtlPointAmount

                # ティック単位からピクセル単位の制御点の間隔に変換
                intervalPx = int(intervalTicks * midiTimeToPxCoffecient)

                # 最初の制御点のピクセルを求める
                leftEdgeCtlPointPx = int(row[1] * midiTimeToPxCoffecient)

                # 内部データに保存場所を作成
                row.append([])

                #print(row)

                # ダイナミクス制御点のスクリーン座標を求めて保存
                for dynamicsCtlPoint in row[5]:

                    # y座標を計算
                    ypos = int(DEFAULT_PARAM_WIN_HEIGHT * (1 - dynamicsCtlPoint))
                    
                    xpos = int(leftEdgeCtlPointPx) 

                    # 内部データに座標を保存
                    row[6].append([xpos ,ypos])

                    # インターバルに基づいて次の制御店のｘ座標を計算
                    leftEdgeCtlPointPx = leftEdgeCtlPointPx + intervalPx
        

                # ノートの長さがティック分解能で割り切れなかった時に備えてノートの末端に強制的にピッチ制御点を作成
                
                # y座標を計算
                ypos = int(DEFAULT_PARAM_WIN_HEIGHT * (1 - dynamicsCtlPoint))
                
                # x座標を計算
                xpos =  int(row[2] * midiTimeToPxCoffecient)
                
                # 内部データに座標を保存 末端データ
                #row[6].append([xpos ,ypos])
                
        # デバッグ用確認表示
        #print("作成したダイナミクス制御点は")
        #for row in composerData.composerInnerData:
            #print(row)

    def makePitchCurve(self,composerData,freq_2_ScreenPos_Table):

        # キャンバス上のピッチ制御点の座標を求めるメソッド
        # スケーリングに対応する為の変数　todo仮
        SCALEING_FACTOR = 2
        scalingFactorVertical = SCALEING_FACTOR

        # midiのtime=1（＝ティック数）が何ピクセルに相当するか係数を計算 x方向
        midiTimeToPxCoffecient = (1 /TIME_PER_BER) * PX_PER_BAR

        if len(composerData.composerInnerData) == 1:

            print("ピッチカーブデータなし")

        else:

            # 描画対象のデータがある時

            print("ピッチカーブデータを描画します")

            # デバッグ用確認表示
            #for row in composerData.composerInnerData:
                #print(row)


            for row in composerData.composerInnerData:
                
                # ダイナミクスの制御点の数を取得
                dynamicsCtlPointAmount = row[4]

                # ダイナミクスの制御点の数はピッチ制御点の数と同じなので代入
                pitchCtlPointAmount = dynamicsCtlPointAmount

               # print(row[2]," ",row[1]," ",pitchCtlPointAmount)

                if pitchCtlPointAmount != 0:
                
                    # ティック単位の制御点の間隔を計算
                    intervalTicks = (row[2] - row[1])/ pitchCtlPointAmount

                # ティック単位からピクセル単位の制御点の間隔に変換
                intervalPx = int(intervalTicks * midiTimeToPxCoffecient)

                # 最初の制御点のピクセルを求める
                leftEdgeCtlPointPx = int(row[1] * midiTimeToPxCoffecient)

                # 内部データに保存場所を作成
                row.append([])

                # ピッチ制御点の周波数をもとめて保存
                for pitchPoint in row[7]:

                    # y座標を計算
                    ypos = freq_2_ScreenPos_Table.interpolateYPos(pitchPoint)
                    
                    xpos = leftEdgeCtlPointPx 

                    # 内部データに座標を保存
                    row[8].append([xpos ,ypos])


                    leftEdgeCtlPointPx = leftEdgeCtlPointPx + intervalPx
        
                # ノートの長さがティック分解能で割り切れなかった時に備えてノートの末端に強制的にピッチ制御点を作成
                
                # y座標を計算
                ypos = freq_2_ScreenPos_Table.interpolateYPos(pitchPoint)
                
                # x座標を計算
                xpos =  int(row[2] * midiTimeToPxCoffecient)

                # 内部データに座標を保存
                row[8].append([xpos ,ypos])

        # デバッグ用確認表示
        print("作成したピッチ制御点は")
        #for row in composerData.composerInnerData:
          #  print(row)

    def setMidiData(self,midisList):

        # midiデータから抽出整理したデータをコンポーザーインスタンスのリストに入れてるだけ
        composerInnerData = midisList

        print("セットされたデータは",composerInnerData)
    
    def check_curren_Inner_Data(self,composerData):

        # 現在の内部データをデバッグ時に確認表示するメソッド

        print("現在の作曲者内部データのリスト")

        # 各行ごとに内容を表示
        for index in composerData.composerInnerData:
            print(index)

    def set_initial_Dynamics(self,composerData):

        #各ノートのダイナミクスの初期値を設定するメソッド

        # デバッグ用確認表示
        #self.check_curren_Inner_Data(composerData)

        # 行カウント用変数の定義
        index = 0

        # midi整理データを総なめにする処理
        for row in composerData.composerInnerData:
            

            # 対象ノートが発音されるティック数を計算
            ticks = composerData.composerInnerData[index][2] - composerData.composerInnerData[index][1]
            
            # ダイナミクスの制御点の数をカウントする変数を用意
            dynamicsCtlPointAmount = 0

            # 制御点をカウント
            for index2 in numpy.arange(0,ticks,TIME_2_TICK_RESOLUTION):
                
                # 制御点カウントの為インクリメント
                dynamicsCtlPointAmount = dynamicsCtlPointAmount + 1   

            # 末尾の値を考慮して１プラス
            dynamicsCtlPointAmount = dynamicsCtlPointAmount + 1

            # デバッグ用確認表示
            #print("ダイナミクス制御点の数は",dynamicsCtlPointAmount,"　ティック数は",ticks,"　分解能は",TIME_2_TICK_RESOLUTION)


            # 内部データの４列目(要素が制御点のリスト)を作成
            row.append(dynamicsCtlPointAmount)

           

            # ダイナミクス制御点の初期値をセットするリストを作成
            dynamics=[]
            # 対象ノートが発音されるティック数 ダイナミクスの分解能はここで決まる
            for index2 in numpy.arange(0,dynamicsCtlPointAmount * TIME_2_TICK_RESOLUTION,TIME_2_TICK_RESOLUTION):
                 dynamics.append(INITIAL_DYNAMICS_VALUE)
            
            #print(dynamics)
            # ノートの右側末端で強制的にダイナミクス制御点を作成する
            dynamics.append(INITIAL_DYNAMICS_VALUE)

            # 内部データの５列目(要素が制御点のリスト)を作成
            row.append([])

            # 作成した空のダイナミクス用リストをmidi整理データに挿入
            row[5] = dynamics

            # 次の行の為に現在の行の変数をインクリメント
            index = index + 1
      
        # デバッグ用確認表示
        self.check_curren_Inner_Data(composerData)

    def set_initial_pitch_curve(self,composerData):

        # ピッチ曲線の初期値を与える

        # 行カウント用変数の定義
        index = 0

        # midi整理データを総なめにする処理
        for row in composerData.composerInnerData:
            
            #各ノート事に格納するピッチの値のリストを最初空の状態で作る
            pitch=[]
            
            # 対象ノートが発音されるティック数を計算
            ticks = composerData.composerInnerData[index][2] - composerData.composerInnerData[index][1]
            
            # ダイナミクスの制御点の数をカウントする変数を用意
            pitchCtlPointAmount = 0

            # 制御点をカウント
            for index2 in numpy.arange(0,ticks,TIME_2_TICK_RESOLUTION):
                
                # 制御点カウントの為インクリメント
                pitchCtlPointAmount = pitchCtlPointAmount + 1   

            pitchCtlPointAmount = pitchCtlPointAmount + 1

            # デバッグ用確認表示
            #print("ピッチ制御点の数は",pitchCtlPointAmount,"　ティック数は",ticks,"　分解能は",TIME_2_TICK_RESOLUTION)

            # 内部データの４列目(要素が制御点数)を作成
            row.append([])

            # 最初のリストの値は制御点の数を代入
            row[0] = pitchCtlPointAmount
           
            # 対象ノートが発音されるティック数 ダイナミクスの分解能はここで決まる
            for index2 in range(0,ticks - TIME_2_TICK_RESOLUTION,TIME_2_TICK_RESOLUTION):
                 pitch.append(row[3])
            
            #print(dynamics)

            # 内部データの５列目(要素が制御点のリスト)を作成
            row.append([])

            # 作成した空のダイナミクス用リストをmidi整理データに挿入
            row[7] = pitch

            # 次の行の為に現在の行の変数をインクリメント
            index = index + 1
      
        # デバッグ用確認表示
        self.check_curren_Inner_Data(composerData)

    def set_Frequency(self,table,composerInnerData):

        # 周波数と鍵盤番号の関係テーブルと整理したmidiデータから全ノートの周波数をデータ追加
        
        #print(table)
        # midi整理データを総なめにする処理
        count2=0
        for indexs in composerInnerData:
            
            #検索したい数値を取得
            searchNumber = indexs[0]

            # 対応する周波数を格納する変数を定義
            frequency = 0

            # カウンタ用変数を定義
            count = 0
            
            # 周波数と鍵盤番号の対応テーブルを総なめにする処理
            for row in table:
            
                if searchNumber == int(row[0]): 

                    #
                    frequency = float(row[1])
                    
                    break
                count = count + 1
            # ４番目の要素を作る
            indexs.append([])
            
            # 値を4番目の所に格納
            indexs[3] = frequency
            count2 = count2 + 1

class freqency_2_Screenpos_Table:

    # 周波数とスクリーン上（キャンバスの座標系での）の位置関係を作るテーブルを定義するクラス

    # アトリビュートの定義
    table = []

    # メソッドの定義
    def __init__(self):

        # リストを作成
        self.table = []


    def interpolateYPos(self,input):

    # 周波数が入力されたらピクセルを、ピクセルが入力されたら周波数を線形補間して返すメソッド
        
        #for row in self.table:
          #  print(row)

        if type(input) == int:

            # 入力が整数でノート番号の時
            print("鍵盤番号が入力されました")
        else:

            # 入力が実数で周波数が渡された時の処理
            #print("周波数が入力されました")

            # 引数と対応テーブルの各周波数の差を計算（最小を求めたい）十分大きな数字ならよい
            differenceInput2Table = 9999

            # テーブルとの差が最小になるテーブルの行を格納する
            minId = 0

            # 対応表を行についてループする
            for row in range(0,len(self.table) - 1,1):

                #print("row",row," input",input)
                
               # print("対応行",self.table[row][0],self.table[row][1])
               #print("次の行",self.table[row + 1][0],self.table[row + 1][1])
                
                ratio = ( input - float(self.table[row + 1][1])) / (float(self.table[row + 1][1]) - float(self.table[row][1])) 

                #print(float(self.table[row + 1][1])," ",float(self.table[row][1]))," ",ratio ," ",float(self.table[row][0] )

                result = int(float(self.table[row + 1][0] - (float(self.table[row + 1][0]) - float(self.table[row][0])) * abs(ratio) ))

                #print("比",ratio,"result",result)

                #print("===================================") 

                # 比が０以下になったら対応表内の該当する項目をスキャンが通過した事になるのでループを抜ける
                if ratio <= 0:
                    break
                
        # 整数値に丸めて出力
        return  result


    def set_up_Table(self,freq_2_ScreenPos_Table,MidiNumber2FreqTable):

        # テーブルの２列目（midiノート番号）を周波数に直しテーブルを完成させるメソッド
        
        KEY_OCTAVE_AMOUNT = 10
        SCALEING_FACTOR = 2 #todo 仮
        midiKeyNumber = 120

         # 10   5オクターブ分(厳密にはノート番号０から??まで扱う)繰り返し描画横方向の帯を白鍵黒鍵に対応する形の色で描画 上から順番に描画している　2000は十分大きな数字ならなんでもよい
        for index in numpy.arange(0,KEY_OCTAVE_AMOUNT * 150 * SCALEING_FACTOR,156 * SCALEING_FACTOR):   

            # Bに相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 0 * SCALEING_FACTOR + index) + (13 * SCALEING_FACTOR  + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


         
            # Bbに相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 13 * SCALEING_FACTOR + index) + (26 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])



            # Aに相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 26*SCALEING_FACTOR + index) + (39 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # G#に相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 39*SCALEING_FACTOR + index) + (52 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # Gに相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 52 * SCALEING_FACTOR + index) + (65 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])

      

            # F#に相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 65 * SCALEING_FACTOR + index) + (78 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # Fに相当する領域について
            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 78 * SCALEING_FACTOR + index) + (91 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])



            # Eに相当する領域について
            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 91 * SCALEING_FACTOR + index) + (104 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # Ebに相当する領域について
 
            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 104 * SCALEING_FACTOR + index) + (117 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # Dに相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 117 * SCALEING_FACTOR + index) + (130 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # C#に相当する領域について

            # midiのノート番号更新の為にディクリメント
            midiKeyNumber = midiKeyNumber - 1

             # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 130 * SCALEING_FACTOR + index) + (143 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


            # Cに相当する領域について
            midiKeyNumber = midiKeyNumber - 1
  
            # 周波数縦位置対応表作成の為に本鍵盤の縦方向のキャンバス座標を格納
            centerPos = int( ( ( 143 * SCALEING_FACTOR + index) + (157 * SCALEING_FACTOR + index) ) / 2)

            # 対応表にmidiキー番号とノート中心の縦座標を格納
            self.table.append([centerPos ,midiKeyNumber])


        # ２列目のデータを設定
        # 周波数とmidi番号のテーブルを１行ごとに総なめにする処理
        for row in self.table:

            for row2 in MidiNumber2FreqTable.table:

                if int(row2[0]) == row[1]:
                   row[1] =  row2[1]
                   break
        #print(self.table)
           
class MidiNumber2FreqTable:

    # 鍵盤番号と周波数の関係を定義するクラス

    # アトリビュートの定義
    table = [[]]

    # メソッドの定義
    def __init__(self):

        # 関係表のリストを制作

        # 空のリストを作成
        table = [[]]

    def def_table(self):

        index = 0
        with open(r"C:\Users\yuto\Desktop\projectVOICE\voice2\projectVoice2\projectVoice2\number2freq.txt",'r') as f:
            for line in f:
                tmp = line.split()
                
                self.table.append([tmp[0] ,tmp[1]])
                index = index + 1

        #print(self.table)
        # 最初の項目に空のデータが入るので削除
        del self.table[0]

        #print("表定義",self.table)
class preprocess():

    #　wavenetの学習に必要な事前処理を実装しているクラス
   
    def __init__(self):
       
        self.juliusSampleWavPath =r"C:\julius\segmentation-kit-4.3.1\wav\sample.wav"
        self.juliusSampleTxtPath =r"C:\julius\segmentation-kit-4.3.1\wav\sample.txt"
        self.juliusSampleLabPath =r"C:\julius\segmentation-kit-4.3.1\wav\sample.lab"
        self.juliusDectationPath =r"C:\julius\segmentation-kit-4.3.1"
   
    def processWavFiles(self,originalWavFolderPath):
       
       
        # ファイルパスたち todo
        backupWavFolderPath = r'C:\Users\yuto\Desktop\projectVOICE\voice2\projectVoice2\projectVoice2'

        # todo 音源ソースフォルダにアクセス
        voiceSorceFolder = os.listdir(originalWavFolderPath)
        print("対象ファイルの絶対パスは",originalWavFolderPath)
        bar = "/"#todo os依存

        # 保存のメインになる属性を追加
        #setattr(fullWavData,"fullWavData",AligmentListData)

      # フォルダないにwavが何個あるかカウント
        count =0
        for list in voiceSorceFolder:
           
            # 確認表示
            print(list)

            # 拡張子を境にファイル名を分割
            splitedName = list.split(".")

            # 拡張子がwavのものかどうかを判定
            if splitedName[1] == "wav":

                count = count+1
       
        # デバッグ用確認表示
        print("認識されたファイルの個数は",count)

        # 音声エンコード済みデータをアトリビュートに追加
        setattr(applicationFormat,"totalWavAmount",str(count))


        # プログレスバー進捗表示用カウンタをリセット
        # ウィジェット変数を作成

        pbval = tkinter.IntVar(value = 0)
       
        # プログレスバー設置
        prgressBar = ttk.Progressbar(application.window,maximum = count,length = 500,orient=tkinter.HORIZONTAL,mode="determinate",variable = pbval)

        # プログレスバーの設置
        prgressBar.grid(row=0,column=0)

        # アトリビュート名末尾につける数字インデックス用変数を定義
        targetFileIndex =0
        
        # 音源ソースフォルダの一覧アクセス用ループ
        for list in voiceSorceFolder:
           
            absFilePath = originalWavFolderPath + bar + list

            # 確認表示
            #print("現在の対象ファイル（未判定）",absFilePath)

            # 拡張子を境にファイル名を分割
            splitedName = list.split(".")

   

            # 拡張子がwavのものかどうかを判定
            if splitedName[1] == "wav":

                # 確認表示
                print("対象ファイル",splitedName[0])#todo 同名ファイルを読み込んだ時の処理がまだ

                originalFileName = splitedName[0]

                # Rを削除
                tmp = originalFileName.replace("R","")

                # _を削除
                cleanTargetFileName = tmp.replace("_","")

                print("クリナップされたファイル名は",cleanTargetFileName)
               
                # todo ファイルが開けなかった　アクセス権限が無かった時の処理がまだ
                # コピー元ファイル名を作成
                copySourceName = originalWavFolderPath + "\\" + originalFileName + ".wav"

                # コピー先ファイル名を作成
                copyToFileName = backupWavFolderPath + "\\" + "originalWav" + cleanTargetFileName + ".wav"

                # プロンプトへ表示
                print("入力ファイル"+ copySourceName + "に対して処理")

                # 該当するファイルをコピー
                shutil.copyfile(copySourceName,copyToFileName)

                # プロンプトへ表示
                print(copyToFileName+"としてバックアップへコピーしました")
               
                # juliusの対象フォルダ（wav）のsample.wavを置き換える為に削除
                print("もともと有ったsample.wavを削除しました。")
                os.remove(self.juliusSampleWavPath)

                # これから強制音素アライメントを求めるファイルとしてsample.wavをコピー
                shutil.copyfile(copySourceName,self.juliusSampleWavPath)

                # プロんプロに新しいsample.wavをおいた事を表示
                print("対象となるsample.wavを配置しました")

                # wavファイルの形式を16kHz, 16bit, RAW にす
                y, sr = librosa.core.load(self.juliusSampleWavPath, sr=16000, mono=True) # 22050Hz、モノラルで読み込み
                soundfile.write(self.juliusSampleWavPath, y, sr, subtype="PCM_16") #16bitで書き込み
               
                # sample.txtを開くjuliusの仕様に合わせて'utf-8で読み込み
                with open(self.juliusSampleTxtPath,mode ='w', encoding='utf-8') as f:

                    # 内容を指定しjuniusのサンプルｔｘｔに書き込み
                    f.write(cleanTargetFileName)
                   
                    # プロンプトに現在の強制アライメントの元になるテキストデータを表示
                    print("音素アライメント検出元のテキストは "+ cleanTargetFileName+" です")
               
                # 強制音素アライメントをリスト形式で取得
                AligmentListData = self.getForceAligment()

                # アライメントの数を取得
                alignmentAmount= len(AligmentListData)

                print("アライメント数",alignmentAmount)
                # 音素アライメントを表示
                print("取得したアライメントは")
                for index in AligmentListData:
                  print(index)

                # f0対数周波数データを求めてグラフにプロット
                estimatedf0data, estimatedLogf0 ,f0time= self.getLogf0(copyToFileName)
               
                # 音素をテキストから抽出
                phones = pyopenjtalk.g2p(cleanTargetFileName,kana=False)

                # 確認表示
                print("正解の音素は"+phones)

                # フルコンテキストラベルの抽出
                fullcontextLabel = pyopenjtalk.extract_fullcontext(cleanTargetFileName)

                # フルコンの確認表示
                #print(fullcontextLabel[0])
                for label in fullcontextLabel:
                   
                    #今の音素を表す行を確認表示
                    #print(label)

                    # フルコンテキストラベルから冒頭の特徴量５つ（該当音素と前後2つの音素）を抽出　正規表現の代わり
                    #^で分
                    tmp = label.split('^')
                    # 文字型歳て1つ目の音素を取得
                    prePre = tmp[0]

                    # 対象文字列を数値に変換
                    prePre = self.convertString2ints(prePre)

                    #+で分割
                    tmp = tmp[1].split('+')
                    pre = tmp[0]
                   
                    # 対象文字列を数値に変換
                    pre = self.convertString2ints(pre)
                   
                    #=で分割
                    tmp = tmp[1].split('=')

                    target = tmp#todo
                    next = tmp[0]
                    # 対象文字列を数値に変換
                    next= self.convertString2ints(next)

                    # 最後の音素
                    nextNext = tmp[1]
                    nextNext= self.convertString2ints(nextNext)

                    # 抽出したカテゴリ特徴量を表示
                    print("音素に関する特徴量は")
                    characterAmount = prePre,' ',pre,' ',target,' ',next,' ',nextNext
                   
                    # 確認表示
                    print(characterAmount)


                    encodedCharacter = ord('x')#todo 数値へ変換する関数の実装あやふや
                    # 数値に変換した特徴量を表示
                    print("数値に変換した特徴量は")

                # fo検出時に生成した時刻についてについて
                # 現ループでの追加アトリビュート名を生成
                f0TimeAttributeName = "f0Time" + str(targetFileIndex)

                # 時刻をアトリビュートに追加
                setattr(applicationFormat,f0TimeAttributeName,f0time)

                # F予測の最高周波数を求める
                estimatedf0Max = max(estimatedf0data)

                # 生の音声データをtorchaudioとして読み込み
                waveform,rawWavSampleRate = torchaudio.load(filepath = copySourceName)

                # ミューロー圧縮を実行
                waveformEncoded = torchaudio.transforms.MuLawEncoding()(waveform)

                # 元の音声データについて
                # 現ループでの追加アトリビュート名を生成
                originalWavAttributeName = "originalWav" + str(targetFileIndex)

                # 音声元データをアトリビュートに追加
                setattr(applicationFormat,originalWavAttributeName,waveform)

                # 録音時間[s]について
                # 本wavの収録時間[s]を計算 todo 未チェック
                recordingTime =  torch.numel(waveform) / rawWavSampleRate
                # 現ループでの追加アトリビュート名（録音時間用）を生成
                originalWavRecordingTimeAttributeName = "originalWavRecordingTime" + str(targetFileIndex)

                # 音声元データをアトリビュートに追加
                setattr(applicationFormat,originalWavRecordingTimeAttributeName, recordingTime)

                # 確認
                print("レコーディング時間は",recordingTime)
                # サンプリングレートについて
                # 現ループでの追加アトリビュート名を生成
                originalWavSamplingRateSAttributeName = "rawWavSampleRate" + str(targetFileIndex)

                # オリジナル音声のサンプリングレートをアトリビュートに追加
                setattr(applicationFormat,originalWavSamplingRateSAttributeName,rawWavSampleRate)
 
                # 正解発音について
                # 現ループでの追加アトリビュート名(正解発音)を生成
                correctPhones = "correctPhones" + str(targetFileIndex)

                # オリジナル音声のサンプリングレートをアトリビュートに追加
                setattr(applicationFormat,correctPhones,cleanTargetFileName)

                # 強制音素アライメントについて
                # 現ループでの追加アトリビュート名(強制音素アライメント)を生成
                PhonesAlignmentAtrributeName = "PhonesAlignment" + str(targetFileIndex)

                # 強制音素アライメントをアトリビュートに追加
                setattr(applicationFormat,PhonesAlignmentAtrributeName,AligmentListData)
               

                # 強制音素アライメントについて
                # 現ループでの追加アトリビュート名(強制音素アライメント)を生成
                PhonesAlignmentAmountAtrributeName = "PhonesAlignmentAmount" + str(targetFileIndex)

                # 強制音素アライメントをアトリビュートに追加
                setattr(applicationFormat,PhonesAlignmentAmountAtrributeName,alignmentAmount)


                # 予測ｆ０について
                # 現ループでの追加アトリビュート名(予測ｆ０)を生成
                f0AtrributeName = "estimatedf0" + str(targetFileIndex)

                # 予測ｆ０をアトリビュートに追加
                setattr(applicationFormat,f0AtrributeName,estimatedf0data)
               
                # 対数じゃないF0予測の最高周波数のアトリビュートを確保
                f0MaxFAtrributeName = "estimatedf0MaxF" + str(targetFileIndex)

                # 予測ｆ０をアトリビュートに追加
                setattr(applicationFormat,f0MaxFAtrributeName,estimatedf0Max)
               
                # 予測対数ｆ０について
                # 現ループでの追加アトリビュート名(予測ｆ０)を生成
                logF0AtrributeName = "estimatedLogf0" + str(targetFileIndex)

                # 予測ｆ０をアトリビュートに追加
                setattr(applicationFormat,logF0AtrributeName,estimatedLogf0)


                # 検出音素について
                # 現ループでの追加アトリビュート名(検出音素用)を生成
                correctPhones = "correctPhones" + str(targetFileIndex)

                # オリジナル音声のサンプリングレートをアトリビュートに追加
                setattr(applicationFormat,correctPhones,cleanTargetFileName)
               
                # エンコードした言語特徴量について
                # 現ループでの追加アトリビュート名(正解発音)を生成
                correctPhones = "lingChara" + str(targetFileIndex)

                # オリジナル音声のサンプリングレートをアトリビュートに追加
                setattr(applicationFormat,correctPhones,cleanTargetFileName)
               
                # 自作の特徴量について
                # 現ループでの追加アトリビュート名(正解発音)を生成
                correctPhones = "addCharactor" + str(targetFileIndex)

                # オリジナル音声のサンプリングレートをアトリビュートに追加
                setattr(applicationFormat,correctPhones,cleanTargetFileName)
       
                #print(applicationData.originalWav0)
                #　プロンプトに区切り線を表示
                print("==========================================================")

                #プログレスバー更新
                pbval.set(pbval.get() + (100 / count))

                # プログレスバーが満タンになったらプログレスバー自体を削除
                if pbval.get() >= 100:
                    prgressBar.destroy()

                # データ名添え字用文字のインクリメント
                targetFileIndex = targetFileIndex + 1
           
    def convertString2ints(self,targetStrings):
   
        # 文字列を1文字ずつのリストに変換
        chatsList= list(targetStrings)

        # 結果保存用（int　）の変数を確保
        #result
                 
        # 1文字ごとのループ処理
        for index in chatsList:

            # アスキー文字コード表に合わせて1つ目の音素を数値（int）に変換
            tmp = ord(index)
        return tmp            
    def getForceAligment(self):

        # juliusの処理結果を受け取り強制音素アライメントを読み込むメソッド
       
        # コマンドプロンプトでセグメンテーションきっとのあるディレクトリに移動
        subprocess.run('perl segment_julius.pl',shell =True,cwd = self.juliusDectationPath )
   
        # ファイルを開く　結果を保存するlabファイル
        f = open( self.juliusSampleLabPath,'r',encoding='UTF-8')
       
 

        # 格納予定のリストの空を作る
        data = []
       
         # ファイルを読み込み
        for line in f:
            line = line.strip()
            line = line.replace('\n','')
            line = line.split(" ")
            data.append(line)
       
        # ファイルハンドラを閉じる
        f.close()

        # 確認表示
       # print("検出したワードは" + data)
       
        # 強制音素アライメントを表現したリストを返却
        return data
   
    def getLogf0(self,fileFullPath):
 
        # ファイルを開く
        samplingFrequency,data = read(fileFullPath)

        # x軸の単位をｓに変更
        x = [q/samplingFrequency for q in numpy.arange(0,len(data),1)]
       
        #todo cpu gpu判

        #仕様に合わせる為にfloatへ型変換
        data = data.astype(float)
       
        # f0対数周波数のデータ群を収納するテンソルデータを確保
        f0dats = torch.Tensor([[0,0]])
       
        # f0基本周波数の抽出
        f0,time = pw.dio(data,samplingFrequency)
       
        # 対数基本周波数に変換
         # データのコピー
        logf0= f0.copy()

        # 非０のインデックス配列を取得
        nonZeroIndex = numpy.nonzero(f0)

        # 対数ｆ０周波数を計算
        logf0[nonZeroIndex] = numpy.log(f0[nonZeroIndex])

        f0 = pw.stonemask(data,f0,time,samplingFrequency)

        return f0 ,logf0,time        
class gui:

    def __init__(self):

        # 初期化メソッド
       
        super().__init__()

        # ウィンドウの作成
        self.window = tkinter.Tk()

        # ウィンドウの名前を設定
        self.window.title("VOICE")

        # ウィンドウサイズ指定用の文字列を指定
        x = 'x'
        windowSize = str(WINDOW_WIDTH_PX) + x + str(WINDOW_HEIGHT_PX)

        # ウィンドウの大きさを初期設定
        self.window.geometry(windowSize)
   
        # ウィンドウの最大の大きさを設定
        self.window.maxsize(width=1500,height=1000)

        # ウィンドウの最小の大きさを設定
        self.window.minsize(width=400,height=400)

        # フレームないにラベルが来てもフレームのサイズが変わらないように設定
        self.window.propagate(False)
 

    def getWindowSize(self,event):

        # 現在のウィンドウサイズをウィジェット変数に保存するメソッド

        print(self.window.winfo_height()," ",self.window.winfo_width())
        
        # ウィジェット変数に現在のウィンドウのサイズを保管
        windowWidth.set(self.window.winfo_height())
        windowHeight.set(self.window.winfo_width())

    def drawSoundEditDisplay(self,applicationFormat,application):

        # 画面全体を形作るフレームを作成
        editSoundsFrame=tkinter.Frame(self.window,width=300,height=100,bg = 'gray',bd = 0)

        # フレームを横幅いっぱいまで広げて配置
        editSoundsFrame.grid(row=0,column=0,sticky="nsew",rowspan=2,columnspan=2)  
        editSoundsFrame.grid_columnconfigure(1, weight=1)

        # ウィジェットの自動調整を解除
        editSoundsFrame.grid_propagate(False)

        # 何も読み込まれていないで最初にこの画面を表示する為の処理
        if hasattr(applicationFormat,'modelDisplayPermitation') == False:
             
            #初めてなので強制的に音源表示の許可を出すように設定する
            setattr(applicationFormat,'modelDisplayPermitation',True)

            print("アトリビュートがないの作りました",applicationFormat.modelDisplayPermitation)
       
        print("許可判定は",applicationFormat.modelDisplayPermitation)

        # 表示が許可されているかで条件分
        if applicationFormat.modelDisplayPermitation==True:#todo　デバッグ中変更

            # wavファイルが何も読み込まれていない時

            # 背景用のフレームを作成
            dataFrame = tkinter.Frame(editSoundsFrame,width=1000,height=1000,bg='white')
            
            # フレームの自動調整機能をオフにする
            dataFrame.grid_propagate(False)

            # 背景用のフレームを表示
            dataFrame.grid(row=1,column=0,columnspan=2)

            #スクロール用キャンバスを作成　注意！これは画面中央の白いキャンバスであってヘッダではない　前方参照を防ぐためにここに記述している。
            tableCanvas = tkinter.Canvas(dataFrame,bg = 'white',width=975,height=900,scrollregion=(0,0,975,1300))
            

            # キャンバスの中にフレームを置く 注意！これは画面中央の白いフレームであってヘッダではない　前方参照を防ぐためにここに記述している。
            whiteFrame = tkinter.Frame(tableCanvas,width=975,height=1200,bg = 'white')

            # 基本設定部の記述
            menus = tkinter.Frame(editSoundsFrame,width=1300,height=140,bg = 'gray18',bd = 0)

            # 自動サイズ調整機能をオフ
            menus.grid_propagate(False)
           
            # 諸設定を包むフレームを表示
            menus.grid(row=0,column=0,columnspan="2")


            # 基本設定部の記述
            extraSettingFrame=tkinter.Frame(menus,width=400,height=140,bg = 'gray18',bd = 0)

            # フレームサイズの自動調整を無効化する
            extraSettingFrame.grid_propagate(False)

            # 諸設定を包むフレームを画面いっぱいに表示
            extraSettingFrame.grid(row=0,column=0,sticky=tkinter.W+tkinter.E)

            # 操作カテゴリを示すラベルの作成
            label12 = tkinter.Label(extraSettingFrame,text="基本設定",bg='gray18',fg='white')
            label12.grid(row = 0,column = 0,columnspan = 3 )

            # 制作者名ラベルの作成
            label13 = tkinter.Label(extraSettingFrame,text="制作者名",bg='gray18',fg='white')
            label13.grid(row = 1,column = 0 ,sticky = tkinter.E)

            # 制作者名のテキスト入力
            createrNameTxt = tkinter.Entry(extraSettingFrame,width=30)
            createrNameTxt.grid(row = 1,column =1 ,sticky= tkinter.W)

            # キャラクタ名ラベルの作成
            charaNameLabel = tkinter.Label(extraSettingFrame,text="キャラクタ名",bg='gray18',fg='white')
            charaNameLabel.grid(row = 2,column =0 ,sticky = tkinter.E)

            # キャラクタ名のテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=30)
            charaName.grid(row = 2,column =1 ,sticky= tkinter.E)

            # 利用条件テキストファイルラベルの設定
            label10 = tkinter.Label(extraSettingFrame,text="利用条件テキストファイル",bg='gray18',fg='white')
            label10.grid(row = 3,column =0 ,sticky = tkinter.E)

            # 利用条件テキストファイルののテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=20)
            charaName.grid(row = 3,column =1 ,sticky= tkinter.E)


            # readMeテキスト設定のラベルを設定
            label10 = tkinter.Label(extraSettingFrame,text="ReadMe.txtの設定",bg='gray18',fg='white')
            label10.grid(row = 4,column =0 ,sticky = tkinter.E)

            # readMeテキスト設定のテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=20)
            charaName.grid(row = 4,column =1 ,sticky= tkinter.E)

            # ユーザー閲覧許可設定のラベル
            label11 = tkinter.Label(extraSettingFrame,text="使編集画面の閲覧と編集を許可",bg='gray18',fg='white')
            label11.grid(row = 5,column =0 ,sticky = tkinter.E)

            # ラジオボタンが初期設定でオンになっているものを指定する変数を確保
            radioChecked = tkinter.IntVar()

            # 許可するにチェック
            radioChecked.set(0)

            # ラジオボタンの作成
            permited = tkinter.Radiobutton(extraSettingFrame,value = 0,variable = radioChecked,text="する",bg='gray18',fg='white')
            notPermited = tkinter.Radiobutton(extraSettingFrame,value = 1,variable = radioChecked,text="しない",bg='gray18',fg='white')

            # ラジオボタンの配置
            permited.grid(row = 5,column =1)
            notPermited.grid(row = 5,column =2)


            # 録音部の記述
            RecordingFrame=tkinter.Frame(menus,width=180,height=140,bg = 'gray30',bd = 0)

            
            # フレームサイズの自動調整を無効化する
            RecordingFrame.grid_propagate(False)
            
            # フレームを画面いっぱいに表示
            RecordingFrame.grid(row = 0,column = 1)


            # 録音カテゴリを示すラベルの作成
            recordingLabel = tkinter.Label(RecordingFrame,text="録音",bg='gray30',fg='white')
            recordingLabel.grid(row = 0,column = 0,columnspan = 2)
            
            



            # 発音名を示すラベルの作成
            recordingLabel = tkinter.Label(RecordingFrame,text="発音",bg='gray30',fg='white')
            recordingLabel.grid(row = 1,column = 0)

            # 発音名のテキスト入力部分の作成
            RecordingName = tkinter.Entry(RecordingFrame,width=20)
            RecordingName.grid(row = 1,column =1 ,sticky= tkinter.E)

            # 録音ボタンを定義
            recordingButton= tkinter.Button(RecordingFrame,text ="●",width=8,height=3,command =lambda:application.recordSound(applicationData,preprocessFrame))

            # 録音ボタンを設置 tkinter.W+tkinter.
            recordingButton.grid(row=2,column=0,columnspan = 2)




            # 音声フォルダ読み込みセクション用のフレームを作成
            soundLoadFrame = tkinter.Frame(menus,width=200,height=140,bg='gray18')

            # 自動サイズ調整機能をオフに
            soundLoadFrame.grid_propagate(False)

            # 音声フォルダ読み込みセクションをグリッド配置
            soundLoadFrame.grid(row=0,column=2)
            
            # フォルダ読み込み用ボタンを作成
            loadFolderButton= tkinter.Button(soundLoadFrame,text ="音声フォルダの読み込み",width=20,height=2,command =lambda:application.loadWavs(whiteFrame))

            # ボタンの配置
            loadFolderButton.grid(row = 1,column = 0,columnspan = 2)

            # 前処理部の記述
            preprocessFrame=tkinter.Frame(menus,width=200,height=140,bg='gray30')

            # フレームサイズの自動調整を無効化する
            preprocessFrame.grid_propagate(False)

            # フレームを表示
            preprocessFrame.grid(row = 0,column = 3)
           
            # 操作カテゴリを示すラベルの作成
            preprocessLabel = tkinter.Label(preprocessFrame,text="前処理",bg='gray30',fg='white')
            preprocessLabel.grid(row = 0,column = 0)


            # 抽出音素とファイル名の比較ボタンを定義
            loadFolderButton= tkinter.Button(preprocessFrame,text ="検出音素と実発音が違うデータを削除",width=26,height=3)

            # 抽出音素とファイル名の比較ボタンを設置
            loadFolderButton.grid(row=1,column=0)


            # 学習部の記述
            learningFrame=tkinter.Frame(menus,width=140,height=140,bg = 'gray18',bd = 0)

            # 自動調節をオフに
            learningFrame.grid_propagate(False)

            # 操作カテゴリを示すラベルの作成
            learningLabel = tkinter.Label(learningFrame,text="学習",width=10,bg='gray18',fg='white')

            # 操作カテゴリを示すラベルの配置
            learningLabel.grid(row = 0,column = 0)

            # フレームを画面いっぱいに表示
            learningFrame.grid(row = 0,column = 4)

            # モデルの学習ボタンを作成
            modelLearnButton= tkinter.Button(learningFrame,text ="モデルの学習",width=14,height=3)

            # モデル学習ボタンの配置
            modelLearnButton.grid(row=1,column=0,padx=20)



            # モデルの書き出し部の記述
            exportLabel=tkinter.Frame(menus,width=200,height=140,bg = 'gray30',bd = 0)

            # 自動配置をオフに
            exportLabel.grid_propagate(False)

            # モデル書き出し部の配置
            exportLabel.grid(row = 0,column = 5)

             # 操作カテゴリを示すラベルの作成(モデル書き出し)
            expoteModel = tkinter.Label(exportLabel,text="書き出し",bg='gray30',fg='white')

            # 自動サイズ調整をオフに
            expoteModel.grid_propagate(False)
            expoteModel.grid(row = 0,column = 0)

            # モデルの学習ボタンを作成
            export= tkinter.Button(exportLabel,text ="モデルの書き出し",width=12,height=3)

            # モデル学習ボタンの配置
            export.grid(row=1,column=0)

            

            # 垂直のスクロールバーを作成
            ybar = tkinter.Scrollbar(dataFrame,orient=tkinter.VERTICAL,command = tableCanvas.yview)

            # キャンバススクロール時に実行する処理を設定 ##
            tableCanvas.configure(yscrollcommand = ybar.set)

            # 垂直スクロールバーの配置
            ybar.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)
   
            # キャンバスのサイズの自動調整機能のオフ
            tableCanvas.grid_propagate(False)

            # スクロールするキャンバスを配置
            tableCanvas.grid(row=0,column=0)

            # キャンバスサイズ自動調整機能をオフに
            whiteFrame.grid_propagate(False)
            
            # キャンバスの内側にあるフレームの配置
            whiteFrame.grid(row=0,column=0)

            # キャンバスにウィジェットを配置
            tableCanvas.create_window((0,0),window=whiteFrame,anchor="nw")

            # 内側のフレームを更新？
            whiteFrame.update_idletasks()
            tableCanvas.config(scrollregion=tableCanvas.bbox("all"))
            
            # データテーブルと読み込みボタンを生成表示
            application.loadDataTable(whiteFrame)

            #test=tkinter.Label(tableInner,text="test")

            #test.grid(row=0,column=0)

        else:

            # デバッグ用確認表示
            print("表示不許可設定を検出")


            # インデックスよう
            index = tkinter.Frame(editSoundsFrame,width=1000,height=1000,bg = 'gray22')
            index.grid(row=1,column=0,columnspan=3)

            # 見出しの作成
            soundEditFrame = tkinter.Label(index,text="音源クリエーターの意向により内部データを表示しません",font=big)
            soundEditFrame.grid(row = 0,column =0 )
   
    def loadDataTable(self,whiteFrame):
        
        # データテーブルを生成表示
        table = tkinter.Frame(whiteFrame,width=800,height=1000,bg='red')

        table.grid_propagate(False)            
        table.grid(row=0,column=0)#ここの４はtodo

        # wavデータが０かそれ以外かで条件分岐
        if applicationFormat.totalWavAmount != 0:

            # wavデータの数だけループ処理    for index in numpy.arange(0,int(applicationFormat.totalWavAmount) + 1,1):

            for index in numpy.arange(0,2,1):

                # 本レコードを格納するフレームを作成
                tableRecord = tkinter.Frame(table,width='800',height=200,bg = 'yellow',bd = 2,relief="ridge")
               
                # 見出しを書く
                if index == 1:
                    
                     # 本レコードを格納するフレームを作成
                    indexLabel = tkinter.Frame(table,width='800',height=100,bg = 'yellow',bd = 2,relief="ridge")
                    # 左側のラベルを作成
                    indesLabelLeft = tkinter.Label(indexLabel,text="ピッチと音素の区切り")
                    indesLabelLeft.grid(row=0,column=0)

                    # 右側のラベルを作成
                    indesLabelRight = tkinter.Label(indexLabel,text="検出された音素と実際の音素")
                    indesLabelRight.grid(row=0,column=0)

                # レコードを配置
                tableRecord.grid(row=index + 1,column=0)

                # グラフの描画 キャンバス
                graphCanvas = application.drawFigAsFrame(applicationFormat,index)
      
                graphCanvas.grid_propagate(False)
                graphCanvas.grid(in_=tableRecord,row=0,column=0)
               
                # 録音カテゴリを示すラベルの作成
                phoneLabel = tkinter.Label(tableRecord,text="音素")
                phoneLabel.grid(row = index,column = 1)

                # 音素についてのループ
                for phone in numpy.arange(0,len(getattr(applicationFormat,"PhonesAlignment" + str(index)))-2,1):

 
                    # 音素の名前を取得
                    alignmentName = getattr(applicationFormat,"correctPhones" + str(index))


                    # アライメントの数だけチェックボックスを表示
                    alignment = tkinter.Checkbutton(tableRecord,text = alignmentName[phone])

                    # チェックボックスの配置
                    alignment.grid(row = phone,column =1)
                
        else:

            # データが読み込まれていない時の処理

            print("wavデータなし")
       
            # 録音カテゴリを示すラベルの作成
            noWavsLabel = tkinter.Label(table,text="WAVファイルが読み込まれていません。ヘッダーから録音または音声フォルダを指定してください。")
            noWavsLabel.grid(row = 0,column = 0)
           

    def drawComposerDisplay(self,applicationFormat,application,table,freq_2_ScreenPos_Table,composerData):

        ##############################################　楽曲クリエーター用画面 ####################################
        

        # 全体を包むフレームを作成 
        totalFrame = tkinter.Frame(application.window,bg='black')

        # 全体を包むフレームを画面いっぱいに表示
        totalFrame.grid(row=0,column=0,sticky="nsew")
        
        # メインエリア（key,pitch,パラメタの合体部分）のフレームを作成
        mainFrame = tkinter.Frame(totalFrame,bg = 'orange')

        # メインエリアの描画
        application.drawMainArea(mainFrame,totalFrame,table,freq_2_ScreenPos_Table,composerData)

        # ツールエリア（右側）のフレームを作成
        optionFrame = tkinter.Frame(application.window,width=WINDOW_WIDTH_PX * RATIO_MAIN_2_TOTAL_WIDTH ,height=WINDOW_HEIGHT_PX ,bg = "gray",bd = 2)

        # ツールエリアの描画
        application.drawToolsArea(optionFrame)

    def drawMainArea(self,mainFrame,totalFrame,table,freq_2_ScreenPos_Table,composerData):

        # メインエリア中を描画するメソッド
        
        # 別の場所で使うのでグローバル変数としてキャンバスを定義
        global dynamicsTabCanvas

        # メインのフレームを描画 
        mainFrame.grid(row = 0,column = 0,sticky="nesw")

        # ピッチ編集部のキャンバスの配置 めいいっぱいに広げる
        totalFrame.grid_columnconfigure(0,weight = 1)
        totalFrame.grid_rowconfigure(0,weight = 1)

        # key,pitch vs パラメタのパンウィンドウを作る
        keyPitchVsParametorWindow = tkinter.PanedWindow(mainFrame,orient = tkinter.VERTICAL,sashwidth=5,bg="gray33")

        # 鍵盤とピッチ操作部が合体したフレームを定義する
        pitchAndKey = tkinter.Frame(keyPitchVsParametorWindow ,bg = "red",bd = 0,height=200)

        # パラメータのフレームを作成
        paramatorFrame = tkinter.Frame(keyPitchVsParametorWindow,bg = "green",bd = 0,height=200,width=400)
     
   
        # パラメータ

        # メーターとぱらめーた部を囲うふれーむの描画
        paramatorFrame.grid(row=0,column=0)

        #メーターとパラメータ部を囲うフレームを限界まで広げる
        paramatorFrame.columnconfigure(0,weight=1)
        paramatorFrame.rowconfigure(0,weight=1)


        # メーター部とパラメータ部に分けるパンウィンドウを作成
        meterVsParmsWindow = tkinter.PanedWindow(paramatorFrame,orient = tkinter.HORIZONTAL,sashwidth=5,height=500,bg="gray33")



        # 左下のメーターゾーンのフレームを作成
        materZone = tkinter.Frame(paramatorFrame,width = C,bg='red')

        # メーターゾーンの描画
        #application.drawMeterZone(materZone)

        # パラメタ部の作成
        paramFrame = tkinter.Frame(paramatorFrame,bg = 'purple',relief = 'flat', bd = 1,width=800,height=100)
        
        
       
      

        # パラメタ設定部の描画

        # キャンバスを配置
        paramFrame.grid(row = 0,column = 1)

        # キャンバスをいっぱいに広げる
        paramFrame.columnconfigure(0,weight=1)
        paramFrame.rowconfigure(0,weight=1)

        # ノートブックを作成
        notebook = ttk.Notebook(paramFrame)

        # ノートブックのショートカットを有効化
        notebook.enable_traversal()
        
        # tab1(ダイナミクス)用フレームを作成
        dynamicsTabFrame = tkinter.Frame(notebook,bg='gray21')#'gray21

        # tab2(地声裏声)用フレームを作成
        voiceTypeTab = tkinter.Frame(notebook,bg='gray21')

        # tab1をノートブックに追加
        notebook.add(dynamicsTabFrame,text="ダイナミクス")

        # tab2をノートブックに追加
        notebook.add(voiceTypeTab,text="地声-裏声")

        # ノートブックを配置
        notebook.grid(row = 0,column = 0,stick="nswe")

        # ノートブックを横いっぱいに広げる
        notebook.columnconfigure(0,weight=1)
        notebook.rowconfigure(0,weight=1)

        # tab1内にキャンバスを描画 注意！ここだけ階層が非常に浅いこの場所で書いてるはのパラメタ部とＢＧ部のスクロールを同期させるために必要
        dynamicsTabCanvas = tkinter.Canvas(dynamicsTabFrame,bg='green',scrollregion=(0,0,INITIAL_LENGTH_PX,DEFAULT_PARAM_WIN_HEIGHT),width=INITIAL_LENGTH_PX)
        
        # 鍵盤とピッチ操作部が合体した内容の描画
        application.drawPitchAndKey(pitchAndKey,keyPitchVsParametorWindow,dynamicsTabCanvas,table,freq_2_ScreenPos_Table,composerData)

        # キャンバスの表示
        dynamicsTabCanvas.grid(row=0,column=0,sticky="nsew")

        # キャンバスの自動サイズ調整機能をオフに
        #dynamicsTabCanvas.grid_propagate(False)

        # test図形を表示
        #dynamicsTabCanvas.create_rectangle(0,0,100,100,fill = 'red')


        # キャンバスの表示領域をめいいっぱいに広げる
        dynamicsTabCanvas.grid_rowconfigure(0,weight=1)
        dynamicsTabCanvas.grid_columnconfigure(0,weight=1)
           
        # 水平スクロールバーの作成
        xbarDynamics = tkinter.Scrollbar(notebook,orient = tkinter.HORIZONTAL)

        # 縦スクロールバーの作成
        ybarDynamics = tkinter.Scrollbar(notebook,orient = tkinter.VERTICAL)

        # 水平スクロールバーの配置
        xbarDynamics.grid(row=1,column= 0 ,sticky = tkinter.W + tkinter.E)

        # 垂直スクロールバーの配置
        ybarDynamics.grid(row = 0,column = 1 ,sticky = tkinter.S + tkinter.N)

        # スクロールバー（横）の機能化
        xbarDynamics.config(command = dynamicsTabCanvas.xview)

        # プレイバーの描画
        playBarId = dynamicsTabCanvas.create_line(200,0,200,5000,fill="white",width=3,tag = "playLine")


        # プレイバーの一更新用関数への紐付け todo
        #dynamicsTabCanvas.tag_bind(playBarId,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = dynamicsTabCanvas,idName = 1))
        
        # マウスで線を描く関数を紐付け 左ボタン押下時に呼び出し
        dynamicsTabCanvas.bind(dynamicsTabCanvas,"<ButtonPress-1>",composerData.on_key_left)
        
         # マウスで線を描く関数を紐付け ドラッグ時に呼び出し
        dynamicsTabCanvas.bind(dynamicsTabCanvas,"<B1-Motion>",composerData.dragging)
       
 
        # グリッドの描画
        application.drawGrid(dynamicsTabCanvas)
        
        # パンウィンドウにフレームを追加
        meterVsParmsWindow.add(materZone,stretch='never',width=C,minsize = C)
        meterVsParmsWindow.add(paramFrame,stretch='always')

        # パンウィンドウを描画
        meterVsParmsWindow.grid(column=0,row=0,sticky=tkinter.NSEW)


        # パンウィンドウにフレームを追加
        keyPitchVsParametorWindow.add(pitchAndKey,height=500,stretch='always')
        keyPitchVsParametorWindow.add(paramatorFrame,height=200,stretch='always')

        # パンウィンドウを配置
        keyPitchVsParametorWindow.grid(row=0,column=0,sticky=tkinter.NSEW)
 
        # 描画位置の調整
        mainFrame.columnconfigure(0,weight=1)
        mainFrame.grid_rowconfigure(0,weight=1)

        # サッシュの位置を描画
        print("サッシュ位置は",keyPitchVsParametorWindow.sash_coord(0))

        
    def drawPitchAndKey(self,pitchAndKey,keyPitchVsParametorWindow,dynamicsTabCanvas,table,freq_2_ScreenPos_Table,composerData):

        # pitchAndKeyをめいいっぱい描画領域を広げる
        pitchAndKey.grid_columnconfigure(0,weight = 1)
        pitchAndKey.grid_rowconfigure(0,weight = 1)

        # key,pitch vs パラメタのパンウィンドウを作る
        keyVsPitchWindow = tkinter.PanedWindow(pitchAndKey,orient = tkinter.HORIZONTAL,sashwidth=5,height=500,bg="gray33")

        # パンドウィンドウで使用するためにキーボードのキャンバスを囲うフレームを作成
        keyFrame = tkinter.Frame(keyVsPitchWindow,bd = 0,bg='green',width = C,height=2000)


        #パンドウィンドウのサイズ設定
        keyVsPitchWindow.paneconfig(keyFrame,width=C,sticky = tkinter.E + tkinter.W + tkinter.S + tkinter.N)

        # 鍵盤部のキャンバスを作成
        keyCanvas= tkinter.Canvas(keyFrame,width = C,height=800,scrollregion = (0,0,C,3000),bd = 0,bg='gray21',relief = 'flat',highlightthickness = 0)
        
        # 鍵盤を含むキャンバスの描画
        keyCanvas.grid(row = 0,column = 0,sticky = tkinter.NS)
        
        # 鍵盤含むキャンバス部分にスクロールバーを追加（y方向）
        keyYBar = tkinter.Scrollbar(keyFrame,orient = tkinter.VERTICAL,command = keyCanvas.yview)

        # 鍵盤を含むキャンバス部にスクロールバーを追加した物を表示
        keyYBar.grid(row = 0,column = 1,sticky = tkinter.N + tkinter.S)

        # 縦スクロールを機能化
        keyYBar.config(command = keyCanvas.yview)

        # キャンバススクロール時に実行する処理を設定
        keyCanvas.config(yscrollcommand=keyYBar.set)


        # 鍵盤を含むキャンバス部に横スクロールばーを追加 一応このコードは残しておくが原則横スクロールは使用しない
       # keyYBar = tkinter.Scrollbar(keyCanvas,orient = tkinter.HORIZONTAL,command= keyCanvas.xview)
        
        # 鍵盤を含むキャンバス部に追加した横スクロールバーを表示
        #keyYBar.grid(row= 1 ,column = 0)

        # 鍵盤を描画
        application.drawKeyboad(keyCanvas)

        # ピッチ編集部のフレームを作成
        pitchEditFrame = tkinter.Frame(keyVsPitchWindow,bg = "purple",bd = 0,highlightthickness = 0)
        

        # ピッチ編集部の描画
        application.drawPitchEditArea(pitchEditFrame,keyCanvas,dynamicsTabCanvas,table,freq_2_ScreenPos_Table,composerData)

        # パンウィンドウにフレームを追加
        keyVsPitchWindow.add(keyFrame,stretch='never',width=C,minsize = C)
        keyVsPitchWindow.add(pitchEditFrame,stretch='always',width=100)

        # パンウィンドウを描画
        keyVsPitchWindow.grid(column=0,row=0,sticky=tkinter.NSEW)
    
    def detectMouceRotationY(self,event,pitchEditCanvas):
        # ピッチ編集部でのマウスホイールの回転量を取得し移動量をウィジェット変数に格納するメソッド
        
        if event.delta > 0:

            pitchEditCanvas.yview_scroll(-1,'units')

            # ウィジェット変数に格納
            xScrollAmount.set(-1)

        elif event.delta < 0:

            pitchEditCanvas.yview_scroll(1,'units')
            
            # ウィジェット変数に格納
            xScrollAmount.set(1)

        print("ウィジェット変数値は",xScrollAmount.get())
    
    def detectMouceRotationX(self,event,pitchEditCanvas,dynamicsTabCanvas):

        # ピッチ編集部でのマウスホイールの回転量を取得し移動量をウィジェット変数に格納するメソッド
               
        # スクロール幅を１ｃｍにする
        pitchEditCanvas.configure(xscrollincrement="1c")

        # スクロール幅を１ｃｍにする
        dynamicsTabCanvas.configure(xscrollincrement="1c")

        if event.delta > 0:

            #ＢＧの部分をヨコスクロール
            pitchEditCanvas.xview_scroll(-1,'units')

            # パラメータ部を横スクロール
            dynamicsTabCanvas.xview_scroll(-1,'units')

            # ウィジェット変数に格納
            xScrollAmount.set(-1)

            print("左へ")

        elif event.delta < 0:

            
            #ＢＧの部分をヨコスクロール
            pitchEditCanvas.xview_scroll(1,'units')
            
            # パラメータ部を横スクロール
            dynamicsTabCanvas.xview_scroll(1,'units')
            
            # ウィジェット変数に格納
            xScrollAmount.set(1)

            print("右へスクロール")

        print("ウィジェット変数値(左右)は",xScrollAmount.get())
    
    def influedMouceRotationY(self,event,canvas):

        # ウィジェット変数の更新に合わせて当該キャンバスをスクロールする縦方向のみ

        if yScrollAmount.get() >0:
            print("下スクロール検出")

            canvas.yview_scroll(-1,'units')

        elif yScrollAmount.get() <0:

            print("上スクロール検出")
            canvas.yview_scroll(1,'units')

    def start_scroll(self,event):
        
        print("中ボタン検出")

    def scroll_now(self,event):
        
        print("中ボタン移動検出")

    def end_scroll(self,event):
        
        print("中ボタン離れ検出")
    def influedMouceRotationX(self,event,canvas):

        # ウィジェット変数の更新に合わせて当該キャンバスをスクロールする　横方向のみ

        print("チェックポイント")
        if xScrollAmount.get() >0:
            print("右スクロール検出")

            canvas.xview_scroll(-1,'units')

        elif xScrollAmount.get() <0:

            print("左スクロール検出")
            canvas.xview_scroll(1,'units')
    def selectEditMode(self,event):

        #タブキーが押されたときに検出し編集モードを切り替えるメソッド

        print("tabキーが押されました")

        # tabが押された時にモードを示すフラグを切り替え
        if editModeType.get() == "音符編集":
            
            editModeType.set("歌詞編集")

        # tabが押された時にもう一つモードを次のモードに設定
        elif(editModeType.get() == "歌詞編集"):
        
            editModeType.set("ピッチ編集")

        # tabが押された時にもう一つモードを次のモードに設定
        else:

            editModeType.set("音符編集")
       
        print("現在のモードは",editModeType.get())

    def drawPitchEditArea(self,pitchEditFrame,keyCanvas,dynamicsTabCanvas,table,freq_2_ScreenPos_Table,composerData):

        # ピッチ編集部を示すキャンバスを囲うふれーむの作成
        pitchEditFrame.grid(row = 0,column = 0,sticky = "nesw")

        # pitchAndKeyをめいいっぱい描画領域を広げる
        pitchEditFrame.grid_columnconfigure(0,weight = 1)
        pitchEditFrame.grid_rowconfigure(0,weight = 1)

        # ノートの描画で使用するのでグローバル変数として定義する
        global pitchEditCanvas

        # ピッチ編集部のキャンバスを作成
        pitchEditCanvas = tkinter.Canvas(pitchEditFrame,width = 100,height=500,bg = "purple",bd = 0,relief = 'flat',scrollregion =(0,0,INITIAL_LENGTH_PX,3000),highlightthickness = 0)

        # ピッチ編集部キャンバスを配置　
        pitchEditCanvas.grid(row =0 ,column = 0,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        # ピッチ編集部でマウススクロール鍵盤部も連動してスクロールするメソッドを紐付け
        pitchEditCanvas.bind("<MouseWheel>", partial(application.scroll_KeysCanvas,keyCanvas = keyCanvas , pitchEditCanvas = pitchEditCanvas))
        
    
        # ピッチ編集部でとパラメタ部のの横スクロールを制御するメソッドを紐付け
        pitchEditCanvas.bind("<Shift-MouseWheel>",partial(application.detectMouceRotationX,pitchEditCanvas = pitchEditCanvas,dynamicsTabCanvas = dynamicsTabCanvas))
        

        # 移動中に実行するメソッドを紐付け
        pitchEditCanvas.bind("<Button2-Motion>",application.scroll_now)

        # ボタンが押されたときの検出メソッドを紐付け
        pitchEditCanvas.bind("<Button-2>",application.start_scroll)
        
        # マウスボタンが離れた時のメソッドを紐付け
        pitchEditCanvas.bind("<ButtonRelease-2>",application.end_scroll)

        #
        #pitchEditFrames
        pitchEditFrame.focus_set()
        # tabで編集モードを選ぶために
        pitchEditFrame.bind("<Key-Tab>",application.selectEditMode)
        


        # ピッチ編集部の水平方向スクロールバーを作成
        pitchXbar = tkinter.Scrollbar(pitchEditCanvas,orient = tkinter.HORIZONTAL)

        # ピッチ編集部のスクロールバーを配置
        pitchXbar.grid(row = 1,column = 0,sticky = tkinter.W + tkinter.E)

        # 列方向にめいいっぱいに広げる　
        pitchEditCanvas.grid_columnconfigure(0,weight = 1)    

        # ピッチ編集部の垂直方向のスクロールバーを作成
        pitchYbar = tkinter.Scrollbar(pitchEditCanvas,orient = tkinter.VERTICAL)

        # ピッチ編集部のキャンバスの下に垂直方向スクロールバーを配置
        pitchYbar.grid(row = 0,column = 1,sticky = tkinter.N + tkinter.S)

        # 列方向にめいいっぱいに広げる　
        pitchEditCanvas.grid_rowconfigure(0,weight = 1)

        # スクロールバーのスライダが動かされた時の実行する処理を設定
        pitchXbar.config(command = pitchEditCanvas.xview)
        pitchYbar.config(command = pitchEditCanvas.yview)

        # キャンバススクロール時に実行する処理を設定
        pitchEditCanvas.config(xscrollcommand = pitchXbar.set)
        pitchEditCanvas.config(yscrollcommand = pitchYbar.set)
   
        # 背景を描画
        application.mainBG(pitchEditCanvas,keyCanvas,table)

        midisList = [[]]#ダミー

        # 最初のmidiノートが追加されたら内部処理メソッドを呼び出す
        #midiLoadFlag.trace_add('write',midi.load_Midis(self,midiData,composerData,MidiNumber2Freq))
        
    def drawDynamicsCurve(self,dynamicsTabCanvas,composerData):

        # ダイナミクスカーブを描画するメソッド
       
        print("ダイナミクスカーブの描画")

        # デバッグ用確認表示
        for row in composerData.composerInnerData:
            print(row)
        
         # 現在操作中のノートの番号を格納する変数を定義
        noteIndex = 0

        # 各ノートについて総なめする処理
        for note in range(0,len(composerData.composerInnerData),1):#

     
           
            # 何個目の制御点を対象に計算しているかを格納する変数を定義
            index = 0

            # ピッチ制御点についてのループ
            for line in range(0,composerData.composerInnerData[note][4],1):
               
                #次のノートにまたぐか跨がないか野判定
                if index < composerData.composerInnerData[note][4] - 1:

                    # 跨がないとき

                    # 座標を計算
                    startXPos = composerData.composerInnerData[note][6][line][0]
                    startYPos = composerData.composerInnerData[note][6][line][1]
                        
                    # 次のノートの最初のピッチ制御点のｘ、ｙ座標を取得
                    endXPos = composerData.composerInnerData[note][6][line + 1][0]
                    endYPos = composerData.composerInnerData[note][6][line + 1][1]

                    idName = dynamicsTabCanvas.create_line(startXPos,startYPos,endXPos,endYPos,fill='blue',width = 4)
                
                else:
                    
                    # 跨ぐとき
   
                   
                    # 次にノートが存在するかどうか判定
                    if len(composerData.composerInnerData) - 1 == noteIndex:
                       
                       # 直近の次のタイミングでノートが存在しないとき
                        #print("ノート存在なし")
                        pass
                    else:

                        # 次のタイミングでノートが存在する時
                        
                        #print("ノート存在あり")
                        # 座標を計算
                        startXPos = composerData.composerInnerData[noteIndex][6][index][0]
                        startYPos = composerData.composerInnerData[noteIndex][6][index][1]
                        
                        # 次のノートの最初のピッチ制御点のｘ、ｙ座標を取得
                        endXPos = composerData.composerInnerData[noteIndex + 1][6][0][0]
                        endYPos = composerData.composerInnerData[noteIndex + 1][6][0][1]

                        
                        # 次のノートにピッチ曲線をつなげる直線を描画
                        idName = dynamicsTabCanvas.create_line(startXPos,startYPos,endXPos,endYPos,fill='blue',width = 4)
                    
                index = index + 1
            noteIndex = noteIndex + 1
          

    def drawPitchCurve(self,pitchEditCanvas,freq_2_ScreenPos_Table,composerData):

        # ピッチカーブを描画するメソッド
       
        #print("ピッチ曲線描画")

        # デバッグ用確認表示
        #for row in composerData.composerInnerData:
         #   print(row)
        
         # 現在操作中のノートの番号を格納する変数を定義
        noteIndex = 0

        # 各ノートについて総なめする処理
        for note in range(0,len(composerData.composerInnerData),1):#

            print(composerData.composerInnerData[note][8])
            # 各制御点についてのループ
            #for ctlPoint in note[8]:
           
            # 何個目の制御点を対象に計算しているかを格納する変数を定義
            index = 0

            # ピッチ制御点についてのループ
            for line in range(0,len(composerData.composerInnerData[note][8]),1):
               
                #次のノートにまたぐか跨がないか野判定
                if index < len(composerData.composerInnerData[note][8]) - 1:

                    # 跨がないとき

                    idName = pitchEditCanvas.create_line(composerData.composerInnerData[note][8][line][0],composerData.composerInnerData[note][8][line][1],composerData.composerInnerData[note][8][line + 1][0],composerData.composerInnerData[note][8][line + 1][1],fill='blue',width = 4)
                
                else:

                    # 跨ぐとき
   
                    #print(len(composerData.composerInnerData) - 1," ",noteIndex )
                    # 次にノートが存在するかどうか判定
                    if len(composerData.composerInnerData) - 1 == noteIndex:
                       
                       # 直近の次のタイミングでノートが存在しないとき
                        pass

                    else:

                        # 次のタイミングでノートが存在する時
                        
                        # 座標を計算
                        startXPos = composerData.composerInnerData[noteIndex][8][index][0]
                        startYPos = composerData.composerInnerData[noteIndex][8][index][1]
                        
                        # 次のノートの最初のピッチ制御点のｘ、ｙ座標を取得
                        endXPos = composerData.composerInnerData[noteIndex + 1][8][0][0]
                        endYPos = composerData.composerInnerData[noteIndex + 1][8][0][1]

                        
                        # 次のノートにピッチ曲線をつなげる直線を描画
                        idName = pitchEditCanvas.create_line(startXPos,startYPos,endXPos,endYPos,fill='blue',width = 4)
                    
                index = index + 1
            noteIndex = noteIndex + 1
            

    def drawMeterZone(self,materZone):

        #　メーターゾーンの描画
            
        # メーターゾーンの配置
        materZone.grid(row = 0,column = 0,stick="nswe")

        # メーターゾーンを縦いっぱいに広げる
        materZone.rowconfigure(0,weight=1)



    def drawcurves(self,event,canvas):

        # カーソル座標を格納
        cuersorX = event.x
        cuersorY = event.y

        #PARM_TIME_RESOLUSION 0.1
        
        '''
        if oldX == None or oldY == None:
            
            #px単位に直したパラメータの時間分解能の計算
            paramPxResolution = 1#PARM_TIME_RESOLUSION#todo 仮
            print("px reso",paramPxResolution)

            # 線描画用リストを作成
            curvePointLocation = numpy.arange()
            # 線(初期値)を描画
            canvas.create_line(cuersorX,cuersorY,oldX,oldY,'white')
        # 確認表示
        print(cuersorX," ",cuersorY," ",oldX," ",oldY)
        # 線を描画
        canvas.create_line(cuersorX,cuersorY,oldX,oldY,'white')

        # 現在のカーソル座標を１ステップ前の座標値として更新
        oldX = cuersorX
        oldY = cuersorY
        '''
 
       
    def drawToolsArea(self,optionFrame):
        
        # 右側のフレームを配置
        optionFrame.grid(row = 0,column = 1,rowspan = 2)

        # 右側のフレームをを配置 いらないはず
       # optionFrame.grid(row = 0,column = 1,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        # 一番上のフレームの作成
        personalityFrame = tkinter.Frame(optionFrame,width="200",height="200",bg="gray33")
        
        # 一番上のフレームを配置
        personalityFrame.grid(row=0,column=0)

        # 一番上のフレームのサイズの自動調整機能をオフ
        personalityFrame.grid_propagate(False)

        # 音源読み込みボタンの作成
        lyricIncertButton = tkinter.Button(optionFrame,text ="音源パーソナリティを読み込み",width=13,height=8)

        # ボタンの配置
        lyricIncertButton.grid(row=0,column=0)



        # 2番上のフレームの作成
        operateFrame = tkinter.Frame(optionFrame,width="200",height="200",bg="gray13")
        
        # 2番上のフレームを配置
        operateFrame.grid(row=1,column=0)

        # 2番上のフレームのサイズの自動調整機能をオフ
        operateFrame.grid_propagate(False)

        # 操作のラベルを作成
        operateLabel = tkinter.Label(operateFrame,text="操作",bg="gray13",fg="white")

        # 操作のラベルを配置
        operateLabel.grid(row=0,column=0,sticky=tkinter.W)
        
        # BPMのラベルを作成
        bpmLabel = tkinter.Label(operateFrame,text="BPM",bg="gray13",fg="white")

        # ＢPＭのラベルを配置
        bpmLabel.grid(row=1,column=0,sticky=tkinter.W)

        # bpmを表示（必要なら修正）
        bpmText = tkinter.Entry(operateFrame,width = 10)

        # ウィジェット変数からこのエントリに入れ込む文字列を抽出して挿入
        bpmText.insert(tkinter.END,str(midisBpm.get()))

        # bpm表示（修正）をグリッドで表示
        bpmText.grid(row =1,column = 1)

        # 4拍子か３拍子か変拍子（←これはtodo）を
        beatTypeLabel = tkinter.Label(operateFrame,text="拍子の種類",fg="white",bg="gray13")

        # ＢbpmLabelＭのラベルを配置
        beatTypeLabel.grid(row=2,column=0,sticky=tkinter.W)

        # 拍子を示すリストを定義
        beatTyopes = ("４拍子","３拍子(未実装)","変拍子（未実装）")
        
        # 拍子の設定用コンボボックスの作成
        beatTypeCombo = ttk.Combobox(operateFrame,width=6,height=1,values = beatTyopes,state='readonly')

        # デフォルトで選択されている項目を設定
        beatTypeCombo.current(0)
   

        # 拍の種類のコンボボックスを配置
        beatTypeCombo.grid(row=2,column=1)

        # midi編集時のスナップ間隔を示すラベルの定義
        snapIntervalLabel = tkinter.Label(operateFrame,text="スナップ間隔",fg="white",bg="gray13")

        # スナップ用のラベルを配置
        snapIntervalLabel.grid(row=3,column=0)

        # スナップの粗さを示すリストを定義
        snapTyopes = ("4分音符","8分音符","16分音符","32分音符","フリー")
        
        # スナップ設定用コンボボックスの作成
        snapTypeCombo = ttk.Combobox(operateFrame,width=10,height=3,values = snapTyopes,textvariable = snapIntervas,state='readonly')

        # デフォルトで選択されている項目を設定
        snapTypeCombo.current(2)

        # コンボボックスの内容を紐づけするウィジェット変数に
        snapTypeCombo.bind('<<ComboboxSelected>>',application.comboboxSelected)

        # スナップ設定用コンボボックスを配置
        snapTypeCombo.grid(row=3,column=1)



        # midi編集時のスナップ間隔を示すラベルの定義
        editModeLabel = tkinter.Label(operateFrame,text="編集モード",fg="white",bg="gray13")

        # スナップ用のラベルを配置
        editModeLabel.grid(row=4,column=0)

        # スナップの粗さを示すリストを定義
        editModeTyopes = ("音符編集","歌詞編集","ピッチ編集")
        
        # スナップ設定用コンボボックスの作成
        editModeCombo = ttk.Combobox(operateFrame,width=10,height=3,values = editModeTyopes,textvariable = editModeType,state='readonly')

        # デフォルトで選択されている項目を設定
        editModeCombo.current(0)

        # コンボボックスの内容を紐づけするウィジェット変数に
        editModeCombo.bind('<<ComboboxSelected>>',application.comboboxSelectedMode)

        # スナップ設定用コンボボックスを配置
        editModeCombo.grid(row=4,column=1)




        # オートピッチ調整ボタンの作成
        lyricIncertButton = tkinter.Button(operateFrame,text ="オートピッチ調整",width=10,height=2)

        # オートピッチ調整ボタンの配置
        lyricIncertButton.grid(row = 5,column=0)


        # 3番上のフレームの作成
        lylicsFrame = tkinter.Frame(optionFrame,width="200",height="200",bg="gray33")
        
        # 3番上のフレームを配置
        lylicsFrame.grid(row=2,column=0)

        # 3番上のフレームのサイズの自動調整機能をオフ
        lylicsFrame.grid_propagate(False)

        # 歌詞のラベルを作成
        lblLyric = tkinter.Label(lylicsFrame,text="歌詞",bg="gray33",fg="white")

        # 歌詞のラベルを配置
        lblLyric.grid(row=0,column=0,sticky=tkinter.W)

        # 歌詞入力用のテキストエントリを作る
        lyricText = tkinter.Entry(lylicsFrame,width=30)

        # 歌詞入力エントリを配置
        lyricText.grid(row=1,column=0)

        # 歌詞読み込みボタンの作成
        lyricIncertButton = tkinter.Button(lylicsFrame,text ="歌詞流し込み",width=10,height=2)

        # ボタンの配置
        lyricIncertButton.grid(row=2,column=0,sticky=tkinter.W)

        # 入力文字を取得
        lyricData = lyricText.get()


        # 4番上のフレームの作成
        generateFrame = tkinter.Frame(optionFrame,width="200",height="200",bg="gray13")
        
        # 4番上のフレームを配置
        generateFrame.grid(row=3,column=0)

        # 4番上のフレームのサイズの自動調整機能をオフ
        generateFrame.grid_propagate(False)

        # クリエイトボイスボタンの作成
        createButton = tkinter.Button(generateFrame,text ="生成",width=10,height=2)

        # ボタンの配置
        createButton.grid(row=3,column=0)
   
        # 垂直方向のスクロールバーを作成
        ybar = tkinter.Scrollbar( application.window,orient = tkinter.VERTICAL)

    def comboboxSelectedMode(self,event):

        # 現在の編集モードを示す

        print("現在のモードは",editModeType.get())

    def drawSourceCreaterDisplay(self,applicationFormat,application,big):
       
        ################################### 音源クリエーターモード ##################################
        #todo 表示禁止はこのメソッドないで書くべき
       # editSoundsFrame.tkraise()

        # 音源クリエーターモードでのベースとなるフレームを作成 todo
        SCMmainFrame = tkinter.Frame(application.window,bg = 'white',bd = 2,width = 500)
        #今作ってるフレームを最前面に
        SCMmainFrame.tkraise()
        # 画面いっぱいにフレームを配置
        SCMmainFrame.grid(row=0,column=0,rowspan=2,columnspan=2)

        # 画面中央にお知らせを表示するようのラベルを作成
        label1 = tkinter.Label(SCMmainFrame,text="音源パーソナリティーを新規作成する時は音源名を入力して新規作成ボタンを押してください。")
        label2 = tkinter.Label(SCMmainFrame,text="UTAU互換モード：UTAUの音声ライブラリから作成します。")
        label3 = tkinter.Label(SCMmainFrame,text="完全オリジナルモード：音声を録音してゼロから音源を作成します")
        label4 = tkinter.Label(SCMmainFrame,text="UTAU拡張モード：UTAUの音声ライブラリに追加して音声を録音して音源を作成します")
        label5 = tkinter.Label(SCMmainFrame,text="音源名")
        label6 = tkinter.Label(SCMmainFrame,text="作成形式")
     
        # 各ラベルを配置
        label1.grid(row = 0,column =0 ,sticky = tkinter.W)
        label2.grid(row = 1,column =0,sticky = tkinter.W)
        label3.grid(row = 2,column =0,sticky = tkinter.W)
        label4.grid(row = 3,column =0,sticky = tkinter.W)
        label5.grid(row = 4,column =0,sticky = tkinter.W)
        label6.grid(row = 5,column =0,sticky = tkinter.W)
       
        # 名前入力用テキストエントリを作る
        personalName = tkinter.Entry(SCMmainFrame,width=30)

        # 既定の文字列を入力
        personalName.insert(tkinter.END,'作成する音源名をここに入力')
       
        # 音源名入力エントリを配置
        personalName.grid(row=4,column=0)

        # 新規作成ボタンを作成
        createVoiceButton = tkinter.Button(SCMmainFrame,text="新規作成",width=20,height=3,font=big,command = lambda:application.drawSoundEditDisplay(applicationFormat,application))

        # 新規作成ボタンの配置
        createVoiceButton.grid(row=6,column=0)
       
        # コンボボックスウィジェットの作成
        createType = tkinter.StringVar()

        # コンボボックスに入力する文字列を作る
        TypeList = ("UTAU互換","完全オリジナルモード","UTAU拡張モード")

        # コンボボックスを作成
        createType = ttk.Combobox(SCMmainFrame,height = 30,justify = tkinter.LEFT,state="readonly",values =TypeList)
   
        # コンボボックスの配置
        createType.grid(row=5,column=0)

        # 横いっぱいに広がるように調整
        SCMmainFrame.grid_columnconfigure(1, weight=1)

    def save_file_as(self,saveData):

        # 本アプリのデータをピックス形式で書き出すイベントハンドラ 保存時最初に呼び出されることを想定
   
        # デバッグ用確認表示
        print("名前を付けて保存するボタンを検出")

        # 保存する拡張子の設定
        type = [('binary','*.binary')]
   
        # デフォルトのディレクトリを設定してダイアログ表示
        file_path = tkinter.filedialog.asksaveasfilename(filetypes = type,initialdir = DEFAULT_READ_LOCATION,title="save as")
        fileNameAdd=".binary"
        file_path = file_path + fileNameAdd


        # ファイルが開けるか判定
        with open(file_path,mode ='wb')as f:

             # アプリケーションの保存ファイルをピックルデータに加工して保存
            b = pickle.dump(saveData,f)
           
 
            print(file_path,"左のパスにデータを保存しました。")


        # ファイルオープン
        f = open(file_path,'rb')
   
        # ピックルデータを読み込み
        loadData = pickle.load(f)

        # インスタンス置き換え
        applicationFormat = loadData

        # 読み込みに関するフラグを変更
        applicationFormat.WavExist = True
   
    def open_file(self,applicationFormat):
   
        # 開くボタンが押されたときのイベントハンドラ

        # 未保存のデータが有る場合ユーザーに保存を促す処理 todo
        tkinter.messagebox.showinfo("未保存のデータがあります。")

        # 確認表示
        print("開くボタンが押されました")

        # タイプの設定
        type = [('binary','*.binary')]
   
        # デフォルトのディレクトリを設定してダイアログ表示
        dataPath = filedialog.askopenfilename(initialdir = DEFAULT_READ_LOCATION)

        # ファイルオープン
        f = open(dataPath,'rb')
   
        # ピックルデータを読み込み
        loadData = pickle.load(f)

        # インスタンス置き換え
        applicationFormat = loadData

        # 読み込みに関するフラグを変更
        applicationFormat.WavExist = True
           
        #アトリビュートを追加
        setattr(applicationFormat,"WavExist",True)
       
    def drawFigAsFrame(self,loadData,index):

        # フレームに図を描画す.るメソッド

        # fuigerインスタンスの生成
        fig = Figure(figsize=(6,2))

        # 座標軸の作成
        self.ax = fig.add_subplot(1,1,1)

        # 呼び出す属性名を作成
        attributeNameData = "estimatedf0" + str(index)
        attributeNameTime = "f0Time" + str(index)
        attributeNameMaxTime = "originalWavRecordingTime" + str(index)
        attributeNameEstimatedf0Max = "estimatedf0MaxF" + str(index)

        x = getattr(loadData,attributeNameTime)
        y = getattr(loadData,attributeNameData)
        estimatedf0Max = getattr(loadData,attributeNameEstimatedf0Max)

        # 対象トラックの収録時間[s]を取得
        truckTimeS = getattr(loadData,attributeNameMaxTime)
        #print("収録時間は[s]",truckTimeS)
       
        # グリッドを表示
        self.ax.grid()

        # f０予測値をプロット
        self.ax.plot(x,y,label='pitch')

        # 縦軸の表示
        self.ax.set_ylabel('Frequency f [Hz]')

        # 横軸の表示
        self.ax.set_xlabel('time s [s]')

        # 横軸の範囲指定
        self.ax.set_xlim([0,truckTimeS])

        # 縦軸の範囲指定
        self.ax.set_ylim([0,estimatedf0Max])

        # データから強制アライメントの区切り時刻を取得
        attributeAligmentName="PhonesAlignment" + str(index)
        tmp =getattr(loadData,attributeAligmentName)
       
        # アライメントの表示
        for index in numpy.arange(len(tmp)):

            # アライメントの区切り支援をプロット
            self.ax.vlines(tmp[index][0],0,1000,color='g',linestyles='dotted')
       
        # matplotlibの描画領域とフレームの関連づけ
        self.canvas = FigureCanvasTkAgg(fig)

        # matplotlibのグラフをキャンバスに配置
        returnData = self.canvas.get_tk_widget()

        return returnData
       
    def collectData(saveData):
        return saveData

    def endMidDrag(event):

        # ドラッグが終わった時のイベントハンドラ
        global isCkicking

        # ドラッグが終了したのでフラグをおろす
        isCkicking =False
   
    def changeMode2Main(self,application):

        # 楽曲クリエーターモードに画面を切り替えるメソッド
       
        application.totalFrame.tkraise()
        mainFrame.tkraise()
        paramatorFrame.tkraise()
        print("楽曲クリエーターモードに画面を切り替え")

    def changeMode2MSC(self,application):

        # 音源クリエーターモードに画面を切り替えるメソッド

        print("音源クリエーターモードに画面を切り替え")
       
        SCMmainFrame.tkraise()

    def changeMode2EditSound(self,application):
       
        # 音声編集画面に画面を切り替えるメソッド
       
        application.editSoundsFrame.tkraise()
        print("音声編集画面へ切り替え")

    def drawMenuBar(self,applicationFormat,composerData,MidiNumber2Freq):

        # メニューバーを描画するメソッド

        # メニューバーを画面にセット
        menu = tkinter.Menu(self.window)

        #メニューバーを画面にセット
        self.window.config(menu = menu)

        # メニューバーに親メニュー（ファイル）を作成
        menu_file = tkinter.Menu(self.window)
        menu.add_cascade(label='file',menu=menu_file)

        # 子要素(ファイルオープン)を設置
        menu_file.add_command(label='open', command = lambda:application.open_file(applicationFormat))
        menu_file.add_separator()

        # 子要素(保存)を設置
        menu_file.add_command(label='save', command = save_file)
        menu_file.add_separator()

        # 子要素(別名保存)を設置
        menu_file.add_command(label='save as', command = lambda:application.save_file_as(applicationFormat))
        menu_file.add_separator()


        # メニューバーに親メニュー（インポート）を作成
        menu_import = tkinter.Menu(self.window)
        menu.add_cascade(label='import',menu=menu_import)

        # 子要素（psnファイル)を設置
        #menu_import.add_command(label='personality', command = import_wav)
        menu_import.add_separator()

        # 子要素（midi読み込み)を設置
        menu_import.add_command(label='MIDI', command = lambda :midi.select_midi_track(composerData,MidiNumber2Freq))
        menu_import.add_separator()

        # 子要素（wav読み込み)を設置
        menu_import.add_command(label='WAV', command = import_wav)
        menu_import.add_separator()

        # メニューバーに親メニュー（エクスポート）を作成
        menu_export = tkinter.Menu(self.window)
        menu.add_cascade(label='export',menu=menu_export)

        # 子要素（wav書き出し)を設置
        menu_export.add_command(label='VOICE', command = export_wav)
        menu_export.add_separator()

        # 子要素（model書き出し)を設置
        menu_export.add_command(label='モデル', command = export_model)
        menu_export.add_separator()

        # メニューバーに親メニュー（モード選択）を作成
        menu_mode = tkinter.Menu(self.window)
        menu.add_cascade(label='mode',menu=menu_mode)

        # モード選択メニューバーに選択メニューを追加
        menu_mode.add_radiobutton(label = "楽曲クリエーターモード",command = lambda:application.changeMode2Main(application))
        menu_mode.add_radiobutton(label = "音源クリエーターモード",command = lambda:application.clickNewCreate(applicationFormat,application,big))
   
    def drawCurve(self,rawData):
       
        # 2次元tensorデータの曲線を表示するメソッド
       
        #生データの確認表示
        print(rawData)

       
        # midiから生成した周波数曲線を表示
        for i in numpy.arange(rawData.size(0)):
           
            # 読み込みのオーバーを防ぐために添え字を制限
            if i < rawData.size(0):
               
                # 描画する座標を設定
                startX = rawData[i,0].item()
                startY = rawData[i,1].item()
                endX = rawData[i + 1,0].item()
                endY = rawData[i + 1,1].item()
           
                # 線を描画
                pitchEditCanvas.create_line(startX,startY,endX,endY,fill="green",width= 1)

    def onclik(self,testEnter):

        # クリック検出時の処理を定義するメソッド
        print("クリック検知")
    
    def noteTrance():
        pass
    def noteScale():
        pass
    def comboboxSelected(self,event):

        # グリッドナップの間隔をウィジェット変数に格納するメソッド

        # 現在選択されているスナップ間隔をしジェット変数で取得
        tmp = snapIntervas.get()

        # フリーモードが選択されている時のみ別処理
        if tmp != "フリー":
            tmp = tmp.replace("分音符","")

            snapInterval = int(tmp)
        else:
            snapInterval = 0

        # ウィジェット変数に格納
        cleanedSnapIntervas.set(snapInterval)

        #確認表示デバッグ用
        print(snapInterval)

    def clickNote(self,event,pitchEditCanvas,idName,color):

        # ノート（を示す長方形が）がクリックされた時の処理

        # 該当するタグ名のキャンバスの色に（ＩＤ指定で）
        pitchEditCanvas.itemconfig(idName,fill = color)
        
        #print("selected Note! ",idName)
        #print("===============================")


    def detectCurrentNote(self,event,pitchEditCanvas):
        
        # 現在マウスオーバーしているノートのmidiノート番号をウィジェット変数として保存するメソッド

        # カーソルのｘ、ｙ座標を取得
        currentX = event.x
        currentY = event.y

        # 空のリストを準備
        detectedTags=[]

        # クリック位置から一番近い図形ＩＤ取得
        detectedTags = [ pitchEditCanvas.itemcget(tmp,'tags') for tmp in pitchEditCanvas.find_overlapping(currentX,currentY,currentX,currentY)]

        # 安全とスコープを広げるためにフラグ変数を偽に設定
        noteDetectedFlag = False
        bgDetectedFlag = False
        notCurrentFlag = False
        
        # 安全とスコープを広げるために検出ID変数にNoneを設定した物を新規作成
        global detectedId
        
        
        # デバッグ用確認表示
        #print("検出したタグは",detectedTags)


        # タプルの全要素についてスキャン
        for targetElemtnt in detectedTags:
            
            #int型になって.findでエラーになることを防ぐ
            targetElemtnt = str(targetElemtnt)

            # ノートが１つでも検知されているとき（つまりノートが優先される時）
            if targetElemtnt.find('noteId'):

                # 後の処理のために
                noteDetectedFlag = True

                break
                # tag文字列がふくまれる場合


        # noteIdが一つも検出されなかったらBGのみとして処理
        if noteDetectedFlag == False:

            # 後処理のためにBGのみ検出フラグを立てる
            bgDetectedFlag = True
           
        
        # rawの内容が空かどうかチェック
        if len(detectedTags) >0:
        
            # ノートに対する処理かBGにたいする処理かで分岐
            if  bgDetectedFlag == True:
            
                # BGについての処理
            
                #print("BG検出")


                # currentを含むインデックスを捜索
                for targetElemtnt in detectedTags:
                
                    # currentを含むインデックス番号を取得
                    if 'current' in targetElemtnt:
               
                        #print("今考えている要素",targetElemtnt)
                    
                        detectedId = targetElemtnt

                        break

                # 注意！　カーソルの位置によって実際に存在するのにcurrentが全くないタプルが渡される時があるがそのときはデフォルトのNoneになる
            
    

            else:
                pass
            
                # ノートに対する処理
            
                # currentが含まれるタプルが前から０始まりで何番目かを示すインデックス　マイナスはデフォルトで存在しないを意味
                index = 0

                # currentを含むインデックスを捜索
                for targetElemtnt in detectedTags:
                
                    # currentを含むインデックス番号を取得
                    if 'current' in targetElemtnt:
               
                        #print("今考えている要素",targetElemtnt)
                    
                        detectedId = targetElemtnt
                        break

                #print("ノート検出") 
            

            # 現在のID名に必ずcurrentが入っているのでそれを取り除く
            detectedId = str(detectedId)
            detectedId = detectedId.replace('current','')
            detectedId = detectedId.replace('tag','')

            # 値をウィジェット変数に格納
            currenTargetId.set(detectedId)
        
            # 確認表示
            #print("対象ID",currenTargetId.get())
        else:

            # どのウィジェットにもマウスが載っていない事を明示的に示すためウィジェット変数に０格納
            currenTargetId.set("0")
            # 注意！　検出元タプルが空なら後続の処理のためににウィジェット変数を1以上にして保存してはならない！！！

    def dragNoteVerticcle(self,event,pitchEditCanvas,scalingFactor,idName):

        # グローバル変数として現在と₁ステップ前のカーソル座標を保存する変数を定義
        global currentY
        global currentX


        # カーソルのｘ、ｙ座標を取得
        currentY = event.y
        currentX = event.x

        # すべてのBGにたいして総なめの処理 BGが最初に描画され1.2.3....とIDが続くこと前提
        for index in numpy.arange(1,30,1):#30は仮todo

            # デバッグ用確認表示　各図形の四隅座標を示す
            #print("i",index ," cood",pitchEditCanvas.coords(index))

            # 各図形の上下方向の中心とマウスの縦軸値の相対的なずれを計算
            relativeDifference = int(abs(pitchEditCanvas.coords(index)[1] + ((pitchEditCanvas.coords(index)[3] - pitchEditCanvas.coords(index)[1]) / 2)  - currentY))
            #print("カーソルｙ",currentY,"縦方向に位置差",relativeDifference)

            # 相対的なずれがない物を探す　１．５は上の式で割り切れない値が発生した時に備える１付近の甘い数値である事
            if relativeDifference == 0:
                #print("jump to",index)

                # 検出した先のidへ図形を移動させる
                application.moveNoteOne(pitchEditCanvas,idName,index) 
                
                break
        print("before",pitchEditCanvas.coords(idName)[0] )
        print("drag move")
        print("=====================================")
 
    def moveNoteOne(self,pitchEditCanvas,idName,targetId):

        # 1つだけノートを移動させる関数

        # 移動先のy座標を計算
        moveToCoordinateY = pitchEditCanvas.coords(targetId)[1]

        #print("afterX",pitchEditCanvas.coords(idName)[0])
        
        # ノートの移動 todo-1は補正値なぜだか必要ずれる
        pitchEditCanvas.moveto(idName,pitchEditCanvas.coords(idName)[0] - 1,moveToCoordinateY)

    def moveNoteDown(self,event,pitchEditCanvas,idName,scaleingFactor):

        #ノートを半音さげるメソッド（見た目だけ）
        #     
        # 相対距離[px]を指定して移動
        #pitchEditCanvas.move(idName,0,30)

        targetTag = pitchEditCanvas.itemcget(idName,"tag")

        #print("該当ノートのタグ",targetTag)
        # デバッグ用確認表示
        #print("note down")
        #print("===================================-")
    
    def daleteNote(self,event,idName):

        # ダブルクリックされたらノートを削除（見た目だけ）するメソッド
        event.widget.delete(idName)

        # デバッグ用確認表示
        #print("Note daleted!!")
        #print("====================================")

    def changeBgColor(self,event,pitchEditCanvas,color,idName):

        #idName = tagName.replace("tag","")

        # 該当するタグ名のキャンバスの色に（ＩＤ指定で）
        pitchEditCanvas.itemconfig(idName,fill = color)

        #print("On!! ",idName)
        #print("===============================")

    def changeBgColor2(self,event,pitchEditCanvas,color,idName):

        # カーソルがエリアから出た時に色を戻すメソッド
        
        #print("Leave",idName)
        #print("=========================================")

        # 元の色で再着色
        pitchEditCanvas.itemconfig(idName,fill = color)

    def changeKeyColor(self,event,idName,pitchEditCanvas):

        # BG上と同じ位置に相当する鍵盤の色を変更するメソッド

        # 鍵盤の色を変える
        pitchEditCanvas.itemconfig(idName,fill='red')

        #print("BG上のＩＤ",idName)
        #ウィジェット変数から現在ＢＧ上でマウスオーバーされているidを取得
        currentId = currenTargetId.get()

        # 確認表示
        print(currentId)

    def changeCousor(self,event,pitchEditCanvas,idName):

        # ノートの端にマウスカーソルが来たらカーソルタイプを変更するメソッド

        # 端から何ピクセルを検知範囲とするかを示す
        detectMarginPx = 10

        # グローバル変数として現在カーソル座標を保存する変数を定義
        global currentX
        global currentY

        # 現在のマウスカーソルを取得
        currentX = event.x
        currentY = event.y

        # 音符のバウンディングボックスを取得
        boundingBox = pitchEditCanvas.bbox(idName)

        # 右端の検出
        if boundingBox[2] - currentX < detectMarginPx:
            
            pitchEditCanvas.config(cursor="sb_h_double_arrow")

        # 左端の検出
        elif currentX - boundingBox[0]  < detectMarginPx:
            
            pitchEditCanvas.config(cursor="sb_h_double_arrow")

        else:

            pitchEditCanvas.config(cursor="arrow")
    def scroll_KeysCanvas(self,event,keyCanvas , pitchEditCanvas):
      
       # ＢＧの上下スクロールに応じて鍵盤部とＢＧ部を上下にスクロールするメソッド

        # 下にホイールが動かされた時
        if event.delta > 0:

            # スクロール幅を１ｃｍにする
            pitchEditCanvas.configure(yscrollincrement="1c")

            # スクロール幅を１ｃｍにする
            keyCanvas.configure(yscrollincrement="1c")

            # 鍵盤部をスクロール
            keyCanvas.yview_scroll(-1, 'units')

            # ＢＧ部をスクロール
            pitchEditCanvas.yview_scroll(-1, 'units')

        #　上にホイールが動かされた時
        elif event.delta < 0:

            # スクロール幅を１ｃｍにする
            pitchEditCanvas.configure(yscrollincrement="1c")

            # スクロール幅を１ｃｍにする
            keyCanvas.configure(yscrollincrement="1c")

            #　鍵盤部をスクロール
            keyCanvas.yview_scroll(1, 'units')

            # ＢＧ部をスクロール
            pitchEditCanvas.yview_scroll(1, 'units')      
    def mainBG(self,pitchEditCanvas,keyCanvas,table):
       
        global PX_PER_BAR
        global C
        midiKeyNumber = 120#対応表作成の為に一時的にmidiのキー番号を保存
        SCALEING_FACTOR=2 
        scalingFactorVertical = SCALEING_FACTOR  #上の置き換えtodo　かつ上下方向のみのスケーリングパラメータ
        
        # 処理予定のmidi番号 IDの代わりに使用　だたしBGの領域を先に描画することで１，２，３とIDが続くことを前提にしているためここより前にpitchEditCanvas
        # 
        # に図形を描画追加しないこと
        midiNumber = 0
    
        # 何オクターブ文BGを描画するか
        KEY_OCTAVE_AMOUNT = 10

        # ノート数 　todoここでノートの数をカウントしておくこと　でないとぷれいばーのインデックスがずれる
        noteAmount = 1
        OCTAVE_KEYS = 12#1オクターブに鍵盤が何個存在するか

        
        # 10   5オクターブ分(厳密にはノート番号０から??まで扱う)繰り返し描画横方向の帯を白鍵黒鍵に対応する形の色で描画 上から順番に描画している　2000は十分大きな数字ならなんでもよい
        for index in numpy.arange(0,KEY_OCTAVE_AMOUNT * 150 * SCALEING_FACTOR,156 * SCALEING_FACTOR):   

            # Bに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            # タグidは文字列なので数値を文字列に変換
            tagName = "tag" + str(midiNumber)

            # BG用長方形を描画
            idName = pitchEditCanvas.create_rectangle((0,0*SCALEING_FACTOR + index,2000,13 * SCALEING_FACTOR  + index),fill="gray31",width= 1,tag = tagName)
  
            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))
            
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

             # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")


            


            # Bbに相当する領域について
            
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            # タグidは文字列なので数値を文字列に変換
            tagName = "tag" +  str(midiNumber)
            
            # BG用長方形を描画
            idName = pitchEditCanvas.create_rectangle((0,13*SCALEING_FACTOR + index,2000,26 * SCALEING_FACTOR + index ),fill="gray21",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray21',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='black'),add = "+")

            # デバッグ用確認表示
            #print("Bb tag",tagName," ID",IdName)
       


            # Aに相当する領域について
            
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            # タグidは文字列なので数値を文字列に変換
            tagName = "tag" +  str(midiNumber)

            # デバッグ用確認表示
            #print("A tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,26*SCALEING_FACTOR + index,2000,39 * SCALEING_FACTOR + index ),fill="gray31",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")

            # デバッグ用確認表示
            #print("A tag",tagName," ID",IdName)
            
 


            # G#に相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName = "tag" +  str(midiNumber)

            #print("G# tag",tagName," ID",IdName)

            idName = IdName = pitchEditCanvas.create_rectangle((0,39*SCALEING_FACTOR + index,2000,52 * SCALEING_FACTOR + index ),fill="gray21",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray21',idName = idName),add = '+')

           # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
           # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='black'),add = "+")




            # Gに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1
            tagName = "tag" +  str(midiNumber)

            #print("G tag",tagName," ID",IdName)

            idName = IdName = pitchEditCanvas.create_rectangle((0,52*SCALEING_FACTOR + index,2000,65 * SCALEING_FACTOR + index ),fill="gray31",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")

      

            # F#に相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber)

            #print("F# tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,65*SCALEING_FACTOR + index,2000,78 * SCALEING_FACTOR + index ),fill="gray21",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray21',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='black'),add = "+")


            # Fに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber)

            #print("F tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,78*SCALEING_FACTOR + index,2000,91 * SCALEING_FACTOR + index ),fill="gray31",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')
          
            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")



            # Eに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1
            
            tagName =  "tag" + str(midiNumber)

            #print("E tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,91 *SCALEING_FACTOR + index,2000, 104 * SCALEING_FACTOR + index),fill="gray31",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")



            # Ebに相当する領域について
            midiNumber = midiNumber + 1
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber)

            #print("Eb tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,104*SCALEING_FACTOR + index,2000,117 * SCALEING_FACTOR + index ),fill="gray21",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray21',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='black'),add = "+")


            # Dに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber)

            #print("D tag",tagName," ID",IdName)
            idName = pitchEditCanvas.create_rectangle((0,117*SCALEING_FACTOR + index,2000,130 * SCALEING_FACTOR + index ),fill="gray31",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')
            
            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")



            # C#に相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber )

            #print("C# tag",tagName," ID",IdName)
            idName = pitchEditCanvas.create_rectangle((0,130*SCALEING_FACTOR + index,2000,143 * SCALEING_FACTOR + index ),fill="gray21",width= 1,tag = tagName)

            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))

            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray21',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='black'),add = "+")

       

            # Cに相当する領域について
            midiNumber = midiNumber + 1 
            midiKeyNumber = midiKeyNumber - 1

            tagName =  "tag" + str(midiNumber)

            #print("C tag",tagName," ID",IdName)

            idName = pitchEditCanvas.create_rectangle((0,143*SCALEING_FACTOR + index,2000, 157 * SCALEING_FACTOR + index),fill="gray31",width= 1,tag = tagName)
 
            # マウスオーバーした時に対象BGのタグ名を返す関数を紐付け
            pitchEditCanvas.tag_bind(tagName,"<Motion>",lambda event:application.detectCurrentNote(event,pitchEditCanvas))
        
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Enter>",partial(application.changeBgColor,pitchEditCanvas = pitchEditCanvas,color = 'gray',idName = idName),add = '+')
          
            # BGの色を変更する関数を紐付け
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.changeBgColor2,pitchEditCanvas = pitchEditCanvas,color = 'gray31',idName = idName),add = '+')

            # プレイバーの位置更新用関数の紐付け
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.drawPlayBar,pitchEditCanvas = pitchEditCanvas,idName =KEY_OCTAVE_AMOUNT * OCTAVE_KEYS + noteAmount + 1),add = "+")
            
            # マウスオーバーした時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Motion>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='gray'),add = "+")

            # マウスが対象えりあから離れたとき時対応する"鍵盤の"色を変える
            pitchEditCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor2,canvas = keyCanvas,idName = idName,color='azure'),add = "+")


            
        
        # マウスカーソルに合わせた縦線を描画　プレイバー？
        # 線を描画 50000は十分大きければなんでも良い数字      
        pitchEditCanvas.create_line(200,0,200,5000,fill="white",width=3,tag = "playLine")

        # 区切り線の描画
        application.drawGrid(pitchEditCanvas)


    def drawGrid(self,pitchEditCanvas):
        endMidiPositionPx = 500#[px]

        # 1小節を何ピクセルにするか定義[px]
        PX_PER_BAR = 400

        #入力された最後のmidiデータから前後何小節マージンを設けるか[bar]
        marginBar = 2

        # 小節数　todo みぢデータから割り出す必要あり
        BarAmount=10
        
        #右方向に向かってループする 小節区切り線の描画
        for index in numpy.arange(0,L + BarAmount * PX_PER_BAR + marginBar,PX_PER_BAR):
  
            # 拍ごとの縦線を描画
            for index2 in numpy.arange(index,index + (L + BarAmount * PX_PER_BAR + marginBar),int(PX_PER_BAR / 4)):
                
                # 線を描画
                pitchEditCanvas.create_line(index2,0,index2,5000,fill="gray",width=1,tag = "beatGrid")
            
            # 線をひく 小節単位
            pitchEditCanvas.create_line(index,0,index,5000,fill="black",width=4,tag = "mesureGrid")#5000は十分大きさ数ならなんでもいい
    def drawPlayBar(self,event,pitchEditCanvas,idName):

        # マウスの位置のスナップ位置に応じて縦線を引くメソッド

        # マウスのｘ座標を取得
        currentX = event.x

        # ウィジェット変数から現在設定されているスナップ間隔を取得
        snapInterval = cleanedSnapIntervas.get()
        
        #print(snapInterval)
        # スナップモードがフリーかそれ以外を０除算回避のために分岐
        if snapInterval != 0:

            # スナップモードがフリーモードでない時

            # どの小節に含まれているかを計算 0除算を防ぐために０はじめでなく小節番号は１はじめとする
            nearBar = int((currentX ) / PX_PER_BAR) + 1

            # オクターブごとの違いをなくしてある小節線から何ピクセル離れているかを計算
            relativeDistance = int((currentX ) % PX_PER_BAR)

            # デバッグ用確認表示
            #print("含まれる小節番号",nearBar,"　左側の小節線からの距離",relativeDistance)
            
            # あるスナップへバーが移動するのに感知する範囲
            snapRangePx = int(PX_PER_BAR / snapInterval)

            #どの区間に含まれているかインデックスを計算
            tmp1 = int((relativeDistance + snapRangePx/ 2) /snapRangePx)
            
            # 最近の区間からどの程度離れているかを計算
            tmp2 = int(relativeDistance % snapRangePx )

            #print("感知範囲",snapRangePx," どの区間か",tmp1," 最近の区間からの距離",tmp2)

            #print("========================================")
 
            # 描画ｘ座標の計算 4は補正値見た目で決定している
            playBarPosX = (PX_PER_BAR * (nearBar - 1))  + tmp1 * snapRangePx - 4

            # 線を描画 
            pitchEditCanvas.moveto(idName,playBarPosX,0)

            # グリッドと重なると見えないので最前面へプレイバーを移動
            pitchEditCanvas.lift(idName)

        else:

            # スナップモードがフリーモードの時
            # 線を描画   
            pitchEditCanvas.moveto(idName,currentX,0)

            # グリッドと重なると見えないので最前面へプレイバーを移動
            pitchEditCanvas.lift(idName)
    def chageKeyColor(self,event,canvas,idName,color):

        # キーボードの色を変えるメソッド
        canvas.itemconfig(idName,fill = color)
    def chageKeyColor2(self,event,canvas,idName,color):

         # キーボードの色を変えるメソッド
        canvas.itemconfig(idName,fill = color)
    def test(self,event):

        print("test")
    def drawKeyboad(self,keyCanvas):

       # 画面左の鍵盤を描画するメソッド
       

       #keyCanvas.grid(row =0 ,column = 0,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        #keyCanvas.bind("<Configure>",partial(application.influedMouceRotation,canvas = keyCanvas))
        #application.detectMouceRotation(tkinter.Event,keyCanvas)#todo
           
        # todo 定数類
        SCALEING_FACTOR=2
        adjustFactor = 1
        cNameDitance = 312      #c○の縦方向の描画間隔
        drawOctaveAmount = 10   # 描画するＣ基準のオクターブ
        cCount = 8             #10オクターブ分を描画するのでその１０
        cNamePositionY = 290    #C10の縦方向の表示位置

        # 1オクターブずつ描画 鍵盤描画用
        for index in numpy.arange(0,int(155 * SCALEING_FACTOR * drawOctaveAmount),int(156 * SCALEING_FACTOR)):#本来は１６５ずつずらすが誤差蓄積(おそらく線の太さ)のため少し小さくしてい   

             # Bを描画
            idName = keyCanvas.create_rectangle(0,int(0 * SCALEING_FACTOR * adjustFactor + index),C,int(22.5* SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           

             # A#を描画
            idName = keyCanvas.create_rectangle(0,int(12 * SCALEING_FACTOR * adjustFactor + index),L,int(26 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1,tag="black")

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
           

             # Aを描画
            idName = keyCanvas.create_rectangle(0,int(22.5 *SCALEING_FACTOR * adjustFactor + index),C,int(45 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           

             # G#を描画
            idName = keyCanvas.create_rectangle(0,int(38 * SCALEING_FACTOR * adjustFactor + index),L,int(52 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1,tag="black")
   
            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
           
            
            # Gを描画
            idName = keyCanvas.create_rectangle(0,int(45 * SCALEING_FACTOR * adjustFactor + index),C,int(67.5 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           
            
            # F#を描画
            idName = keyCanvas.create_rectangle(0,int(64 * SCALEING_FACTOR * adjustFactor + index),L,int(78 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1,tag="black")

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
           
            
            # Fを描画
            idName = keyCanvas.create_rectangle(0,int(67.5 * SCALEING_FACTOR * adjustFactor + index),C,int(90 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           
            
            # Eを描画
            idName = keyCanvas.create_rectangle(0,int(90 * SCALEING_FACTOR * adjustFactor + index),C,int(112.5 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           

             # D#を描画
            idName = keyCanvas.create_rectangle(0,int(103.5 * SCALEING_FACTOR * adjustFactor + index),L,int(117.5 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1,tag="black")

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
           
            
            
            # Dを描画
            idName = keyCanvas.create_rectangle(0,int(112.5 * SCALEING_FACTOR * adjustFactor+ index),C,int(135 * SCALEING_FACTOR* adjustFactor + index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))
           

            
            # C#を描画
            idName = keyCanvas.create_rectangle(0,int(130.5 * SCALEING_FACTOR * adjustFactor + index),L,int(144.5 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1,tag="black")

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
            
             # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'black'))
           



            # Cを描画
            idName = keyCanvas.create_rectangle(0,int(135 * SCALEING_FACTOR * adjustFactor+ index),C,int(156* SCALEING_FACTOR * adjustFactor+ index),fill="azure",width= 1)

            # マウスオーバーした時に色を変える
            keyCanvas.tag_bind(idName,"<Enter>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'gray'))
            
            # マウスが去ったら時に色を変える
            keyCanvas.tag_bind(idName,"<Leave>",partial(application.chageKeyColor,canvas = keyCanvas,idName = idName,color = 'azure'))



            # キャンバス生成時にタグで黒鍵とした所を全面に出す
            keyCanvas.lift("black")


        # ドの位にC3などの表示（yamaha基準でなく）国際基準で表示C8から
        for index in numpy.arange(cCount,1,-1):

            # 文字列の作成
            cName="C" + str(index)
            
            # 文字列オブジェクトの作成
            cNames = keyCanvas.create_text(120,cNamePositionY ,text = cName)

            # todo 文字を最前面にする部分を書く事
            #lift(cNames)
            cNamePositionY = cNamePositionY + cNameDitance
    def recordSound(self,applicationData,preprocessFrame):
       
        # 音声録音の時に呼び出されるイベントハンドラ

        # 使用可能なデバイスリストを取得
        deviceList = sounddevice.query_device()

        # 確認表示
        print("使用可能なデバイスは",deviceList)

        # todo 選択リストの表示

        # デバイスの選択
        sounddevice.default.device[1,6]

        # デフォルトで5秒間のの録音とする
        recordingDurationS = 5
    def loadWavs(self,whiteFrame):

        # フォルダを読み込むメソッド　フォルダパスを返す

        # デバッグ用確認表示
        print("wav読み込みを実行")
   
        # デフォルトの読み込み位置を指定
        idir = os.path.abspath(os.path.dirname(__file__))

        # フォルダ選択ダイアログを表示してファイルパスを取得
        wavFolederPats = filedialog.askdirectory(initialdir = idir)

        # ウィジェット変数にファイルパスを渡す
        #lodaFileName.set(wavFolederPats)

        # 確認表示
        print("読み込んだファイルは",wavFolederPats)

        # wavファイルを読み込み　解析
        wavDatas.processWavFiles(wavFolederPats)

        # 音声データ読み込んだフラグの修正
        applicationFormat.loadWavFlag = True


        # データテーブルを生成表示
        application.loadDataTable(whiteFrame)
    def clickNewCreate(self,applicationFormat,application,big):
       
        # 新規作成ボタンが押されたときのイベントハンドラ

        # デバッグ用確認表示
        print("音源新規作成ボタンを検出")

        # 本アプリでの情報が入ったインスタンス（作曲者、音源製作者共通）を生成
        applicationFormat = applicationDataFormat()

        # モードによらず共通して保持するパラメータ
        # 仮のファイル名を登録
        setattr(applicationFormat,'fileName','untitled')

        # 仮の著者名をアトリビュート登録
        setattr(applicationFormat,'voiceAutherName',"音源製作者名")

        # キャラクター名をアトリビュートに登録
        setattr(applicationFormat,'voicePersonalityName',"　著者名")

        # 使用許諾のテキストデータをアトリビュートに追加
        setattr(applicationFormat,'howToUse',"　list")

        # 仮の著者名をアトリビュート登録# 作曲者モードがcomposer 音源製作者モードsourceになるモードの判別文字
        setattr(applicationFormat,'usingMode',"sorceCreater")

        # 仮の著者名をアトリビュート登録 許可でTrue　不許可でFalseになる音源製作者が作曲者に編集の表示を許可するかのフラグ
        setattr(applicationFormat,'modelDisplayPermitation',True)#todo

        # 仮の著者名をアトリビュート登録Flase
        setattr(applicationFormat,'loadWavFlag',False)
   
        # デフォルトのテーブルの行数0
        setattr(applicationFormat,'totalWavAmount',0)
       
        # 音声編集画面の描画
        application.drawSourceCreaterDisplay(applicationFormat,application,big)

######################################## メイン処理 #########################################

# 本ソフトが内部データとして格納　保存するデータ形式を定義したインスタンスを生成 todo 危険なのでいつか修正したい
applicationFormat= applicationDataFormat()

# 鍵盤番号と周波数の関係を示すテーブルを作成
MidiNumber2Freq = MidiNumber2FreqTable()

# テーブルの内容を定義するメソッドを使用
MidiNumber2Freq.def_table()

# ピッチ曲線とスクリーン上の縦方向の位置の関係を示すクラスをインスタンス化
freq_2_ScreenPos_Table = freqency_2_Screenpos_Table()

# 周波数とキャンバスｙ座標の関係のテーブルを完成させる
freq_2_ScreenPos_Table.set_up_Table(freq_2_ScreenPos_Table,MidiNumber2Freq)

# guiクラスのインスタンスを生成
application = gui()

# midi関連クラスのインスタンス生成
midi = midi()

# ウィジェット変数を定義
selectedTruck = tkinter.IntVar()        # midiデータ中の選択されたトラック（０からカウント）を格納するウィジェット変数を定義
currenTargetId = tkinter.StringVar(value=0)
snapIntervas = tkinter.StringVar()
cleanedSnapIntervas = tkinter.IntVar()
windowWidth = tkinter.IntVar()          # ウィンドウ幅
windowHeight = tkinter.IntVar()         # ウィンドウ高さ
snapAmount = tkinter.IntVar()           # スナップの間隔
xScrollAmount = tkinter.IntVar()        # BGとパラメタ部を連動させたりＢＧ部のプレイバーの位置を正しくするために保存するスクロール量
yScrollAmount = tkinter.IntVar()        # BGとパラメタ部を連動させたりＢＧ部のプレイバーの位置を正しくするために保存する縦方向のスクロール量
midisBpm = tkinter.IntVar()             # BPM
startMakeNote = tkinter.BooleanVar()       # ユーザーが最初にノートを書き始めたらtrueになるフラグ
midiLoadFlag = tkinter.BooleanVar(value = False)     # midiが読み込まれたらtrueになるフラグ
editModeType = tkinter.StringVar(value = "音符編集")    # 現在の編集モードを整数で保存０が音符編集　１が歌詞編集２がピッチ編集

# 使用フォントを定義
big =ft.Font(size=20)

# コンポーザーインスタンスを生成
composerData = composer()

# メニューバーを描画
application.drawMenuBar(applicationFormat,composerData,MidiNumber2Freq.table)

# wavファイルの加工に関するクラスのインスタンスを作成
wavDatas = preprocess()

# 音源製作者モードの新規作成画面を表示
application.drawSourceCreaterDisplay(applicationFormat,application,big)

# 音源製作者モードの音声編集画面を表示
application.drawSoundEditDisplay(applicationFormat,application)

# 作曲者モードの表示
application.drawComposerDisplay(applicationFormat,application,freq_2_ScreenPos_Table.table,freq_2_ScreenPos_Table,composerData)






# 全体を囲んでるパネルに対して列方向に自動高さ調節
application.window.grid_columnconfigure(0,weight=1)
application.window.grid_rowconfigure(0,weight=1)

# イベントループ
tkinter.mainloop()
