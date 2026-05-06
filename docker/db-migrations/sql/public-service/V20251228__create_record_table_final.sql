-- =====================================================
-- Record Table - Final Version
-- Version: V20251229001
-- Description: Create record table for versioned snapshots with data merging
-- =====================================================

-- Create record table
CREATE TABLE IF NOT EXISTS record (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Record Identification (same across versions)
    record_number VARCHAR(255) NOT NULL,

    -- Version Information
    version INTEGER NOT NULL DEFAULT 1,
    previous_record_id UUID,

    -- Application Reference (different per version)
    application_id UUID NOT NULL,
    application_number VARCHAR(255) NOT NULL,
    service_number VARCHAR(255),

    -- Tenant and Service Information
    tenant_id VARCHAR(255) NOT NULL,
    module VARCHAR(255) NOT NULL,
    business_service VARCHAR(255) NOT NULL,
    service_code VARCHAR(255) NOT NULL,
    workflow_status VARCHAR(255),
    channel VARCHAR(255),

    -- Merged Data (JSONB columns)
    applicant JSONB,
    fields JSONB,
    address JSONB,
    documents JSONB,
    additional_details JSONB,

    -- Consolidated Merged Data (Cache for quick search)
    data JSONB,

    -- Record Status
    status VARCHAR(255) DEFAULT 'ACTIVE',
    is_current BOOLEAN DEFAULT true,

    -- Audit Details
    created_at BIGINT NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    updated_at BIGINT,
    updated_by VARCHAR(255)
);

-- Create indexes for record table
CREATE INDEX IF NOT EXISTS idx_record_number ON record(record_number);
CREATE INDEX IF NOT EXISTS idx_record_number_version ON record(record_number, version);
CREATE INDEX IF NOT EXISTS idx_record_application_id ON record(application_id);
CREATE INDEX IF NOT EXISTS idx_record_application_number ON record(application_number);
CREATE INDEX IF NOT EXISTS idx_record_tenant_id ON record(tenant_id);
CREATE INDEX IF NOT EXISTS idx_record_service_code ON record(service_code);
CREATE INDEX IF NOT EXISTS idx_record_module ON record(module);
CREATE INDEX IF NOT EXISTS idx_record_business_service ON record(business_service);
CREATE INDEX IF NOT EXISTS idx_record_workflow_status ON record(workflow_status);
CREATE INDEX IF NOT EXISTS idx_record_status ON record(status);
CREATE INDEX IF NOT EXISTS idx_record_is_current ON record(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_record_previous_id ON record(previous_record_id);

-- Add record_number column to application table (stores record_number string like "REC-2025-01-02-000001")
ALTER TABLE application
ADD COLUMN IF NOT EXISTS record_number VARCHAR(255);

-- Add foreign key for previous_record_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_record_previous'
        AND table_name = 'record'
    ) THEN
        ALTER TABLE record ADD CONSTRAINT fk_record_previous
        FOREIGN KEY (previous_record_id) REFERENCES record(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added foreign key constraint fk_record_previous';
    ELSE
        RAISE NOTICE 'Foreign key constraint fk_record_previous already exists';
    END IF;
END $$;

-- Add index on application.record_number
CREATE INDEX IF NOT EXISTS idx_application_record_number ON application(record_number);

-- Add comments for documentation
COMMENT ON TABLE record IS 'Record table storing versioned snapshots with merged data from multiple services';
COMMENT ON COLUMN record.id IS 'UUID primary key for this record version';
COMMENT ON COLUMN record.record_number IS 'Record number - SAME across all versions (e.g., VL-REC-2025-12-29-000001)';
COMMENT ON COLUMN record.version IS 'Version number (1, 2, 3, ...) - increments with each new version';
COMMENT ON COLUMN record.previous_record_id IS 'Reference to previous version of this record (NULL for version 1)';
COMMENT ON COLUMN record.application_id IS 'Application that created this record version';
COMMENT ON COLUMN record.application_number IS 'Application number - DIFFERENT per version';
COMMENT ON COLUMN record.service_number IS 'Service number if applicable';
COMMENT ON COLUMN record.tenant_id IS 'Tenant identifier';
COMMENT ON COLUMN record.module IS 'Module name (e.g., VehicleManagement)';
COMMENT ON COLUMN record.business_service IS 'Business service name';
COMMENT ON COLUMN record.service_code IS 'Service code';
COMMENT ON COLUMN record.workflow_status IS 'Workflow status when record was created';
COMMENT ON COLUMN record.channel IS 'Channel (CITIZEN, EMPLOYEE, API)';
COMMENT ON COLUMN record.applicant IS 'JSONB - Merged applicant data';
COMMENT ON COLUMN record.fields IS 'JSONB - Merged fields/service_details';
COMMENT ON COLUMN record.address IS 'JSONB - Merged address data';
COMMENT ON COLUMN record.documents IS 'JSONB - Document snapshots';
COMMENT ON COLUMN record.additional_details IS 'JSONB - Additional details';
COMMENT ON COLUMN record.data IS 'JSONB - Consolidated merged data (applicant + fields + address + documents) - CACHED for fast search';
COMMENT ON COLUMN record.status IS 'Record status (ACTIVE, INACTIVE, CLOSED)';
COMMENT ON COLUMN record.is_current IS 'Boolean - true if this is the latest version, false for superseded versions';
COMMENT ON COLUMN record.created_at IS 'Record creation timestamp (epoch milliseconds)';
COMMENT ON COLUMN record.created_by IS 'User UUID who created the record';
COMMENT ON COLUMN record.updated_at IS 'Record update timestamp (epoch milliseconds)';
COMMENT ON COLUMN record.updated_by IS 'User UUID who last updated the record';

COMMENT ON COLUMN application.record_number IS 'Stores the record_number string (e.g., REC-2025-01-02-000001) to link to an existing record for versioning. Empty for new records, populated when creating a version of an existing record.';

-- Log completion
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration V20251229001 completed successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Created: record table with versioning support';
    RAISE NOTICE '  - Record identification: id, record_number';
    RAISE NOTICE '  - Versioning: version, previous_record_id, is_current';
    RAISE NOTICE '  - Application reference: application_id, application_number';
    RAISE NOTICE '  - Tenant/Service: tenant_id, module, business_service, service_code';
    RAISE NOTICE '  - Data (JSONB): applicant, fields, address, documents, additional_details';
    RAISE NOTICE '  - Consolidated Data (JSONB): data (cached merged data for fast search)';
    RAISE NOTICE '  - Status: status, workflow_status, channel';
    RAISE NOTICE '  - Audit: created_at, created_by, updated_at, updated_by';
    RAISE NOTICE 'Added: record_number VARCHAR(255) column to application table';
    RAISE NOTICE '  - Stores record_number string for linking to existing records';
    RAISE NOTICE '  - No FK constraint (string reference, not relational FK)';
    RAISE NOTICE 'Created: Foreign key constraint for record.previous_record_id';
    RAISE NOTICE 'Created: Performance indexes on all key columns';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Record Creation Trigger:';
    RAISE NOTICE '  - When application reaches states in workflow.ACTIVE[] (from MDMS)';
    RAISE NOTICE '  - If application.recordNumber exists → Create version with merge';
    RAISE NOTICE '  - If application.recordNumber is null → Create new record';
    RAISE NOTICE '========================================';
END $$;
