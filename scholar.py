from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scholarly import scholarly
from json import dumps, loads


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = ""
SAMPLE_RANGE_NAME = "P1!A4:E999"


def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )

        search_query = scholarly.search_author("Arthur Caye")
        author = scholarly.fill(next(search_query))
        # resultList = result["values"]

        values = []

        for pub in author["publications"]:
            row = [
                pub["bib"]["title"],
                pub["bib"]["citation"],
                pub["bib"].get("pub_year", "N/A"),
                pub["num_citations"],
                f"""https://scholar.google.com/citations?view_op=view_citation&hl=en&user={author["scholar_id"]}&citation_for_view={pub["author_pub_id"]}""",
            ]
            values.append(row)

        result = (
            sheet.values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range="A4",
                valueInputOption="USER_ENTERED",
                body={"values": values},
            )
            .execute()
        )

        print(result)

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
