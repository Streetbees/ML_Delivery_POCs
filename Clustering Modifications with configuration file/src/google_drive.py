import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


def set_gsheet_tab(data, sheet, tab, cred_file, clear=True, **kwargs):
    # use credentials (creds) to create a client to interact with the Google Drive API
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    client = gspread.authorize(creds)
    sheet_hook = client.open(sheet)

    try:
        tab_hook = sheet_hook.worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        print("Creating tab")
        sheet_hook.add_worksheet(title=tab, rows=data.shape[0], cols=data.shape[1])
        tab_hook = sheet_hook.worksheet(tab)

    if clear:
        tab_hook.clear()

    try:
        set_with_dataframe(dataframe=data, worksheet=tab_hook, **kwargs)
    except gspread.exceptions.SpreadsheetNotFound as e:
        raise AssertionError("Make sure the sheet properly named and is shared with the client_email appearing in your "
                             "authentication JSON")


def get_gsheet_tab(sheet, tab, cred_file, **kwargs):
    # use credentials (creds) to create a client to interact with the Google Drive API
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    client = gspread.authorize(creds)
    return get_as_dataframe(client.open(sheet).worksheet(tab), **kwargs)


def list_gsheet_tab(sheet, cred_file):
    # use credentials (creds) to create a client to interact with the Google Drive API
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(sheet)
    return spreadsheet.worksheets()
