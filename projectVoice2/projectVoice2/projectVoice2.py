

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
WHIHTE_KEYBOAD_WIDTH = 100  #[px]白鍵の幅
WHIHTE_KEYBOAD_AMOUNT = 51  # 白鍵の数
WHIHTE_KEYBOAD_SPACE = 20   #[px]白鍵同士の間隔
BLACK_KEYBOAD_WIDTH = 60    #[px]白鍵の幅
BLACK_KEYBOAD_AMOUNT = 51   # 白鍵の数（間引く前）
BLACK_KEYBOAD_SPACE = 20    #[px]白鍵同士の間隔
HORIZON_LENGTH = 2000       #[px]水平線グリッドの長さ

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

def import_wav(event):
   
    # wavファイルを読み込みの時のイベント関数

    # タイプの設定
    type = [('WAV','*.wav')]
   
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
   
    def startMidDrag(event):
        global isClicking
        global cousolPosX
        global cousolPosY

        # クリックしてる時のイベントハンドラなのでフラグを立てる
        isClicking

        # 現在のマウスの位置を記憶
        oldCourslePosX = event.x
        oldCourslePosy = event.y

    def import_Midi(self):
   
        # 読み込んだを時間vs周波数と時間vs継続長のデータに変換するメソッド
        # タイプの設定
        type = [('MIDI','*.mid')]
   
        # デフォルトのディレクトリを設定してダイアログ表示
        readMidiData = filedialog.askopenfilename(filetypes = type,initialdir = DEFAULT_READ_LOCATION)
   
        # midiデータを読み込み変数に格納
        midiData = mido.MidiFile(readMidiData,clip=True)

        #確認表示
        print(midiData)

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
            # テキストラベルの作成
            setWavLabel = tkinter.Label(editSoundsFrame,text="wavファイルが入ったフォルダを指定してください。")
            setWavLabel.grid(row = 0,column =0 )

              # 基本設定部の記述
            menus = tkinter.Frame(editSoundsFrame,width=800,height=140,bg = 'gray8',bd = 0)


            menus.grid_propagate(False)
           
            # 諸設定を包むフレームを画面いっぱいに表示
            menus.grid(row=0,column=0,columnspan="2",sticky=tkinter.W+tkinter.E)


            # 基本設定部の記述
            extraSettingFrame=tkinter.Frame(menus,width=400,height=140,bg = 'red',bd = 0)

            # フレームサイズの自動調整を無効化する
            extraSettingFrame.grid_propagate(False)

            # 諸設定を包むフレームを画面いっぱいに表示
            extraSettingFrame.grid(row=0,column=0,sticky=tkinter.W+tkinter.E)

            # 操作カテゴリを示すラベルの作成
            label12 = tkinter.Label(extraSettingFrame,text="基本設定")
            label12.grid(row = 0,column = 0,columnspan = 3 )

            # 制作者名ラベルの作成
            label13 = tkinter.Label(extraSettingFrame,text="制作者名")
            label13.grid(row = 1,column = 0 ,sticky = tkinter.E)

            # 制作者名のテキスト入力
            createrNameTxt = tkinter.Entry(extraSettingFrame,width=30)
            createrNameTxt.grid(row = 1,column =1 ,sticky= tkinter.W)

            # キャラクタ名ラベルの作成
            charaNameLabel = tkinter.Label(extraSettingFrame,text="キャラクタ名")
            charaNameLabel.grid(row = 2,column =0 ,sticky = tkinter.E)

            # キャラクタ名のテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=30)
            charaName.grid(row = 2,column =1 ,sticky= tkinter.E)

            # 利用条件テキストファイルラベルの設定
            label10 = tkinter.Label(extraSettingFrame,text="利用条件テキストファイル")
            label10.grid(row = 3,column =0 ,sticky = tkinter.E)

            # 利用条件テキストファイルののテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=20)
            charaName.grid(row = 3,column =1 ,sticky= tkinter.E)


            # readMeテキスト設定のラベルを設定
            label10 = tkinter.Label(extraSettingFrame,text="ReadMe.txtの設定")
            label10.grid(row = 4,column =0 ,sticky = tkinter.E)

            # readMeテキスト設定のテキスト入力
            charaName = tkinter.Entry(extraSettingFrame,width=20)
            charaName.grid(row = 4,column =1 ,sticky= tkinter.E)

            # ユーザー閲覧許可設定のラベル
            label11 = tkinter.Label(extraSettingFrame,text="使編集画面の閲覧と編集を許可")
            label11.grid(row = 5,column =0 ,sticky = tkinter.E)

            # ラジオボタンが初期設定でオンになっているものを指定する変数を確保
            radioChecked = tkinter.IntVar()

            # 許可するにチェック
            radioChecked.set(0)

            # ラジオボタンの作成
            permited = tkinter.Radiobutton(extraSettingFrame,value = 0,variable = radioChecked,text="する")
            notPermited = tkinter.Radiobutton(extraSettingFrame,value = 1,variable = radioChecked,text="しない")

            # ラジオボタンの配置
            permited.grid(row = 5,column =1)
            notPermited.grid(row = 5,column =2)


            # 録音部の記述
            RecordingFrame=tkinter.Frame(menus,width=180,height=140,bg = 'purple',bd = 0)

            
            # フレームサイズの自動調整を無効化する
            RecordingFrame.grid_propagate(False)
            
            # フレームを画面いっぱいに表示
            RecordingFrame.grid(row = 0,column = 1)


            # 録音カテゴリを示すラベルの作成
            recordingLabel = tkinter.Label(RecordingFrame,text="録音")
            recordingLabel.grid(row = 0,column = 0,columnspan = 2)
            
            
            # 発音名を示すラベルの作成
            recordingLabel = tkinter.Label(RecordingFrame,text="発音")
            recordingLabel.grid(row = 1,column = 0,sticky= tkinter.E)

            # 発音名のテキスト入力
            RecordingName = tkinter.Entry(RecordingFrame,width=20)
            RecordingName.grid(row = 1,column =1 ,sticky= tkinter.E)

            #録音ボタンを定義
            recordingButton= tkinter.Button(RecordingFrame,text ="●",width=8,height=3,command =lambda:application.recordSound(applicationData,preprocessFrame))

            # 録音ボタンを設置
            recordingButton.grid(row=2,column=0,columnspan = 2,sticky= tkinter.W+tkinter.E)


            
            # 前処理部の記述
            preprocessFrame=tkinter.Frame(menus,width=200,height=140,bg = 'orange',bd = 0)

            # フレームサイズの自動調整を無効化する
            preprocessFrame.grid_propagate(False)

            # フレームを表示
            preprocessFrame.grid(row = 0,column = 2)
           
            # 操作カテゴリを示すラベルの作成
            preprocessLabel = tkinter.Label(preprocessFrame,text="前処理")
            preprocessLabel.grid(row = 0,column = 0)


            # 抽出音素とファイル名の比較ボタンを定義
            loadFolderButton= tkinter.Button(preprocessLabel,text ="検出音素と実発音が違うデータを削除",width=25,height=2)

            # 抽出音素とファイル名の比較ボタンを設置
            loadFolderButton.grid(row=1,column=0)


            # 学習部の記述
            learningFrame=tkinter.Frame(menus,width=200,height=140,bg = 'black',bd = 0)

            # 自動調節をオフに
            learningFrame.grid_propagate(False)

            # 操作カテゴリを示すラベルの作成
            learningLabel = tkinter.Label(learningFrame,text="学習")
            learningLabel.grid(row = 0,column = 0)

            # フレームを画面いっぱいに表示
            learningFrame.grid(row = 0,column = 3)

            # モデルの学習ボタンを作成
            modelLearnButton= tkinter.Button(learningFrame,text ="モデルの学習",width=10,height=3)

            # モデル学習ボタンの配置
            modelLearnButton.grid(row=1,column=0)

            # モデルの書き出し部の記述
            exportLabel=tkinter.Frame(menus,width=200,height=140,bg = 'red',bd = 0)

            # 自動配置をオフに
            exportLabel.grid_propagate()
            # モデル書き出し部の配置
            exportLabel.grid(row = 0,column = 4)

             # 操作カテゴリを示すラベルの作成(モデル書き出し)
            expoteModel = tkinter.Label(exportLabel,text="モデル書き出し")
            expoteModel.grid_propagate(False)
            expoteModel.grid(row = 0,column = 0)

            # モデルの学習ボタンを作成
            export= tkinter.Button(expoteModel,text ="モデルの書き出し",width=10,height=3)

            # モデル学習ボタンの配置
            export.grid(row=1,column=0)

            # 背景用のフレームを作成
            dataFrame = tkinter.Frame(editSoundsFrame,width=1000,height=1000,bg='white')
            
            # フレームの自動調整機能をオフにする
            dataFrame.grid_propagate(False)

            # 背景用のフレームを表示
            dataFrame.grid(row=1,column=0,columnspan=2)
            

            #スクロール用キャンバスを作成
            tableCanvas = tkinter.Canvas(dataFrame,bg = 'red',width=975,height=800,scrollregion=(0,0,1000,2000))
            
            # キャンバスのサイズの自動調整機能のオフ
            tableCanvas.grid_propagate(False)

            # スクロールするキャンバスを配置
            tableCanvas.grid(row=0,column=0)
            #frame = tkinter.Frame(tableCanvas)

            # 垂直のスクロールバーを作成
            vsb = tkinter.Scrollbar(dataFrame,orient=tkinter.VERTICAL)

            # 垂直スクロールバーの配置
            vsb.grid(row=0,column=1,sticky=tkinter.N+tkinter.S)

  
            # 縦スクロールバーの機能を書く
            tableCanvas.configure(yscrollcommand=vsb.set)


            # キャンバスの中にフレームを置く
            #tableInnerCanvas = tkinter.Canvas(width=800,height=800,bg = 'yellow')

            # キャンバスサイズ自動調整機能をオフに
            #tableInnerCanvas.grid_propagate(False)

            # キャンバスの内側にあるフレームの配置
           # tableInnerCanvas.grid(row=0,column=0)

            # データテーブルと読み込みボタンを生成表示
            #application.loadDataTable(tableInnerCanvas)

        else:

            # デバッグ用確認表示
            print("表示不許可設定を検出")


            # インデックスよう
            index = tkinter.Frame(editSoundsFrame,width=1000,height=1000,bg = 'gray22')
            index.grid(row=1,column=0,columnspan=3)

            # 見出しの作成
            soundEditFrame = tkinter.Label(index,text="音源クリエーターの意向により内部データを表示しません",font=big)
            soundEditFrame.grid(row = 0,column =0 )
   
    def loadDataTable(self,dataTable):
        
        # データテーブルを生成表示
        #dataTable = application.loadDataTable(editSoundsFrame)
        dataTable.grid_propagate(False)            
        dataTable.grid(row=0,column=0,columnspan=4)#ここの４はtodo

        # wavデータが０かそれ以外かで条件分岐
        if applicationFormat.totalWavAmount != 0:

            # wavデータの数だけループ処理
            for index in numpy.arange(0,int(applicationFormat.totalWavAmount),1):

                # 本レコードを格納するフレームを作成
                tableRecord = tkinter.Frame(dataTable,width='1000',height=100,bg = 'yellow',bd = 2)
               
                # レコードを配置
                tableRecord.grid(row=index + 2,column=0)

                # グラフの描画 キャンバス
                graphFrame = application.drawFigAsFrame(applicationFormat,index)
      
                graphFrame.grid(row=index,column=0)
               
                # 録音カテゴリを示すラベルの作成
                phoneLabel = tkinter.Label(tableRecord,text="音素")
                phoneLabel.grid(row = index + 2,column = 1)

                
                # 音素についてのループ
                for phone in numpy.arange(0,int(getattr(applicationFormat,"PhonesAlignment" + str(index))[2]),1):

 
                    # 音素の名前を取得
                    alignmentName = getattr(applicationFormat,"correctPhones" + str(index))

                    print(alignmentName)
                    # アライメントの数だけチェックボックスを表示
                    alignment = tkinter.Checkbutton(tableRecord,text = alignmentName[phone])

                    # チェックボックスの配置
                    alignment.grid(row = phone + 1,column =1)
                
        else:

            # データが読み込まれていない時の処理
            # フォルダ読み込み用ボタンを作成
            loadFolderButton= tkinter.Button(dataTable,text ="音声フォルダの読み込み",width=20,height=2,command =lambda:application.loadWavs(editSoundsFrame))

            # ボタンの配置
            loadFolderButton.grid(row = 2,column = 0,columnspan = 3)

            print("wavデータなし")
       
            return dataTable
           

    def drawComposerDisplay(self,applicationFormat,application):
        ##############################################　楽曲クリエーター用画面 ####################################

        # 全体を包むフレームを作成
        totalFrame = tkinter.Frame(application.window)

        # 全体を包むフレームを画面いっぱいに表示
        totalFrame.grid(row=0,column=0,sticky="nsew")

        # メインとパラメータ用パンウィンドウを作る
        mainParamaterWindow = tkinter.PanedWindow(application.window,orient = tkinter.VERTICAL)

        # ピッチ編集部とパラメタ編集部を含む部分のフレームを作成
        mainFrame = tkinter.Frame(application.window,height=100,bg = 'red',bd = 0)
       
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

       
        test = tkinter.Label(pitchEditCanvas,text="ラベル")
        test.grid(row=0,column=0)
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
        #paramYbar = tkinter.Scrollbar(paramCanvas,orient = tkinter.VERTICAL)

        # パラメタ部のスクロールバーを配置
        #paramYbar.grid(row = 0,column = 1,sticky = tkinter.N + tkinter.S)

        # 列方向にめいいっぱいに広げる　
        #paramCanvas.grid_columnconfigure(0,weight = 1)



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

        # 右側のフレームをを配置
        optionFrame.grid(row = 0,column = 1,sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)




        # 歌詞のラベルを作成
        lblLyric = tkinter.Label(text="歌詞")

        # 歌詞のラベルを配置
        lblLyric.grid(row=0,column=0,sticky=tkinter.W)

        # 歌詞入力用のテキストエントリを作る
        lyricText = tkinter.Entry(optionFrame,width=30)

        # 歌詞入力エントリを配置
        lyricText.grid(row=1,column=0)

        # 歌詞読み込みボタンの作成
        lyricIncertButton = tkinter.Button(optionFrame,text ="歌詞流し込み",width=10,height=2)

        # ボタンの配置
        lyricIncertButton.grid(row=2,column=0,sticky=tkinter.W)

        # 入力文字を取得
        lyricData = lyricText.get()

        print(lyricData)


        # クリエイトボイスボタンの作成
        createButton = tkinter.Button(optionFrame,text ="生成",width=10,height=2)

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
        application.drawGrid(pitchEditCanvas)


        # 鍵盤を描画
        application.drawKeyboad(pitchEditCanvas)

    def drawSourceCreaterDisplay(self,applicationFormat,application,big):
       
        ################################### 音源クリエーターモード ##################################

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
        #self.canvas.draw()
       # plt.show()
       
        #returnData = self.canvas

        # matplotlibのグラフをキャンバスに配置
        returnData = self.canvas.get_tk_widget()

        return returnData
       
    def collectData(saveData):
        return saveData

    def drawFrames(self):
       
 
        totalFrame.tkraise()
   
    def MidDrag(event):
       
        # ドラッグ中の移動処理を記述する関数
        pass
       
    def endMidDrag(event):

        # ドラッグが終わった時のイベントハンドラ
        global isCkicking

        # ドラッグが終了したのでフラグをおろす
        isCkicking =False
   
    def changeMode2Main(self,application):

        # 楽曲クリエーターモードに画面を切り替えるメソッド
       
        totalFrame.tkraise()
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
        menu_import.add_command(label='personality', command = import_wav)
        menu_import.add_separator()

        # 子要素（midi読み込み)を設置
        menu_import.add_command(label='MIDI', command = midi.import_Midi)
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

    def drawGrid(self,pitchEditCanvas):
       
       # 横区切り線を描画するメソッド

        # グリッド水平線を描画
        for index in range(WHIHTE_KEYBOAD_AMOUNT):
           
            # 長方形の左上と右下の座標を計算
            startX = 0
            startY = WHIHTE_KEYBOAD_SPACE * index
            endX = HORIZON_LENGTH
            endY =  WHIHTE_KEYBOAD_SPACE * index

            # 計算された座標に基づいて線を描画
            pitchEditCanvas.create_line(startX,startY,endX,endY,fill="gray8",width= 1)

        # グリッド垂直線を描画
        for index in range(WHIHTE_KEYBOAD_AMOUNT):
           
            # 長方形の左上と右下の座標を計算
            startX = WHIHTE_KEYBOAD_WIDTH + VERTICAL_GRID_SPACE * index
            startY = 0
            endX = WHIHTE_KEYBOAD_WIDTH + VERTICAL_GRID_SPACE * index
            endY =  VERTICAL_LENGTH

            # 計算された座標に基づいて線を描画
            pitchEditCanvas.create_line(startX,startY,endX,endY,fill="gray8",width= 2)
   
    def mainBG(self,pitchEditCanvas):
       
        # グリッド水平線を描画
        for index in range(0,WHIHTE_KEYBOAD_AMOUNT,2):
           
            GRID_HEIGHT_SPACE = WHIHTE_KEYBOAD_SPACE * 0.8
            # 長方形の左上と右下の座標を計算
            startX = 0
            startY = index * GRID_HEIGHT_SPACE
            endX = 6000
            endY =  (index + 1 ) *GRID_HEIGHT_SPACE

            # 計算された座標に基づいて線を描画
            pitchEditCanvas.create_rectangle(startX,startY,endX,endY,fill="gray0",width= 0)

    def drawKeyboad(self,pitchEditCanvas):

       # 画面左の鍵盤を描画するメソッド
       
        BLACK_KEYBOAD_SHRINK_RATIO = 0.7#[nd]黒鍵の高さの白鍵の高さに対する割合
        #mainFrame.update_idletasks() todo?

        # 白鍵を描画
        for index in range(WHIHTE_KEYBOAD_AMOUNT):
           
            # 長方形の左上と右下の座標を計算
            startX = 0
            startY = WHIHTE_KEYBOAD_SPACE * index
            endX = WHIHTE_KEYBOAD_WIDTH
            endY =  WHIHTE_KEYBOAD_SPACE * index

            # 計算された座標に基づいて長方形を描画
            pitchEditCanvas.create_rectangle(startX,startY,endX,endY,fill="azure",width= 1)

        # 黒鍵を描画

        #[px]黒鍵の白鍵に対するずらし幅を計算
        blackKeyboadOffset = int(WHIHTE_KEYBOAD_SPACE / 2)

        # 黒鍵のループで描画

        # 1オクターブ分の描画ループ
       # for index in range(0,BLACK_KEYBOAD_AMOUNT,2):
           



        # 計算された座標に基づいて長方形を描画
        pitchEditCanvas.create_rectangle(0,startY,BLACK_KEYBOAD_WIDTH,endY,fill="gray10",width= 1)
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
   
    def loadWavs(self,soundEdifFrame):

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
        application.loadDataTable(soundEdifFrame)


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



	
