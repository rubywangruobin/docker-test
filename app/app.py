from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from azure.cognitiveservices import speech as speechsdk
from azure.storage.blob import BlockBlobService
import os

app = Flask(__name__)

# Create the BlockBlockService that the system uses to call the Blob service for the storage account.
block_blob_service = BlockBlobService(
    account_name='citysettlersstorage',
    account_key='n71kvCnTmIkIwGvAnDRk7JlChA4R0rV1lzh1jH5uVDShnhJITgL9yDF3YEU2Inlogn49zMukrOswgc4S+Wtobg==')

# Create a container called 'quickstartblobs'.
container_name = 'wavtextblobs'
block_blob_service.create_container(container_name)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'static',
                                   secure_filename(f.filename))
        f.save(upload_path)
        from_file(basepath + '/static/', f.filename)
        return redirect(url_for('upload'))
    return render_template('upload.html')


def from_file(base='', filename='default'):
    speech_config = speechsdk.SpeechConfig(subscription="b5c77ef7e3e94bf09e8fb847e42cfc34", region="eastus")
    wav_path = base + filename  # wav 路径
    blob_file_name = filename.split('.')[0] + '.txt'  # txt文件名
    txt_path = base + blob_file_name  # txt文件路径

    audio_input = speechsdk.AudioConfig(filename=wav_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()

    with open(txt_path, 'w', encoding="UTF-8") as fp:
        fp.write(result.text)

    # 进行备份
    block_blob_service.create_blob_from_path(container_name, filename, wav_path)
    block_blob_service.create_blob_from_path(container_name, blob_file_name, txt_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
