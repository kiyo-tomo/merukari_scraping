# Python でメルカリとラクマから最安値をスクレイピングで取得する

日経ソフトウエアの記事で面白そうな事をやっていたので試してみましょう。

## 環境
私の実行環境はMacのため、多少WindowsやLinuxで異なることがあるかも知れません。

- Python3.XX
- Selenium


## 環境準備

### Selenium 環境準備
Anacondaを利用します。
Anaconda Navigator から、Environments から "Selenium" を選択しApplyします。

当然、各自の環境にpipでインストールしてもOKです。

### Chrome Driver

http://chromedriver.chromium.org/downloads  

こちらから、SeleniumからChromeを制御するドライバを用意します。
各自の環境に合ったものを選択します。
自身のChromeのバージョンは ヘルプ -> Google Chromeについて から確認できる。

ダウンロードして解答したら、 chromedriver.exe をプログラムと同じディレクトリに配置する。


## 概要

メルカリで商品を検索し、最安値を取得してみよう。

### メルカリの検索用URLを準備する

メルカリは、以下の条件で商品を検索する際のURLは

- keyword1 and keyword2	で検索
- keyword3 and keyword4 を除外
- 販売ステータスは販売中
- 値段の安い順にソート

```
https://www.mercari.com/jp/search/?sort_order=price_asc&keyword={
keyword1 + keyword2 +-keyword3 +- keyword4
}&status_on_sale=1
```

の様になる。

### DOM解析

実際にメルカリで検索してみよう。
F12を押すことでChromeのディベロッパーツールを表示できる。
値段が表示されるのは

```
    <div class="items-box-price font-5">¥ 500</div>
 		 <div class="font-2">
			<i class="icon-like-border"></i>
      		  <span>1</span>
  		</div>
	</div>
```

この div class="items-box-price 要素となる。また、最安値が欲しい場合は予めソートしておくことで、最安値が格納されるのはこの要素の最初の要素という事になる。

つまり、最安値を取得する場合はこのDOMをスクレイピングしてくればよい。

## Code

ディレクトリ構成

```
$ tree -L 1
.
├── chromedriver
├── data.csv
├── scraping.py
└── venv

```


```Python:scraping.py
import urllib
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# 検索用URL。検索パラメータ部分は{}
URL_MERCARI = 'https://www.mercari.com/jp/search/?sort_order=price_asc&keyword={}&status_on_sale=1' # メルカリ

# 最安値の要素取得用セレクタ
SELECTOR_MERCARI = '.items-box-price' # メルカリ

CAT_CHAR = ' ' # AND検索キーワード連結用文字
NOT_CHAR = '-' # NOT検索キーワードの冒頭に付与する文字。

# 検索キーワード
keywords_all = [
    {
        'and': ['Canon', 'EOS1N'],
        'not': ['説明書', 'スイッチ', 'アイカップ',  '互換品', '方眼スクリーン']
    },
]


def get_min_price(browser, base_url, query_params, selector):
    """指定したキーワードの商品の最安値を取得
    :param browser: ブラウザ
    :param base_url: 検索用URL
    :param query_params: 連結したキーワード
    :param selector: 価格の要素のセレクタ
    :return: 最安値の文字列
    """
    # 取得した価格内の余計な文字削除用辞書
    dic = str.maketrans({
        '\\': '',
        '￥': '',
        ',': '',
        ' ': '',
        '¥': '',
    })

    # キーワードをエンコードし、URLに埋め込んでアクセス
    url = base_url.format(urllib.parse.quote(query_params))

    try:
        # 最安値の要素を取得して返す
        browser.get(url)
        elm_min = browser.find_element_by_css_selector(selector)
    except NoSuchElementException as e:
        print(f'指定した要素が見つかりませんでした:{e.args}')
    except TimeoutException as e:
        print(f'読み込みがタイムアウトしました:{e.args}')

    return elm_min.text.translate(dic)  # 余計な文字を削除してから返す


# ブラウザ準備
browser = webdriver.Chrome('./chromedriver')
browser.set_page_load_timeout(30) # 読み込みタイムアウト設定


# 商品ごとに最安値を取得
for keywords in keywords_all:
    # 商品ごとの検索キーワードを連結
    query_params_and = CAT_CHAR.join(keywords['and']) # AND用
    query_params_not = CAT_CHAR.join([NOT_CHAR + kw for kw in keywords['not']]) # NOT用

    # メルカリの最安値を取得し、保存用リストに追加。
    query_params_mercari = query_params_and + CAT_CHAR + query_params_not
    min_price = get_min_price(browser, URL_MERCARI, query_params_mercari, SELECTOR_MERCARI)
    print('%s の最安値は %s' % (keywords, min_price))

browser.quit() # ブラウザ終了

```

実行すると

```
$ python scraping.py 
{'and': ['Canon', 'EOS1N'], 'not': ['説明書', 'スイッチ', 'アイカップ', '互換品', '方眼スクリーン']} の最安値は 3980
```

と表示される。


## 最後に

日経ソフトウエア2019/7月号では、更にラクマの最安値を取得し、これをCSVに出力し、Jupiterを利用して最安値の遷移を解析する特集が組まれていた。
これを利用すればカカクコムのフリマアプリ版の様なWebサービスをリリース出来るかもしれない。
興味深い記事だったので、自身の勉強がてら纏めさせて貰った。