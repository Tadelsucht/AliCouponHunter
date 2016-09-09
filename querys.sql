SELECT (CheapestItemPrice - Discount), CheapestItem, Keywords, Shop, URL AS 'Price' 
FROM processed 
WHERE Discount IS NOT NULL 
	AND  BestCouponDifference < 1
ORDER BY (CheapestItemPrice - Discount)  ASC


DELETE
--SELECT *
FROM processed
WHERE CheapestItem LIKE "%Zusätzlich%"
	OR CheapestItem LIKE "%Gebühr%"
	OR CheapestItem LIKE "%preis unterschied%"
	OR CheapestItem LIKE "%Preisunterschied%"
	OR CheapestItem LIKE "%Verschiffen nur%"
	OR CheapestItem LIKE "%Porto%"
	OR CheapestItem LIKE "%Bestellung%"
	OR CheapestItem LIKE "%Zurückzahlen%"
	OR CheapestItem LIKE "%geld zurück%"
	OR CheapestItem LIKE "%Zahlung Zurück%"
	OR CheapestItem LIKE "%konten%"
	OR CheapestItem LIKE "%Anzahlung%"
	OR CheapestItem LIKE "%Hinzufügen%"
	OR CheapestItem LIKE "%differenz%"
	OR CheapestItem LIKE "%transaktion%"
	OR (CheapestItem LIKE "%Versandkosten%" AND CheapestItem NOT LIKE "%Versandkosten frei%")
	

SELECT * 
FROM processed
WHERE  CheapestItem LIKE "%Versandkosten%" 
	AND CheapestItem NOT LIKE "%Versandkostenfrei%"