-- Migration: V20260109__drop_data_column_from_record
-- Description: Remove the data column from record table to eliminate redundancy
--              The data column was a consolidated cache that duplicated information
--              already present in individual JSONB fields (applicant, fields, address, documents)
-- Date: 2026-01-09

-- Log start
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Starting migration: V20260109__drop_data_column_from_record';
    RAISE NOTICE '========================================';
END $$;

-- Drop the data column from record table
-- This column was redundant as all information is already stored in individual fields
ALTER TABLE record DROP COLUMN IF EXISTS data;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration V20260109__drop_data_column_from_record completed successfully';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Removed: data JSONB column from record table';
    RAISE NOTICE 'Reason: Eliminated data redundancy';
    RAISE NOTICE '  - All data is already stored in individual fields:';
    RAISE NOTICE '    * applicant JSONB';
    RAISE NOTICE '    * fields JSONB';
    RAISE NOTICE '    * address JSONB';
    RAISE NOTICE '    * documents JSONB';
    RAISE NOTICE '    * additional_details JSONB';
    RAISE NOTICE 'Benefits:';
    RAISE NOTICE '  - Reduced storage size (no duplicate data)';
    RAISE NOTICE '  - Simplified code (no consolidated cache building)';
    RAISE NOTICE '  - Improved maintainability';
    RAISE NOTICE '========================================';
END $$;
