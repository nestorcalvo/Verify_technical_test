from utils import *

DOCUMENTS_PATH = './documents'
JSON_PATH = './json_files'
files_path = []
for file_path in os.listdir(path=DOCUMENTS_PATH):
  files_path.append(os.path.abspath(os.path.join(DOCUMENTS_PATH, file_path)))

create_folder(JSON_PATH)
client = api_connection()

for file_path in files_path:
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name = file_name + '.json'
    response = client.process_document(file_path) 
    text_to_process = response['ocr_text']
    json_file = json_generation(text_to_process)
    store_json(json_file, os.path.join(JSON_PATH, file_name))
    