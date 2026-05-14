# egov-digit-studio — laptop-local DIGIT (Docker Compose + Tilt)
# Run: tilt up
#
# Optional: set DIGIT_DEVOPS_PATH to your clone of egovernments/DIGIT-DevOps
# on branch unified-demo (for browsing Helm env files / configs alongside this stack).

allow_k8s_contexts(k8s_context())

load('ext://uibutton', 'cmd_button', 'location')


docker_compose('./docker-compose.yml')

# ==================== Infrastructure ====================
dc_resource('postgres-db', labels=['infrastructure'])
dc_resource('db-migrations', labels=['infrastructure'],
    resource_deps=['postgres-db'],
)
dc_resource('pgbouncer', labels=['infrastructure'])
dc_resource('redis', labels=['infrastructure'])
dc_resource('redpanda', labels=['infrastructure'])
dc_resource('gatus', labels=['infrastructure'], auto_init=True,
    links=[
        link('http://localhost:18889', 'Health Dashboard'),
    ])

# ==================== Core Services ====================
dc_resource('mdms-backend', labels=['core-services'],
    resource_deps=['pgbouncer', 'redpanda'],
)

dc_resource('egov-mdms-service', labels=['core-services'],
    resource_deps=['mdms-backend'],
    links=[
        link('http://localhost:18094/mdms-v2/health', 'Health'),
    ])

dc_resource('egov-enc-service', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:11234/egov-enc-service/actuator/health', 'Health'),
    ])

dc_resource('egov-idgen', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18088/egov-idgen/health', 'Health'),
    ])

dc_resource('egov-otp', labels=['studio'],
    resource_deps=['pgbouncer', 'redpanda'],
    links=[
        link('http://localhost:18115/otp/health', 'Health'),
    ])

dc_resource('egov-user', labels=['core-services'],
    resource_deps=['egov-enc-service', 'egov-otp'],
    links=[
        link('http://localhost:18107/user/health', 'Health'),
    ])

dc_resource('egov-workflow-v2', labels=['core-services'],
    resource_deps=['egov-idgen'],
    links=[
        link('http://localhost:18109/egov-workflow-v2/health', 'Health'),
    ])

dc_resource('egov-localization', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18096/localization/actuator/health', 'Health'),
    ])

dc_resource('boundary-service', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18081/boundary-service/actuator/health', 'Health'),
    ])

dc_resource('egov-accesscontrol', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18090/access/health', 'Health'),
    ])

dc_resource('egov-persister', labels=['core-services'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18091/common-persist/actuator/health', 'Health'),
    ])

dc_resource('digit-ui', labels=['core-services'],
    resource_deps=['kong'],
    links=[
        link('http://localhost:18000/digit-ui/', 'DIGIT UI via Kong'),
    ])

# ==================== API Gateway ====================
dc_resource('kong', labels=['gateway'],
    links=[
        link('http://localhost:18000', 'Proxy'),
        link('http://localhost:18001', 'Admin API'),
        link('http://localhost:18002', 'Manager GUI'),
    ])

dc_resource('jupyter', labels=['tools'], auto_init=True,
    links=[
        link('http://localhost:18888/jupyter/lab', 'Jupyter Lab'),
    ])

dc_resource('digit-studio', labels=['frontend'],
    resource_deps=['kong'],
    links=[
        link('http://localhost:18110/digit-studio/', 'Direct'),
        link('http://localhost:18000/digit-studio/', 'Via Kong'),
    ])

# ==================== HRMS ====================
dc_resource('egov-hrms', labels=['hrms'],
    resource_deps=['egov-mdms-service', 'egov-idgen', 'egov-user'],
    links=[
        link('http://localhost:18092/egov-hrms/employees/_search', 'Health'),
    ])

# ==================== Additional Services ====================
dc_resource('minio', labels=['infrastructure'])
dc_resource('minio-init', labels=['infrastructure'],
    resource_deps=['minio'],
)
dc_resource('user-seed', labels=['maintenance'],
    resource_deps=['egov-user'],
)
dc_resource('egov-filestore', labels=['core-services'],
    resource_deps=['minio-init', 'egov-mdms-service'],
    links=[
        link('http://localhost:18084/filestore/health', 'Health'),
    ])
dc_resource('egov-bndry-mgmnt', labels=['core-services'],
    resource_deps=['boundary-service', 'egov-filestore'],
    links=[
        link('http://localhost:18086/health', 'Health'),
    ])

dc_resource('egov-url-shortening', labels=['core-services'],
    resource_deps=['pgbouncer'],
    links=[
        link('http://localhost:18085/egov-url-shortening/actuator/health', 'Health'),
    ])

# ==================== Studio (DIGIT-DevOps studio-services) ====================
dc_resource('elasticsearch', labels=['studio'])

dc_resource('health-individual', labels=['studio'],
    resource_deps=['egov-mdms-service', 'egov-enc-service', 'egov-idgen', 'egov-user', 'egov-localization'],
    links=[
        link('http://localhost:18111/health-individual/actuator/health', 'Health'),
    ])

dc_resource('health-service-request', labels=['studio'],
    resource_deps=['egov-mdms-service'],
    links=[
        link('http://localhost:18112/health-service-request/actuator/health', 'Health'),
    ])

dc_resource('public-service-init', labels=['studio'],
    resource_deps=['egov-workflow-v2', 'egov-idgen', 'egov-localization', 'health-individual', 'health-service-request'],
    links=[
        link('http://localhost:18113/', 'Service'),
    ])

dc_resource('public-service', labels=['studio'],
    resource_deps=['public-service-init', 'health-individual', 'health-service-request'],
    links=[
        link('http://localhost:18114/', 'Service'),
    ])

dc_resource('user-otp', labels=['studio'],
    resource_deps=['egov-otp', 'egov-user', 'egov-localization'],
    links=[
        link('http://localhost:18116/user-otp/actuator/health', 'Health'),
    ])

dc_resource('egov-notification-sms', labels=['studio'],
    resource_deps=['redpanda'],
    links=[
        link('http://localhost:18117/egov-notification-sms/actuator/health', 'Health'),
    ])

dc_resource('pdf-service', labels=['studio'],
    resource_deps=['egov-mdms-service', 'egov-localization', 'egov-filestore'],
    links=[
        link('http://localhost:18119/', 'Health'),
    ])

dc_resource('studio-pdf', labels=['studio'],
    resource_deps=['pdf-service', 'public-service', 'egov-user', 'egov-workflow-v2'],
    links=[
        link('http://localhost:18118/', 'Service'),
    ])

dc_resource('inbox', labels=['studio'],
    resource_deps=['elasticsearch', 'egov-workflow-v2', 'egov-user', 'egov-mdms-service'],
    links=[
        link('http://localhost:18120/inbox/actuator/health', 'Health'),
    ])

# ==================== Local Resources ====================
local_resource(
    'nuke-db',
    cmd='docker compose down -v && docker compose up -d postgres-db redis redpanda',
    auto_init=False,
    labels=['maintenance'],
)

cmd_button(
    name='nuke-db-btn',
    argv=['sh', '-c', 'docker compose down -v && docker compose up -d postgres-db redis redpanda'],
    location=location.NAV,
    icon_name='delete_forever',
    text='Nuke DB',
)

cmd_button(
    name='health-check',
    argv=['./scripts/health-check.sh'],
    location=location.NAV,
    icon_name='favorite',
    text='Health Check',
)

cmd_button(
    name='smoke-tests',
    argv=['./scripts/smoke-tests.sh'],
    location=location.NAV,
    icon_name='science',
    text='Smoke Tests',
)

cmd_button(
    name='reseed-mdms',
    argv=['sh', '-c', 'docker exec -i docker-postgres psql -U egov -d egov < ./db/seed.sql'],
    location=location.NAV,
    icon_name='refresh',
    text='Re-seed MDMS',
)

cmd_button(
    name='kong-test',
    argv=['./scripts/kong-test.sh', 'test'],
    location=location.NAV,
    icon_name='security',
    text='Kong Test',
)

cmd_button(
    name='idgen-test',
    argv=['sh', '-c', '''curl -s -X POST "http://localhost:18088/egov-idgen/id/_generate" \
      -H "Content-Type: application/json" \
      -d '{"RequestInfo":{"apiId":"digit","ver":"1.0"},"idRequests":[{"tenantId":"pg","idName":"pgr.servicerequestid"}]}' | jq .'''],
    location=location.NAV,
    icon_name='tag',
    text='Test idgen',
)

cmd_button(
    name='jupyter-start',
    argv=['sh', '-c', 'docker compose --profile tools up -d jupyter && echo "Jupyter Lab: http://localhost:18888"'],
    location=location.NAV,
    icon_name='science',
    text='Start Jupyter',
)

cmd_button(
    name='gatus-start',
    argv=['sh', '-c', 'docker compose --profile tools up -d gatus && echo "Gatus Dashboard: http://localhost:18889"'],
    location=location.NAV,
    icon_name='monitor_heart',
    text='Start Gatus',
)

cmd_button(
    name='seed-users',
    argv=['./seeds/user-seed.sh'],
    location=location.NAV,
    icon_name='person_add',
    text='Seed Users',
)
