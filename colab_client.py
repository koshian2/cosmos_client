import requests
import shutil
import subprocess

def save(settings):
    """COSMOSに訓練結果を保存
    
    Arguments:
        settings {dict} -- 設置値のdict。output_dir, token, endpoint, dataset, codenameが必須
    """

    assert settings.keys() >= {"output_dir", "token", "endpoint", "dataset", "codename"}
    # 説明があれば書き込む
    if "description" in settings.keys():
        with open(f"{settings['output_dir']}/description.txt", "w") as fp:
            fp.write(settings["description"])
    # TODO: 自身のソースファイルを追加
    # tarファイル化
    subprocess.run(f"tar -cvf cosmos_save.tar {settings['output_dir']}", shell=True).check_returncode()
    # バイナリ化
    files = {}
    with open("cosmos_save.tar", "rb") as fp:
        files["tar"] = ("cosmos_save.tar", fp.read())
    # ヘッダー
    param = {"token": settings["token"]}
    # 送信
    url = f"{settings['endpoint']}/save/{settings['dataset']}/{settings['codename']}"
    res = requests.post(url, files=files, data=param)
    # 結果を表示
    print("--- Send to cosmos --")
    print(res)
    print(res.text)

def load(settings, rev=None):
    """COSMOSから訓練結果を取得
    
    Arguments:
        settings {dict} -- 設定値のdict。output_dir, token, endpoint, dataset, codenameが必須
    
    Keyword Arguments:
        rev {int} -- revisionの指定。Noneなら最新のを取得 (default: {None})
    """
    assert settings.keys() >= {"output_dir", "token", "endpoint", "dataset", "codename"}
    # parameters
    params = {
        "token": settings["token"],
    }
    if rev is not None:
        params["rev"] = rev
    url = f"{settings['endpoint']}/load/{settings['dataset']}/{settings['codename']}"
    res = requests.get(url, params=params, stream=True)
    if res.status_code == 200:
        with open("cosmos_load.tar", "wb") as fp:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, fp)
            
        # extract tar
        subprocess.run(f"tar -xvf cosmos_load.tar -C {settings['output_dir']} --strip-components=1", shell=True).check_returncode()

    print("--- Load from cosmos --")
    print(res)
    print(res.text)
