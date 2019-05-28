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
