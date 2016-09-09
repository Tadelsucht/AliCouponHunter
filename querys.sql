SELECT (CheapestItemPrice - Discount), CheapestItem, Keywords, Shop, URL AS 'Price' 
FROM processed 
WHERE Discount IS NOT NULL 
	AND  BestCouponDifference < 1
ORDER BY (CheapestItemPrice - Discount)  ASC


SELECT * 
FROM processed
WHERE CheapestItem LIKE "%Zusätzlich%"
	OR CheapestItem LIKE "%Gebühr%"
	OR CheapestItem LIKE "%preis unterschied%"
	OR CheapestItem LIKE "%Preisunterschied%"
	OR (CheapestItem LIKE "%Versandkosten%" AND CheapestItem NOT LIKE "%Versandkosten frei%")
	

SELECT * 
FROM processed
WHERE  CheapestItem LIKE "%Versandkosten%" 
	AND CheapestItem NOT LIKE "%Versandkostenfrei%"