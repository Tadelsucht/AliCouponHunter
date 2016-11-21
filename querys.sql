SELECT ID, Shop, Keywords, URL, Discount, MinimumPurchase, CheapestItem, CheapestItemPrice
FROM processed 
WHERE Discount IS NOT NULL 
	AND BestCouponDifference < 1
	AND CheapestItemPrice IS NOT NULL
	--AND AddedOrUpdated > DATE(DATE('now'), '-7 day')
ORDER BY Discount DESC, CheapestItemPrice ASC


SELECT (CheapestItemPrice - Discount) AS 'Price', MinimumPurchase, CheapestItem, Keywords, Shop, URL, ID
FROM processed 
WHERE Discount IS NOT NULL 
	AND  BestCouponDifference < 1
	AND Price IS NOT NULL
	--AND AddedOrUpdated > DATE(DATE('now'), '-7 day')
ORDER BY (CheapestItemPrice - Discount)  ASC


SELECT ID, Shop, Keywords, URL, CheapestItem, CheapestItemPrice
FROM processed 
WHERE CheapestItemPrice IS NOT NULL 
ORDER BY CheapestItemPrice ASC


SELECT 
	1.0 *
	(
		SELECT COUNT(*)
		FROM processed 
		WHERE Discount IS NOT NULL 
	) / (
		SELECT COUNT(*)
		FROM processed 
		WHERE Discount IS NULL 
	)
	* 100 AS 'Percent of shops with coupons';


DELETE FROM processed WHERE ID = 1382496
