from Google import Create_Service
from googleapiclient.http import MediaFileUpload # Untuk mengupload file memakai library ini
from googleapiclient.http import MediaIoBaseDownload #
from subprocess import check_output, STDOUT, CalledProcessError # Library untuk menjalankan tes
import os
import io
import pandas as pd

# Menghubungkan ke API Google Drive
CLIENT_SECRET_FILE = 'auth_client.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# List file dari Folder Submission

def listOfFile():
    folder_id = '1_JtFuFUoMUfV4NS-_H62_yRtuCy21cdV'
    query = f"parents = '{folder_id}'"

    response = service.files().list(q=query).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.files().list(q=query, pageToken=nextPageToken).execute()
        files = response.get('files')
        nextPageToken = response.get('nextPageToken')

    data = pd.DataFrame(files)
    # print(data)

    # Tambah nama file dan id file
    idFiles = data['id']
    nameFiles = data['name']
    return idFiles, nameFiles

# Study Case untuk Mengetes
def study_case(file_path):
    score = 0
    message = "\n"
    case = [0, 10, -2]
    for index, number_test in enumerate(case):
        # print(number_test)
        # print(file_path)
        output_file = check_output(["python", file_path, str(number_test)])
        output_file = output_file.decode('utf-8').replace('\r\n', '')
        # print(output_file)
        if number_test == 0 or number_test == -2:
            expected = []
        elif number_test == 10:
            expected = [1, 3, 5, 7, 9]


        if output_file == '{}'.format(expected):
            score += 1
            message += "Test Case {}: SUCCESS\n".format(index+1)

        else:
            message += "Test Case {}: FAILED\n".format(index+1)
            message += "Whoops, got wrong output.\n"

        message += 'Number : {}\n'.format(number_test)
        message += "Expected output: {}\n".format('{}'.format(expected))
        message += "Your Output: {}\n".format(output_file)
        message += "Score ({}/{}).\n".format(score, len(case))
        message +='\n'
    return score, message


def main():
    files_id, files_name = listOfFile()
    print(files_id, files_name)
    for file_id, file_name in zip(files_id, files_name):
        request = service.files().get_media(fileId = file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd = fh, request = request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            # print('Progress {}'.format(status.progress() * 100))

        fh.seek(0)
        # print(fh.read().decode('utf-8'))
        # Menyimpan file di lokal
        file_path = os.path.join('./StudentCode', file_name)
        with open(file_path, 'wb') as f:
            f.write(fh.read())
            f.close()

        # Testing file
        msg = ""
        try:
            print('TRY OPEN {}'.format(file_path))
            # output = study_case(file_path)
            output_file = check_output(["python", file_path, "20"], stderr = STDOUT)
            # 1/0
            # print(output_file)
        except CalledProcessError as exc:
            print('ERROR IN {}'.format(file_path))
            msg += "There is Error in your code\n"
            # print(exc.output)
            msg += exc.output.decode('utf-8')
        except ZeroDivisionError as er:
            print('ERROR {}'.format(file_path))
            msg += "CANT'DIVIDE BY ZERO"
        else:
            # output_file = check_output(["python", "odd.py", "10"])
            print('DO TESTING {}'.format(file_path))
            score, msg = study_case(file_path)

        report_file = file_name[:-3]+'.txt'
        with open(os.path.join('./StudentCode', report_file), 'w') as f:
            f.write(msg)

        # Upload files
        reportfolder_id = '1osIwmAJ6WrNqP_ia4NiydUT03QXKNuQr'
        mime_type = 'text/plain'
        name = "[RESULT] " + report_file
        file_metadata = {
            'name' : name,
            'parents' : [reportfolder_id]
        }
        media = MediaFileUpload('./StudentCode/{}'.format(report_file), mimetype = mime_type)

        service.files().create(
            body = file_metadata,
            media_body =  media,
            fields = 'id'
        ).execute()

        # service.files().delete(fileId=file_id).execute()
main()


    # Mulai mendownload
