import urllib.request
import zipfile

deps = [
    'https://files.pythonhosted.org/packages/6c/69/05837f91dfe42109203ffa3e488214ff86a6d68b2ed6c167da6cdc42349b/werkzeug-3.0.6-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/62/a1/3d680cbfd5f4b8f15abc1d571870c5fc3e594bb582bc3b64ea099db13e56/jinja2-3.1.6-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/04/96/92447566d16df59b2a776c0fb82dbc4d9e07cd95062562af01e408583fc4/itsdangerous-2.2.0-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/7e/d4/7ebdbd03970677812aac39c869717059dbb71a4cfc033ca6e5221787892c/click-8.1.8-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/bb/2a/10164ed1f31196a2f7f3799368a821765c62851ead0e630ab52b8e14b4d0/blinker-1.8.2-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/a0/d9/a1e041c5e7caa9a05c925f4bdbdfb7f006d1f74996af53467bc394c97be7/importlib_metadata-8.5.0-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/62/8b/5ba542fa83c90e09eac972fc9baca7a88e7e7ca4b221a89251954019308b/zipp-3.20.2-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/92/21/357205f03514a49b293e214ac39de01fadd0970a6e05e4bf1ddd0ffd0881/MarkupSafe-2.1.5-cp38-cp38-win_amd64.whl',
    'https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl',
    'https://files.pythonhosted.org/packages/17/95/77624cff50d08fedfe45a2cd1e43736587c7a04ecabfc265d8429d30f08b/sqlalchemy-2.0.51-cp38-cp38-win_amd64.whl',
    'https://files.pythonhosted.org/packages/1d/6a/89963a5c6ecf166e8be29e0d1bf6806051ee8fe6c82e232842e3aeac9204/flask_sqlalchemy-3.1.1-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/59/f5/67e9cc5c2036f58115f9fe0f00d203cf6780c3ff8ae0e705e7a9d9e8ff9e/Flask_Login-0.6.3-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/8b/72/af9a3a3dbcf7463223c089984b8dd4f1547593819e24d57d9dc5873e04fe/Flask_Bcrypt-1.0.1-py3-none-any.whl',
    'https://files.pythonhosted.org/packages/9e/11/aa3e000827a90285dc0485b4c01efb5359342d70729042c850a5e9194954/bcrypt-4.0.1-cp38-cp38-win_amd64.whl'
]

for url in deps:
    fname = url.split('/')[-1]
    print('Downloading ' + fname + '...')
    urllib.request.urlretrieve(url, fname)
    print('Extracting ' + fname + '...')
    z = zipfile.ZipFile(fname)
    z.extractall('lib')
    z.close()
    print('Done ' + fname)

print('All dependencies downloaded and extracted!')
