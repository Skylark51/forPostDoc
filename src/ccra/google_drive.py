from __future__ import annotations
from pathlib import Path
from typing import Any

SCOPES=[
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

class GoogleDriveUnavailable(RuntimeError): pass

class GoogleDriveClient:
    def __init__(self, credentials_path: Path, token_path: Path):
        self.credentials_path=Path(credentials_path); self.token_path=Path(token_path); self._drive=None; self._sheets=None
    def connect(self) -> None:
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError as exc: raise GoogleDriveUnavailable("Install: pip install -e .[google]") from exc
        creds=None
        if self.token_path.exists():
            try: creds=Credentials.from_authorized_user_file(str(self.token_path),SCOPES)
            except Exception: creds=None
        if creds and not creds.has_scopes(SCOPES): creds=None
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        if not creds or not creds.valid:
            if not self.credentials_path.exists(): raise GoogleDriveUnavailable(f"OAuth desktop credentials not found: {self.credentials_path}")
            creds=InstalledAppFlow.from_client_secrets_file(str(self.credentials_path),SCOPES).run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True,exist_ok=True); self.token_path.write_text(creds.to_json(),encoding="utf-8")
        self._drive=build("drive","v3",credentials=creds,cache_discovery=False); self._sheets=build("sheets","v4",credentials=creds,cache_discovery=False)
    def _require(self):
        if self._drive is None or self._sheets is None: raise GoogleDriveUnavailable("Google Drive is not connected.")
    def folder_items(self, folder_id: str) -> list[dict[str,Any]]:
        self._require(); q=f"'{folder_id}' in parents and trashed=false"; items=[]; token=None
        while True:
            res=self._drive.files().list(q=q,fields="nextPageToken,files(id,name,mimeType,modifiedTime,webViewLink)",pageSize=100,pageToken=token,orderBy="folder,name").execute(); items.extend(res.get("files",[])); token=res.get("nextPageToken")
            if not token: return items
    def spreadsheet_metadata(self, spreadsheet_id: str) -> dict[str,Any]:
        self._require(); return self._sheets.spreadsheets().get(spreadsheetId=spreadsheet_id,fields="spreadsheetId,properties.title,sheets.properties").execute()
    def sheet_values(self, spreadsheet_id: str, a1_range: str):
        self._require(); return self._sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id,range=a1_range).execute().get("values",[])
    def si_json_files(self, folder_id: str) -> list[dict[str,Any]]:
        self._require(); q=f"'{folder_id}' in parents and trashed=false and name contains 'CCRA-SI-'"; items=[]; token=None
        while True:
            res=self._drive.files().list(q=q,fields="nextPageToken,files(id,name,mimeType,modifiedTime)",pageSize=100,pageToken=token,orderBy="modifiedTime desc").execute(); items.extend(res.get("files",[])); token=res.get("nextPageToken")
            if not token: return items
    def upload_text(self, folder_id: str, name: str, content: str, *, file_id: str|None=None, mime_type: str="application/json") -> str:
        self._require()
        try: from googleapiclient.http import MediaInMemoryUpload
        except ImportError as exc: raise GoogleDriveUnavailable("Install: pip install -e .[google]") from exc
        media=MediaInMemoryUpload(content.encode("utf-8"),mimetype=mime_type,resumable=False)
        if file_id:
            result=self._drive.files().update(fileId=file_id,media_body=media,fields="id").execute()
        else:
            result=self._drive.files().create(body={"name":name,"mimeType":mime_type,"parents":[folder_id]},media_body=media,fields="id").execute()
        return result["id"]
    def download_text(self, file_id: str) -> str:
        self._require(); data=self._drive.files().get_media(fileId=file_id).execute()
        if isinstance(data,bytes): return data.decode("utf-8")
        return str(data)
