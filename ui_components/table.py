import os.path as path
import math
import io
import time
import numpy as np
from datetime import datetime, timedelta

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def conv(x):
    return x.replace(',', '.').encode()


class MegaTable(object):

    # other time with no better solution than to pass the function
    def __init__(self, service, ricevitore_id, month, file, elevation, azimuth,
                 max_lenght):
        try:
            month_id = None
            page_token = None

            while True:
                # Call the Drive v3 API
                response = (service.files().list(
                    q=
                    f"mimeType='application/vnd.google-apps.folder' and '{ricevitore_id}' in parents and name='{month}'",
                    spaces="drive",
                    fields="nextPageToken, files(id)",
                    pageToken=page_token,
                ).execute())
                month_id = response.get("files", [])[0].get("id")
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
            if month_id is None:
                print("No files found.")
                return
        except HttpError as error:
            print(f"An error occurred: {error}")

        filepath = f"./files/{file['name']}"
        if path.isfile(filepath
                       ) and path.getmtime(filepath) - time.time() < 3600 * 24:
            print("File exists and is recent")
        else:
            try:
                request = service.files().get_media(fileId=file["id"])
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(
                        f"Download {int(status.progress() * 100)}. For file {filepath}"
                    )
            except HttpError as error:
                print(f"An error occurred: {error}")
            with open(filepath, "wb") as f:
                f.write(file.getbuffer())

        data = np.genfromtxt(filepath, delimiter=";", dtype="str")

        sensitivity = 0.11  # sensibilità
        posizione_iniziale = -1
        posizione_piu_lunga = -1
        lunghezza_massima = 0
        is_start = True
        for i in range(len(data)):
            if (np.abs(float(data[i][9]) - azimuth) <= sensitivity
                    and np.abs(float(data[i][10]) - elevation) <= sensitivity):
                if is_start:
                    posizione_iniziale = i
                    is_start = False
            elif not is_start:
                if i - posizione_iniziale > lunghezza_massima:
                    lunghezza_massima = i - posizione_iniziale
                    posizione_piu_lunga = posizione_iniziale
                is_start = True

        if (lunghezza_massima == 0):
            print("No interval Found")
            raise Exception(
                'Interval not found',
                'there was no moment in which az and el fit with the data')

        print(f"elevation: {elevation}")
        print(f"azimuth: {azimuth}")
        pos_start = data[posizione_piu_lunga]
        date_start = datetime.strptime(
            f"{(pos_start[0])}/{(pos_start[1])}/{(pos_start[2][2:])} {(pos_start[3])}:{(pos_start[4])}:{(pos_start[5])}",
            '%d/%m/%y %H:%M:%S')
        pos_end = data[posizione_piu_lunga + lunghezza_massima - 1]
        date_end = datetime.strptime(
            f"{(pos_end[0])}/{(pos_end[1])}/{(pos_end[2][2:])} {(pos_end[3])}:{(pos_end[4])}:{(pos_end[5])}",
            '%d/%m/%y %H:%M:%S')
        files_name = []
        files_id = []
        page_token = None

        while True:
            # Call the Drive v3 API
            response = (service.files().list(
                q=f"mimeType='text/plain' and '{month_id}' in parents",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            ).execute())
            for file in response.get("files", []):
                # Process change
                files_name.append(file.get("name"))
                files_id.append(file.get("id"))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        print(f"start: {date_start}")
        print(f"end: {date_end}")
        files_name.sort()
        print(files_name[0])
        print(files_name[1])
        for i in range(len(files_name)):
            check_date = datetime.strptime(files_name[i],
                                           '%y%m%d_%H%M%S_USRP.txt')
            if date_start.date() == check_date.date() and timedelta(
                    seconds=0) <= check_date - date_start <= timedelta(
                        minutes=7):
                print(check_date)
                starting_index = i
                break
        for i in range(starting_index + 1, len(files_name)):
            check_date = datetime.strptime(files_name[i],
                                           '%y%m%d_%H%M%S_USRP.txt')
            if date_end.date() == check_date.date() and timedelta(
                    seconds=0) <= date_end - check_date <= timedelta(
                        minutes=7):
                ending_index = i
                break

        is_first = True
        for i in range(starting_index, ending_index):
            filepath = f"./files/{files_name[i]}"
            if path.isfile(filepath) and path.getmtime(
                    filepath) - time.time() < 3600 * 24:
                print(f"{filepath} exists and is recent")
            else:
                try:
                    request = service.files().get_media(fileId=files_id[i])
                    file = io.BytesIO()
                    downloader = MediaIoBaseDownload(file, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(
                            f"Download {int(status.progress() * 100)}. for {filepath}"
                        )
                except HttpError as error:
                    print(f"An error occurred: {error}")
                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())

            if is_first:
                self.video = np.genfromtxt((conv(x) for x in open(filepath)),
                                           delimiter=';')
                is_first = False
            else:
                addon = np.genfromtxt((conv(x) for x in open(filepath)),
                                      delimiter=';')
                self.video = np.concatenate((self.video, addon))
        self.max_lenght = max_lenght
        self.mean = self.get_mean(self.video)
        self.x = np.arange(self.video[0][1],
                           self.video[0][1] + 8192 * self.video[0][2],
                           self.video[0][2])

    def get_mean(self, table):
        num_freq = len(table[0]) - 3
        total_lenght = len(table)
        total_mean = np.zeros(
            (math.ceil(len(table) / self.max_lenght), num_freq))
        pos = 0
        for k in range(math.ceil(total_lenght / self.max_lenght)):
            pos = k * self.max_lenght
            for i in range(num_freq):
                sum = 0
                lenght = min(total_lenght - pos, self.max_lenght)
                for j in range(lenght):
                    sum += 10**(table[j + pos][i + 3] / 10)
                total_mean[k][i] = np.log10(sum / lenght) * 10
        return total_mean
