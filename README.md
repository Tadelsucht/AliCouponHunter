# AliCouponHunter
Aliexpress coupon search | Find cheapest item and show possible coupon freebies.

## Run
```sh
python2.7 main.py
```
## Result
### Analyse
Use [DB Browser for SQLite](http://sqlitebrowser.org/) and the querys.txt.

### Example
```sh
ID   Shop   Keywords   URL Discount   MinimumPurchase   CouponDifference   CheapestItem   CheapestItemPrice   AddedOrUpdated
...
"2025014"	"carll"	""	"http://aliexpress.com/store/2025014"	"3.0"	"15.0"	"12.0"	"ad16 6 dark flower Hard Black Case Cover for Samsung Galaxy s3 s4 s5 mini s6 s7 edge plus "	"1.99"	"2016-09-15 05:18:58.265162"
"622711"	"Shenzhen B VESR Electronic Tech CO. LTD"	""	"http://aliexpress.com/store/622711"	"2.0"	"25.0"	"23.0"	"Luxury Ultra Thin Clear Rubber Plating Electroplating TPU Soft Cover Case For iPhone 6 6S 6 Plus 5 5S SE"	"1.99"	"2016-09-15 05:23:29.253632"
"2170050"	"EITOR Electric Store"	""	"http://aliexpress.com/store/2170050"	"1.0"	"29.0"	"28.0"	"2016 New Hot Black Frame Red"	"1.99"	"2016-09-15 06:42:17.086296"
"2342049"	"7-24 Online"	""	"http://aliexpress.com/store/2342049"	"2.0"	"17.0"	"15.0"	"Creative PC Computer Gamer Gaming Mice Mouse Pad 20"	"1.99"	"2016-09-15 07:59:57.701420"
"632018"	"milk tien&#39;s store"	""	"http://aliexpress.com/store/632018"	"7.0"	"137.0"	"130.0"	"Owl Pattern National Cute Case For Apple iPod Touch 5 Hard Soft Rubber Hybrid Armor Owls Case Cover Screen Portector"	"1.99"	"2016-09-15 08:01:10.038077"
"423587"	"Best Lady Jewelry Store"	",Best Lady Jewelry Store,-Onlineshop"	"http://de.aliexpress.com/store/423587"	"2.0"	"32.0"	"30.0"	"Ladyfirst 2016 New Big Strass Luxus Aussage Geometrischen Kristall Vintage Perlen Ohrstecker Für Frauen Edelstein Schmuck 3388"	"2.39"	"2016-09-10 07:31:14.009000"
...
```

## Requirements
- Python2.7
- BeautifulSoup

## Configuration
### main.py
All capitalized variables under "Config".

### shop_search_item_phrases.txt
List of item phrases for shop search.

### already_searched_shop_search_item_phrases.txt
List already searched phrases.

### forbidden_item_phrases.txt
Protect against "extra shipping charge"-products.
