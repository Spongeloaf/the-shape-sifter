def get_google_drive_path():
    """
    Get Google Drive path on windows machines.
    :return: str
    """
    # this code written by /u/Vassilis Papanikolaou from this post:
    # https://stackoverflow.com/a/53430229/10236951

    import sqlite3
    import os

    db_path = (os.getenv('LOCALAPPDATA')+'\\Google\\Drive\\user_default\\sync_config.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * from data where entry_key = 'local_sync_root_path'")
    res = cursor.fetchone()
    path = res[2][4:]
    db.close()

    return path


if __name__ == '__main__':
    print(get_google_drive_path())