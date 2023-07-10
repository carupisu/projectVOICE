


## 480ティックのみ対応 一定テンポのみ対応　サンプリングレート44.1kのみ対応 4/4のみ確認している　ベロシティは１２７が最大　ファイル名は＿Rが混入してるののみ除外
# 学習用音声デ＾た音声ファイルは WAV形式で 16kHz, 16bit, PCM（無圧縮）形式である必要があり ます。テキストファイルはテキスト形式で、文字コードは UTF-8です。
############################### ファイルインポート ######################

import os
import torch
import tkinter
from tkinter import filedialog
import mido
import torchaudio
import matplotlib.pyplot as plt
import time
import simpleaudio
import numpy
#from playsound import playsound
from PIL import Image,ImageDraw
from torch import nn
import pyworld as pw
import scipy.io
from scipy.io.wavfile import read
from scipy.interpolate  import interp1d
from pocketsphinx import LiveSpeech
import subprocess
import re
import shutil
import librosa
import soundfile
import pyopenjtalk
#from nnmnkwii.io import hts
#import ttslearn
import sounddevice as sd
import tkinter.font as ft
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle
################################## 定数 #################################

# gui関連
WINDOW_WIDTH_PX = 1280  #横方向のデフォルトウィンドウサイズ
WINDOW_HEIGHT_PX = 800  #縦方向のデフォルトウィンドウサイズ
FONT_STYLE = "MSゴシック"
# 音楽関連
SAMPLE_RATE = 44100     # サンプリングレートを44.1kHzで固定して定義
DEFAULT_READ_LOCATION = r'C:\Users\yuto\Desktop\projectVOICE\voice\voice'# デフォルトの読み込み位置
DELTA_TIME = 1          # 微小な時間[ms]
S_PER_BEAT = 0.5        # テンポ120の時の１拍あたりの秒数[s]
QUARTER_NOTE_TICKS = 480#4分音符一つのティック数
STANDARD_TEMPOS_S = 0.0010416666#[s]120bpmの時の秒数 todo 1テンポの秒数？
MAX_VEROCITY = 127      # ０からカウントのベロシティーの最大値

# ピアノロール関係
L=80
C = L*1.8

# グリッド線関連
VERTICAL_LENGTH = 2000      #[px]垂直線のグリッドの長さ
VERTICAL_GRID_SPACE = 300   #[px]垂直線のグリッドの間隔

# gui
RATIO_MAIN_2_TOTAL_HEIGHT = 0.6 #ウィンドウの高さに対するメイン画面の割合
RATIO_MAIN_2_TOTAL_WIDTH = 0.2  # 全体のウィンドウの幅に対する右側のエリアの幅割合

#エンジン関連
SAMPLE_RATE_MIDI_2_FREQ = 100   # midiデータから周波数データに変換する時のサンプリングレート[ms]
DEFAOUT_MIDI_TEMPO = 500000.0
MIDI_TIME_RESOLUSION_S = 0.01   #[s]のmidiデータを元に音高の周波数に変換する時間分解能

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
def save_file(event):

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

        # 引数trackNumberが不正な値でない事をチェックする
        #if type(trackNumber) is int and trackNumber >= 0 and trackNumber < len(midiFile.tracks):
        
            # 正常系の処理
            
        for msg in midiFile.tracks[trackNumber]:
             if msg.type =="note_on" and msg.dict()["velocity"] !=0:
                 count +=1
        #else:
            # 異常系のしょり

            #return None

        return count
    def draw_Midis(self,midiData,selectedTruck):

        # 指定されたmidiファイルのトラックを元に画面にノートを表示するメソッド
        
        # キャンバスを作成
        #canvas = tkinter.Canvas(root,bg="white")

        #id = canvas.create_rectangle(20,10,280,190,fill = "blue2",width=1)

       # print(selectedTruck)
       pass

    def kill_window(self,dlg_modal):
        
        #　ウィンドウを消す
        dlg_modal.destroy()

    def get_Index(event):

        # 選択された要素を変数にする
        selectedTruck = event.widget.curselection[0]

        print("選択トラックは",selectedTruck)

        return selectedTruck
    def select_midi_track(self):

        # 読み込んだを時間vs周波数と時間vs継続長のデータに変換するメソッド
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
            addData = index ,' :音符の総数',self.countNotes(midiData,index)
            
            trackList.append(addData)

        v1 = tkinter.StringVar(value = trackList)

        # リストボックスの作成
        listBox = tkinter.Listbox(dlgTop,width = 20,selectmode=tkinter.SINGLE,listvariable=v1)
        
        #listBox.bind("<<ListboxSelect>>",midi.get_Index)

                # 選択された要素を変数にする
        selectedTruck = listBox.curselection()

        print(selectedTruck)
        # スクロールバーの作成
        scrollbar = ttk.Scrollbar(dlgTop,orient="vertical",command=listBox.yview)

        # スクロールバーの機能化
        listBox['yscrollcommand']= scrollbar.set

        # スクロールバーの配置
        scrollbar.grid(row=0,column=1,sticky=(tkinter.N, tkinter.S))

        # リストボックスを配置
        listBox.grid(row=0,column=0)


        # ボタンの作成
        okButton = ttk.Button(dlgTop ,text = "読み込み",command=lambda:[midi.get_Index,midi.draw_Midis(midiData,selectedTruck),midi.kill_window(dlg_modal)])
        
        # ボタンの配置
        okButton.grid(row=1,column=0)

    def import_Midi(self):
   
        

        # midiデータからビートあたりのティック数を読み込み
        ticksPerBeat = midiData.ticks_per_beat


        # 1
        #msPerTicks = S_PER_BEAT * tempo ticksPerBeat / 1000
        # 確認表示
        #print("1拍あたりのティック数",ticksPerBeat,"ビートあたりのティック数は[ms]",msPerTicks)

        # 全体時間を算出
        totalTimeMs = DEFAOUT_MIDI_TEMPO / ticksPerBeat / 1000.0
        # 確認表示
        print("全体時間[s]",totalTimeMs)

        # 1ティックあたりの時間[s]を計算
        TimePerTicks = midiData.ticks_per_beat
        # 確認表示
        print("1ティックの時間[s]",TimePerTicks)

        # 対象トラックのメッセージ数にアクセス

        #for note in inreadMidiData
        #print("総timeは",midiData)

        # 時間（横軸）vs周波数（縦軸）のテンソルデータ型を定義
        timeVsFreqVsVel = torch.Tensor([[0,0]])

        # 確認表示
        print("トーチのサイズは",timeVsFreqVsVel.size())
        print("総トラック数は")

        # 選択されるトラック番号 todo
        choicedTrackNo = 0;

        # 選択されたトラックの
        messagesAmount = midiData.tracks[choicedTrackNo]
   
        # ms単位での周波数をプロットする時刻を格納する変数を定義
        currentTime = 0

        # 現在取り扱ってるノートの番号を格納
        currentNoteIndex = 0

        # 最初のトラックのメッセージにアクセス
        for targetMassage in midiData.tracks[choicedTrackNo]:

            # 現在時刻[ms]を計算
            currentTime = currentTime + targetMassage.time * totalTimeMs

            # テンポを取得
            if targetMassage.type =='set_tempo':

                tempo = 60000000.0 / targetMassage.tempo
                print("tenpo:",tempo)

            # 全体時間を算出
            #absTimeMs = tempo / ticksPerBeat / 1000.0
            # 確認表示
            #print("時刻",absTimeMs)

            # メタデータ以外のみを取り出す
            if not targetMassage.is_meta:
           
                # ノートがオンオフの時かどうか反映
                if targetMassage.type == 'note_off' or targetMassage.type == 'note_on' :

                    # midiノートを周波数に変換する
                    freq = float(440 * 2 **((targetMassage.note- 69) / 12))

                    # 記録する時刻[s]を計算する
                    mS = STANDARD_TEMPOS_S * tempo / 120
               
                    # 記録する時刻[s]を計算する
                    currentTime = currentTime + targetMassage.time * mS
               
                    # 確認表示
                    #print("index",currentNoteIndex," ノート番号:",targetMassage.note , " 周波数[Hz]:" ,freq,"現在時刻[ms]" ,currentTime," 時間（midi）",targetMassage.time )
               
                    # 追加要素を作成(周波数)
                    addElement = torch.Tensor([[currentTime,freq]])

                    # 追加要素をテンソルデータに追加
                    timeVsFreqVsVel = torch.cat((timeVsFreqVsVel,addElement),dim=0)

                    # ベロシティを正規化する
                    normalizedVerocity = float(targetMassage.velocity / MAX_VEROCITY)

                    # 追加要素を作成(強さ（最小０最大１）)
                    addElement2 = torch.Tensor([[currentTime,normalizedVerocity]])

                    # 追加要素をテンソルデータに追加
                    #timeVsFreqVsVel = torch.cat((timeVsFreqVsVel,addElement2),dim=0)

                    # 現在のノートのインデックスを更新
                    currentNoteIndex = currentNoteIndex + 1
               
                    #print(addElement)
                    #print(timeVsFreqVsVel)

                # ノートがオフの時の処理
                #else:

   
        # GPU用データに変換
        timeVsFreqVsVel.cuda()

        # 確認表示 ms VS freq
        print(timeVsFreqVsVel)

        return timeVsFreqVsVel

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
   
    #@staticmethod
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
           

    def drawComposerDisplay(self,applicationFormat,application):

        ##############################################　楽曲クリエーター用画面 ####################################
        global pitchEditCanvas
        # 全体を包むフレームを作成
        totalFrame = tkinter.Frame(application.window)

        # 全体を包むフレームを画面いっぱいに表示
        totalFrame.grid(row=0,column=0,sticky="nsew")

        # メインとパラメータ用パンウィンドウを作る
        mainParamaterWindow = tkinter.PanedWindow(application.window,orient = tkinter.VERTICAL)

        # ピッチ編集部とパラメタ編集部を含む部分のフレームを作成
        mainFrame = tkinter.Frame(application.window,height=100,bg = 'orange',bd = 0)
       
        # ピッチとパラメタが合わさった部分を列方向にめいいっぱいに広げる　
        mainFrame.grid_columnconfigure(0,weight = 1)

        # ピッチとパラメタが合わさった部分を行方向にめいいっぱいに広げる　
        mainFrame.grid_rowconfigure(0,weight = 1)

        # ピッチ編集部のキャンバスを作成
        pitchEditCanvas = tkinter.Canvas(mainFrame,width = 100,height=400,bg = "white",bd = 0,relief = 'flat',scrollregion =(0,0,1600,1000))

        # ピッチ編集部キャンバスを配置
        pitchEditCanvas.grid(row =0 ,column = 0,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        # ピッチ編集部のキャンバスの配置
        mainParamaterWindow.grid_columnconfigure(0,weight = 1)
        mainParamaterWindow.grid_rowconfigure(0,weight = 1)

       
 
        #イベント処理の設定
        #pitchEditCanvas.bind("<Enter>",self.startMidDrag)
        #pitchEditCanvas.bind("<ButtonPress>",self.midDrag)
        #pitchEditCanvas.bind("<ButtonRelease>",self.endMidDrag)

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
   
        # パラメータのフレームを作成
        paramatorFrame = tkinter.Frame(application.window,bg = "gray",bd = 2)

        # フレームはスクロール出来ないので内側にキャンバスを作成(パラメタキャンバスと呼称)
        paramCanvas = tkinter.Canvas(paramatorFrame,bg = 'gray10',relief = 'flat', bd = 1)

        # パラメタキャンバスを配置
        paramCanvas.grid(row = 0,column = 0,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)


        paramatorFrame.grid_columnconfigure(0,weight = 1)
        paramatorFrame.grid_rowconfigure(0,weight = 1)

        # パラメタ部の水平方向スクロールバーを作成
        paramXbar = tkinter.Scrollbar(paramCanvas,orient = tkinter.HORIZONTAL)

        # パラメタ部のスクロールバーを配置
        paramXbar.grid(row = 1,column = 0,sticky = tkinter.W + tkinter.E)

        # 列方向にめいいっぱいに広げる　
        paramCanvas.grid_columnconfigure(0,weight = 1)



        # パラメタ部の垂直方向スクロールバーを作成
        paramYbar = tkinter.Scrollbar(paramCanvas,orient = tkinter.VERTICAL)

        # パラメタ部のスクロールバーを配置
        paramYbar.grid(row = 0,column = 1,sticky = tkinter.N + tkinter.S)

        # 列方向にめいいっぱいに広げる　
        paramCanvas.grid_rowconfigure(0,weight = 1)



        # メイン、パラメータウィンドウをパンドウィンドウに追加
        mainParamaterWindow.add(mainFrame)
        mainParamaterWindow.add(paramatorFrame)

        # パンドウィンドウを配置
        mainParamaterWindow.grid(row = 0,column = 0,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        # 全体を囲んでるパネルに対して列方向に自動高さ調節
        application.window.grid_columnconfigure(0,weight=1)
        application.window.grid_rowconfigure(0,weight=1)
       
        # 右側のフレームを作成
        optionFrame = tkinter.Frame(application.window,width=WINDOW_WIDTH_PX * RATIO_MAIN_2_TOTAL_WIDTH ,height=WINDOW_HEIGHT_PX ,bg = "gray",bd = 2)

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

       
        # BPMのラベルを作成
        bpmLabel = tkinter.Label(operateFrame,text="BPM",bg="gray13",fg="white")

        # ＢbpmLabelＭのラベルを配置
        bpmLabel.grid(row=1,column=0,sticky=tkinter.W)

        # 4拍子か３拍子か変拍子（←これはtodo）を
        beatTypeLabel = tkinter.Label(operateFrame,text="拍子の種類",fg="white",bg="gray13")

        # ＢbpmLabelＭのラベルを配置
        beatTypeLabel.grid(row=2,column=0,sticky=tkinter.W)

        # 拍子を示すリストを定義
        beatTyopes = ("４拍子","３拍子","変拍子（未実装）")
        
        # 拍子の設定用コンボボックスの作成
        beatTypeCombo = ttk.Combobox(operateFrame,width=6,height=1,values = beatTyopes)

        # midi編集時のスナップ間隔を示すラベルの定義
        snapIntervalLabel = tkinter.Label(operateFrame,text="midi操作時のスナップ間隔",fg="white",bg="gray13")


        # スナップの粗さを示すリストを定義
        snapTyopes = ("４分音符","８分音符","１６音符","32分音符","フリー")
        
        # スナップ設定用コンボボックスの作成
        snapTypeCombo = ttk.Combobox(operateFrame,width=6,height=1,values = snapTyopes)

        # スナップ用のラベルを配置
        snapIntervalLabel.grid(row=2,column=0,sticky=tkinter.W)


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

        # キャンバスの右に垂直方向スクロールバーを配置
        #ybar.grid(row = 0,column = 1,sticky=tkinter.N + tkinter.S)

        # スクロールバーのスライダーが動かされた時に実行する処理を設定
        #xbar.config(command=mainCanvas.xview)
        #ybar.config(command=mainCanvas.yview)

        # キャンバススクロール時に実行する処理を設定
        #mainCanvas.config(xscrollcommand=xbar.set)
        #mainCanvas.config(yscrollcommand=ybar.set)

        # 背景を描画
        application.mainBG(pitchEditCanvas)

        # グリッド線を描画
        #application.drawGrid(pitchEditCanvas)


        # 鍵盤を描画
        application.drawKeyboad(pitchEditCanvas)

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

    def drawFrames(self):
       pass
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

    def drawMenuBar(self,applicationFormat):

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
        menu_import.add_command(label='MIDI', command = midi.select_midi_track)
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

    def click(self,event):

        # ノート（を示す長方形が）がクリックされた時の処理
        
        global oldX,oldY
        global selectedNoteFig
        
        # カーソルのｘ、ｙ座標を取得
        currentX = event.x
        currentY = event.y

        # クリック位置から一番違い図形ＩＤ取得
        selectedNoteFig = pitchEditCanvas.find_closest(currentX,currentY)

        # 相対移動処理が終わったので現在のｘ、ｙ座標を１つ前時刻のｘ、ｙ座標として記録
        oldX = currentX 
        oldY = currentY

    def drag(self,event):

        global oldX,oldY

        # カーソルのｘ、ｙ座標を取得
        currentX = event.x
        currentY = event.y

        # 前回のマウスからの移動量だけ図形を相対移動
        pitchEditCanvas.move(selectedNoteFig,currentX - oldX,currentY - oldY)

        # 相対移動処理が終わったので現在のｘ、ｙ座標を１つ前時刻のｘ、ｙ座標として記録
        oldX = currentX 
        oldY = currentY

    def mainBG(self,pitchEditCanvas):
       

        SCALEING_FACTOR=2 
         # 4オクターブ分繰り返し描画横方向の帯を白鍵黒鍵に対応する形の色で描画
        for index in numpy.arange(0,5 * 150 * SCALEING_FACTOR,156 * SCALEING_FACTOR):   

            pitchEditCanvas.create_rectangle((0,0*SCALEING_FACTOR + index,2000,13 * SCALEING_FACTOR  + index),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,13*SCALEING_FACTOR + index,2000,26 * SCALEING_FACTOR + index ),fill="gray21",width= 1)

            pitchEditCanvas.create_rectangle((0,26*SCALEING_FACTOR + index,2000,39 * SCALEING_FACTOR + index ),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,39*SCALEING_FACTOR + index,2000,52 * SCALEING_FACTOR + index ),fill="gray21",width= 1)

            pitchEditCanvas.create_rectangle((0,52*SCALEING_FACTOR + index,2000,65 * SCALEING_FACTOR + index ),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,65*SCALEING_FACTOR + index,2000,78 * SCALEING_FACTOR + index ),fill="gray21",width= 1)

            pitchEditCanvas.create_rectangle((0,78*SCALEING_FACTOR + index,2000,91 * SCALEING_FACTOR + index ),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,91 *SCALEING_FACTOR + index,2000, 104 * SCALEING_FACTOR + index),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,104*SCALEING_FACTOR + index,2000,117 * SCALEING_FACTOR + index ),fill="gray21",width= 1)

            pitchEditCanvas.create_rectangle((0,117*SCALEING_FACTOR + index,2000,130 * SCALEING_FACTOR + index ),fill="gray31",width= 1)

            pitchEditCanvas.create_rectangle((0,130*SCALEING_FACTOR + index,2000,143 * SCALEING_FACTOR + index ),fill="gray21",width= 1)

            pitchEditCanvas.create_rectangle((0,143*SCALEING_FACTOR + index,2000, 157 * SCALEING_FACTOR + index),fill="gray31",width= 1)
        
            noteAmount=10 #todo 仮
           
            # 音符の数だけ長方形を描画
            for index in numpy.arange(0,noteAmount,1):

                notes = pitchEditCanvas.create_rectangle(100,100,200,200,fill="blue2")

                # 縦線を描画するメソッド

                # 描画した図形にイベント処理設定
                pitchEditCanvas.tag_bind(notes,"<ButtonPress-1>",application.click)
                pitchEditCanvas.tag_bind(notes,"<Button1-Motion>",application.drag)
        endMidiPositionPx = 500#[px]
        # 1小節を何ピクセルにするか定義[px]
        PX_PER_BAR = 400

        #入力された最後のmidiデータから前後何小節マージンを設けるか[bar]
        marginBar = 2

        # 小節数　todo みぢデータから割り出す必要あり
        BarAmount=10

        #右方向に向かってループする 小節区切り線の描画
        for index in numpy.arange(C,L + BarAmount * PX_PER_BAR + marginBar,PX_PER_BAR):

          
            # 拍ごとの縦線を描画
            for index2 in numpy.arange(index,index + (L + BarAmount * PX_PER_BAR + marginBar),int(PX_PER_BAR / 4)):
                
                # 長方形を描画
                pitchEditCanvas.create_line(index2,0,index2,5000,fill="gray",width=1)

            pitchEditCanvas.create_line(index,0,index,5000,fill="black",width=4)#5000は十分大きさ数ならなんでもいい

    def drawKeyboad(self,pitchEditCanvas):

       # 画面左の鍵盤を描画するメソッド
       
  
        SCALEING_FACTOR=2
        adjustFactor = 1

        # 1オクターブずつ描画
        for index in numpy.arange(0,int(155 * SCALEING_FACTOR * 5),int(156 * SCALEING_FACTOR)):#本来は１６５ずつずらすが誤差蓄積(おそらく線の太さ)のため少し小さくしてい   

            # Cを描画
            pitchEditCanvas.create_rectangle(0,int(135 * SCALEING_FACTOR * adjustFactor+ index),C,int(156* SCALEING_FACTOR * adjustFactor+ index),fill="azure",width= 1)

            # ドの位置を（yamaha基準でなく）国際基準で表示
            #cPosition="1"
            #test = tkinter.Label(pitchEditCanvas,text=cPosition)
            #test.grid(row=0,column=0)
            # Dを描画
            pitchEditCanvas.create_rectangle(0,int(112.5 * SCALEING_FACTOR * adjustFactor+ index),C,int(135 * SCALEING_FACTOR* adjustFactor + index),fill="azure",width= 1)

            # Eを描画
            pitchEditCanvas.create_rectangle(0,int(90 * SCALEING_FACTOR * adjustFactor + index),C,int(112.5 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # Fを描画
            pitchEditCanvas.create_rectangle(0,int(67.5 * SCALEING_FACTOR * adjustFactor + index),C,int(90 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # Gを描画
            pitchEditCanvas.create_rectangle(0,int(45 * SCALEING_FACTOR * adjustFactor + index),C,int(67.5 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # Aを描画
            pitchEditCanvas.create_rectangle(0,int(22.5 *SCALEING_FACTOR * adjustFactor + index),C,int(45 * SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # Bを描画
            pitchEditCanvas.create_rectangle(0,int(0 * SCALEING_FACTOR * adjustFactor + index),C,int(22.5* SCALEING_FACTOR * adjustFactor + index),fill="azure",width= 1)

            # C#を描画
            pitchEditCanvas.create_rectangle(0,int(130.5 * SCALEING_FACTOR * adjustFactor + index),L,int(144.5 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1)

            # D#を描画
            pitchEditCanvas.create_rectangle(0,int(103.5 * SCALEING_FACTOR * adjustFactor + index),L,int(117.5 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1)

            # F#を描画
            pitchEditCanvas.create_rectangle(0,int(64 * SCALEING_FACTOR * adjustFactor + index),L,int(78 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1)

            # G#を描画
            pitchEditCanvas.create_rectangle(0,int(38 * SCALEING_FACTOR * adjustFactor + index),L,int(52 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1)
   
            # A#を描画
            pitchEditCanvas.create_rectangle(0,int(12 * SCALEING_FACTOR * adjustFactor + index),L,int(26 * SCALEING_FACTOR * adjustFactor + index),fill="black",width= 1)

          
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

# ウィジェット変数を定義
# 音符を示す長方形をグローバル変数として定義

# 本ソフトが内部データとして格納　保存するデータ形式を定義したインスタンスを生成
applicationFormat= applicationDataFormat()

# guiクラスのインスタンスを生成
application = gui()

# midi関連クラスのインスタンス生成
midi = midi()

# 使用フォントを定義
big =ft.Font(size=20)

# メニューバーを描画
application.drawMenuBar(applicationFormat)

# wavファイルの加工に関するクラスのインスタンスを作成
wavDatas = preprocess()

# 音源製作者モードの新規作成画面を表示
application.drawSourceCreaterDisplay(applicationFormat,application,big)

# 音源製作者モードの音声編集画面を表示
application.drawSoundEditDisplay(applicationFormat,application)

# 作曲者モードの表示
application.drawComposerDisplay(applicationFormat,application)

# イベントループ
tkinter.mainloop()



	
