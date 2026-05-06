-- ============================================================================
-- Migration: Add Performance Indexes
-- Description: Adds indexes for optimal query performance
-- Date: 2025-10-14
-- ============================================================================

-- SERVICE TABLE INDEXES
-- ============================================================================

-- Index for tenant-based searches (most common filter)
CREATE INDEX IF NOT EXISTS idx_service_tenant_id
ON service(tenant_id);

-- Composite index for tenant + module + business_service (duplicate check query)
CREATE INDEX IF NOT EXISTS idx_service_tenant_module_bs
ON service(tenant_id, module, business_service);

-- Composite index for tenant + module (common search filter)
CREATE INDEX IF NOT EXISTS idx_service_tenant_module
ON service(tenant_id, module);

-- Composite index for tenant + business_service (common search filter)
CREATE INDEX IF NOT EXISTS idx_service_tenant_bs
ON service(tenant_id, business_service);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_service_status
ON service(status);

-- Composite index for tenant + status
CREATE INDEX IF NOT EXISTS idx_service_tenant_status
ON service(tenant_id, status);

-- Index for sorting by created_at (default sort)
CREATE INDEX IF NOT EXISTS idx_service_created_at
ON service(created_at DESC);

-- Index for sorting by updated_at
CREATE INDEX IF NOT EXISTS idx_service_updated_at
ON service(updated_at DESC);

-- Composite index for tenant + created_at (optimal for paginated searches)
CREATE INDEX IF NOT EXISTS idx_service_tenant_created
ON service(tenant_id, created_at DESC, id DESC);

-- Partial index for active services (improves performance for common queries)
CREATE INDEX IF NOT EXISTS idx_service_tenant_active
ON service(tenant_id, module, business_service)
WHERE status = 'ACTIVE';


-- SERVICE VERSION CONFIG MAPPING TABLE
-- ============================================================================

-- Create the table if it doesn't exist


-- Composite index for service_code + version lookups (GetServiceVersionConfig query)
CREATE INDEX IF NOT EXISTS idx_svc_version_code_ver
ON service_version_config_mapping(service_code, version);

-- Index for service_code lookups
CREATE INDEX IF NOT EXISTS idx_svc_version_code
ON service_version_config_mapping(service_code);

-- Index for latest version queries
CREATE INDEX IF NOT EXISTS idx_svc_version_code_ver_desc
ON service_version_config_mapping(service_code, version DESC);


-- APPLICATION TABLE INDEXES
-- ============================================================================

-- Index for tenant-based searches (most common filter)
CREATE INDEX IF NOT EXISTS idx_application_tenant_id
ON application(tenant_id);

-- Index for service_code foreign key
CREATE INDEX IF NOT EXISTS idx_application_service_code
ON application(service_code);

-- Composite index for tenant + service_code
CREATE INDEX IF NOT EXISTS idx_application_tenant_service
ON application(tenant_id, service_code);

-- Index for application_number lookups
CREATE INDEX IF NOT EXISTS idx_application_number
ON application(application_number);

-- Composite index for tenant + application_number (fast tenant-scoped lookups)
CREATE INDEX IF NOT EXISTS idx_application_tenant_app_num
ON application(tenant_id, application_number);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_application_status
ON application(status);

-- Composite index for tenant + status
CREATE INDEX IF NOT EXISTS idx_application_tenant_status
ON application(tenant_id, status);

-- Index for workflow_status filtering
CREATE INDEX IF NOT EXISTS idx_application_workflow_status
ON application(workflow_status);

-- Composite index for tenant + workflow_status
CREATE INDEX IF NOT EXISTS idx_application_tenant_workflow_status
ON application(tenant_id, workflow_status);

-- Index for module filtering
CREATE INDEX IF NOT EXISTS idx_application_module
ON application(module);

-- Composite index for tenant + module
CREATE INDEX IF NOT EXISTS idx_application_tenant_module
ON application(tenant_id, module);

-- Index for business_service filtering
CREATE INDEX IF NOT EXISTS idx_application_business_service
ON application(business_service);

-- Composite index for tenant + business_service
CREATE INDEX IF NOT EXISTS idx_application_tenant_bs
ON application(tenant_id, business_service);

-- Composite index for tenant + module + business_service (service type searches)
CREATE INDEX IF NOT EXISTS idx_application_tenant_mod_bs
ON application(tenant_id, module, business_service);

-- Index for createdby filtering
CREATE INDEX IF NOT EXISTS idx_application_createdby
ON application(createdby);

-- Composite index for tenant + createdby
CREATE INDEX IF NOT EXISTS idx_application_tenant_createdby
ON application(tenant_id, createdby);

-- Index for version filtering
CREATE INDEX IF NOT EXISTS idx_application_version
ON application(version);

-- Composite index for tenant + version
CREATE INDEX IF NOT EXISTS idx_application_tenant_version
ON application(tenant_id, version);

-- Index for created_at sorting (default sort column)
CREATE INDEX IF NOT EXISTS idx_application_created_at
ON application(created_at DESC);

-- Index for updated_at sorting
CREATE INDEX IF NOT EXISTS idx_application_updated_at
ON application(updated_at DESC);

-- Composite index for optimal pagination with default sort
CREATE INDEX IF NOT EXISTS idx_application_tenant_created_id
ON application(tenant_id, created_at DESC, id DESC);

-- Composite index for tenant + service_code + created_at (service-specific pagination)
CREATE INDEX IF NOT EXISTS idx_application_tenant_svc_created
ON application(tenant_id, service_code, created_at DESC);

-- Composite index for tenant + status + created_at (status-filtered pagination)
CREATE INDEX IF NOT EXISTS idx_application_tenant_status_created
ON application(tenant_id, status, created_at DESC);

-- Composite index for tenant + module + business_service + created_at
CREATE INDEX IF NOT EXISTS idx_application_tenant_mod_bs_created
ON application(tenant_id, module, business_service, created_at DESC);


-- REFERENCE TABLE INDEXES
-- ============================================================================

-- Index for application_id lookups (JOIN queries)
CREATE INDEX IF NOT EXISTS idx_reference_app_id
ON reference(application_id);

-- Composite index for application + active
CREATE INDEX IF NOT EXISTS idx_reference_app_active
ON reference(application_id, active)
WHERE active = true;

-- Index for reference_no lookups
CREATE INDEX IF NOT EXISTS idx_reference_no
ON reference(reference_no);

-- Index for tenant_id filtering
CREATE INDEX IF NOT EXISTS idx_reference_tenant_id
ON reference(tenant_id);

-- Composite index for tenant + module
CREATE INDEX IF NOT EXISTS idx_reference_tenant_module
ON reference(tenant_id, module);


-- APPLICANT TABLE INDEXES
-- ============================================================================

-- Index for application_id lookups (JOIN queries)
CREATE INDEX IF NOT EXISTS idx_applicant_app_id
ON applicant(application_id);

-- Composite index for application + active
CREATE INDEX IF NOT EXISTS idx_applicant_app_active
ON applicant(application_id, active)
WHERE active = true;

-- Index for user_id lookups
CREATE INDEX IF NOT EXISTS idx_applicant_user_id
ON applicant(user_id);


-- Index for applicant type filtering
CREATE INDEX IF NOT EXISTS idx_applicant_type
ON applicant(type);

-- Composite index for user_id + active
CREATE INDEX IF NOT EXISTS idx_applicant_user_active
ON applicant(user_id, active)
WHERE active = true;


-- APPLICATION DOCUMENT TABLE INDEXES
-- ============================================================================

-- Index for application_number lookups (critical for JOIN performance)
CREATE INDEX IF NOT EXISTS idx_app_doc_app_number
ON application_document(application_number);

-- Index for document_type filtering
CREATE INDEX IF NOT EXISTS idx_app_doc_type
ON application_document(document_type);

-- Composite index for application + document_type
CREATE INDEX IF NOT EXISTS idx_app_doc_app_type
ON application_document(application_number, document_type);

-- Index for file_store_id lookups
CREATE INDEX IF NOT EXISTS idx_app_doc_file_store_id
ON application_document(file_store_id);

-- Index for document_uid lookups
CREATE INDEX IF NOT EXISTS idx_app_doc_uid
ON application_document(document_uid);

-- Index for created_at sorting
CREATE INDEX IF NOT EXISTS idx_app_doc_created_at
ON application_document(created_at DESC);


-- PUBLIC SERVICE PROCESS TABLE
-- ============================================================================



-- Index for business_service lookups
CREATE INDEX IF NOT EXISTS idx_process_business_service
ON public_service_process(business_service);

-- Index for module lookups
CREATE INDEX IF NOT EXISTS idx_process_module
ON public_service_process(module);

-- Composite index for business_service + module
CREATE INDEX IF NOT EXISTS idx_process_bs_module
ON public_service_process(business_service, module);

-- Index for success filtering
CREATE INDEX IF NOT EXISTS idx_process_success
ON public_service_process(success);

-- Index for created_time sorting
CREATE INDEX IF NOT EXISTS idx_process_created_time
ON public_service_process(created_time DESC);


-- ============================================================================
-- VERIFICATION QUERIES (Uncomment to verify indexes after migration)
-- ============================================================================

-- Verify service table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'service' ORDER BY indexname;

-- Verify service_version_config_mapping table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'service_version_config_mapping' ORDER BY indexname;

-- Verify application table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'application' ORDER BY indexname;

-- Verify reference table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'reference' ORDER BY indexname;

-- Verify applicant table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'applicant' ORDER BY indexname;

-- Verify application_document table indexes
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'application_document' ORDER BY indexname;

-- Check index usage statistics (run after some time in production)
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
-- ORDER BY idx_scan DESC;

-- Check table sizes and index sizes
-- SELECT
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
--     pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Analyze query performance with EXPLAIN ANALYZE
-- EXPLAIN ANALYZE
-- SELECT a.id, a.tenant_id, a.application_number, a.status
-- FROM application a
-- LEFT JOIN applicant ap ON a.id = ap.application_id
-- WHERE a.tenant_id = 'pb.amritsar'
-- AND a.module = 'birth-registration'
-- AND a.status = 'ACTIVE'
-- ORDER BY a.created_at DESC, a.id DESC
-- LIMIT 100;