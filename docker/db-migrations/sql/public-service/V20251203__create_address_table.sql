-- Create or alter studio_address table to match model.Address struct
-- This migration handles both new table creation and existing table updates

-- Create table if it doesn't exist
CREATE TABLE IF NOT EXISTS studio_address (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address_number VARCHAR(255),
    address_line1 VARCHAR(500),
    address_line2 VARCHAR(500),
    landmark VARCHAR(255),
    city VARCHAR(255),
    pincode VARCHAR(20),
    properties JSONB,
    hierarchy_type VARCHAR(255),
    boundary_type VARCHAR(255),
    boundary_code VARCHAR(255),
    application_number VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add missing columns if table already exists but has old schema
DO $$
BEGIN
    -- Add tenant_id if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='tenant_id') THEN
        ALTER TABLE studio_address ADD COLUMN tenant_id VARCHAR(255);
    END IF;

    -- Add latitude if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='latitude') THEN
        ALTER TABLE studio_address ADD COLUMN latitude DECIMAL(10, 8);
    END IF;

    -- Add longitude if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='longitude') THEN
        ALTER TABLE studio_address ADD COLUMN longitude DECIMAL(11, 8);
    END IF;

    -- Add address_number if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='address_number') THEN
        ALTER TABLE studio_address ADD COLUMN address_number VARCHAR(255);
    END IF;

    -- Add address_line1 if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='address_line1') THEN
        ALTER TABLE studio_address ADD COLUMN address_line1 VARCHAR(500);
    END IF;

    -- Add address_line2 if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='address_line2') THEN
        ALTER TABLE studio_address ADD COLUMN address_line2 VARCHAR(500);
    END IF;

    -- Add landmark if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='landmark') THEN
        ALTER TABLE studio_address ADD COLUMN landmark VARCHAR(255);
    END IF;

    -- Add city if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='city') THEN
        ALTER TABLE studio_address ADD COLUMN city VARCHAR(255);
    END IF;

    -- Add pincode if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='pincode') THEN
        ALTER TABLE studio_address ADD COLUMN pincode VARCHAR(20);
    END IF;

    -- Add properties if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='properties') THEN
        ALTER TABLE studio_address ADD COLUMN properties JSONB;
    END IF;

    -- Add hierarchy_type if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='hierarchy_type') THEN
        ALTER TABLE studio_address ADD COLUMN hierarchy_type VARCHAR(255);
    END IF;

    -- Add boundary_type if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='boundary_type') THEN
        ALTER TABLE studio_address ADD COLUMN boundary_type VARCHAR(255);
    END IF;

    -- Add boundary_code if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='boundary_code') THEN
        ALTER TABLE studio_address ADD COLUMN boundary_code VARCHAR(255);
    END IF;

    -- Add application_number if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='application_number') THEN
        ALTER TABLE studio_address ADD COLUMN application_number VARCHAR(255);
    END IF;

    -- Add created_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='created_at') THEN
        ALTER TABLE studio_address ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;

    -- Add updated_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='studio_address' AND column_name='updated_at') THEN
        ALTER TABLE studio_address ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Create indexes for better performance (IF NOT EXISTS is safe)
CREATE INDEX IF NOT EXISTS idx_studio_address_tenant_id ON studio_address(tenant_id);
CREATE INDEX IF NOT EXISTS idx_studio_address_application_number ON studio_address(application_number);
CREATE INDEX IF NOT EXISTS idx_studio_address_city ON studio_address(city);
CREATE INDEX IF NOT EXISTS idx_studio_address_pincode ON studio_address(pincode);
CREATE INDEX IF NOT EXISTS idx_studio_address_boundary_code ON studio_address(boundary_code);

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_studio_address_application_number'
        AND table_name = 'studio_address'
    ) THEN
        ALTER TABLE studio_address ADD CONSTRAINT fk_studio_address_application_number
        FOREIGN KEY (application_number) REFERENCES application(application_number) ON DELETE CASCADE;
    END IF;
END $$;