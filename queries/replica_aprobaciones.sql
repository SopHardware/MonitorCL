SELECT COUNT(*) FROM ReplicateData (NOLOCK) 
WHERE DocumentName = 'TransferOrderGains' 
  AND CreateAt >= CAST(
      CONCAT(
          CAST(
              CASE 
                  WHEN DATEPART(HOUR, GETDATE()) < 5 THEN DATEADD(DAY, -1, GETDATE())
                  ELSE GETDATE()
              END AS DATE
          ), 
          ' 19:00:05.540'
      ) AS DATETIME
  )