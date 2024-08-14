import pandas as pd

data = {
    "title": [
        "Футбольный мяч - Ekip Sport",
        "Футбольный мяч - Wildberries",
        "Футбольный мяч - Sportmaster"
    ],
    "url": [
        "https://ekip-sport.ru/myachi/myachi-futbolnye/",
        "https://www.wildberries.ru/catalog/sport/vidy-sporta/futbol/myachi",
        "https://www.sportmaster.ru/catalog/vidy_sporta_/futbol/myachi/?utm_referrer=https%3A%2F%2Fwww.google.ru%2F"
    ],
    "xpath": [
        '//div[@class="products-item__price"]/span[1]/text()',
        '//ins[@class="price__lower-price wallet-price"]/text()',
        '//span[@class="sm-amount__value" and @data-selenium="amount"]/text()'
    ]
}

df = pd.DataFrame(data)

df.to_excel("Balls_Shop.xlsx", index=False)

print("Success")