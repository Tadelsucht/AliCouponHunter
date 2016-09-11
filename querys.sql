SELECT ID, Shop, Keywords, URL, Discount, MinimumPurchase, CheapestItem, CheapestItemPrice
FROM processed 
WHERE Discount IS NOT NULL 
	AND  BestCouponDifference < 1
ORDER BY Discount DESC, CheapestItemPrice ASC


SELECT (CheapestItemPrice - Discount) AS 'Price', MinimumPurchase, CheapestItem, Keywords, Shop, URL, ID AS 'Price' 
FROM processed 
WHERE Discount IS NOT NULL 
	AND  BestCouponDifference < 1
ORDER BY (CheapestItemPrice - Discount)  ASC
	

DELETE FROM processed WHERE ID = 1382496