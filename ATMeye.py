import winreg
import os
from tkinter import messagebox
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import tempfile
import shutil
import sys
import time
import logging
import psutil


######################### INIT LOGGER #####################################

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
py_handler = logging.FileHandler(f"__main__.log", mode='a')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)

############################################################################



video = 'Y'
time_video = '60'

def change_param_probase_default():  # Добавляет значения для работы ATMeye
 if os.path.exists('C:\ATMeye\TOOLS'):
#    messagebox.showinfo('Info','ATMeye reestr is schanges')
    try:
        reg_path_probase = [
            r"SOFTWARE\WOW6432Node\Diebold Nixdorf\ProBase\MV\OSI\User"
        ]
        for reg_path in reg_path_probase:
            reg_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "portrait.always_on", 0, winreg.REG_SZ, 'true')
            winreg.SetValueEx(reg_key, 'fascia.always_on', 0, winreg.REG_SZ, 'true')
            winreg.CloseKey(reg_key)
            py_logger.info("Reestr OSI was changed")
    except WindowsError as e:
        py_logger.exception(f"{e}")
        print(f'Error: {e}')
    try:
        reg_path_video = [r'SOFTWARE\WOW6432Node\BS/2\ATMeye\VIDEO']
        for reg_path in reg_path_video:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, 'Enabled (Y/N)', 0, winreg.REG_SZ, video)
            winreg.SetValueEx(reg_key, 'Capture timeout (sec)', 0, winreg.REG_SZ, time_video)
            winreg.CloseKey(reg_key)
            py_logger.info("Reestr VIDEO was changed")
    except WindowsError as e:
        py_logger.exception(f"{e}")
        print(f'Error: {e}')
 else:
     messagebox.showerror('Error', 'ATMeye not found')
     py_logger.exception("ATMeye not found")


def install():
    py_logger.info("install ATMeye starting...")
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    installer = os.path.join(base_path, "CoreInstaller-5.3.0.188-8065e65-1d7968b-2025-07-14.exe")

    args = [installer, "/quiet", "/norestart"]
    subprocess.run(args, check=True)



def get_license():
    py_logger.info("get_license starting...")
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    installer = os.path.join(base_path, "Bs2LCli.exe")

    if not os.path.exists(installer):
        messagebox.showerror("Ошибка", f"Не найден файл {installer}")
        return

    args = [
        installer,
        "--generate-atmeye",
        "--days", "10000",
        "--features", "ATMeye Core",
        "--customer", "Ipak Yuli"
    ]

    try:
        with open("license_request_Ipak_Yuli.txt", "w") as outfile:
            subprocess.run(args, check=True, stdout=outfile, stderr=subprocess.STDOUT)
        py_logger.info("The License_request_Ipak_Yuli.txt file was created successfully")
        messagebox.showinfo("Успех", "Файл license_request_Ipak_Yuli.txt успешно создан")
    except subprocess.CalledProcessError as e:
        py_logger.exception(f"Failed to execute command {e}")
        messagebox.showerror("Ошибка", f"Не удалось выполнить команду:\n{e}")
    except Exception as e:
        py_logger.exception(f"An unexpected error occurred {e}")
        messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка:\n{e}")

def chek_atmeye():
    if uninstall():
        install_silent()
    else:
        py_logger.exception("Installation silent atmeye error")
        print("error")


def resource_path(relative_path):
    """Возвращает путь к ресурсу внутри exe или при запуске из .py"""
    if getattr(sys, 'frozen', False):  # если программа собрана в exe
        base_path = sys._MEIPASS
    else:  # обычный запуск
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def filter_ini():
    target_filter = r"C:\ATMeye\filter.ini"
    my_filter = resource_path("filter.ini")
    try:
        with open (my_filter, "rb") as src, open(target_filter, 'wb') as dst:
            dst.write(src.read())
            print("Filter.ini заменен")
            py_logger.info("Filter.ini was changed")
    except Exception as e:
        py_logger.exception(f"filter.ini {e}")
        print(f"шибка замены {e}")



def uninstall():
        os.system('cckill')
        target_uninstal = r"C:\ATMeye\uninstall.exe"
        my_uninstal = resource_path("uninstall.exe")

        if not os.path.exists(target_uninstal):
            py_logger.info("ATMeye not found install start...")
            print("ATMeye не установлен")
            return True

        print("Выполняем cckill...")
        try:
            proc = subprocess.Popen(
                "cckill",
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # отправляем "Enter"
            proc.communicate(input="\n")
            py_logger.info("cckill successfully")
            print("cckill успешно завершён")
        except Exception as e:
            print(f"Ошибка при выполнении cckill: {e}")
            py_logger.exception(f"cckill error {e}")
            messagebox.showerror("Ошибка", "Не удалось выполнить cckill")
            return False

        print("Обнаружен uninstall.exe, замена на встроенный...")
        try:
            # копируем свой uninstall.exe поверх
            with open(my_uninstal, "rb") as src, open(target_uninstal, "wb") as dst:
                dst.write(src.read())
            py_logger.info("Replaced uninstall.exe")
            print("Заменили uninstall.exe")
        except Exception as e:
            py_logger.exception(f"Error replacing uninstall.exe: {e}")
            print(f"Ошибка при замене uninstall.exe: {e}")
            return False

        print("Запуск деинсталляции ATMeye...")
        py_logger.info("Starting ATMeye uninstallation...")
        subprocess.Popen([target_uninstal, "/S"])  # запускаем, но не ждём

        # ждём, пока WinFastDS.dll исчезнет
        for _ in range(60):  # максимум 10 минут
            if not os.path.exists(r"C:\ATMeye\WinFastDS.dll"):
                py_logger.info("Old ATMeye successfully removed")
                print("Старый ATMeye успешно удалён")
                return True
            time.sleep(1)

        print("Таймаут: ATMeye не удалился за 1 минуту")
        py_logger.exception("Timeout: ATMeye did not delete within 1 minute")
        messagebox.showerror(
            'Ошибка',
            "Не удалось удалить старую версию ATMeye. "
            "Пожалуйста удалите ATMeye вручную и повторите попытку"
        )
        return False


def install_silent():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    installer = os.path.join(base_path, "CoreInstaller-5.3.0.188-8065e65-1d7968b-2025-07-14.exe")

    args = [
        installer,
        "/s",
        "/ATMTYPE=PROTOPAS",
        "/VIDEOARCHIVEPATH=D:\\VIDEOARCHIVE",
        "/PRERECORDPATH=D:\\VIDEOARCHIVE\\PRERECORD",
        "/USECAMS=3",
        "/FRAMEGRABBER=BS2_OsiWn.dll",
        "/SERVICEDELAYED=YES"
    ]

    def show_auto_close_message(title, text, delay=3000):
        """Окно, которое закрывается через delay мс (по центру экрана)."""
        msg = tk.Toplevel()
        msg.title(title)
        msg.resizable(False, False)

        # Размер окна
        w, h = 320, 120
        # Центрируем по экрану
        sw = msg.winfo_screenwidth()
        sh = msg.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        msg.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(msg, text=text, wraplength=300, justify="center").pack(expand=True, pady=20)

        # Автоматическое закрытие
        msg.after(delay, msg.destroy)

    def run_installer():
        try:
            subprocess.run(args, check=True)
            root.after(100, lambda: show_auto_close_message("Успех", "Установка успешно завершена", 3000))
            py_logger.info("Installation completed successfully")
            change_param_probase_default()
            filter_ini()
        except subprocess.CalledProcessError as e:
            root.after(100, lambda: show_auto_close_message("Ошибка", f"Установка завершилась с ошибкой:\n{e}", 5000))
        except Exception as e:
            root.after(100, lambda: show_auto_close_message("Ошибка", f"Не удалось запустить установку:\n{e}", 5000))
        finally:
            root.after(100, root.destroy)  # закрыть окно прогресса

    # Окно с прогресс баром
    root = tk.Tk()
    root.title("Установка приложения")
    root.geometry("400x100")
    root.resizable(False, False)

    label = tk.Label(root, text="Идёт установка, пожалуйста подождите...")
    label.pack(pady=10)

    progress = ttk.Progressbar(root, mode="indeterminate")
    progress.pack(fill="x", padx=20, pady=10)
    progress.start(10)

    # Запускаем установку в отдельном потоке
    thread = threading.Thread(target=run_installer, daemon=True)
    thread.start()

    root.mainloop()