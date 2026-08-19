-- ============================================================
-- SQL Practice Queries — Core Data Analytics Foundation
-- Bluestock Fintech Internship Prerequisite
-- ============================================================

-- 1. Total Revenue and Units Sold per Product Category
SELECT 
    Product,
    SUM(Units_Sold) AS Total_Units,
    SUM(Total_Revenue) AS Total_Revenue,
    ROUND(AVG(Customer_Rating), 2) AS Avg_Rating
FROM sales_data
GROUP BY Product
ORDER BY Total_Revenue DESC;

-- 2. Regional Performance with HAVING Filter
SELECT 
    Region,
    COUNT(Order_ID) AS Total_Orders,
    SUM(Total_Revenue) AS Total_Revenue
FROM sales_data
GROUP BY Region
HAVING SUM(Total_Revenue) > 100000
ORDER BY Total_Revenue DESC;

-- 3. Monthly Sales Trend Analysis
SELECT 
    strftime('%Y-%m', Order_Date) AS Sales_Month,
    COUNT(Order_ID) AS Order_Count,
    SUM(Total_Revenue) AS Monthly_Revenue
FROM sales_data
GROUP BY Sales_Month
ORDER BY Sales_Month ASC;

-- 4. Window Functions — Running Total of Revenue per Region
SELECT 
    Order_ID,
    Order_Date,
    Region,
    Product,
    Total_Revenue,
    SUM(Total_Revenue) OVER (PARTITION BY Region ORDER BY Order_Date) AS Running_Regional_Revenue,
    RANK() OVER (PARTITION BY Region ORDER BY Total_Revenue DESC) AS Revenue_Rank
FROM sales_data;

-- 5. Top Performing Products Subquery
SELECT 
    Order_ID, Product, Region, Total_Revenue
FROM sales_data
WHERE Total_Revenue > (
    SELECT AVG(Total_Revenue) FROM sales_data
)
ORDER BY Total_Revenue DESC;
