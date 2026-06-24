ALTER TABLE eg_service_attribute_value ADD COLUMN IF NOT EXISTS clientReferenceId character varying(64);
ALTER TABLE eg_service_attribute_value ADD COLUMN IF NOT EXISTS serviceClientReferenceId character varying(64);
