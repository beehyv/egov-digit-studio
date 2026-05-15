"""
Digit Studion Data Loader - Simple Wrapper
Provides clean abstraction over unified_loader.py for notebook usage.

Usage:
    from crs_loader import CRSLoader

    loader = CRSLoader("https://unified-dev.digit.org")
    loader.login("admin", "password", tenant_id="pg")

    loader.load_tenant("Tenant And Branding Master.xlsx")
    loader.load_boundaries("Boundary Master.xlsx")
    loader.load_common_masters("Common and Complaint Master.xlsx")
    loader.load_employees("Employee Master.xlsx")
"""

from unified_loader import UnifiedExcelReader, APIUploader
from typing import Optional, Dict
import os


class CRSLoader:
    """Simple wrapper for Digit Studio Data Loading operations"""

    def __init__(self, base_url: str):
        """Initialize CRS Loader with DIGIT environment URL

        Args:
            base_url: DIGIT gateway URL (e.g., "https://unified-dev.digit.org")
        """
        self.base_url = base_url.rstrip('/')
        self.uploader: Optional[APIUploader] = None
        self.tenant_id: Optional[str] = None
        self._authenticated = False

    def login(self, username: str = None, password: str = None,
              tenant_id: str = "pg", user_type: str = "EMPLOYEE") -> bool:
        """Authenticate with DIGIT gateway

        Args:
            username: Admin username (prompts if not provided)
            password: Admin password (prompts if not provided)
            tenant_id: Root tenant ID (default: "pg")
            user_type: User type (default: "EMPLOYEE")

        Returns:
            bool: True if authentication successful
        """
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ")
        if not password:
            import getpass
            password = getpass.getpass("Password: ")

        self.tenant_id = tenant_id

        try:
            self.uploader = APIUploader(
                base_url=self.base_url,
                username=username,
                password=password,
                user_type=user_type,
                tenant_id=tenant_id
            )
            self._authenticated = self.uploader.authenticated
            return self._authenticated
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def _check_auth(self):
        """Check if authenticated before operations"""
        if not self._authenticated or not self.uploader:
            raise RuntimeError("Not authenticated. Call login() first.")

    def load_tenant(self, excel_path: str, target_tenant: str = None) -> Dict:
        """Phase 1: Load tenant configuration and branding

        Args:
            excel_path: Path to "Tenant And Branding Master.xlsx"
            target_tenant: Target tenant ID (uses tenant from Excel if not specified)

        Returns:
            dict: Summary of operations (created, exists, failed counts)
        """
        self._check_auth()

        print(f"\n{'='*60}")
        print(f"PHASE 1: TENANT & BRANDING")
        print(f"{'='*60}")
        print(f"File: {os.path.basename(excel_path)}")

        reader = UnifiedExcelReader(excel_path)
        results = {'tenants': None, 'branding': None, 'localization': None}

        # 1. Read and create tenants
        print(f"\n[1/3] Creating tenants...")
        tenants, localizations = reader.read_tenant_info()

        if not tenants:
            print("   No tenants found in Excel")
            return results

        # Use first tenant's code if target not specified
        if not target_tenant:
            target_tenant = tenants[0].get('code', self.tenant_id)

        # Upload tenants to MDMS
        results['tenants'] = self.uploader.create_mdms_data(
            schema_code='tenant.tenants',
            data_list=tenants,
            tenant=self.tenant_id,  # Tenants go to root tenant
            sheet_name='Tenant Info',
            excel_file=excel_path
        )

        # 2. Create branding
        print(f"\n[2/3] Creating branding...")
        branding = reader.read_tenant_branding(target_tenant)

        if branding:
            results['branding'] = self.uploader.create_mdms_data(
                schema_code='tenant.citymodule',
                data_list=branding,
                tenant=target_tenant,
                sheet_name='Tenant Branding Deatils',
                excel_file=excel_path
            )

        # 3. Create localizations
        print(f"\n[3/3] Creating localizations...")
        if localizations:
            results['localization'] = self.uploader.create_localization_messages(
                localization_list=localizations,
                tenant=target_tenant
            )

        self._print_summary("Tenant & Branding", results)
        return results

    def load_boundaries(self, excel_path: str, target_tenant: str = None,
                       hierarchy_type: str = "ADMIN") -> Dict:
        """Phase 2: Load boundary hierarchy from Excel

        Args:
            excel_path: Path to "Boundary Master.xlsx"
            target_tenant: Target tenant ID
            hierarchy_type: Hierarchy type (default: "ADMIN")

        Returns:
            dict: Processing result with status
        """
        self._check_auth()

        print(f"\n{'='*60}")
        print(f"PHASE 2: BOUNDARIES")
        print(f"{'='*60}")
        print(f"File: {os.path.basename(excel_path)}")
        print(f"Hierarchy: {hierarchy_type}")

        tenant = target_tenant or self.tenant_id

        # 1. Upload Excel to FileStore
        print(f"\n[1/2] Uploading boundary file...")
        filestore_id = self.uploader.upload_file_to_filestore(
            file_path=excel_path,
            tenant_id=tenant,
            module="HCM-ADMIN-CONSOLE"
        )

        if not filestore_id:
            print("   Failed to upload file")
            return {'status': 'failed', 'error': 'File upload failed'}

        print(f"   FileStore ID: {filestore_id}")

        # 2. Process boundaries
        print(f"\n[2/2] Processing boundary data...")
        result = self.uploader.process_boundary_data(
            tenant_id=tenant,
            filestore_id=filestore_id,
            hierarchy_type=hierarchy_type,
            action="create"
        )

        status = result.get('status', 'unknown')
        print(f"\n   Status: {status}")

        return result

    def load_common_masters(self, excel_path: str, target_tenant: str = None) -> Dict:
        """Phase 3: Load departments, designations, and complaint types

        Args:
            excel_path: Path to "Common and Complaint Master.xlsx"
            target_tenant: Target tenant ID

        Returns:
            dict: Summary of operations for each master type
        """
        self._check_auth()

        print(f"\n{'='*60}")
        print(f"PHASE 3: COMMON MASTERS")
        print(f"{'='*60}")
        print(f"File: {os.path.basename(excel_path)}")

        tenant = target_tenant or self.tenant_id
        reader = UnifiedExcelReader(excel_path)
        results = {'departments': None, 'designations': None, 'complaint_types': None}

        # 1. Load departments and designations
        print(f"\n[1/2] Loading departments & designations...")
        dept_data, desig_data, dept_loc, desig_loc, dept_name_to_code = \
            reader.read_departments_designations(tenant, self.uploader)

        # Upload departments
        if dept_data:
            print(f"   Creating {len(dept_data)} departments...")
            results['departments'] = self.uploader.create_mdms_data(
                schema_code='common-masters.Department',
                data_list=dept_data,
                tenant=tenant,
                sheet_name='Department',
                excel_file=excel_path
            )

            # Department localizations
            if dept_loc:
                self.uploader.create_localization_messages(dept_loc, tenant)

        # Upload designations
        if desig_data:
            print(f"   Creating {len(desig_data)} designations...")
            results['designations'] = self.uploader.create_mdms_data(
                schema_code='common-masters.Designation',
                data_list=desig_data,
                tenant=tenant,
                sheet_name='Designation',
                excel_file=excel_path
            )

            # Designation localizations
            if desig_loc:
                self.uploader.create_localization_messages(desig_loc, tenant)

        # 2. Load complaint types
        print(f"\n[2/2] Loading complaint types...")
        complaint_data, complaint_loc = reader.read_complaint_types(tenant, dept_name_to_code)

        if complaint_data:
            print(f"   Creating {len(complaint_data)} complaint types...")
            results['complaint_types'] = self.uploader.create_mdms_data(
                schema_code='RAINMAKER-PGR.ServiceDefs',
                data_list=complaint_data,
                tenant=tenant,
                sheet_name='Complaint Type',
                excel_file=excel_path
            )

            # Complaint type localizations
            if complaint_loc:
                self.uploader.create_localization_messages(complaint_loc, tenant)

        self._print_summary("Common Masters", results)
        return results

    def load_employees(self, excel_path: str, target_tenant: str = None) -> Dict:
        """Phase 4: Load employee master data

        Args:
            excel_path: Path to "Employee Master.xlsx"
            target_tenant: Target tenant ID

        Returns:
            dict: Summary of employee creation results
        """
        self._check_auth()

        print(f"\n{'='*60}")
        print(f"PHASE 4: EMPLOYEES")
        print(f"{'='*60}")
        print(f"File: {os.path.basename(excel_path)}")

        tenant = target_tenant or self.tenant_id
        reader = UnifiedExcelReader(excel_path)

        # 1. Read employee data (converts names to codes internally)
        print(f"\n[1/2] Reading employee data...")
        employees = reader.read_employees_bulk(tenant, self.uploader)

        if not employees:
            print("   No employees found in Excel")
            return {'created': 0, 'exists': 0, 'failed': 0}

        print(f"   Found {len(employees)} employees")

        # 2. Create employees via HRMS
        print(f"\n[2/2] Creating employees...")
        results = self.uploader.create_employees(
            employee_list=employees,
            tenant=tenant,
            sheet_name='Employee Master',
            excel_file=excel_path
        )

        self._print_summary("Employees", {'employees': results})
        return results

    def _print_summary(self, phase: str, results: Dict):
        """Print clean summary of results"""
        print(f"\n{'─'*40}")
        print(f"{phase} Summary:")

        total_created = 0
        total_exists = 0
        total_unauthorized = 0
        total_forbidden = 0
        total_invalid = 0
        total_failed = 0

        for key, value in results.items():
            if value and isinstance(value, dict):
                total_created += value.get('created', 0)
                total_exists += value.get('exists', 0)
                total_unauthorized += value.get('unauthorized', 0)
                total_forbidden += value.get('forbidden', 0)
                total_invalid += value.get('invalid', 0)
                total_failed += value.get('failed', 0)

        print(f"   Created:        {total_created}")
        print(f"   Already existed:{total_exists}")
        if total_unauthorized:
            print(f"   Unauthorized:   {total_unauthorized}  ← Re-login required (401)")
        if total_forbidden:
            print(f"   Forbidden:      {total_forbidden}  ← Insufficient permissions (403)")
        if total_invalid:
            print(f"   Invalid Req:    {total_invalid}  ← Validation/bad request (400)")
        print(f"   Failed:         {total_failed}")
        print(f"{'─'*40}")


    def load_localizations(self, excel_path: str, target_tenant: str = None,
                              language_label: str = None, locale_code: str = None) -> Dict:
            """Phase 5: Load bulk localization messages from Excel

            Args:
                excel_path: Path to localization Excel file
                           Must have 'Localization' or 'localization' sheet
                           Required columns: Code, Message, Locale (optional: Module)
                target_tenant: Target tenant ID
                language_label: Display name for new language (e.g., 'Hindi', 'ਪੰਜਾਬੀ')
                               If provided, updates StateInfo with this language
                locale_code: Locale code for new language (e.g., 'hi_IN', 'pa_IN')
                            Required if language_label is provided

            Returns:
                dict: Summary of localization upload and StateInfo update
            """
            self._check_auth()

            print(f"\n{'='*60}")
            print(f"PHASE 5: LOCALIZATIONS")
            print(f"{'='*60}")
            print(f"File: {os.path.basename(excel_path)}")

            tenant = target_tenant or self.tenant_id
            reader = UnifiedExcelReader(excel_path)
            results = {'messages': None, 'stateinfo': None}

            # 1. Read localization data from Excel
            print(f"\n[1/2] Reading localization data...")
            localization_data = reader.read_localization()

            if not localization_data:
                print("   No localization data found in Excel")
                print("   Make sure the Excel has a 'Localization' sheet with Code and Message columns")
                return results

            print(f"   Found {len(localization_data)} messages")

            # Show locale breakdown
            from collections import defaultdict
            by_locale = defaultdict(int)
            for loc in localization_data:
                by_locale[loc.get('locale', 'unknown')] += 1
            for locale, count in by_locale.items():
                print(f"   - {locale}: {count} messages")

            # 2. Upload localization messages
            print(f"\n[2/2] Uploading localization messages...")
            results['messages'] = self.uploader.create_localization_messages(
                localization_list=localization_data,
                tenant=tenant,
                sheet_name='Localization'
            )

            # 3. Optionally update StateInfo with new language
            if language_label and locale_code:
                print(f"\n[BONUS] Updating StateInfo with new language...")
                print(f"   Language: {language_label} ({locale_code})")
                results['stateinfo'] = self.uploader.update_stateinfo_language(
                    language_label=language_label,
                    language_value=locale_code,
                    state_tenant=tenant
                )

            self._print_summary("Localizations", results)
            return results



    def load_mdms_schema(
        self,
        excel_path: str,
        target_tenant: str = None,
        sheet_name: str = "schemas"
    ) -> dict:
        """
        Load MDMS schema definitions from Excel.

        Excel must contain column:
        - schemaDefinition

        The column should contain FULL SchemaDefinition JSON.

        tenantId will be overridden dynamically.
        """

        self._check_auth()

        tenant = target_tenant or self.tenant_id

        print(f"\n{'='*60}")
        print("PHASE: MDMS SCHEMA CREATION")
        print(f"{'='*60}")
        print(f"File: {excel_path}")
        print(f"Sheet: {sheet_name}")
        print(f"Target Tenant: {tenant}")

        reader = UnifiedExcelReader(excel_path)

        schemas = reader.read_mdms_schema_definitions(
            target_tenant=tenant,
            sheet_name=sheet_name
        )

        if not schemas:
            print("No schema definitions found")

            return {
                "created": 0,
                "failed": 0
            }

        created = 0
        failed = 0

        for schema_definition in schemas:

            result = self.uploader.create_mdms_schema(
                schema_definition
            )

            if result.get("created"):
                created += 1
            else:
                failed += 1

        print(f"\n{'─'*40}")
        print("MDMS Schema Summary")
        print(f"Created: {created}")
        print(f"Failed: {failed}")
        print(f"{'─'*40}")

        return {
            "created": created,
            "failed": failed
        }

    def load_mdms_data(
        self,
        excel_path: str,
        target_tenant: str = None,
        sheet_name: str = "data"
    ) -> dict:
        """
        Load MDMS data from Excel.

        Excel must contain columns:
        - schemaCode
        - mdmsData

        mdmsData should contain FULL JSON.

        tenantId inside mdmsData will be overridden dynamically.
        """

        self._check_auth()

        tenant = target_tenant or self.tenant_id

        print(f"\n{'='*60}")
        print("PHASE: MDMS DATA CREATION")
        print(f"{'='*60}")
        print(f"File: {excel_path}")
        print(f"Sheet: {sheet_name}")
        print(f"Target Tenant: {tenant}")

        reader = UnifiedExcelReader(excel_path)

        mdms_records = reader.read_mdms_data_definitions(
            target_tenant=tenant,
            sheet_name=sheet_name
        )

        if not mdms_records:

            print("No mdms data definitions found")

            return {
                "created": 0,
                "failed": 0
            }

        created = 0
        failed = 0

        errors = []

        for i, mdms_record in enumerate(mdms_records, 1):
            schema_code = mdms_record["schemaCode"]
            unique_id = mdms_record.get("data", {}).get("uniqueIdentifier") or schema_code

            try:
                response = self.uploader.create_mdms_data_v2(
                    schema_code=schema_code,
                    tenant_id=mdms_record["tenantId"],
                    mdms_data=mdms_record["data"]
                )
                status_code = response.status_code

                if status_code == 401:
                    print(f"   [UNAUTHORIZED] [{i}/{len(mdms_records)}] {unique_id} (HTTP 401) - Login token invalid or expired")
                    failed += 1
                    errors.append({'id': unique_id, 'error': '401 Unauthorized: re-login required'})
                elif status_code == 403:
                    print(f"   [FORBIDDEN] [{i}/{len(mdms_records)}] {unique_id} (HTTP 403) - Insufficient permissions")
                    failed += 1
                    errors.append({'id': unique_id, 'error': '403 Forbidden'})
                elif status_code in (200, 201):
                    print(f"   [OK] [{i}/{len(mdms_records)}] {unique_id}")
                    created += 1
                else:
                    error_text = response.text[:200] if response.text else str(status_code)
                    print(f"   [FAILED] [{i}/{len(mdms_records)}] {unique_id} (HTTP {status_code})")
                    print(f"   ERROR: {error_text}")
                    failed += 1
                    errors.append({'id': unique_id, 'error': error_text})

            except Exception as e:
                print(f"   [ERROR] [{i}/{len(mdms_records)}] {unique_id} - {str(e)[:100]}")
                failed += 1
                errors.append({'id': unique_id, 'error': str(e)[:200]})

        print(f"\n{'─'*40}")
        print("MDMS Data Summary")
        print(f"   Created: {created}")
        print(f"   Failed:  {failed}")
        print(f"{'─'*40}")

        return {
            "created": created,
            "failed": failed,
            "errors": errors
        }


# Convenience function for quick setup
def quick_start(url: str = "https://unified-dev.digit.org") -> CRSLoader:
    """Quick start - creates loader and prompts for login

    Args:
        url: DIGIT environment URL

    Returns:
        Authenticated CRSLoader instance
    """
    loader = CRSLoader(url)
    loader.login()
    return loader
