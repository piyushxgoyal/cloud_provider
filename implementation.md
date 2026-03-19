Cloud Service Providers — Dataset Generation & Project Structure
Goal
Generate production-grade raw datasets with realistic dirty data for a multi-cloud (AWS/Azure/GCP) billing & operations use case, covering all 20 cleaning and 20 transformation scenarios from the PDF.

Project Structure
pro1/
├── data/
│   ├── raw/
│   │   ├── usage_billing.csv          ← Main table (10,000 rows)
│   │   ├── account_master.csv         ← Lookup (50 rows)
│   │   ├── sku_catalog.csv            ← Reference (~90 rows: 30 SKUs × 3 versions)
│   │   ├── resource_inventory.csv     ← S11 inventory validation (~300 resources)
│   │   ├── support_tickets.csv        ← S12 PII/severity (~200 rows)
│   │   ├── incidents.csv              ← S13/S19 incident linkage + SLA (~100 rows)
│   │   └── log_events.csv             ← S20 log time skew (~500 rows)
│   └── cleaned/
│       └── cleaned_usage_billing.csv
├── scenarios/                         ← Cleaning .py files (s01–s20)
├── validations/                       ← Validation .py files (v01–v20)
├── transforms/                        ← Transformation .py files (t01–t20)
├── feature_engineering.py
├── pipeline.py
├── cleaning_notebook.ipynb
├── transform_notebook.ipynb
├── tests/
│   ├── test_cleaning.py
│   └── test_transforms.py
└── Cloud_Service_Providers_UseCase.pdf
Dataset Schemas
1. usage_billing.csv — Main Table (10,000 rows)
IMPORTANT

Central table. Most cleaning scenarios operate on columns here.

Column	Type	Used By	Dirty Injection
Usage_ID	str	All	U0001–U10000, unique per row
Account_ID	str	S01	Canonical: AWS-ACCT-001, AZ-ACCT-021, GCP-ACCT-036. Dirty: mixed case (aws-acct-001), whitespace ( AWS-ACCT-001), wrong separators (AWS_ACCT_001, AWS--ACCT-001), ~2% unknown accounts not in master
Timestamp	str	S02	3 formats: ISO+tz (2026-01-15T10:30:00+05:30), ISO+Z (2026-01-15T10:30:00Z), slash (2026/01/15 10:30). ~2% nulls/NULL/N/A, ~1% garbage strings, ~0.5% out-of-range (1970, 2099)
Service	str	S03	Dirty: compute, COMPUTE, Compute etc.
SKU	str	S03	Realistic names like EC2-t3.medium. Dirty: wrong case (ec2-T3.Medium), underscores (EC2_t3_medium), ~2% unknown SKUs
Usage_Value	float	S04, S09	Numeric. ~500 rows with anomaly spikes (Z-score > 3 and IQR outliers)
Unit	str	S04	Dirty: sec, seconds, mins, minutes, hrs, hours, gb, GB, gigabytes, mb, MB
Cost	str	S05	Dirty: ₹1,200.50, $500.00, €200, commas, ~1% negative, ~1% zero
Currency	str	S05,S15	INR, USD, EUR, GBP
FX_Rate	float	S15	Rate to USD. ~625 null. Some wrong direction (INR with 84 instead of 0.012)
Region	str	S06	AWS: us east 1, US-EAST-1. Azure: East US, eastus. GCP: us central1. ~1% unresolvable
Resource_ID	str	S11	AWS: aws-ec2-001. Azure: az-vm-001. GCP: gcp-inst-001. Dirty: ~3% have wrong cloud prefix (e.g., an AWS account's row has az-vm-005 instead of aws-ec2-*), ~2% IDs not in resource_inventory.csv, ~1% zombie/deleted resources
Tag_Owner	str	S10	Clean: backend, frontend, security, data, devops, platform. Dirty: BE, FE, SEC, Backend, BACKEND, back-end
Tag_Env	str	S10	Clean: production, development, staging. Dirty: prod, Prod, PROD, prd, dev, DEV, stg
Charge_Type	str	S08	Dirty: billable, BILLABLE, free, FREE_TIER, credit, refund. ~2% contradictions (FREE_TIER + Cost > 500)
Purchase_Type	str	S17	Dirty: on-demand, On Demand, on_demand, reserved, Reserved, spot, SPOT
Department	str	S18	~7% invalid dept+project combos, ~5% unknown dept
Project	str	S18	Paired with Department for combo validation
CPU_Util	float	S16	0–100 for compute. NULL for storage/non-applicable (~47.5%). IDLE: <10, OVER: >80
Memory_Util	float	S16	Same pattern as CPU_Util
Incident_ID	str	S13	Reference to incidents.csv. ~80% null (most rows have no incident)
Ticket_ID	str	S12	Reference to support_tickets.csv. ~70% null (most usage rows don't generate support tickets)
Price_Version	str	S14	Dirty: V1, version1, ver-2, missing. Clean: v1/v2/v3 per month
SLA_Event	str	S19	Dirty booleans: true, True, 1, yes, false, 0, no
Log_Skew_Seconds	float	S20	Range: -120 to +120. ~50% flagged (>60s). Some nulls
S07 Duplicates: ~550 exact duplicate rows (same Account+TS+SKU + all fields identical).

Incident_ID vs Ticket_ID: These are independent. An incident is a system event (outage/degradation). A ticket is a customer support request. A row can have both, one, or neither. They are NOT linked to each other.

2. account_master.csv — Lookup (50 rows)
Column	Type	Notes
Account_ID	str	AWS-ACCT-001→AWS-ACCT-020, AZ-ACCT-021→AZ-ACCT-035, GCP-ACCT-036→GCP-ACCT-050
Account_Name	str	e.g., Acme Corp, TechStart Inc
Cloud_Provider	str	AWS, Azure, GCP
Parent_Account_ID	str	~10 parent groups for S15 cross-account consolidation
Default_Currency	str	INR, USD, EUR, GBP
3. sku_catalog.csv — Reference (~54 rows: 18 SKUs × 3 price versions)
Column	Type	Notes
SKU_ID	str	Realistic cloud names (see table below)
Service	str	Compute, Storage, Database
Cloud_Provider	str	AWS, Azure, GCP — derived from SKU name
SKU_Description	str	Human-readable description
Unit	str	seconds or GB
Price_Per_Unit	float	Base price
Price_Currency	str	INR, USD, EUR
Price_Version	str	v1, v2, v3
Effective_From	date	v1: 2026-01-01, v2: 2026-02-01, v3: 2026-03-01
Effective_To	date	v1: 2026-01-31, v2: 2026-02-28, v3: 2026-03-31
18 SKUs across 3 clouds, 3 services (Compute, Storage, Database — no serverless/networking/AI):

Cloud	Service	SKU	Unit	Description
AWS	Compute	EC2-t3.medium	seconds	2 vCPU, 4 GB
AWS	Compute	EC2-t3.large	seconds	2 vCPU, 8 GB
AWS	Compute	EC2-t3.xlarge	seconds	4 vCPU, 16 GB
AWS	Storage	S3-Standard	GB	General purpose
AWS	Storage	S3-IA	GB	Infrequent access
AWS	Database	RDS-db.m5.large	seconds	2 vCPU, 8 GB
Azure	Compute	VM-Standard_D2s	seconds	2 vCPU, 8 GB
Azure	Compute	VM-Standard_D4s	seconds	4 vCPU, 16 GB
Azure	Compute	VM-Standard_D8s	seconds	8 vCPU, 32 GB
Azure	Storage	Blob-Hot	GB	Frequently accessed
Azure	Storage	Blob-Cool	GB	Infrequently accessed
Azure	Database	SQLDb-S2	seconds	Standard tier
GCP	Compute	GCE-n1-standard-2	seconds	2 vCPU, 7.5 GB
GCP	Compute	GCE-n1-standard-4	seconds	4 vCPU, 15 GB
GCP	Compute	GCE-n1-standard-8	seconds	8 vCPU, 30 GB
GCP	Storage	GCS-Standard	GB	Multi-region
GCP	Storage	GCS-Nearline	GB	Backup/archive
GCP	Database	CloudSQL-db.standard-2	seconds	2 vCPU, 7.5 GB
4. resource_inventory.csv — S11 Validation (~300 rows)
NOTE

Used for proper S11 validation: billing Resource_ID must exist in this inventory. Catches fake IDs, deleted/zombie resources, and prefix mismatches.

Column	Type	Notes
Resource_ID	str	aws-ec2-001, az-vm-001, gcp-inst-001 etc.
Cloud_Provider	str	AWS, Azure, GCP
Account_ID	str	Owner account (canonical)
Service	str	Compute, Storage, etc.
Region	str	Canonical region
Status	str	active, terminated, zombie (~10% zombie/terminated for detection)
Created_At	date	Resource creation date
S11 validation logic:

Resource_ID must exist in inventory → if not: NOT_IN_INVENTORY
Cloud prefix must match row's provider → if not: PREFIX_MISMATCH
Status must not be zombie/terminated → if zombie: ZOMBIE_RESOURCE
5. support_tickets.csv — S12 (~200 rows)
Column	Type	Notes
Ticket_ID	str	T-001 to T-200
Account_ID	str	References account_master
Created_At	str	Dirty timestamps (same S02 patterns)
Severity	str	Dirty: sev1, SEV1, 1, high, P1, P2, low, medium
Ticket_Text	str	PII injected (~30%): emails, phones, IPs, names
Status	str	open, closed, in_progress
Resource_ID	str	Affected resource
6. incidents.csv — S13/S19 (~100 rows)
Column	Type	Notes
Incident_ID	str	INC-001 to INC-100
Account_ID	str	References account_master
Incident_Start	str	Dirty timestamps. ~10% null
Incident_End	str	Dirty timestamps. ~10% null
Affected_Service	str	Compute, Storage, etc.
Affected_Region	str	Dirty regions (same S06 patterns)
Severity	str	SEV1, SEV2, SEV3
Root_Cause	str	Brief description
SLA_Breach	str	Dirty booleans: true, True, 1, yes, false, 0, no
7. log_events.csv — S20 (~500 rows)
Column	Type	Notes
Log_ID	str	LOG-0001 to LOG-0500
Source	str	cloudwatch, azure_monitor, gcp_logging, syslog, app_log
Timestamp	str	Dirty timestamps with deliberate skew
Reference_Timestamp	str	"True" timestamp from trusted source
Skew_Seconds	float	-120 to +120, ~50% > 60s
Resource_ID	str	References resource in main table
Log_Level	str	INFO, WARN, ERROR, DEBUG
Message	str	Log message text
Reference Tables
S18 — Valid Department/Project Combos
Department	Valid Projects
ENGINEERING	ALPHA, BETA, PHOENIX
FINANCE	DELTA, EPSILON, NOVA
MARKETING	GAMMA, OMEGA
DATA_SCIENCE	ALPHA, PHOENIX, NOVA
SECURITY	BETA, DELTA
DEVOPS	ALPHA, BETA, PHOENIX, GAMMA
PRODUCT	OMEGA, EPSILON
HR	DELTA, GAMMA
LEGAL	EPSILON, NOVA
OPERATIONS	ALPHA, DELTA, GAMMA
S14 — Price Version Effective Dates
Version	From	To	Month
v1	2026-01-01	2026-01-31	January
v2	2026-02-01	2026-02-28	February
v3	2026-03-01	2026-03-31	March
Canonical Regions (15 total)
Cloud	Region	Carbon (g CO₂/kWh)	Location
AWS	us-east-1	379.6	Virginia
AWS	eu-west-1	316.2	Ireland
AWS	ap-south-1	708.2	Mumbai
AWS	us-west-2	102.8	Oregon
AWS	ap-southeast-1	408.0	Singapore
Azure	eastus	379.6	Virginia
Azure	westeurope	268.0	Netherlands
Azure	centralindia	708.2	Pune
Azure	canadacentral	26.0	Toronto
Azure	southeastasia	408.0	Singapore
GCP	us-central1	394.5	Iowa
GCP	europe-west1	158.0	Belgium
GCP	asia-south1	708.2	Mumbai
GCP	us-west1	54.0	Oregon
GCP	asia-southeast1	408.0	Singapore
S15 — FX Rates
Currency	To USD	Notes
USD	1.00	Base
INR	0.012	~₹84/USD
EUR	1.08	~€1 = $1.08
GBP	1.27	~£1 = $1.27
Verification Plan
Run python generate_dataset.py → all 7 CSVs created with correct row counts
Spot-check dirty injection per scenario
Verify duplicates (~550), FX nulls (~625), PII in tickets, anomaly spikes (~500)
