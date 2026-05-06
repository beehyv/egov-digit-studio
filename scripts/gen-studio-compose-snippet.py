#!/usr/bin/env python3
"""Emit docker-compose YAML fragment for Studio services (stdout)."""
print(
    r"""
  # --- Studio stack (DIGIT-DevOps studio-services / core-services patterns) ---
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.23
    container_name: digit-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    ports:
      - "19200:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:9200/_cluster/health >/dev/null"]
      interval: 15s
      timeout: 10s
      retries: 30
      start_period: 90s
    deploy:
      resources:
        limits:
          memory: 1536M
          cpus: "1"
    networks:
      - egov-network

  health-individual:
    image: ${IMAGE_HEALTH_INDIVIDUAL:-egovio/health-individual:Individual-master-register-studio-d307985}
    container_name: health-individual
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      redis:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-enc-service:
        condition: service_healthy
      egov-idgen:
        condition: service_healthy
      egov-user:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      SPRING_KAFKA_CONSUMER_GROUP_ID: health-individual
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /health-individual
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: "6379"
      SPRING_CACHE_TYPE: redis
      SPRING_CACHE_REDIS_TIME-TO-LIVE: "60"
      SPRING_CACHE_AUTOEXPIRY: "true"
      EGOV_MDMS_HOST: http://egov-mdms-service:8094
      EGOV_MDMS_SEARCH_ENDPOINT: /mdms-v2/v1/_search
      EGOV_ENC_HOST: http://egov-enc-service:1234
      EGOV_LOCALIZATION_HOST: http://egov-localization:8096
      EGOV_ENC_ENCRYPT_ENDPOINT: /egov-enc-service/crypto/v1/_encrypt
      EGOV_ENC_DECRYPT_ENDPOINT: /egov-enc-service/crypto/v1/_decrypt
      EGOV_IDGEN_HOST: http://egov-idgen:8088
      EGOV_IDGEN_PATH: egov-idgen/id/_generate
      EGOV_IDGEN_INTEGRATION_ENABLED: "true"
      EGOV_USER_HOST: http://egov-user:8107
      EGOV_CREATE_USER_URL: /user/users/_createnovalidate
      EGOV_SEARCH_USER_URL: /user/_search
      EGOV_UPDATE_USER_URL: /user/users/_updatenovalidate
      EGOV_USER_INTEGRATION_ENABLED: "true"
      USER_SYNC_ENABLED: "true"
      USER_SERVICE_USER_TYPE: CITIZEN
      USER_SERVICE_ACCOUNT_LOCKED: "false"
      NOTIFICATION_SMS_ENABLED: "false"
      STATE_LEVEL_TENANT_ID: pg
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx192m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18111:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/health-individual/actuator/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    networks:
      - egov-network

  health-service-request:
    image: ${IMAGE_HEALTH_SERVICE_REQUEST:-egovio/health-service-request:multiarch-changes-digit-studio-3fd88be}
    container_name: health-service-request
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      SPRING_KAFKA_CONSUMER_GROUP_ID: service-request-health
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /health-service-request
      SERVER_CONTEXT_PATH: /health-service-request
      EGOV_SERVICE_DEFINITION_CREATE_TOPIC: save-service-definition-health
      EGOV_SERVICE_CREATE_TOPIC: save-service-health
      EGOV_SERVICE_UPDATE_TOPIC: update-service-health
      EGOV_SERVICE_DEFINITION_UPDATE_TOPIC: update-service-definition-health
      EGOV_SERVICE_REQUEST_DEFAULT_OFFSET: "0"
      EGOV_SERVICE_REQUEST_DEFAULT_LIMIT: "10"
      EGOV_SERVICE_REQUEST_MAX_LIMIT: "100"
      EGOV_MAX_STRING_INPUT_SIZE: "8192"
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx256m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18112:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/health-service-request/actuator/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    networks:
      - egov-network

  public-service-init:
    image: ${IMAGE_PUBLIC_SERVICE_INIT:-egovio/public-service-init:develop-e42fed4}
    container_name: public-service-init
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-workflow-v2:
        condition: service_healthy
      egov-idgen:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
      health-individual:
        condition: service_healthy
      health-service-request:
        condition: service_healthy
    environment:
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: egov
      DB_USER: egov
      DB_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      DB_SSL_MODE: disable
      PGSSLMODE: disable
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /public-service-init
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      WORKFLOW_HOST: http://egov-workflow-v2:8109
      WORKFLOW_TRANSITION_PATH: egov-workflow-v2/egov-wf/process/_transition
      WORKFLOW_SEARCH_PATH: egov-workflow-v2/egov-wf/process/_search
      WF_BUSINESS_SERVICE_CREATE_URL: egov-workflow-v2/egov-wf/businessservice/_create
      WF_BUSINESS_SERVICE_SEARCH_PATH: egov-workflow-v2/egov-wf/businessservice/_search
      WF_BUSINESS_SERVICE_UPDATE_PATH: egov-workflow-v2/egov-wf/businessservice/_update
      INDIVIDUAL_SERVICE_HOST: http://health-individual:8080
      INDIVIDUAL_CREATE_ENDPOINT: health-individual/v1/_create
      INDIVIDUAL_UPDATE_ENDPOINT: health-individual/v1/_update
      INDIVIDUAL_SEARCH_ENDPOINT: health-individual/v1/_search
      MDMS_SERVICE_HOST: http://egov-mdms-service:8094
      MDMS_SEARCH_ENDPOINT: mdms-v2/v1/_search
      MDMS_V2_SEARCH_ENDPOINT: mdms-v2/v2/_search
      MDMS_SEARCH_V2_ENDPOINT: mdms-v2/v2
      MDMS_V2_CREATE_ENDPOINT: mdms-v2/v2/_create
      MDMS_V2_UPDATE_ENDPOINT: mdms-v2/v2/_update
      BILLING_SERVICE_HOST: http://egov-mdms-service:8094
      DEMAND_CREATE_ENDPOINT: billing-service/demand/_create
      BILL_FETCH_ENDPOINT: billing-service/bill/v2/_fetchbill
      IDGEN_SERVICE_HOST: http://egov-idgen:8088
      IDGEN_SERVICE_GENERATE_URL: egov-idgen/id/_generate
      LOCALIZATION_SERVICE_HOST: http://egov-localization:8096
      LOCALIZATION_CONTEXT_PATH: localization/messages/v1
      LOCALIZATION_SEARCH_ENDPOINT: /_search
      LOCALIZATION_UPSERT_ENDPOINT: /_upsert
      SERVICE_MASTER_NAME: ServiceConfiguration
      SERVICE_MODULE_NAME: Studio
      NOTIFICATION_LOCALE: en_IN
      KAFKA_PAYMENT_CONSUMER_ENABLED: "false"
      SAVE_PUBLIC_SERVICE_APPLICATION_TOPIC: save-public-service-application
      UPDATE_PUBLIC_SERVICE_APPLICATION_TOPIC: update-public-service-application
      SAVE_PUBLIC_SERVICE_APPLICATION_TOPIC_INDEXER: save-public-service-application-indexer
      UPDATE_PUBLIC_SERVICE_APPLICATION_TOPIC_INDEXER: update-public-service-application-indexer
      SEND_SMS_TOPIC: egov.core.notification.sms
      SEND_EMAIL_TOPIC: egov.core.notification.email
      KAFKA_TOPICS_PAYMENT_CREATE_NAME: egov.collection.payment-create
      UPDATE_PUBLIC_SERVICE: update-public-service
      SAVE_PUBLIC_SERVICE: save-public-service
      MDMS_MAPPING: '{"documents": {"schemaCode": "DigitStudio.DocumentConfig2"}, "idgen":{"schemaCode": "common-masters.IdFormat"}, "bill":{"schemaCode":"BillingService"}}'
      TAXHEAD: TaxHeadMaster
      TAXPERIOD: TaxPeriod
      BusinessService: BusinessService
      LOCALIZATION_MODULE: rainmaker-studio-
      SAVE_PUBLIC_SERVICE_PROCESS: save-public-service-process
      SERVICE_REQUEST_HOST: http://health-service-request:8080
      SERVICE_REQUEST_CREATE_ENDPOINT: health-service-request/service/definition/v1/_create
      SERVICE_REQUEST_SEARCH_ENDPOINT: health-service-request/service/definition/v1/_search
      SERVICE_REQUEST_UPDATE_ENDPOINT: health-service-request/service/definition/v1/_update
      SAVE_SERVICE_VERSION_CONFIG_MAPPING: save-service-version-config-mapping
      DELETE_BUSINESS_SERVICE_TOPIC: delete-business-service-topic
      STUDIO_CITIZEN_ROLE: STUDIO_CITIZEN
      JAVA_TOOL_OPTIONS: -Xms256m -Xmx512m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18113:8080"
    healthcheck:
      test: ["CMD-SHELL", "nc -z 127.0.0.1 8080 >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 180s
    deploy:
      resources:
        limits:
          memory: 768M
          cpus: "0.5"
    networks:
      - egov-network

  public-service:
    image: ${IMAGE_PUBLIC_SERVICE:-egovio/public-service:develop-4351bc1}
    container_name: public-service
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-workflow-v2:
        condition: service_healthy
      egov-idgen:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
      health-individual:
        condition: service_healthy
      health-service-request:
        condition: service_healthy
      public-service-init:
        condition: service_healthy
    environment:
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: egov
      DB_USER: egov
      DB_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      DB_SSL_MODE: disable
      PGSSLMODE: disable
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /public-service
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      WORKFLOW_HOST: http://egov-workflow-v2:8109
      WORKFLOW_TRANSITION_PATH: egov-workflow-v2/egov-wf/process/_transition
      WORKFLOW_SEARCH_PATH: egov-workflow-v2/egov-wf/process/_search
      WF_BUSINESS_SERVICE_CREATE_URL: egov-workflow-v2/egov-wf/businessservice/_create
      WF_BUSINESS_SERVICE_SEARCH_PATH: egov-workflow-v2/egov-wf/businessservice/_search
      WF_BUSINESS_SERVICE_UPDATE_PATH: egov-workflow-v2/egov-wf/businessservice/_update
      INDIVIDUAL_SERVICE_HOST: http://health-individual:8080
      INDIVIDUAL_CREATE_ENDPOINT: health-individual/v1/_create
      INDIVIDUAL_UPDATE_ENDPOINT: health-individual/v1/_update
      INDIVIDUAL_SEARCH_ENDPOINT: health-individual/v1/_search
      MDMS_SERVICE_HOST: http://egov-mdms-service:8094
      MDMS_SEARCH_ENDPOINT: mdms-v2/v1/_search
      MDMS_V2_SEARCH_ENDPOINT: mdms-v2/v2/_search
      MDMS_SEARCH_V2_ENDPOINT: mdms-v2/v2
      MDMS_V2_CREATE_ENDPOINT: mdms-v2/v2/_create
      MDMS_V2_UPDATE_ENDPOINT: mdms-v2/v2/_update
      BILLING_SERVICE_HOST: http://egov-mdms-service:8094
      DEMAND_CREATE_ENDPOINT: billing-service/demand/_create
      BILL_FETCH_ENDPOINT: billing-service/bill/v2/_fetchbill
      IDGEN_SERVICE_HOST: http://egov-idgen:8088
      IDGEN_SERVICE_GENERATE_URL: egov-idgen/id/_generate
      LOCALIZATION_SERVICE_HOST: http://egov-localization:8096
      LOCALIZATION_CONTEXT_PATH: localization/messages/v1
      LOCALIZATION_SEARCH_ENDPOINT: /_search
      LOCALIZATION_UPSERT_ENDPOINT: /_upsert
      SERVICE_MASTER_NAME: ServiceConfiguration
      SERVICE_MODULE_NAME: Studio
      NOTIFICATION_LOCALE: en_IN
      KAFKA_PAYMENT_CONSUMER_ENABLED: "false"
      SAVE_PUBLIC_SERVICE_APPLICATION_TOPIC: save-public-service-application
      UPDATE_PUBLIC_SERVICE_APPLICATION_TOPIC: update-public-service-application
      SAVE_PUBLIC_SERVICE_APPLICATION_TOPIC_INDEXER: save-public-service-application-indexer
      UPDATE_PUBLIC_SERVICE_APPLICATION_TOPIC_INDEXER: update-public-service-application-indexer
      SEND_SMS_TOPIC: egov.core.notification.sms
      SEND_EMAIL_TOPIC: egov.core.notification.email
      KAFKA_TOPICS_PAYMENT_CREATE_NAME: egov.collection.payment-create
      UPDATE_PUBLIC_SERVICE: update-public-service
      SAVE_PUBLIC_SERVICE: save-public-service
      MDMS_MAPPING: '{"documents": {"schemaCode": "DigitStudio.DocumentConfig2"}, "idgen":{"schemaCode": "common-masters.IdFormat"}, "bill":{"schemaCode":"BillingService"}}'
      TAXHEAD: TaxHeadMaster
      TAXPERIOD: TaxPeriod
      BusinessService: BusinessService
      LOCALIZATION_MODULE: rainmaker-studio-
      SAVE_PUBLIC_SERVICE_PROCESS: save-public-service-process
      SERVICE_REQUEST_HOST: http://health-service-request:8080
      SERVICE_REQUEST_CREATE_ENDPOINT: health-service-request/service/definition/v1/_create
      SERVICE_REQUEST_SEARCH_ENDPOINT: health-service-request/service/definition/v1/_search
      SERVICE_REQUEST_UPDATE_ENDPOINT: health-service-request/service/definition/v1/_update
      SAVE_SERVICE_VERSION_CONFIG_MAPPING: save-service-version-config-mapping
      DELETE_BUSINESS_SERVICE_TOPIC: delete-business-service-topic
      PUBLIC_SERVICE_HOST: http://public-service-init:8080
      PUBLIC_SERVICE_SEARCH_ENDPOINT: public-service-init/v1/service
      DEFAULT_LIMIT: "100"
      MAX_LIMIT: "1000"
      DEFAULT_OFFSET: "0"
      JAVA_TOOL_OPTIONS: -Xms256m -Xmx512m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18114:8080"
    healthcheck:
      test: ["CMD-SHELL", "nc -z 127.0.0.1 8080 >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 180s
    deploy:
      resources:
        limits:
          memory: 768M
          cpus: "0.5"
    networks:
      - egov-network

  egov-otp:
    image: ${IMAGE_EGOV_OTP:-egovio/egov-otp:master-1e8d2bb}
    container_name: egov-otp
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /otp
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx256m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18115:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/otp/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.25"
    networks:
      - egov-network

  user-otp:
    image: ${IMAGE_USER_OTP:-egovio/user-otp:sandbox-log-86902f9}
    container_name: user-otp
    depends_on:
      egov-otp:
        condition: service_healthy
      egov-user:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
    environment:
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /user-otp
      OTP_HOST: http://egov-otp:8080/otp
      USER_HOST: http://egov-user:8107
      EGOV_LOCALISATION_HOST: http://egov-localization:8096
      SMS_TOPIC: egov.core.notification.sms
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx256m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18116:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/user-otp/actuator/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.25"
    networks:
      - egov-network

  egov-notification-sms:
    image: ${IMAGE_EGOV_NOTIFICATION_SMS:-egovio/egov-notification-sms:sandbox-d760d6b}
    container_name: egov-notification-sms
    depends_on:
      redpanda:
        condition: service_healthy
    environment:
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /egov-notification-sms
      KAFKA_TOPICS_NOTIFICATION_SMS_NAME: egov.core.notification.sms
      KAFKA_TOPICS_NOTIFICATION_SMS_ID: egov.core.notification.sms
      KAFKA_TOPICS_NOTIFICATION_SMS_GROUP: egov.core.notification.sms
      SMS_ENABLED: "false"
      SMS_PROVIDER_URL: "https://example.invalid/sms"
      SMS_SENDER_USERNAME: "local-dev"
      SMS_SENDER_PASSWORD: "local-dev"
      SMS_SPICEDIGITAL_PROVIDER_URL: "https://example.invalid/sms"
      SMS_SPICEDIGITAL_SENDER_USERNAME: "local-dev"
      SMS_SPICEDIGITAL_SENDER_PASSWORD: "local-dev"
      SMS_PROVIDER_USERNAME: "local-dev"
      SMS_PROVIDER_PASSWORD: "local-dev"
      SMS_SENDER: egov
      SMS_GATEWAY_TO_USE: MSDG
      SMS_PROVIDER_CLASS: MSDG
      SMS_PROVIDER_REQUESTTYPE: POST
      SMS_PROVIDER_CONTENTTYPE: application/json
      STATE_LEVEL_TENANT_ID: pg
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx256m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18117:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/egov-notification-sms/actuator/health >/dev/null 2>&1 || wget -qO- http://localhost:8080/actuator/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.25"
    networks:
      - egov-network

  pdf-service:
    image: ${IMAGE_PDF_SERVICE:-egovio/pdf-service:multiarch-master-99a308d}
    container_name: pdf-service
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
      egov-filestore:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      KAFKA_BROKER_HOST: redpanda:9092
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /pdf-service
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: egov
      DB_USER: egov
      DB_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      EGOV_EXTERNAL_HOST: http://localhost:18000
      EGOV_HOST: http://localhost:18000
      DEFAULT_LOCALISATION_TENANT: pg
      STATE_LEVEL_TENANT_ID: pg
      EGOV_LOCALISATION_HOST: http://egov-localization:8096
      EGOV_FILESTORE_SERVICE_HOST: http://egov-filestore:8083
      MAX_NUMBER_PAGES: "80"
      DATA_CONFIG_URLS: file:///pdf-config/data-config/pt-receipt.json
      FORMAT_CONFIG_URLS: file:///pdf-config/format-config/pt-receipt.json
      JAVA_TOOL_OPTIONS: -Xms128m -Xmx256m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18119:8080"
    volumes:
      - ./configs/pdf-service/data-config:/pdf-config/data-config:ro
      - ./configs/pdf-service/format-config:/pdf-config/format-config:ro
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/ >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    networks:
      - egov-network

  studio-pdf:
    image: ${IMAGE_STUDIO_PDF:-egovio/studio-pdf:develop-16d12f1}
    container_name: studio-pdf
    depends_on:
      pgbouncer:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-localization:
        condition: service_healthy
      egov-filestore:
        condition: service_healthy
      egov-user:
        condition: service_healthy
      egov-workflow-v2:
        condition: service_healthy
      pdf-service:
        condition: service_healthy
      public-service:
        condition: service_healthy
    environment:
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: egov
      DB_USER: egov
      DB_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      KAFKA_BROKER_HOST: redpanda:9092
      EGOV_MDMS_HOST: http://egov-mdms-service:8094
      EGOV_PDF_HOST: http://pdf-service:8080
      EGOV_USER_HOST: http://egov-user:8107
      EGOV_WORKFLOW_HOST: http://egov-workflow-v2:8109
      EGOV_FILESTORE_SERVICE_HOST: http://egov-filestore:8083
      EGOV_LOCALIZATION_HOST: http://egov-localization:8096
      CONTEXT_PATH: /studio-pdf
      EGOV_HOST: http://localhost:18000
      PUBLIC_SERVICE_HOST: http://public-service:8080
      SERVER_PORT: "8080"
      NODE_ENV: production
    ports:
      - "18118:8080"
    healthcheck:
      test: ["CMD-SHELL", "node -e \"require('http').get('http://127.0.0.1:8080/',(r)=>{r.resume();r.on('end',()=>process.exit(0));}).on('error',()=>process.exit(1))\""]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    networks:
      - egov-network

  digit-studio:
    image: ${IMAGE_DIGIT_STUDIO:-egovio/digit-studio:studio-e60896a-833}
    container_name: digit-studio
    depends_on:
      kong:
        condition: service_healthy
    ports:
      - "18110:80"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:80/digit-studio/ >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.25"
    networks:
      - egov-network

  inbox:
    image: ${IMAGE_INBOX:-egovio/inbox:inbox-parallel-workflow-b5cd4a6}
    container_name: inbox
    env_file:
      - ./configs/studio/inbox.env
    depends_on:
      elasticsearch:
        condition: service_healthy
      redpanda:
        condition: service_healthy
      egov-mdms-service:
        condition: service_healthy
      egov-user:
        condition: service_healthy
      egov-workflow-v2:
        condition: service_healthy
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/egov?sslmode=disable
      SPRING_DATASOURCE_USERNAME: egov
      SPRING_DATASOURCE_PASSWORD: ${POSTGRES_PASSWORD:-egov123}
      SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE: "5"
      SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE: "2"
      SPRING_FLYWAY_ENABLED: "false"
      SPRING_KAFKA_BOOTSTRAP_SERVERS: redpanda:9092
      SERVER_PORT: "8080"
      SERVER_SERVLET_CONTEXT_PATH: /inbox
      WORKFLOW_HOST: http://egov-workflow-v2:8109
      EGOV_MDMS_HOST: http://egov-mdms-service:8094
      EGOV_USER_HOST: http://egov-user:8107
      EGOV_SEARCHER_HOST: http://egov-mdms-service:8094
      SERVICES_ESINDEXER_HOST: http://elasticsearch:9200
      WORKFLOW_PROCESS_SEARCH_PATH: egov-workflow-v2/egov-wf/process/_search
      WORKFLOW_BUSINESSSERVICE_SEARCH_PATH: egov-workflow-v2/egov-wf/businessservice/_search
      WORKFLOW_PROCESS_COUNT_PATH: egov-workflow-v2/egov-wf/process/_count
      WORKFLOW_PROCESS_STATUSCOUNT_PATH: egov-workflow-v2/egov-wf/process/_statuscount
      EGOV_VEHICLE_HOST: http://egov-mdms-service:8094
      EGOV_ES_USERNAME: ""
      EGOV_ES_PASSWORD: ""
      SERVICES_ESINDEXER_USERNAME: ""
      SERVICES_ESINDEXER_PASSWORD: ""
      WATER_ES_INDEX: pg-water-services
      SEWERAGE_ES_INDEX: pg-sewerage-services
      JAVA_OPTS: -Xms256m -Xmx512m
      JAVA_ARGS: -Dspring.profiles.active=monitoring
      JAVA_ENABLE_DEBUG: "true"
      JAVA_TOOL_OPTIONS: -Xms256m -Xmx512m
      OTEL_TRACES_EXPORTER: none
    ports:
      - "18120:8080"
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/inbox/actuator/health >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 180s
    deploy:
      resources:
        limits:
          memory: 768M
          cpus: "0.5"
    networks:
      - egov-network
"""
)
