SELECT COUNT(*) FROM ReplicateData(NOLOCK)
WHERE DocumentVersion = 'V4' 
  AND DocumentName = 'OrdenTransferenciaEnviarOrdenTransferencia' 
  AND ReplicationDataStatus = 0