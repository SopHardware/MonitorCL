#Aprobaciones

--Para saber el estatus de Envío de GAINS A RÉPLICA (3.66)

SELECT COUNT(DISTINCT(IdRegistro)) FROM PO_Traspasos WHERE ExportStatus = 0

--Para saber el estatus de envío de Réplica a Epicor (3.83)

SELECT * FROM ReplicateData (NOLOCK) 
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
ORDER BY CreateAt DESC

# Cola de Material
-- Para saber el estatus del Envío del CL a RÉPLICA (192.168.20.19)

SELECT 
    COUNT(DISTINCT(E.FolioFecha))
FROM BXCJ_ConsolidadoEncabezadoCLON E (NOLOCK)
LEFT JOIN bxcj_EmpaqueMasterDetalle MD (NOLOCK) ON MD.FolioSegCont = E.FolioFecha
LEFT JOIN bxcj_Embarque EM (NOLOCK) ON (EM.FOLIOEMBARCADO = E.FOLIOFECHA or MD.FOLIOFECHA = EM.FOLIOEMBARCADO)
LEFT JOIN EmbarqueEncabezado EE (nolock) ON EE.EE_FolioArmadoRuta = EM.Ruta
WHERE CONVERT(NVARCHAR,E.FECHA,23) >= '2026-01-03' and EE_Estatus = 'FINALIZADO' and (E.ExportStatus = 0)
and CONVERT(NVARCHAR,EE.EE_FechaAutoriza,23) < CONVERT(NVARCHAR,GETDATE(),23)

-- Envio de Replica a Epicor
SELECT COUNT(*) FROM ReplicateData(NOLOCK)
WHERE DocumentVersion = 'V4' AND DocumentName = 'CreateOTMtlQueue' AND ReplicationDataStatus = 0

-- Estatus de reprocesamiento
SELECT COUNT(*) FROM ICE.UD24 WHERE Company = '5001' AND  Key1 = 'MaterialQueueGains' AND CheckBox02 = 1 AND Character01 <> 'Finalizado'

# Embarque:
-- Envio de CL a Replica (192.168.20.19)
SELECT 
    COUNT(DISTINCT(E.FolioFecha))
FROM BXCJ_ConsolidadoEncabezadoCLON E (NOLOCK)
LEFT JOIN bxcj_EmpaqueMasterDetalle MD (NOLOCK) ON MD.FolioSegCont = E.FolioFecha
LEFT JOIN bxcj_Embarque EM (NOLOCK) ON (EM.FOLIOEMBARCADO = E.FOLIOFECHA or MD.FOLIOFECHA = EM.FOLIOEMBARCADO)
LEFT JOIN EmbarqueEncabezado EE (nolock) ON EE.EE_FolioArmadoRuta = EM.Ruta
WHERE CONVERT(NVARCHAR,E.FECHA,23) >= '2026-01-03' and EE_Estatus = 'FINALIZADO' and (E.ExportStatus = 0)
and CONVERT(NVARCHAR,EE.EE_FechaAutoriza,23) < CONVERT(NVARCHAR,GETDATE(),23)

-- Envio de Replica a CL
SELECT COUNT(*) FROM ReplicateData(NOLOCK)
WHERE  DocumentVersion = 'V4' AND DocumentName = 'OrdenTransferenciaEnviarOrdenTransferencia' AND ReplicationDataStatus = 0

-- Estatus de reprocesamiento
SELECT COUNT(*) FROM ICE.UD24 WHERE Company = '5001' AND Key1 = 'ShipCLOT' AND CheckBox02 = 1 AND Character01 <> 'Shipped'
