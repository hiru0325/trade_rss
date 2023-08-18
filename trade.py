from datetime import datetime, timedelta
from trade_rss import rss, rss_dict, fetch_open

import jpholiday
import threading
import traceback
import configparser
import sys
sys.path.append("..\common")

# ----- ↓作成ファイルインポート↓ -----
import trade_const
import common_const
import log_setting
import sqlite3_setting
# ----- ↑作成ファイルインポート↑ -----

# ----- ファイル内容ヘッダー -----
aryFieldHeader = ['実施日時', '銘柄名', '株数', '合計金額']

# ----- スレッド処理 -----
class BrandThread(threading.Thread):

    def __init__(self, strBrandCode):
        self.strBrandCode = strBrandCode
        threading.Thread.__init__(self)

    def run(self):

        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, '銘柄コード：' + self.strBrandCode)

        # ----- 休日または祝日は取引がない為、処理を終了 -----
        if datetime.now().date().weekday() >= 5 or jpholiday.is_holiday(datetime.now().date()):

            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：休日または祝日の為、処理を終了')

            # ----- アプリを終了 -----
            exit()

        if mode == '1':

            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：トレーニング開始')

        else:

            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：取引開始')

        self.__dtStartTime = datetime.now().strftime('%H:%M:%S')

        # ----- テーブル確認 -----
        DB.sqlitef3_DBCreate('trade.db', self.strBrandCode)

        if mode == '1':

            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：1週間以前のデータ削除開始')

            # ----- 1週間経過したデータは削除 -----
            __strSQL = 'delete from '
            __strSQL += '[' + self.strBrandCode + '] '
            __strSQL += 'where '
            __strSQL += 'TRADING_DATE < ' + (datetime.now() + timedelta(weeks=-1)).strftime('%Y/%m/%d')

            DB.sqlite3_DBExecute(__strSQL)

            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：1週間以前のデータ削除完了')

        while True:

            # ----- 現在日時の取得 -----
            self.__dtStartTime = datetime.now().strftime('%H:%M:%S')

            # ----- 前場確認 -----
            if self.__dtStartTime < trade_const.TRADING_START_TIME:

                # ----- 取引開始時間になるまで繰り返す -----
                continue

            elif self.__dtStartTime < trade_const.MAEBA_END_TIME:

                log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：前場開始')

                # ----- 現在日時の取得 -----
                self.__dtCurrentTime = datetime.now()

                # ----- 前場が終了するまで監視 -----
                while True:

                    # ----- 前場が終了した場合、ループから抜ける -----
                    if self.__dtCurrentTime.strftime('%H:%M:%S') >= trade_const.MAEBA_END_TIME:

                        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：前場終了')

                        # ----- 前場終了 -----
                        break

                    # ----- 確認時刻から1分が経過後、値を確認 -----
                    if (self.__dtCurrentTime + timedelta(minutes=1)).strftime('%H:%M:%S') < datetime.now().strftime('%H:%M:%S'):

                        # ----- 実行機能 -----
                        if mode == '1':

                            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：DB登録')

                            __strSQL = 'insert into '
                            __strSQL += '[' + self.strBrandCode +'] '
                            __strSQL += '('
                            __strSQL += 'trading_date '
                            __strSQL += ',trading_time '
                            __strSQL += ',amount '
                            __strSQL += ') '
                            __strSQL += 'values '
                            __strSQL += '( '
                            __strSQL += '\'' + dtNow + '\' '
                            __strSQL += ',\'' + self.__dtCurrentTime.strftime('%H:%M:00') + '\' '
                            __strSQL += ',' + rss(self.strBrandCode, '現在値') + ' '
                            __strSQL += ')'

                            DB.sqlite3_DBExecute(__strSQL)

                        # ----- 現在時刻を取得 -----
                        self.__dtCurrentTime = datetime.now()

            elif self.__dtStartTime < trade_const.GOBA_START_TIME:

                # ----- 後場開始時間になるまで繰り返す -----
                continue

            elif self.__dtStartTime < trade_const.TRADING_END_TIME:

                log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：後場開始')

                # ----- 現在日時の取得 -----
                self.__dtCurrentTime = datetime.now()

                # ----- 後場が終了するまで監視 -----
                while True:

                    # ----- 後場が終了した場合、ループから抜ける -----
                    if self.__dtCurrentTime.strftime('%H:%M:%S') >= trade_const.TRADING_END_TIME:

                        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：後場終了')

                        break

                    # ----- 確認時刻から1分が経過後、値を確認 -----
                    if (self.__dtCurrentTime + timedelta(minutes=1)).strftime('%H:%M:%S') < datetime.now().strftime('%H:%M:%S'):

                        # ----- 実行機能 -----
                        if mode == '1':

                            log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：DB登録')

                            __strSQL = 'insert into '
                            __strSQL += '[' + self.strBrandCode +'] '
                            __strSQL += '('
                            __strSQL += 'trading_date '
                            __strSQL += ',trading_time '
                            __strSQL += ',amount '
                            __strSQL += ') '
                            __strSQL += 'values '
                            __strSQL += '( '
                            __strSQL += '\'' + dtNow + '\' '
                            __strSQL += ',\'' + self.__dtCurrentTime.strftime('%H:%M:00') + '\' '
                            __strSQL += ',' + rss(self.strBrandCode, '現在値') + ' '
                            __strSQL += ')'

                            DB.sqlite3_DBExecute(__strSQL)

                        # ----- 現在時刻を取得 -----
                        self.__dtCurrentTime = datetime.now()

            else:

                if mode == '1':
                    
                    log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：トレーニング開始')

                else:

                    log.OutputLogName(common_const.LOG_LEVEL_DEBUG, self.strBrandCode + '：取引終了')

                # ----- 取引時間終了の為、アプリを終了 -----
                exit()

# ----- メイン関数 -----
if __name__ == '__main__':

    log = log_setting.Log_Operation

    try:
        # ----- 現在の日付を取得 -----
        dtNow = datetime.now().strftime('%Y/%m/%d')

        # ----- ログレベル設定(ココの設定を帰変えるだけでログレベルに応じた出力になる) -----
        log.SetLogLevel(common_const.LOG_LEVEL_DEBUG)

        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, 'INIファイル読込み開始')

        # ----- configファイルの読み込み -----
        config = configparser.ConfigParser()
        config.read('./rakuten_trade_config.ini')

        print(config['setting']['対象銘柄'])

        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, 'INIファイル読込み完了')

    except Exception as exFileErr:

        # ----- ログファイル出力 -----
        log.OutputLogName(common_const.LOG_LEVEL_ERROR, repr(exFileErr) + '\r\n\r\n' + traceback.format_exc())

        # ----- アプリ終了 -----
        exit()

    else:

        if config['setting']['取引方法'] == '現物取引':

            intCharges = config['setting']['手数料(現物)']

        else:

            intCharges = config['setting']['手数料(信用)']

        # ----- 投資金額 -----
        intAmount = config['setting']['投資金額']

        strLogInfo = '取引方法：' + str(intCharges)
        strLogInfo += '\r\n'
        strLogInfo += '投資金額：' + str(intAmount)
        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, strLogInfo)

        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, '銘柄のスレッド開始')

        DB = sqlite3_setting.DB_Operation

        # ----- 実行機能の取得 -----
        mode = str.strip(config['setting']['実行機能'])

        for __strBrandCode in config['setting']['対象銘柄'].split(','):

            # ----- スレッド処理開始 -----
            BrandThread(strBrandCode=str.strip(__strBrandCode)).start()

        # ----- ログファイル出力 -----
        log.OutputLogName(common_const.LOG_LEVEL_DEBUG, '銘柄のスレッド完了')
