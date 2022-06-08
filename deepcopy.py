from __future__ import print_function

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/drive']


def get_arg_parser():
    """Creates argument parser object"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('source', metavar='S', type=int, nargs='+',
                        help='UID of the source directory')
    parser.add_argument('destination', metavar='D', type=int, nargs='+',
                        help='UID of the destination directory')
    parser.add_argument('--token', default='./token.json',
                        help='path to token.json generated automatically in the first run (default: "./token.json") []')
    parser.add_argument('--cred', default='./credentials.json',
                        help='path to credentials.json obtained from GCP Console (default: "./credentials.json") [FMI see bit.ly/credjson]')

    return parser


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    # parse cli args
    parser = get_arg_parser()
    parser.parse_args(os.argv)

    token_json_path = parser.token
    root_src_dir = parser.source
    root_dst_dir = parser.dest
    cred_json_path = parser.cred

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_json_path):
        creds = Credentials.from_authorized_user_file(token_json_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_json_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_json_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        all_copied = []

        all_errors = []

        kwargs = {
            "supportsAllDrives": True,
            "supportsTeamDrives": True
        }

        # blacklisting apps whose content that should not be copied
        mimeBlacklist = {
            'application/vnd.google-apps.drive-sdk.1062019541050',
        }

        def list_dir_page(dir_id, write_to, token=None):
            results = service.files().list(pageToken=token, pageSize=1000, q=f"'{dir_id}' in parents", includeItemsFromAllDrives=True, **kwargs).execute()
            items = results.get('files', [])
            write_to.extend(items)
            return results.get('nextPageToken', None)

        def list_dir(dir_, prefix=''):
            dir_id = dir_['id']
            out = []
            token = list_dir_page(dir_id, write_to=out)
            while token:
                token = list_dir_page(dir_id, write_to=out)
            print(f"{prefix} {len(out)} items listed in {dir_['name']}")
            return out

        def copy_file(file_, dst_dir, file_prefix="test__"):
            try:
                newfile = {'name': file_prefix + file_['name'], 'parents': [dst_dir['id']]}
                res = service.files().copy(fileId=file_['id'], body=newfile, **kwargs).execute()
                all_copied.append(res)
            except HttpError as e:
                all_errors.append((e, file_, dst_dir))


        src_dir = service.files().get(fileId=root_src_dir, **kwargs).execute()
        dst_dir = service.files().get(fileId=root_dst_dir, **kwargs).execute()

        def iter_copy(src_dir, dst_dir, prefix=''):

            print(f'{prefix} duplicate {src_dir["name"]} at {dst_dir["name"]}')
            out = list_dir(src_dir, prefix=prefix)

            while True:
                extra = []
                for f in out:
                    if f['mimeType'] in mimeBlacklist:
                        print(f'{prefix + "##"} ignoring blacklisted {f["name"]} ({f["mimeType"]}) in {dst_dir["name"]}')
                    elif f['mimeType'] == "application/vnd.google-apps.folder":

                        print(f'{prefix + "##"} mkdir {f["name"]} in {dst_dir["name"]}')
                        body = {
                            "name": f["name"],
                            "mimeType": f["mimeType"],
                            "parents": [dst_dir["id"]]
                        }
                        newdir = service.files().create(body=body, **kwargs).execute()
                        iter_copy(f, newdir, prefix=prefix + '##')

                    elif f['mimeType'] == "application/vnd.google-apps.shortcut":
                        print(f'{prefix + "##"} resolve {src_dir["name"]}/{f["name"]}')
                        resolve = service.files().get(fileId=f['id'], fields='*', **kwargs).execute()['shortcutDetails']
                        extra.append({
                            'name': f['name'],
                            'id': resolve['targetId'],
                            'mimeType': resolve['targetMimeType']
                        })

                    else:
                        print(f'{prefix + "##"} copying {src_dir["name"]}/{f["name"]} to {dst_dir["name"]}/')
                        copy_file(f, dst_dir, file_prefix='test__F3CD363F__v2__')

                if not extra:
                    break
                else:
                    print(f'{prefix} duplicate symlinks of {src_dir["name"]} in {dst_dir["name"]}')
                    out = extra
        
        iter_copy(src_dir, dst_dir)

        print('copied', len(all_copied), 'files')

        from IPython import embed
        embed()

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()

