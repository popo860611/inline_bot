#!/usr/bin/env python
#encoding=utf-8
# 'seleniumwire' and 'selenium 4' raise error when running python 2.x
# PS: python 2.x will be removed in future.
try:
    # for Python2
    from Tkinter import *
    import ttk
    import tkMessageBox as messagebox
except ImportError:
    # for Python3
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
import os
import sys
import platform
import webbrowser
import base64
import time
import threading
import subprocess
import json

CONST_APP_VERSION = "Max inline Bot (2023.08.21)"

CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"

CONST_HOMEPAGE_DEFAULT = "https://inline.app/zh/?language=zh-tw"
CONST_GENDER_DEFAULT = '小姐'
CONST_OCCASION_DEFAULT = '朋友聚餐'

URL_DONATE = 'https://max-everyday.com/about/#donate'
URL_HELP = 'https://max-everyday.com/2022/09/inline-bot/'
URL_RELEASE = 'https://github.com/max32002/inline_bot/releases'
URL_FB = 'https://www.facebook.com/maxbot.ticket'

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
#CONST_WEBDRIVER_TYPE_STEALTH = "stealth"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"

translate={}

def load_translate():
    translate = {}
    en_us={}
    en_us["homepage"] = 'Homepage'
    en_us["browser"] = 'Browser'
    en_us["language"] = 'Language'
    en_us["enable"] = 'Enable'

    en_us["party_size"] = "Party size"
    en_us["force_party_size"] = "Force Party size"
    en_us["booking_time"] = "Time"
    en_us["booking_time_alt"] = "Time (Alternative)"

    en_us["user_info"] = "User Info"
    en_us["user_name"] = "Name"
    en_us["user_gender"] = "Gender"
    en_us["user_tel"] = "Tel"
    en_us["user_email"] = "Email"
    en_us["booking_occasion"] = "Occasion"
    en_us["booking_note"] = "Note"
    
    en_us["credit_card_holder"] = "Credit Card Holder"
    en_us["cardholder_name"] = "Name"
    en_us["cardholder_email"] = "Email"
    en_us["card_number"] = "Number"
    en_us["card_exp"] = "Exp (MM/YY)"
    en_us["card_ccv"] = "ccv"
    en_us["auto_submit"] = "Auto submit"

    en_us["verbose"] = 'Verbose mode'
    en_us["running_status"] = 'Running Status'
    en_us["running_url"] = 'Running URL'
    en_us["status_idle"] = 'Idle'
    en_us["status_paused"] = 'Paused'
    en_us["status_enabled"] = 'Enabled'
    en_us["status_running"] = 'Running'

    en_us["idle"] = 'Idle'
    en_us["resume"] = 'Resume'

    en_us["preference"] = 'Preference'
    en_us["advanced"] = 'Advanced'
    en_us["runtime"] = 'Runtime'
    en_us["about"] = 'About'

    en_us["run"] = 'Run'
    en_us["save"] = 'Save'
    en_us["exit"] = 'Close'
    en_us["copy"] = 'Copy'
    en_us["restore_defaults"] = 'Restore Defaults'
    en_us["done"] = 'Done'

    en_us["maxbot_slogan"] = 'MaxinlineBot is a FREE and open source bot program. Wish you booking successfully.'
    en_us["donate"] = 'Donate'
    en_us["help"] = 'Help'
    en_us["release"] = 'Release'

    zh_tw={}
    zh_tw["homepage"] = '售票網站'
    zh_tw["browser"] = '瀏覽器'
    zh_tw["language"] = '語言'
    zh_tw["enable"] = '啟用'

    zh_tw["party_size"] = "用餐人數"
    zh_tw["force_party_size"] = "覆寫用餐人數"
    zh_tw["booking_time"] = "用餐時段"
    zh_tw["booking_time_alt"] = "用餐時段(備用)"
    
    zh_tw["user_info"] = "聯絡資訊"
    zh_tw["user_name"] = "訂位人姓名"
    zh_tw["user_gender"] = "性別"
    zh_tw["user_tel"] = "訂位人手機號碼"
    zh_tw["user_email"] = "訂位人Email"
    zh_tw["booking_occasion"] = "用餐目的"
    zh_tw["booking_note"] = "其他備註"
    
    zh_tw["credit_card_holder"] = "信用卡持有人"
    zh_tw["cardholder_name"] = "持卡人姓名"
    zh_tw["cardholder_email"] = "持卡人Email"
    zh_tw["card_number"] = "卡號"
    zh_tw["card_exp"] = "到期日 (MM/YY)"
    zh_tw["card_ccv"] = "安全碼"
    zh_tw["auto_submit"] = "自動「確認訂位」"

    zh_tw["verbose"] = '輸出詳細除錯訊息'
    zh_tw["running_status"] = '執行狀態'
    zh_tw["running_url"] = '執行網址'
    zh_tw["status_idle"] = '閒置中'
    zh_tw["status_paused"] = '已暫停'
    zh_tw["status_enabled"] = '已啟用'
    zh_tw["status_running"] = '執行中'

    zh_tw["idle"] = '暫停搶票'
    zh_tw["resume"] = '接續搶票'

    zh_tw["preference"] = '偏好設定'
    zh_tw["advanced"] = '進階設定'
    zh_tw["runtime"] = '執行階段'
    zh_tw["about"] = '關於'

    zh_tw["run"] = '搶票'
    zh_tw["save"] = '存檔'
    zh_tw["exit"] = '關閉'
    zh_tw["copy"] = '複製'
    zh_tw["restore_defaults"] = '恢復預設值'
    zh_tw["done"] = '完成'

    zh_tw["maxbot_slogan"] = 'MaxinlineBot 是一個免費、開放原始碼的搶票機器人。\n祝您預訂成功。'
    zh_tw["donate"] = '打賞'
    zh_tw["release"] = '所有可用版本'
    zh_tw["help"] = '使用教學'

    zh_cn={}
    zh_cn["homepage"] = '售票网站'
    zh_cn["browser"] = '浏览器'
    zh_cn["language"] = '语言'
    zh_cn["enable"] = '启用'

    zh_cn["party_size"] = "用餐人数"
    zh_cn["force_party_size"] = "覆写用餐人数"
    zh_cn["booking_time"] = "用餐时段"
    zh_cn["booking_time_alt"] = "用餐时段(备用)"

    zh_cn["user_info"] = "联络资讯"
    zh_cn["user_name"] = "订位人姓名"
    zh_cn["user_gender"] = "性别"
    zh_cn["user_tel"] = "订位人手机号码"
    zh_cn["user_email"] = "订位人Email"
    zh_cn["booking_occasion"] = "用餐目的"
    zh_cn["booking_note"] = "其他備註"

    zh_cn["credit_card_holder"] = "信用卡持有人"
    zh_cn["cardholder_name"] = "持卡人姓名"
    zh_cn["cardholder_email"] = "持卡人Email"
    zh_cn["card_number"] = "卡号"
    zh_cn["card_exp"] = "到期日 (MM/YY)"
    zh_cn["card_ccv"] = "安全码"
    zh_cn["auto_submit"] = "自动“确认订位”"

    zh_cn["verbose"] = '输出详细除错讯息'
    zh_cn["running_status"] = '执行状态'
    zh_cn["running_url"] = '执行网址'
    zh_cn["status_idle"] = '闲置中'
    zh_cn["status_paused"] = '已暂停'
    zh_cn["status_enabled"] = '已启用'
    zh_cn["status_running"] = '执行中'

    zh_cn["idle"] = '暂停抢票'
    zh_cn["resume"] = '接续抢票'

    zh_cn["preference"] = '偏好设定'
    zh_cn["advanced"] = '进阶设定'
    zh_cn["runtime"] = '运行'
    zh_cn["about"] = '关于'

    zh_cn["run"] = '抢票'
    zh_cn["save"] = '存档'
    zh_cn["exit"] = '关闭'
    zh_cn["copy"] = '复制'
    zh_cn["restore_defaults"] = '恢复默认值'
    zh_cn["done"] = '完成'

    zh_cn["maxbot_slogan"] = 'MaxinlineBot 是一个免费的开源机器人程序。\n祝您预订成功。'
    zh_cn["donate"] = '打赏'
    zh_cn["help"] = '使用教学'
    zh_cn["release"] = '所有可用版本'

    ja_jp={}
    ja_jp["homepage"] = 'ホームページ'
    ja_jp["browser"] = 'ブラウザ'
    ja_jp["language"] = '言語'
    ja_jp["enable"] = '有効'

    ja_jp["party_size"] = "食事人数"
    ja_jp["force_party_size"] = "人数を変更する"
    ja_jp["booking_time"] = "食事時間"
    ja_jp["booking_time_alt"] = "食事時間 (代替)"
    
    ja_jp["user_info"] = "連絡先情報"
    ja_jp["user_name"] = "予約者氏名"
    ja_jp["user_gender"] = "性別"
    ja_jp["user_tel"] = "携帯電話番号"
    ja_jp["user_email"] = "メールアドレス"
    ja_jp["booking_occasion"] = "ご利用目的"
    ja_jp["booking_note"] = "その他ご希望"

    ja_jp["credit_card_holder"] = "クレジット カード所有者"
    ja_jp["cardholder_name"] = "所有者名"
    ja_jp["cardholder_email"] = "所有者Email"
    ja_jp["card_number"] = "番号"
    ja_jp["card_exp"] = "Exp (MM/YY)"
    ja_jp["card_ccv"] = "ccv"
    ja_jp["auto_submit"] = "自動送信フォーム"

    ja_jp["verbose"] = '詳細モード'
    ja_jp["running_status"] = 'スターテス'
    ja_jp["running_url"] = '現在の URL'
    ja_jp["status_idle"] = '閒置中'
    ja_jp["status_paused"] = '一時停止'
    ja_jp["status_enabled"] = '有効'
    ja_jp["status_running"] = 'ランニング'

    ja_jp["idle"] = 'アイドル'
    ja_jp["resume"] = '再開する'

    ja_jp["preference"] = '設定'
    ja_jp["advanced"] = '高度な設定'
    ja_jp["runtime"] = 'ランタイム'
    ja_jp["about"] = '情報'

    ja_jp["run"] = 'チケットを取る'
    ja_jp["save"] = '保存'
    ja_jp["exit"] = '閉じる'
    ja_jp["copy"] = 'コピー'
    ja_jp["restore_defaults"] = 'デフォルトに戻す'
    ja_jp["done"] = '終わり'

    ja_jp["maxbot_slogan"] = 'MaxinlineBot は無料のオープン ソース ボット プログラムです。 予約が成功しますように。'
    ja_jp["donate"] = '寄付'
    ja_jp["help"] = '利用方法'
    ja_jp["release"] = 'リリース'

    translate['en_us']=en_us
    translate['zh_tw']=zh_tw
    translate['zh_cn']=zh_cn
    translate['ja_jp']=ja_jp
    return translate

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_default_config():
    config_dict = {}
    config_dict["homepage"] = CONST_HOMEPAGE_DEFAULT
    config_dict["browser"] = "chrome"
    config_dict["language"] = "English"
    config_dict["adult_picker"] = "2"
    config_dict["force_adult_picker"] = True
    config_dict["book_now_time"] = ""
    config_dict["book_now_time_alt"] = ""
    config_dict["user_name"] = ""
    config_dict["user_gender"] = CONST_GENDER_DEFAULT
    config_dict["user_phone"] = ""
    config_dict["user_email"] = ""
    config_dict["booking_occasion"] = CONST_OCCASION_DEFAULT
    config_dict["booking_note"] = ""

    config_dict["cardholder_name"] = ""
    config_dict["cardholder_email"] = ""
    config_dict["cc_number"] = ""
    config_dict["cc_exp"] = ""
    config_dict["cc_ccv"] = ""
    config_dict['cc_auto_submit'] = False

    config_dict['advanced']={}
    config_dict["advanced"]["adblock_plus_enable"] = False
    config_dict["advanced"]["headless"] = False
    config_dict["advanced"]["verbose"] = False

    config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_UC

    return config_dict

def read_last_url_from_file():
    ret = ""
    if os.path.exists(CONST_MAXBOT_LAST_URL_FILE):
        with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
            ret = text_file.readline()
    return ret

def load_json():
    app_root = get_app_root()

    # overwrite config path.
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    else:
        config_dict = get_default_config()
    return config_filepath, config_dict

def btn_restore_defaults_clicked(language_code):
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = get_default_config()
    import json
    with open(config_filepath, 'w') as outfile:
        json.dump(config_dict, outfile)
    messagebox.showinfo(translate[language_code]["restore_defaults"], translate[language_code]["done"])

    global root
    load_GUI(root, config_dict)

def btn_idle_clicked(language_code):
    app_root = get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
        text_file.write("")
    update_maxbot_runtime_status()

def btn_resume_clicked(language_code):
    app_root = get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    for i in range(10):
        force_remove_file(idle_filepath)
    update_maxbot_runtime_status()

def btn_save_clicked(language_code):
    btn_save_act(language_code)

def format_time_string(data):
    if not data is None:
        data = data.replace('：',':')
    return data

def btn_save_act(language_code, slience_mode=False):
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, 'settings.json')
    
    config_dict = get_default_config()

    # read user input
    global txt_homepage
    global combo_browser
    global combo_language

    global txt_adult_picker
    global txt_book_now_time
    global txt_book_now_time_alt

    global txt_user_name
    global combo_user_gender
    global txt_user_phone
    global txt_user_email
    global combo_booking_occasion
    global txt_booking_note

    global txt_cardholder_name
    global txt_cardholder_email
    global txt_card_number
    global txt_card_exp
    global txt_card_ccv

    global chk_state_cc_auto_submit
    global chk_state_force_adult_picker
    global chk_state_verbose

    global tabControl

    is_all_data_correct = True

    if is_all_data_correct:
        #if combo_homepage.get().strip()=="":
        if txt_homepage.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please enter homepage")
        else:
            #config_dict["homepage"] = combo_homepage.get().strip()
            config_dict["homepage"] = txt_homepage.get().strip()

    if is_all_data_correct:
        if combo_browser.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please select a browser: chrome or firefox")
        else:
            config_dict["browser"] = combo_browser.get().strip()

    if is_all_data_correct:
        if combo_language.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please select a language")
        else:
            config_dict["language"] = combo_language.get().strip()
            
            # display as new language.
            language_code = get_language_code_by_name(config_dict["language"])

    if is_all_data_correct:
        if txt_adult_picker.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please enter party size")
        else:
            config_dict["adult_picker"] = txt_adult_picker.get().strip()

    if is_all_data_correct:
        if txt_book_now_time.get().strip()=="":
            is_all_data_correct = False
            tabControl.select(0)
            txt_book_now_time.focus_set()
            messagebox.showerror("Error", "Please enter booking time")
        else:
            config_dict["book_now_time"] = txt_book_now_time.get().strip()
            config_dict["book_now_time"] = format_time_string(config_dict["book_now_time"])

    if is_all_data_correct:
        if txt_user_name.get().strip()=="":
            is_all_data_correct = False
            tabControl.select(0)
            txt_user_name.focus_set()
            messagebox.showerror("Error", "Please enter user name")
        else:
            config_dict["user_name"] = txt_user_name.get().strip()

    if is_all_data_correct:
        if txt_user_phone.get().strip()=="":
            is_all_data_correct = False
            tabControl.select(0)
            txt_user_phone.focus_set()
            messagebox.showerror("Error", "Please enter user phone")
        else:
            config_dict["user_phone"] = txt_user_phone.get().strip()

    if is_all_data_correct:
        if txt_user_email.get().strip()=="":
            is_all_data_correct = False
            tabControl.select(0)
            txt_user_email.focus_set()
            messagebox.showerror("Error", "Please enter user email")
        else:
            config_dict["user_email"] = txt_user_email.get().strip()

    if is_all_data_correct:
        config_dict["book_now_time_alt"] = txt_book_now_time_alt.get().strip()
        config_dict["book_now_time_alt"] = format_time_string(config_dict["book_now_time_alt"])

        config_dict["user_gender"] = combo_user_gender.get().strip()
        config_dict["booking_occasion"] = combo_booking_occasion.get().strip()
        config_dict["booking_note"] = txt_booking_note.get().strip()

        config_dict["cardholder_name"] = txt_cardholder_name.get().strip()
        config_dict["cardholder_email"] = txt_cardholder_email.get().strip()
        config_dict["cc_number"] = txt_card_number.get().strip()
        config_dict["cc_exp"] = txt_card_exp.get().strip()
        config_dict["cc_ccv"] = txt_card_ccv.get().strip()

        config_dict["cc_auto_submit"] = bool(chk_state_cc_auto_submit.get())

        config_dict["force_adult_picker"] = bool(chk_state_force_adult_picker.get())

        config_dict["advanced"]["verbose"] = bool(chk_state_verbose.get())

    # save config.
    if is_all_data_correct:
        import json
        with open(config_filepath, 'w') as outfile:
            json.dump(config_dict, outfile)

        if slience_mode==False:
            messagebox.showinfo(translate[language_code]["save"], translate[language_code]["done"])

    return is_all_data_correct

def btn_run_clicked(language_code):
    print('run button pressed.')
    Root_Dir = ""
    save_ret = btn_save_act(language_code, slience_mode=True)
    print("save config result:", save_ret)
    if save_ret:
        threading.Thread(target=launch_maxbot).start()

def launch_maxbot():
    working_dir = os.path.dirname(os.path.realpath(__file__))
    print("working_dir:", working_dir)

    if hasattr(sys, 'frozen'):
        print("execute in frozen mode")

        # check platform here.
        if platform.system() == 'Darwin':
            print("execute MacOS python script")
            subprocess.Popen("./inline_bot", shell=True, cwd=working_dir)
        if platform.system() == 'Linux':
            print("execute linux binary")
            subprocess.Popen("./inline_bot", shell=True, cwd=working_dir)
        if platform.system() == 'Windows':
            print("execute .exe binary.")
            subprocess.Popen("inline_bot.exe", shell=True, cwd=working_dir)
    else:
        interpreter_binary = 'python'
        interpreter_binary_alt = 'python3'
        if platform.system() == 'Darwin':
            # try python3 before python.
            interpreter_binary = 'python3'
            interpreter_binary_alt = 'python'
        print("execute in shell mode.")
        #print("script path:", working_dir)
        #messagebox.showinfo(title="Debug0", message=working_dir)

        # some python3 binary, running in 'python' command.
        try:
            print('try', interpreter_binary)
            s=subprocess.Popen([interpreter_binary, 'inline_bot.py'], cwd=working_dir)
            #s=subprocess.Popen(['./chrome_tixcraft'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
            #s=subprocess.run(['python3', 'chrome_tixcraft.py'], cwd=working_dir)
            #messagebox.showinfo(title="Debug1", message=str(s))
        except Exception as exc:
            print('try', interpreter_binary_alt)
            try:
                s=subprocess.Popen([interpreter_binary_alt, 'inline_bot.py'], cwd=working_dir)
            except Exception as exc:
                msg=str(exc)
                print("exeption:", msg)
                #messagebox.showinfo(title="Debug2", message=msg)
                pass


def open_url(url):
    webbrowser.open_new(url)

def btn_exit_clicked():
    root.destroy()

def callbackLanguageOnChange(event):
    applyNewLanguage()

def get_language_code_by_name(new_language):
    language_code = "en_us"
    if u'繁體中文' in new_language:
        language_code = 'zh_tw'
    if u'簡体中文' in new_language:
        language_code = 'zh_cn'
    if u'日本語' in new_language:
        language_code = 'ja_jp'
    #print("new language code:", language_code)

    return language_code

def applyNewLanguage():
    global combo_language
    new_language = combo_language.get().strip()
    #print("new language value:", new_language)

    language_code=get_language_code_by_name(new_language)

    global lbl_homepage
    global lbl_browser
    global lbl_language

    global lbl_adult_picker
    global lbl_force_adult_picker
    global lbl_book_now_time
    global lbl_book_now_time_alt

    global lbl_user_profile
    global lbl_user_name
    global lbl_user_gender
    global lbl_user_phone
    global lbl_user_email
    global lbl_booking_occasion
    global lbl_booking_note

    global lbl_credit_card_holder
    global lbl_cardholder_name
    global lbl_cardholder_email
    global lbl_card_number
    global lbl_card_exp
    global lbl_card_ccv
    global lbl_cc_auto_submit

    # for checkbox
    global chk_cc_auto_submit
    global chk_force_adult_picker

    global tabControl

    global lbl_slogan
    global lbl_help
    global lbl_donate
    global lbl_release

    global lbl_verbose
    global chk_verbose

    global lbl_maxbot_status
    global lbl_maxbot_last_url

    lbl_homepage.config(text=translate[language_code]["homepage"])
    lbl_browser.config(text=translate[language_code]["browser"])
    lbl_language.config(text=translate[language_code]["language"])

    lbl_adult_picker.config(text=translate[language_code]["party_size"])
    lbl_force_adult_picker.config(text=translate[language_code]["force_party_size"])
    lbl_book_now_time.config(text=translate[language_code]["booking_time"])
    lbl_book_now_time_alt.config(text=translate[language_code]["booking_time_alt"])
    lbl_user_profile.config(text=translate[language_code]["user_info"])
    lbl_user_name.config(text=translate[language_code]["user_name"])
    lbl_user_gender.config(text=translate[language_code]["user_gender"])
    lbl_user_phone.config(text=translate[language_code]["user_tel"])
    lbl_user_email.config(text=translate[language_code]["user_email"])
    lbl_booking_occasion.config(text=translate[language_code]["booking_occasion"])
    lbl_booking_note.config(text=translate[language_code]["booking_note"])

    lbl_credit_card_holder.config(text=translate[language_code]["credit_card_holder"])
    lbl_cardholder_name.config(text=translate[language_code]["cardholder_name"])
    lbl_cardholder_email.config(text=translate[language_code]["cardholder_email"])
    lbl_card_number.config(text=translate[language_code]["card_number"])
    lbl_card_exp.config(text=translate[language_code]["card_exp"])
    lbl_card_ccv.config(text=translate[language_code]["card_ccv"])
    lbl_cc_auto_submit.config(text=translate[language_code]["auto_submit"])

    chk_cc_auto_submit.config(text=translate[language_code]["enable"])
    chk_force_adult_picker.config(text=translate[language_code]["enable"])

    tabControl.tab(0, text=translate[language_code]["preference"])
    tabControl.tab(1, text=translate[language_code]["advanced"])
    tabControl.tab(2, text=translate[language_code]["runtime"])
    tabControl.tab(3, text=translate[language_code]["about"])

    lbl_slogan.config(text=translate[language_code]["maxbot_slogan"])
    lbl_help.config(text=translate[language_code]["help"])
    lbl_donate.config(text=translate[language_code]["donate"])
    lbl_release.config(text=translate[language_code]["release"])

    lbl_verbose.config(text=translate[language_code]["verbose"])
    chk_verbose.config(text=translate[language_code]["enable"])

    lbl_maxbot_status.config(text=translate[language_code]["running_status"])
    lbl_maxbot_last_url.config(text=translate[language_code]["running_url"])

    global btn_run
    global btn_save
    global btn_exit
    global btn_restore_defaults

    global btn_idle
    global btn_resume

    btn_run.config(text=translate[language_code]["run"])
    btn_save.config(text=translate[language_code]["save"])
    btn_exit.config(text=translate[language_code]["exit"])
    btn_restore_defaults.config(text=translate[language_code]["restore_defaults"])

    btn_idle.config(text=translate[language_code]["idle"])
    btn_resume.config(text=translate[language_code]["resume"])

def btn_exit_clicked():
    root.destroy()

# PS: nothing need to do, at current process.
def callbackUserGenderOnChange(event):
    showHideBlocks()

# PS: nothing need to do, at current process.
def callbackHomepageOnChange(event):
    showHideBlocks()

def showHideBlocks(all_layout_visible=False):
    pass

def PreferenctTab(root, config_dict, language_code, UI_PADDING_X):
    homepage = None
    language = "English"

    homepage_list = (CONST_HOMEPAGE_DEFAULT)
    gender_list = (CONST_GENDER_DEFAULT, '先生')
    occasion_list = [
        '慶生',
        '約會',
        '週年慶',
        '家庭用餐',
        '朋友聚餐',
        '商務聚餐'
    ]

    # output config:
    print("config:", config_dict)

    # output to GUI.
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    global lbl_homepage
    lbl_homepage = Label(frame_group_header, text=translate[language_code]["homepage"])
    lbl_homepage.grid(column=0, row=group_row_count, sticky = E)

    '''
    global combo_homepage
    combo_homepage = ttk.Combobox(frame_group_header, state="readonly")
    combo_homepage['values']= homepage_list
    combo_homepage.set(homepage)
    # PS: nothing need to do when on change event at this time.
    combo_homepage.bind("<<ComboboxSelected>>", callbackHomepageOnChange)
    combo_homepage.grid(column=1, row=group_row_count, sticky = W)
    '''

    global txt_homepage
    txt_homepage_value = StringVar(frame_group_header, value=config_dict["homepage"])
    txt_homepage = Entry(frame_group_header, width=30, textvariable = txt_homepage_value)
    txt_homepage.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # party size
    global lbl_adult_picker
    lbl_adult_picker = Label(frame_group_header, text=translate[language_code]["party_size"])
    lbl_adult_picker.grid(column=0, row=group_row_count, sticky = E)

    global txt_adult_picker
    txt_adult_picker_value = StringVar(frame_group_header, value=config_dict["adult_picker"])
    txt_adult_picker = Entry(frame_group_header, width=30, textvariable = txt_adult_picker_value)
    txt_adult_picker.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    force_adult_picker = config_dict['force_adult_picker']

    global lbl_force_adult_picker
    lbl_force_adult_picker = Label(frame_group_header, text=translate[language_code]["force_party_size"])
    lbl_force_adult_picker.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_force_adult_picker
    chk_state_force_adult_picker = BooleanVar()
    chk_state_force_adult_picker.set(force_adult_picker)

    global chk_force_adult_picker
    chk_force_adult_picker = Checkbutton(frame_group_header, text=translate[language_code]["enable"], variable=chk_state_force_adult_picker)
    chk_force_adult_picker.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # Time
    global lbl_book_now_time
    lbl_book_now_time = Label(frame_group_header, text=translate[language_code]["booking_time"])
    lbl_book_now_time.grid(column=0, row=group_row_count, sticky = E)

    global txt_book_now_time
    txt_book_now_time_value = StringVar(frame_group_header, value=config_dict["book_now_time"])
    txt_book_now_time = Entry(frame_group_header, width=30, textvariable = txt_book_now_time_value)
    txt_book_now_time.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # Time Alt
    global lbl_book_now_time_alt
    lbl_book_now_time_alt = Label(frame_group_header, text=translate[language_code]["booking_time_alt"])
    lbl_book_now_time_alt.grid(column=0, row=group_row_count, sticky = E)

    global txt_book_now_time_alt
    txt_book_now_time_alt_value = StringVar(frame_group_header, value=config_dict["book_now_time_alt"])
    txt_book_now_time_alt = Entry(frame_group_header, width=30, textvariable = txt_book_now_time_alt_value)
    txt_book_now_time_alt.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # add first block to UI.
    frame_group_header.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)
    row_count+=1

    '''
    lbl_hr = Label(root, text="")
    lbl_hr.grid(column=0, row=row_count)

    row_count+=1
    '''

    # frame - user profile
    frame_user_profile = Frame(root)
    user_profile_row_count = 0

    global lbl_user_profile
    lbl_user_profile = Label(frame_user_profile, text=translate[language_code]["user_info"])
    lbl_user_profile.grid(column=0, row=user_profile_row_count, columnspan=2, sticky = W, padx=UI_PADDING_X)

    user_profile_row_count+=1

    # User Name
    global lbl_user_name
    lbl_user_name = Label(frame_user_profile, text=translate[language_code]["user_name"])
    lbl_user_name.grid(column=0, row=user_profile_row_count, sticky = E)

    global txt_user_name
    txt_user_name_value = StringVar(frame_user_profile, value=config_dict["user_name"])
    txt_user_name = Entry(frame_user_profile, width=30, textvariable = txt_user_name_value)
    txt_user_name.grid(column=1, row=user_profile_row_count, sticky = W)

    user_profile_row_count+=1

    # User Gender
    global lbl_user_gender
    lbl_user_gender = Label(frame_user_profile, text=translate[language_code]["user_gender"])
    lbl_user_gender.grid(column=0, row=user_profile_row_count, sticky = E)

    global combo_user_gender
    combo_user_gender = ttk.Combobox(frame_user_profile, state="readonly")
    combo_user_gender['values']= gender_list
    combo_user_gender.set(config_dict["user_gender"])
    # PS: nothing need to do when on change event at this time.
    combo_user_gender.bind("<<ComboboxSelected>>", callbackUserGenderOnChange)
    combo_user_gender.grid(column=1, row=user_profile_row_count, sticky = W)

    user_profile_row_count+=1

    # User Tel
    global lbl_user_phone
    lbl_user_phone = Label(frame_user_profile, text=translate[language_code]["user_tel"])
    lbl_user_phone.grid(column=0, row=user_profile_row_count, sticky = E)

    global txt_user_phone
    txt_user_phone_value = StringVar(frame_user_profile, value=config_dict["user_phone"])
    txt_user_phone = Entry(frame_user_profile, width=30, textvariable = txt_user_phone_value)
    txt_user_phone.grid(column=1, row=user_profile_row_count, sticky = W)

    user_profile_row_count+=1

    # User Email
    global lbl_user_email
    lbl_user_email = Label(frame_user_profile, text=translate[language_code]["user_email"])
    lbl_user_email.grid(column=0, row=user_profile_row_count, sticky = E)

    global txt_user_email
    txt_user_email_value = StringVar(frame_user_profile, value=config_dict["user_email"])
    txt_user_email = Entry(frame_user_profile, width=30, textvariable = txt_user_email_value)
    txt_user_email.grid(column=1, row=user_profile_row_count, sticky = W)

    user_profile_row_count+=1

    # User Gender
    global lbl_booking_occasion
    lbl_booking_occasion = Label(frame_user_profile, text=translate[language_code]["booking_occasion"])
    lbl_booking_occasion.grid(column=0, row=user_profile_row_count, sticky = E)

    global combo_booking_occasion
    combo_booking_occasion = ttk.Combobox(frame_user_profile, state="readonly")
    combo_booking_occasion['values']= occasion_list
    combo_booking_occasion.set(config_dict["booking_occasion"])
    # PS: nothing need to do when on change event at this time.
    combo_booking_occasion.grid(column=1, row=user_profile_row_count, sticky = W)

    user_profile_row_count+=1

    # User Email
    global lbl_booking_note
    lbl_booking_note = Label(frame_user_profile, text=translate[language_code]["booking_note"])
    lbl_booking_note.grid(column=0, row=user_profile_row_count, sticky = E)

    global txt_booking_note
    txt_booking_note_value = StringVar(frame_user_profile, value=config_dict["booking_note"])
    txt_booking_note = Entry(frame_user_profile, width=30, textvariable = txt_booking_note_value)
    txt_booking_note.grid(column=1, row=user_profile_row_count, sticky = W)

    # add second block to UI.
    frame_user_profile.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)
    row_count+=1

    '''
    lbl_hr = Label(root, text="")
    lbl_hr.grid(column=0, row=row_count)

    row_count+=1
    '''

    # frame - credit card
    frame_cc = Frame(root)
    cc_row_count = 0

    global lbl_credit_card_holder
    lbl_credit_card_holder = Label(frame_cc, text=translate[language_code]["credit_card_holder"])
    lbl_credit_card_holder.grid(column=0, row=cc_row_count, columnspan=2, sticky = W, padx=UI_PADDING_X)

    cc_row_count+=1

    global lbl_cardholder_name
    lbl_cardholder_name = Label(frame_cc, text=translate[language_code]["cardholder_name"])
    lbl_cardholder_name.grid(column=0, row=cc_row_count, sticky = E)

    global txt_cardholder_name
    global txt_cardholder_name_value
    txt_cardholder_name_value = StringVar(frame_cc, value=config_dict["cardholder_name"])
    txt_cardholder_name = Entry(frame_cc, width=30, textvariable = txt_cardholder_name_value)
    txt_cardholder_name.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    global lbl_cardholder_email
    lbl_cardholder_email = Label(frame_cc, text="Email")
    lbl_cardholder_email.grid(column=0, row=cc_row_count, sticky = E)

    global txt_cardholder_email
    txt_cardholder_email_value = StringVar(frame_cc, value=config_dict["cardholder_email"])
    txt_cardholder_email = Entry(frame_cc, width=30, textvariable = txt_cardholder_email_value)
    txt_cardholder_email.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    global lbl_card_number
    lbl_card_number = Label(frame_cc, text=translate[language_code]["card_number"])
    lbl_card_number.grid(column=0, row=cc_row_count, sticky = E)

    global txt_card_number
    txt_card_number_value = StringVar(frame_cc, value=config_dict["cc_number"])
    txt_card_number = Entry(frame_cc, width=30, textvariable = txt_card_number_value)
    txt_card_number.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    global lbl_card_exp
    lbl_card_exp = Label(frame_cc, text=translate[language_code]["card_exp"])
    lbl_card_exp.grid(column=0, row=cc_row_count, sticky = E)

    global txt_card_exp
    txt_card_exp_value = StringVar(frame_cc, value=config_dict["cc_exp"])
    txt_card_exp = Entry(frame_cc, width=30, textvariable = txt_card_exp_value)
    txt_card_exp.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    global lbl_card_ccv
    lbl_card_ccv = Label(frame_cc, text=translate[language_code]["card_ccv"])
    lbl_card_ccv.grid(column=0, row=cc_row_count, sticky = E)

    global txt_card_ccv
    global txt_card_ccv_value
    txt_card_ccv_value = StringVar(frame_cc, value=config_dict["cc_ccv"])
    txt_card_ccv = Entry(frame_cc, width=30, textvariable = txt_card_ccv_value)
    txt_card_ccv.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    cc_auto_submit = config_dict['cc_auto_submit']

    global lbl_cc_auto_submit
    lbl_cc_auto_submit = Label(frame_cc, text=translate[language_code]["auto_submit"])
    lbl_cc_auto_submit.grid(column=0, row=cc_row_count, sticky = E)

    global chk_state_cc_auto_submit
    chk_state_cc_auto_submit = BooleanVar()
    chk_state_cc_auto_submit.set(cc_auto_submit)

    global chk_cc_auto_submit
    chk_cc_auto_submit = Checkbutton(frame_cc, text=translate[language_code]["enable"], variable=chk_state_cc_auto_submit)
    chk_cc_auto_submit.grid(column=1, row=cc_row_count, sticky = W)

    cc_row_count+=1

    # add third block to UI.
    frame_cc.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)


def AdvancedTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    global lbl_browser
    lbl_browser = Label(frame_group_header, text=translate[language_code]['browser'])
    lbl_browser.grid(column=0, row=group_row_count, sticky = E)

    global combo_browser
    combo_browser = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_browser['values']= ("chrome","firefox","edge","safari","brave")
    combo_browser.set(config_dict['browser'])
    combo_browser.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_language
    lbl_language = Label(frame_group_header, text=translate[language_code]['language'])
    lbl_language.grid(column=0, row=group_row_count, sticky = E)

    #global txt_language
    #txt_language = Entry(root, width=30, textvariable = StringVar(root, value=language))
    #txt_language.grid(column=1, row=group_row_count)

    global combo_language
    combo_language = ttk.Combobox(frame_group_header, state="readonly")
    combo_language['values']= ("English","繁體中文","簡体中文","日本語")
    #combo_language.current(0)
    combo_language.set(config_dict['language'])
    combo_language.bind("<<ComboboxSelected>>", callbackLanguageOnChange)
    combo_language.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_verbose
    lbl_verbose = Label(frame_group_header, text=translate[language_code]['verbose'])
    lbl_verbose.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_verbose
    chk_state_verbose = BooleanVar()
    chk_state_verbose.set(config_dict['advanced']["verbose"])

    global chk_verbose
    chk_verbose = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_verbose)
    chk_verbose.grid(column=1, row=group_row_count, sticky = W)


    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)


def settings_timer():
    while True:
        update_maxbot_runtime_status()
        time.sleep(0.6)

def update_maxbot_runtime_status():
    is_paused = False
    if os.path.exists(CONST_MAXBOT_INT28_FILE):
        is_paused = True

    try:
        global combo_language
        new_language = combo_language.get().strip()
        language_code=get_language_code_by_name(new_language)

        global lbl_maxbot_status_data
        maxbot_status = translate[language_code]['status_enabled']
        if is_paused:
            maxbot_status = translate[language_code]['status_paused']

        lbl_maxbot_status_data.config(text=maxbot_status)

        global btn_idle
        global btn_resume

        if not is_paused:
            btn_idle.grid(column=1, row=0)
            btn_resume.grid_forget()
        else:
            btn_resume.grid(column=2, row=0)
            btn_idle.grid_forget()

        global lbl_maxbot_last_url_data
        last_url = read_last_url_from_file()
        if len(last_url) > 60:
            last_url=last_url[:60]+"..."
        lbl_maxbot_last_url_data.config(text=last_url)
    except Exception as exc:
        pass


def RuntimeTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    maxbot_status = ""
    global lbl_maxbot_status
    lbl_maxbot_status = Label(frame_group_header, text=translate[language_code]['running_status'])
    lbl_maxbot_status.grid(column=0, row=group_row_count, sticky = E)


    frame_maxbot_interrupt = Frame(frame_group_header)

    global lbl_maxbot_status_data
    lbl_maxbot_status_data = Label(frame_maxbot_interrupt, text=maxbot_status)
    lbl_maxbot_status_data.grid(column=0, row=group_row_count, sticky = W)

    global btn_idle
    global btn_resume

    btn_idle = ttk.Button(frame_maxbot_interrupt, text=translate[language_code]['idle'], command= lambda: btn_idle_clicked(language_code) )
    btn_idle.grid(column=1, row=0)

    btn_resume = ttk.Button(frame_maxbot_interrupt, text=translate[language_code]['resume'], command= lambda: btn_resume_clicked(language_code))
    btn_resume.grid(column=2, row=0)

    frame_maxbot_interrupt.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_maxbot_last_url
    lbl_maxbot_last_url = Label(frame_group_header, text=translate[language_code]['running_url'])
    lbl_maxbot_last_url.grid(column=0, row=group_row_count, sticky = E)

    last_url = ""
    global lbl_maxbot_last_url_data
    lbl_maxbot_last_url_data = Label(frame_group_header, text=last_url)
    lbl_maxbot_last_url_data.grid(column=1, row=group_row_count, sticky = W)

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)
    update_maxbot_runtime_status()

def AboutTab(root, language_code):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    logo_filename = "maxbot_logo2_single.ppm"
    logo_img = PhotoImage(file=logo_filename)

    lbl_logo = Label(frame_group_header, image=logo_img)
    lbl_logo.image = logo_img
    lbl_logo.grid(column=0, row=group_row_count, columnspan=2)

    group_row_count +=1

    global lbl_slogan
    global lbl_help
    global lbl_donate
    global lbl_release

    lbl_slogan = Label(frame_group_header, text=translate[language_code]['maxbot_slogan'], wraplength=400, justify="center")
    lbl_slogan.grid(column=0, row=group_row_count, columnspan=2)

    group_row_count +=1

    lbl_help = Label(frame_group_header, text=translate[language_code]['help'])
    lbl_help.grid(column=0, row=group_row_count, sticky = E)

    lbl_help_url = Label(frame_group_header, text=URL_HELP, fg="blue", bg="gray", cursor="hand2")
    lbl_help_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_help_url.bind("<Button-1>", lambda e: open_url(URL_HELP))

    group_row_count +=1

    lbl_donate = Label(frame_group_header, text=translate[language_code]['donate'])
    lbl_donate.grid(column=0, row=group_row_count, sticky = E)

    lbl_donate_url = Label(frame_group_header, text=URL_DONATE, fg="blue", bg="gray", cursor="hand2")
    lbl_donate_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_donate_url.bind("<Button-1>", lambda e: open_url(URL_DONATE))

    group_row_count +=1

    lbl_release = Label(frame_group_header, text=translate[language_code]['release'])
    lbl_release.grid(column=0, row=group_row_count, sticky = E)

    lbl_release_url = Label(frame_group_header, text=URL_RELEASE, fg="blue", bg="gray", cursor="hand2")
    lbl_release_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_release_url.bind("<Button-1>", lambda e: open_url(URL_RELEASE))

    group_row_count +=1

    lbl_fb_fans = Label(frame_group_header, text=u'Facebook')
    lbl_fb_fans.grid(column=0, row=group_row_count, sticky = E)

    lbl_fb_fans_url = Label(frame_group_header, text=URL_FB, fg="blue", bg="gray", cursor="hand2")
    lbl_fb_fans_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_fb_fans_url.bind("<Button-1>", lambda e: open_url(URL_FB))

    frame_group_header.grid(column=0, row=row_count)

def get_action_bar(root, language_code):
    frame_action = Frame(root)

    global btn_run
    global btn_save
    global btn_exit
    global btn_restore_defaults

    btn_run = ttk.Button(frame_action, text=translate[language_code]['run'], command= lambda: btn_run_clicked(language_code))
    btn_run.grid(column=0, row=0)

    btn_save = ttk.Button(frame_action, text=translate[language_code]['save'], command= lambda: btn_save_clicked(language_code) )
    btn_save.grid(column=1, row=0)

    btn_exit = ttk.Button(frame_action, text=translate[language_code]['exit'], command=btn_exit_clicked)
    btn_exit.grid(column=2, row=0)

    btn_restore_defaults = ttk.Button(frame_action, text=translate[language_code]['restore_defaults'], command= lambda: btn_restore_defaults_clicked(language_code))
    btn_restore_defaults.grid(column=3, row=0)

    return frame_action


def clearFrame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
       widget.destroy()

def load_GUI(root, config_dict):
    clearFrame(root)

    language_code="en_us"
    if not config_dict is None:
        if u'language' in config_dict:
            language_code = get_language_code_by_name(config_dict["language"])

    row_count = 0

    global tabControl
    tabControl = ttk.Notebook(root)
    tab1 = Frame(tabControl)
    tabControl.add(tab1, text=translate[language_code]['preference'])
    tab2 = Frame(tabControl)
    tabControl.add(tab2, text=translate[language_code]['advanced'])
    tab3 = Frame(tabControl)
    tabControl.add(tab3, text=translate[language_code]['runtime'])
    tab4 = Frame(tabControl)
    tabControl.add(tab4, text=translate[language_code]['about'])
    tabControl.grid(column=0, row=row_count)
    tabControl.select(tab1)

    row_count+=1

    frame_action = get_action_bar(root,language_code)
    frame_action.grid(column=0, row=row_count)

    PreferenctTab(tab1, config_dict, language_code, UI_PADDING_X)
    AdvancedTab(tab2, config_dict, language_code, UI_PADDING_X)
    RuntimeTab(tab3, config_dict, language_code, UI_PADDING_X)
    AboutTab(tab4, language_code)

def main():
    global translate
    # only need to load translate once.
    translate = load_translate()

    global config_filepath
    global config_dict
    # only need to load json file once.
    config_filepath, config_dict = load_json()

    global root
    root = Tk()
    root.title(CONST_APP_VERSION)

    global UI_PADDING_X
    UI_PADDING_X = 15

    load_GUI(root, config_dict)

    GUI_SIZE_WIDTH = 480
    GUI_SIZE_HEIGHT = 610

    GUI_SIZE_MACOS = str(GUI_SIZE_WIDTH) + 'x' + str(GUI_SIZE_HEIGHT)
    GUI_SIZE_WINDOWS=str(GUI_SIZE_WIDTH-80) + 'x' + str(GUI_SIZE_HEIGHT-120)

    GUI_SIZE =GUI_SIZE_MACOS

    if platform.system() == 'Windows':
        GUI_SIZE = GUI_SIZE_WINDOWS

    root.geometry(GUI_SIZE)

    # for icon.
    icon_filepath = 'tmp.ico'

    # icon format.
    iconImg = 'AAABAAEAAAAAAAEAIAD4MgAAFgAAAIlQTkcNChoKAAAADUlIRFIAAAEAAAABAAgGAAAAXHKoZgAAAAFzUkdCAK7OHOkAAABQZVhJZk1NACoAAAAIAAIBEgADAAAAAQABAACHaQAEAAAAAQAAACYAAAAAAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAQCgAwAEAAAAAQAAAQAAAAAAdTc0VwAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAMPFJREFUeAHtndmTJNd13rP36e7pWXt6OFiHGAxACssApChTskRZom1J3ETS9ov/AIclO/Tm8JMj/OxQBMNhO0IRdvjNtB0SSYirTFEiJZoSTBAidoAAZjCYAYazb73M9O7vdzKzOqu6qmvLyr5VeW5MT3VXVea997s3v3vOueecO/SlmYnNyIsj4AiUEoHhUvbaO+0IOAKGgBOATwRHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECIzuWt83N3et6oGpeGioflf6FFtmhPWoUb/q9zafd4VZpf587ljIXSpt7hCz4glADR0ZH49GJiai4dHRaGh4JErbbvOW/2wweAVD+68QMPupks2NzWhlfj7a3FivavbQ8HA0PjMjXPtRuBuK1u7eidbu3KnqUxF/jAmzkbFxVdVv820o2lhbjVYWFuy5aRer4glALYQAJg/PRlNzc9H00Q/o9aj9znt7Dh6MJvbtj8amp6ORPXs0KGPR0MiIloYhWx02Y5aAI+IO2y/tdru/v8/DffPM6eh7f/D70Z1r1wRNLAlsbmxEhz704eiTX/pP0fi+fR1NiN1EhnF+/X99OfrJl/6wMAJjPk3NHok++R//c3TgoRMi1I3dhKDtusHswt/+KPrBv/030cbqStvXF08AAnzl9u1oWT9MYiYvnRgeHYtG90zYgz8+s09EcCianD0cTR2Zi6ZEEtMpSRw5Ek3qs4n9B6KxvXuj0clJkyTa7nmfXzD/3nvRqlg/ffjpDpN37tRT0T2//CuFPUB5w3jw5MlC2765vh7d92ufiD7425+yhSnv/hRxv6uvvhJtSgropBRPALQyWc3TBjMI6/xI/Lt784Zmsj4RUcSrPd/XP6kKqAwj4yKJqSkTcycOHIgmDx2OJkUK00clRSREwd+8z+eQydjUpF1nkkRaaZ+/XnnpBROVs33i96NPfaTQByhvGMen91r7i1qJmUuPfPGf9u3DD/4LF96PNvT8dKL27Q4BNJo1Rgw87fEXkpfK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'
    if platform.system() == 'Linux':
        # PNG format.
        iconImg = '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'

    tmpIcon = open(icon_filepath, 'wb+')
    tmpIcon.write(base64.b64decode(iconImg))
    tmpIcon.close()
    if platform.system() == 'Windows':
        root.iconbitmap(icon_filepath)
    if platform.system() == 'Darwin':
        #from PIL import Image, ImageTk
        #logo = ImageTk.PhotoImage(Image.open(icon_filepath).convert('RGB'))
        #root.call('wm', 'iconphoto', root._w, logo)
        pass
    if platform.system() == 'Linux':
        logo = PhotoImage(file=icon_filepath)
        root.call('wm', 'iconphoto', root._w, logo)
    os.remove(icon_filepath)

    threading.Thread(target=settings_timer, daemon=True).start()
    root.mainloop()

def force_remove_file(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as exc:
            pass

def clean_tmp_file():
    remove_file_list = [CONST_MAXBOT_LAST_URL_FILE
        ,CONST_MAXBOT_INT28_FILE
    ]
    for filepath in remove_file_list:
        force_remove_file(filepath)

if __name__ == "__main__":
    clean_tmp_file()
    main()
