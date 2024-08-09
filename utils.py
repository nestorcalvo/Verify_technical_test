import os
import re
import json
from dotenv import load_dotenv
from veryfi import Client

def api_connection():
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    username = os.getenv('USERNAME_API')
    api_key = os.getenv('API_KEY')
    veryfi_client = Client(client_id, client_secret, username, api_key)    
    return veryfi_client

def store_json(JSON_file, JSON_path):
    with open(JSON_path, 'w') as f:
        json.dump(JSON_file, f)
        print(f'File {JSON_path} was saved')
def create_folder(folder_path):

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")
        
def get_pages(text_to_analyze):
  pages = re.search(r"Page\s*([\d]+)\s*of\s*([\d]+)", text_to_analyze)
  try:
    total_page = pages.group(2)
  except:
    total_page = None
  return total_page

def get_invoice_info(text_to_analyze):
    invoice_dict = {
        'Invoice Date': '',
        'Due Date': '',
        'Invoice No.': '',
    }
    try:
        invoice_info = re.findall(r"(^\t[\d\/]+\t.+\t.+)", text_to_analyze, re.MULTILINE)
        for i, info in enumerate(invoice_info):
            separated = info.strip().split('\t')
            keys = invoice_dict.keys()
            for j, key in enumerate(keys):      
                invoice_dict[key] = separated[j]
            break
    except:
        invoice_dict = {
            'Invoice Date': None,
            'Due Date': None,
            'Invoice No.': None,
        }
    return invoice_dict

def get_invoice_ammounts(text_to_analyze):
    data_dict = {}
    try:
        remaining_text_regex = re.search(r"(?s)Description\s+Quantity\s+Rate\s+Amount\s*(.*)Total", text_to_analyze, re.DOTALL)
        remaining_text = remaining_text_regex.group(1)
        data = re.findall(r"\s+(-?[\d,\.]+)\s+(-?[\d,\.]+)\s+(-?[\d,\.]+)", remaining_text, re.DOTALL)
        type_description = re.findall(r"^(.*?)(?=\s*[|:])|^(.*?)(\s*Discount)", remaining_text, re.MULTILINE)
        
        for i, item in enumerate(data):
            data_dict[f'item_{i+1}'] = {'quantity': item[0], 'rate': item[1], 'amount': item[2]}
        for i, item in enumerate(type_description):
            item = ''.join(item)
            if 'Discount' in item:
                data_dict[f'item_{i+1}']['type'] = 'Discount'
            
            elif 'Transport' in item:
                data_dict[f'item_{i+1}']['type'] = 'Transport'
            elif 'Installation' in item:
                data_dict[f'item_{i+1}']['type'] = 'Installation'
            else:
                data_dict[f'item_{i+1}']['type'] = item
            data_dict[f'item_{i+1}']['full_type'] = item
    except:
        data_dict['item_1'] = 'Information not found'
    return data_dict

def get_po_box_info(text_to_analyze):
    po_box_number = re.search(r'(?<=PO Box) (\d+)\s+([\w,\-\d\s]+)\n+', text_to_analyze)
    try:
        po_box = po_box_number.group(1)
        address = po_box_number.group(2)
    except:
        address = None
        po_box = None
    return po_box, address

def get_account_info(text_to_analyze):
    try:
        account_regex = re.findall(r"P\.O\.\s+Number\s+.+of\s+([\w]+)\s+([\-\d\w]+)\s+([\-\d\w]+)", text_to_analyze, re.MULTILINE)
        account_regex = list(account_regex)[0]
        month = account_regex[0]
        account = account_regex[1]
        po_number = account_regex[2]
    except:
        month = None
        account = None
        po_number = None
    return month, account, po_number

def get_info_name(text_to_analyze):
  name_regex = re.search(r"Invoice Date\s+Due\s+Date\s+Invoice\s+No\.\s+[\d\/\s]+[\d\/]+\s+([^\n]+)\s+([\d\w\s\,]+)\n+", text_to_analyze,re.DOTALL)
  try:
    name = name_regex.group(1)
    address = name_regex.group(2)
  except:
    name = None
    address = None
  return name, address

def get_value_currency(text_to_analyze):
  value_regex = re.search(r"Total\s*([\w]+)\s*([\$\d\.\,]+)", text_to_analyze, re.DOTALL)
  try:
    value = value_regex.group(2)
    currency = value_regex.group(1)
  except:
    value = None
    currency = None
  return value, currency

def get_bank_info(text_to_analyze):
  bank_regex = re.search(r"to\:\s+([\d\w\,\.\s]+)\s+.+\s+Payment:\s+([\w\s\,\.]+)\s+Account\s+No\.\:([\d]+)\s+ACH\s*Routing\:([\d]+)\s+Wire\s+Routing\:\s*([\d]+)\s+SWIFT\:([\d\w]+)", text_to_analyze, re.DOTALL)
  try:
    payment_place = bank_regex.group(1)
    bank = bank_regex.group(2)
    account = bank_regex.group(3)
    ach_routing = bank_regex.group(4)
    wire_routing = bank_regex.group(5)
    swift = bank_regex.group(6)
  except:
    payment_place = None
    bank = None
    account = None
    ach_routing = None
    wire_routing = None
    swift = None
  return payment_place,bank, account, ach_routing, wire_routing, swift

def get_deparment_info(text_to_analyze):
  deparment_regex = re.search(r"Phone\s*No\.\s*Fax\s*No\.\s*E\-Mail\s*Web\s*Site\s*([\s\w\d\.\@]+)\n", text_to_analyze, re.DOTALL)
  try:
    deparment = deparment_regex.group(1)
    deparment = deparment.split('\t')
    deparment = list(filter(None, deparment))
    phone = deparment[0]
    fax = deparment[1]
    email = deparment[2]
    website = deparment[3]
  except:
    phone = None
    fax = None
    email = None
    website = None
  return phone, fax, email, website

def json_generation(text_to_analyze):
  JSON_file = {}
  JSON_file['invoice_info'] = get_invoice_info(text_to_analyze)
  JSON_file['pages'] = get_pages(text_to_analyze)
  JSON_file['month'], JSON_file['account'],JSON_file['po_number'] = get_account_info(text_to_analyze)
  JSON_file['invoice_ammounts'] = get_invoice_ammounts(text_to_analyze)
  JSON_file['po_box'], JSON_file['po_box_address'] = get_po_box_info(text_to_analyze)
  JSON_file['user_name'], JSON_file['user_address'] = get_info_name(text_to_analyze)
  JSON_file['value'], JSON_file['currency'] = get_value_currency(text_to_analyze)
  JSON_file['place_of_payment'],JSON_file['bank_name'],JSON_file['account_number'],JSON_file['ACH_routing'],JSON_file['wire_routing'],JSON_file['swift'] = get_bank_info(text_to_analyze)
  JSON_file['deparment_phone'],JSON_file['deparment_fax'], JSON_file['deparment_email'],JSON_file['deparment_website'] = get_deparment_info(text_to_analyze)
  return JSON_file

                                                       