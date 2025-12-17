import os
import sys
import ctypes
import configparser
from pathlib import Path
from tkinter import *
from tkinter import font
from tkinter import messagebox
import tkinter as tk
import re
import winreg
import logging
import configatm
from datetime import datetime
import ATMeye




######################### INIT LOGGER #####################################

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
py_handler = logging.FileHandler(f"{__name__}.log", mode='a')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)

############################################################################
version = 'aboutATM - v2.0.101025'
py_logger.info(f'Starting.. {version}')

############################################################################
def log_rename_changes(old_values, new_values, log_file=r"C:\ProTopas\Trace\rename.log"):
    try:
        # Убедимся, что папка существует
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== Changes from {now} ===\n")
            for key_display in new_values:
                for val_name in new_values[key_display]:
                    old_val = old_values.get(key_display, {}).get(val_name, "<empty>")
                    new_val = new_values[key_display][val_name]
                    if old_val != new_val:
                        f.write(f"{key_display} -> {val_name}:\  Old_value: {old_val} \  New_value: {new_val}\n\n")
    except Exception as e:
        py_logger.exception(f"Error log: {e}")

############################################################################

def resource_path(relative_path):
    """Возвращает путь к ресурсу (работает и в .py, и в .exe)"""
    try:
        base_path = sys._MEIPASS  # при запуске .exe
    except Exception:
        base_path = os.path.abspath(".")  # при запуске .py
    return os.path.join(base_path, relative_path)

def log(new_values, old_values):
    for val_name in new_values:
        print(val_name)

#---------- Init Form ----------


root = Tk()
root.iconbitmap(default=resource_path("favicon.ico"))
root.title(f"{version}")
root.geometry("575x500+280+550")
#root.geometry("575x600+280+550")
root.resizable(False, False)
#	RGB (35,171,189), HEX: #23abbd
img_Main = PhotoImage(file=resource_path("bankomat.png"))
bg_Main = Label(image=img_Main)
bg_Main.place(x=300, y=100)
#ToolTip(bg_Main, msg="Hover info")

root.option_add("*tearOff", FALSE)

main_menu = Menu()
file_menu = Menu()

py_logger.info(f'Form Init - OK')
#+++++++++++++++++++++++++++++++++++++++++++++ Пути в реестре и отображаемые ключи
REG_PATHS = [
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\bs2FCXstt',
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\bs2FCXstt\Communication',
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\BS2ServiceFW',
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2',
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\PaymentsNG',
    r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProAgent\CurrentVersion\SSTP',
    r'SOFTWARE\WOW6432Node\BS/2\ATMeye',
    r'SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName',
    r'SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName'
]

# Отображаемые ключи (названия для интерфейса)
DISPLAY_KEYS = ["bs2FCXstt", "Communication", "BS2ServiceFW", "BS/2", "PaymentsNG", "SSTP", 'ATMeye', "ComputerName", "ActiveComputerName"]

# Сопоставление ключей и значений, которые нужно читать
REG_VALUE_NAMES = {
    "bs2FCXstt": ["TerminalID"],
    "Communication": ["IpAddress"],
    "BS2ServiceFW": ["TerminalID"],
    "BS/2": ["TerminalID"],
    "PaymentsNG": ["TerminalID"],
    "SSTP": ["TerminalID"],
    "ATMeye": ["AtmID", "Path", "PrerecordPath"],
    "ComputerName": ["ComputerName"],
    "ActiveComputerName": ["ComputerName"]
}


def read_registry():
    values = {}
    for i, reg_path in enumerate(REG_PATHS):
        key_display = DISPLAY_KEYS[i]
        values[key_display] = {}
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
            for val_name in REG_VALUE_NAMES[key_display]:
                try:
                    print({reg_path}, {val_name})
                    value, _ = winreg.QueryValueEx(registry_key, val_name)
                    values[key_display][val_name] = value
                except FileNotFoundError:
                    values[key_display][val_name] = ""
            winreg.CloseKey(registry_key)
        except FileNotFoundError:
            py_logger.exception("Error read registry!")
            for val_name in REG_VALUE_NAMES[key_display]:
                values[key_display][val_name] = ""
    return values
py_logger.info(f'Registry path is reading')

def write_registry(new_values):
    old_values = read_registry()
    for i, reg_path in enumerate(REG_PATHS):
        key_display = DISPLAY_KEYS[i]
        if key_display in new_values:
            try:
                registry_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for val_name, val_value in new_values[key_display].items():
                    winreg.SetValueEx(registry_key, val_name, 0, winreg.REG_SZ, str(val_value))
                winreg.CloseKey(registry_key)


                ##################RENAME_PC_START##################################
                active_pc = new_values["ComputerName"]["ComputerName"]
                computer_name_physical_dns_hostname = 5
                ctypes.windll.kernel32.SetComputerNameExW(computer_name_physical_dns_hostname, active_pc)
                ##################RENAME_PC_END###################################

                ##################ADD_VALUE_AFTER_ATM##############################
                def add_value_after_atm(active_pc, TID):
                    RECMSG1160 = f'#SOP##LPI8##DHPC##NCT##LF##CR##LF##CR##CPI12##EPM#PRINT COUNTERS#EPMC##CPI15##LF##CR##NL#ATM: {active_pc} / {TID} #NL#'
                    RECMSG1185 = f'#SOP##CPI15##DHPC##NCT##LF##CR##LF##CR##CPI12##EPM##NL##NL#CASS. EXCHANGE#EPMC##CPI15##LF##CR##LF##CR#ATM:  {active_pc} / {TID} #NL#'
                    RECMSG1195 = f'#SOP##DHPC##NCT##LF##CR##LF##CR##CPI12##EPM#   ADD BILLS#EPMC##CPI15##LF##CR##LF##CR#ATM:  {active_pc} / {TID} #NL#'
                    try:

                        reg_path = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\CCSOPSTEP\PRTMSG\ENGLISH'
                        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
                        winreg.SetValueEx(reg_key, 'RECMSG1160', 0, winreg.REG_SZ, RECMSG1160)
                        winreg.SetValueEx(reg_key, 'RECMSG1185', 0, winreg.REG_SZ, RECMSG1185)
                        winreg.SetValueEx(reg_key, 'RECMSG1195', 0, winreg.REG_SZ, RECMSG1195)
                        winreg.CloseKey(reg_key)

                    except WindowsError as e:
                        print(f'Error: {e}')

                try:
                    TID = new_values["BS/2"]["TerminalID"]
                except:
                    TID = ""
                add_value_after_atm(active_pc, TID)

                ##################RENAME_MULTIAGENT_START##########################
                if os.path.exists('c:/BS2/IQMultiagent/configuration/config.ini'):
                    val_atmeye = new_values["ATMeye"]["AtmID"]

                    config = configparser.ConfigParser()
                    config.optionxform = str

                    # Удаление первой строки без секции

                    with open(file='C:\BS2\IQMultiagent\configuration\config.ini', mode='r') as f:
                        lines = f.readlines()
                    with open(file='C:\BS2\IQMultiagent\configuration\config.ini', mode='w') as f:
                        for line in lines:
                            if line.strip('\n') != 'CRON_PRECISION = 60':
                                f.write(line)

                    myfile = Path('C:\BS2\IQMultiagent\configuration\config.ini')
                    config.read(myfile)

                    # Измененине конфиг файла
                    config.set(' properties ', 'AGENT_NAME', f'{val_atmeye}')
                    config.set(' atmeye ', 'ATM_EYE_VIDEOARCHIVE', f'D:\VIDEOARCHIVE\{val_atmeye}')
                    config.set(' vfs ', 'ATM_EYE_VIDEOARCHIVE', f'D:\VIDEOARCHIVE\{val_atmeye}')
                    config.write(myfile.open('w'))

                    # Добавление первой строки без секции
                    with open(f'C:\BS2\IQMultiagent\configuration\config.ini', 'r+') as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write('CRON_PRECISION = 60\n')
                        f.write('\n' + content)
                else:
                    py_logger.exception("Multiagent_not_found")
                    print("Multiagent_not_found")
                ##################RENAME_MULTIAGENT_END############################

            except OSError as e:
                py_logger.exception("WinError - Access error")
                messagebox.showerror("Ошибка", f"Не удалось записать в реестр:\n{e}")
                return
    log_rename_changes(old_values, new_values)
    messagebox.showinfo("Info!","Данные сохранены в реестр. необходима перезагрузка!")
    py_logger.info(f'Registry path is change')



#######################################################################################################
#def add_value_after_atm(active_pc, TID):
#    try:
#        with winreg.OpenKey(
#            winreg.HKEY_LOCAL_MACHINE,
#            r"SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\CCSOPSTEP\PRTMSG\ENGLISH",
#            0, winreg.KEY_READ | winreg.KEY_WRITE
#        ) as key:
#            try:
#                current_value_1160, reg_type = winreg.QueryValueEx(key, "RECMSG1160")
#                current_value_1185, reg_type = winreg.QueryValueEx(key, "RECMSG1185")
#                current_value_1195, reg_type = winreg.QueryValueEx(key, "RECMSG1195")
#            except FileNotFoundError:
#                py_logger.exception("ATM not founf in reestr module add_value_after_atm")
#                print("Ошибка: Значение отсутствует.")
#                return
#
#            pattern = r"ATM:\s*[^/]+/\S*"
#            replacement = f"ATM: {active_pc}/{TID}"
#
#            def update_value(current_value):
#                # если нет ATM: → пропускаем
#                if "ATM:" not in current_value:
#                    return current_value.strip()
#                # если уже нужное значение (по шаблону) → не меняем
#                if re.fullmatch(rf".*{re.escape(replacement)}.*", current_value.strip()):
#                    return current_value.strip()
#                # иначе заменяем только один раз
#                return re.sub(pattern, replacement, current_value.strip(), count=1)
#
#            updated_value_1160 = update_value(current_value_1160)
#            updated_value_1185 = update_value(current_value_1185)
#            updated_value_1195 = update_value(current_value_1195)
#
#            winreg.SetValueEx(key, "RECMSG1160", 0, reg_type, updated_value_1160)
#            winreg.SetValueEx(key, "RECMSG1185", 0, reg_type, updated_value_1185)
#            winreg.SetValueEx(key, "RECMSG1195", 0, reg_type, updated_value_1195)
#
#            print("Updated values:")
#            py_logger.info(f"Value updated: {updated_value_1160}", {updated_value_1185}, {updated_value_1195})
#            print(updated_value_1160)
#            print(updated_value_1185)
#            print(updated_value_1195)
#
#    except Exception as e:
#        py_logger.exception(f"Error module add_value_after_atm {e}")
#        print(f"Ошибка: {e}")





#######################################################################################################


#######################################################################################################
def click_fcx():
    py_logger.info(f'Open window Rename Configuration')
    window_fcx = tk.Toplevel(root)
    window_fcx.title("Rename Configuration")
    window_fcx.geometry("780x400+210+650")
    window_fcx.resizable(False, False)
    py_logger.info(f'Init form Rename Configuration - OK')
    py_logger.info(f'Check configuration...')

    labels = {}
    entries = {}

    registry_data = read_registry()

    # Заголовки столбцов
    tk.Label(window_fcx, text="Ключ", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10)
    tk.Label(window_fcx, text="Параметр", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10)
    tk.Label(window_fcx, text="Текущее значение", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10)
    tk.Label(window_fcx, text="Новое значение", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=10)
    tk.Label(window_fcx, text="Global TID", font=('Arial', 10, 'bold')).grid(row=0, column=4, padx=10)

    # Global TID
    global_tid_entry = tk.Entry(window_fcx)
    global_tid_entry.grid(row=1, column=4, padx=10)

    # Сохраняем оригинальные пути ATMeye
    original_atmeye_paths = {
        "Path": registry_data.get("ATMeye", {}).get("Path", ""),
        "PrerecordPath": registry_data.get("ATMeye", {}).get("PrerecordPath", "")
    }

    # ===================== Функции =====================

    # Создание отсутствующего параметра
    import tkinter.simpledialog as simpledialog
    def create_missing_param(key_display, val_name):
        # перечитываем данные реестра заново
        current_registry = read_registry()
        current_value = current_registry.get(key_display, {}).get(val_name, "")

        if current_value == "":
            new_value = simpledialog.askstring(
                "Создание параметра",
                f"Введите значение для нового параметра:\n{key_display} → {val_name}"
            )
            if new_value:
                write_registry({key_display: {val_name: new_value}})
                py_logger.info(f"Created missing registry param: {key_display}/{val_name} = {new_value}")
                refresh_ui()  # обновляем интерфейс

    # Синхронизация Global TID
    def sync_terminal_id(*args):
        global_tid = global_tid_entry.get()
        for key_display in DISPLAY_KEYS:
            if key_display == "BS/2":
                continue
            for val_name in REG_VALUE_NAMES[key_display]:
                if val_name in ["TerminalID", "AtmID", "ComputerName"]:
                    entry_widget = entries[key_display][val_name]
                    if entry_widget['state'] != 'disabled':
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, global_tid)

        # Обновляем ATMeye пути
        for path_key in ["Path", "PrerecordPath"]:
            if "ATMeye" in entries and path_key in entries["ATMeye"]:
                path_entry = entries["ATMeye"][path_key]
                if path_entry['state'] != 'disabled':
                    base_path = original_atmeye_paths.get(path_key, "")
                    new_value = re.sub(r'[^\\]+$', global_tid, base_path) if base_path else global_tid
                    path_entry.delete(0, tk.END)
                    path_entry.insert(0, new_value)

    global_tid_entry.bind("<KeyRelease>", sync_terminal_id)

    # Функция построения/обновления формы
    def fill_form(registry_data):
        for widget in window_fcx.grid_slaves():
            row_info = int(widget.grid_info()["row"])
            col_info = int(widget.grid_info()["column"])
            # Не трогаем заголовки (row=0) и Global TID (row=1, column=4)
            if row_info > 0 and not (row_info == 1 and col_info == 4):
                widget.destroy()

        row = 1
        for key_display in DISPLAY_KEYS:
            labels[key_display] = {}
            entries[key_display] = {}
            for val_name in REG_VALUE_NAMES[key_display]:

                tk.Label(window_fcx, text=key_display).grid(row=row, column=0, padx=10, pady=3)
                tk.Label(window_fcx, text=val_name).grid(row=row, column=1, padx=10, pady=3)

                val_label = tk.Label(window_fcx, text=registry_data[key_display][val_name])
                val_label.grid(row=row, column=2, padx=10, pady=3)
                labels[key_display][val_name] = val_label

                # двойной клик на label
                val_label.bind("<Double-Button-1>",
                               lambda e, k=key_display, v=val_name: create_missing_param(k, v))

                entry = tk.Entry(window_fcx)
                entry.insert(0, registry_data[key_display][val_name])
                if registry_data[key_display][val_name] == "":
                    entry.config(state='disabled')
                entry.grid(row=row, column=3, padx=10, pady=3)
                entries[key_display][val_name] = entry

                # двойной клик на entry
                entry.bind("<Double-Button-1>",
                           lambda e, k=key_display, v=val_name: create_missing_param(k, v))

                row += 1

        # кнопка Save changes
        tk.Button(window_fcx, text="Save changes", command=save_changes).grid(
            row=row + 1, column=0, columnspan=4, pady=10
        )

    # Обновление интерфейса
    def refresh_ui():
        new_data = read_registry()
        fill_form(new_data)

    # Сохранение изменений
    def save_changes():
        py_logger.info(f'Save registry path..')
        try:
            new_values = {}
            for key_display in DISPLAY_KEYS:
                new_values[key_display] = {}
                for val_name in REG_VALUE_NAMES[key_display]:
                    entry_widget = entries[key_display][val_name]
                    if entry_widget['state'] != 'disabled':
                        value = entry_widget.get()
                        if value:
                            new_values[key_display][val_name] = value

            write_registry(new_values)
            refresh_ui()  # обновляем форму после записи

        except:
            py_logger.exception(f'Error save registry path')
            print(f'Error save registry path')

    # ===================== Построение формы =====================
    fill_form(registry_data)


#####################################GET_CONF_ATM################################################

def get ():
    if os.path.exists(r'C:\ProBase\conf\LOG_1\deviceTrace'):
        configatm.get_conf()
        messagebox.showinfo("Info", r"Успех файл сохранен в C:\CONFIG_ATM")
        py_logger.info("The file was saved C:CONFIG_ATM")
    else:
        messagebox.showerror("Error", r"Ошибка. Нужный файл не найден")
        py_logger.info("Error file not found")
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


main_menu.add_cascade(label="Rename", command=click_fcx)
main_menu.add_cascade(label="Config_ATM", command=get)
main_menu.add_cascade(label='ATMeye', command=ATMeye.install)
main_menu.add_cascade(label='ATMeye_silent', command=ATMeye.chek_atmeye)
main_menu.add_cascade(label='Get_license', command=ATMeye.get_license)
#main_menu.add_cascade(label='uninstall', command=ATMeye.filter_ini)

root.config(menu=main_menu)


#---------- Init Fonts ----------


font1 = font.Font(family= "candara", size=14, weight="bold", slant="roman")
font2 = font.Font(family= "tahoma", size=10)


#---------- Init Titles ----------


label1 = Label(text="DeviceInfo:", cursor="star", foreground="#23abbd", font=font1)
label1.pack(anchor='nw', padx=28, pady=15)


#---------- Check registry and Render Form----------


ProSetup = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\DEVICEINFO\Software'
ProBase = r'SOFTWARE\WOW6432Node\Diebold Nixdorf\ProBase\Install'
#JInstall = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\JInstall\CurrentVersion'
ProAgent = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProAgent\CurrentVersion\InstallationInfo'
ProAgentSSTP = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProAgent\CurrentVersion\SSTP'
ATMeye = r'SOFTWARE\WOW6432Node\BS/2\ATMeye'
#CoreXFS = r'SOFTWARE\WOW6432Node\ATM Software\Versions'
PaymentsNG = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\PaymentsNG'
FCX = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2'
BS2FCXSTT = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\bs2FCXstt'
BS2ServiceFW = r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\BS2ServiceFW'




productsPath = [ProSetup, ProBase, ProAgent, ProAgentSSTP, ATMeye, PaymentsNG, FCX, BS2FCXSTT, BS2ServiceFW]
py_logger.info(f'Check path DeviceInfo..')
for i in productsPath:
    locPath = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    m = 2

    try:
        checkPath = winreg.OpenKey(locPath, i)

        match i:

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\DEVICEINFO\Software':
                vProSetup = winreg.QueryValueEx(checkPath, "ProSetup_version")
                # Для RM3 путь тот же, только параметр называется "ProSetup_name"
                label1 = Label(text="ProSetup:   " + vProSetup[0], font=font2)
                label1.pack(anchor='nw', padx=28, pady=m)

                if vProSetup:
                    vProSetupInstallData = winreg.QueryValueEx(checkPath, "ProSetup_version_Data")
                    # Для RM3 путь тот же, только параметр называется "ProSetup_data"
                    label2 = Label(text="ProSetupData:   " + vProSetupInstallData[0], font=font2)
                    label2.pack(anchor='nw', padx=28, pady=m)

                if vProSetup:
                    machineType = winreg.QueryValueEx(checkPath, "ProSetup_version_Type")
                    label3 = Label(text="Type ATM:   " + machineType[0], font=font2)
                    label3.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Diebold Nixdorf\ProBase\Install':
                vProBase = winreg.QueryValueEx(checkPath, "Version")
                label4 = Label(text="ProBase:   " + vProBase[0], font=font2)
                label4.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProAgent\CurrentVersion\InstallationInfo':
                vProAgent = winreg.QueryValueEx(checkPath, "InstalledVersion")
                label5 = Label(text="ProAgent:   " + vProAgent[0], font=font2)
                label5.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProAgent\CurrentVersion\SSTP':
                ProAgentTID = winreg.QueryValueEx(checkPath, "TerminalID")
                label6 = Label(text=f"ProAgen TID:   " + ProAgentTID[0], font=font2)
                label6.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\BS/2\ATMeye':
                vATMeye = winreg.QueryValueEx(checkPath, "AgentVersion")
                label7 = Label(text="ATMeye:   " + vATMeye[0], font=font2)
                label7.pack(anchor='nw', padx=28, pady=m)

                if vATMeye :
                    ATMID = winreg.QueryValueEx(checkPath, "AtmID")
                    label8 = Label(text="ATMeye-AtmID:   " + ATMID[0], font=font2)
                    label8.pack(anchor='nw', padx=28, pady=m)

                if vATMeye :
                    ATMeyePath = winreg.QueryValueEx(checkPath, "Path")
                    label9 = Label(text="ATMeye-Path:   " + ATMeyePath[0], font=font2)
                    label9.pack(anchor='nw', padx=28, pady=m)

                #if vATMeye :
                #    ATMeyePreRecPath = winreg.QueryValueEx(checkPath, "PrerecordPath")
                #    label10 = Label(text="ATMeye-PrerecordPath:   " + ATMeyePreRecPath[0], font=font2)
                #    label10.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\PaymentsNG':
                PaymentsNGTID = winreg.QueryValueEx(checkPath, "TerminalID")
                label10 = Label(text="PaymentsNG TID:   " + PaymentsNGTID[0], font=font2)
                label10.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2':
                FCXTID = winreg.QueryValueEx(checkPath, "TerminalID")
                label11 = Label(text="FCX-TID:   " + FCXTID[0], font=font2)
                label11.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\bs2FCXstt':
                BS2FCXSTTTID = winreg.QueryValueEx(checkPath, "TerminalID")
                label12 = Label(text="BS2FCXSTT-TID:   " + BS2FCXSTTTID[0], font=font2)
                label12.pack(anchor='nw', padx=28, pady=m)

            case r'SOFTWARE\WOW6432Node\Wincor Nixdorf\ProTopas\CurrentVersion\BS/2\BS2ServiceFW':
                BS2SERVICEFW = winreg.QueryValueEx(checkPath, "TerminalID")
                label13 = Label(text="BS2ServiceFW-TID:   " + BS2SERVICEFW[0], font=font2)
                label13.pack(anchor='nw', padx=28, pady=m)

        if checkPath:
            winreg.CloseKey(checkPath)

    except FileNotFoundError:
        py_logger.exception(f'Key is not found: {i}')
    except Exception as e:
        py_logger.exception(f'Error read {i}: {e}')
py_logger.info(f'Read path DeviceInfo - OK')



##############################-------CDF-------##############################

try:
    py_logger.info('Read CDF files')
    file_path = r'C:\ProBase\INVENTORY'
    pattern = 'INVENTORY.XML'

    # правильные значения, с которыми сравниваем
    VALID_USD = ["1048 movem_cdaa_usd.cdf"]
    VALID_UZS = ["1009 movem_cdaa_uzs.cdf"]
    VALID_FRM = ["1065 MOVEM_CDXX.PKG"]

    VALID_USD_RM3 = ['1031 MOVE_AWAA_USD.CDF']
    VALID_UZS_RM3 = ['1005 MOVE_AWAA_UZS.CDF']

    for filename in os.listdir(file_path):
        if re.findall(pattern, filename):
            filepath = os.path.join(file_path, filename)

            with open(filepath, mode='r', encoding='ANSI') as datacollect:
                data = datacollect.read()

            # ищем строки по шаблонам
            USD = re.findall(r'\d\d\d\d+ movem_cdaa_usd.cdf', data)
            UZS = re.findall(r'\d\d\d\d+ movem_cdaa_uzs.cdf', data)
            FRM = re.findall(r'\d\d\d\d+ MOVEM_CDXX.PKG', data)

            USDRM3 = re.findall(r'\d\d\d\d+ MOVE_AWAA_USD.CDF', data)
            UZSRM3 = re.findall(r'\d\d\d\d+ MOVE_AWAA_UZS.CDF', data)
            FRM3   = re.findall(r'\d\d\d\d+ MOVE_AWAA.FRM', data)

            # собираем все в список для проверки
            ALL = [
                ("USD", USD, VALID_USD),
                ("UZS", UZS, VALID_UZS),
                ("FRM", FRM, VALID_FRM),
                ("USDRM3", USDRM3, VALID_USD_RM3),
                ("UZSRM3", UZSRM3, VALID_UZS_RM3),
                ("FRM3", FRM3, None),
            ]

            # выводим на экран
            for name, sublist, valid_list in ALL:
                if sublist:
                    for item in sublist:
                        # по умолчанию чёрный текст
                        color = "black"

                        # если есть список валидных значений и item не входит — подсветить красным
                        if valid_list and item not in valid_list:
                            color = "red"

                        label2 = Label(
                            text=f"{name}: {item}",
                            font=font2,
                            fg=color
                        )
                        label2.pack(anchor='nw', padx=28, pady=1)
                        py_logger.info(f"Read CDF OK {sublist}")

except Exception as e:
    py_logger.exception(f"error: {e}")
    print("error:", e)

##############################-------CDF-------##############################

#############################################################################




#def replace_cdf():
#    if VALID_USD != USD:
#        messagebox.showinfo("Внимание","Необходимо обновить CDF файл USD!!!")
#    if VALID_UZS != UZS:
#        messagebox.showinfo("Внимание", "Необходимо обновить CDF файл UZS!!!")
#    else:
#        print("false")
#
#replace_cdf()



##############################################################################



##############################-------Update-------##############################
file_path = r'C:\JINSTALL'
pattern = 'bs2update.log'


if os.path.exists(r"C:\JINSTALL\bs2update.log"):
    for filename in os.listdir(file_path):
        if re.findall(pattern, filename):
            filepath = os.path.join(file_path, filename)
            with open(filepath, mode='r', encoding='ANSI') as datacollect:
                data = datacollect.read()

    lab = re.search('comment: \w{15,40}', data)
    if lab:
     label16 = Label(text='' + lab.group(0), font=font2)
     label16.pack(anchor='nw', padx=28, pady=1)
    else:
        py_logger.exception("Patern_not_found")
        print("Patern_not_found")
else:
    py_logger.exception("File_bs2update_notfound")
    print("File_bs2update_notfound")


##############################-------Update-------##############################

root.mainloop()