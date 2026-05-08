SELECT COUNT(*) FROM ReplicateData(NOLOCK)
WHERE DocumentVersion = 'V4' 
  AND DocumentName = 'CreateOTMtlQueue' 
  AND ReplicationDataStatus = 0