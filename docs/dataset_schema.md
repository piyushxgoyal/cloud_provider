# Dataset Schema — Cloud Service Providers

> Data dictionary for all raw datasets. Use this as reference for cleaning & transformation logic.

---

## 1. `usage_billing.csv` — Main Billing Table (~10,550 rows)

| Column | Type | Scenario | Description |
|--------|------|----------|-------------|
| `Usage_ID` | str | — | Unique row ID (`U00001`–`U10000`) |
| `Account_ID` | str | S01 | Cloud account. Dirty: mixed case, whitespace, wrong separators |
| `Timestamp` | str | S02 | Event time. Dirty: 5+ formats, nulls, garbage, out-of-range |
| `Service` | str | S03 | `Compute`/`Storage`/`Database`. Dirty: case variations |
| `SKU` | str | S03 | e.g., `EC2-t3.medium`. Dirty: case, underscores, unknowns |
| `Usage_Value` | float | S04,S09 | Numeric usage. ~500 rows have anomaly spikes |
| `Unit` | str | S04 | Dirty: `sec`/`seconds`/`mins`/`hours`/`gb`/`MB`/`megabytes` |
| `Cost` | str | S05 | Dirty: `₹1,200.50`, `$500`, commas, negatives, zeros |
| `Currency` | str | S05,S15 | Dirty: `inr`/`dollar`/`Indian Rupee`/`pound` |
| `FX_Rate` | float | S15 | To-USD rate. ~625 null, some wrong direction |
| `Region` | str | S06 | Dirty: `us east 1`/`US-EAST-1`/`eastus2` |
| `Resource_ID` | str | S11 | `aws-ec2-001`/`az-vm-001`/`gcp-inst-001`. Dirty: prefix mismatches, missing from inventory |
| `Tag_Owner` | str | S10 | Dirty: `BE`/`FE`/`BACKEND`/`back-end` |
| `Tag_Env` | str | S10 | Dirty: `prod`/`PROD`/`prd`/`DEV`/`stg` |
| `Charge_Type` | str | S08 | Dirty: `billable`/`FREE_TIER`/`credit`/`true`/`BILLABLE` |
| `Purchase_Type` | str | S17 | Dirty: `on-demand`/`On Demand`/`RESERVED`/`RI`/`SPOT` |
| `Department` | str | S18 | ~7% invalid combos with Project, ~5% unknown |
| `Project` | str | S18 | Paired with Department for combo validation |
| `CPU_Util` | float | S16 | 0–100 for Compute/Database. NULL for Storage |
| `Memory_Util` | float | S16 | Same as CPU_Util |
| `Incident_ID` | str | S13 | FK → `incidents.csv`. ~80% null |
| `Ticket_ID` | str | S12 | FK → `support_tickets.csv`. ~70% null |
| `Price_Version` | str | S14 | Dirty: `V1`/`version1`/`ver-2`/null. Clean: `v1`/`v2`/`v3` |
| `SLA_Event` | str | S19 | Dirty booleans: `true`/`1`/`yes`/`false`/`0`/`no` |
| `Log_Skew_Seconds` | float | S20 | -120 to +120. ~50% flagged (>60s) |

**S07:** ~550 exact duplicate rows included.

---

## 2. `account_master.csv` — Account Lookup (50 rows)

| Column | Type | Description |
|--------|------|-------------|
| `Account_ID` | str | Canonical: `AWS-ACCT-001`..`GCP-ACCT-050` |
| `Account_Name` | str | Company name |
| `Cloud_Provider` | str | `AWS` / `Azure` / `GCP` |
| `Parent_Account_ID` | str | 10 parent groups for S15 consolidation |
| `Default_Currency` | str | `INR`/`USD`/`EUR`/`GBP` |

---

## 3. `sku_catalog.csv` — Price Reference (54 rows)

| Column | Type | Description |
|--------|------|-------------|
| `SKU_ID` | str | e.g., `EC2-t3.medium`, `VM-Standard_D2s` |
| `Service` | str | `Compute`/`Storage`/`Database` |
| `Cloud_Provider` | str | `AWS`/`Azure`/`GCP` |
| `SKU_Description` | str | Human-readable |
| `Unit` | str | `seconds` or `GB` |
| `Price_Per_Unit` | float | Base price in USD |
| `Price_Currency` | str | `USD` |
| `Price_Version` | str | `v1`/`v2`/`v3` |
| `Effective_From` | date | v1: Jan, v2: Feb, v3: Mar 2026 |
| `Effective_To` | date | End of respective month |

---

## 4. `resource_inventory.csv` — Resource Registry (~287 rows)

| Column | Type | Description |
|--------|------|-------------|
| `Resource_ID` | str | `aws-ec2-001`, `az-vm-001`, `gcp-inst-001` |
| `Cloud_Provider` | str | `AWS`/`Azure`/`GCP` |
| `Account_ID` | str | Owner account |
| `Service` | str | Service type |
| `Region` | str | Canonical region |
| `Status` | str | `active`/`terminated`/`zombie` (~10% non-active) |
| `Created_At` | date | Resource creation date |

---

## 5. `support_tickets.csv` — Support Data (200 rows)

| Column | Type | Description |
|--------|------|-------------|
| `Ticket_ID` | str | `T-001`→`T-200` |
| `Account_ID` | str | Account reference |
| `Created_At` | str | Dirty timestamps |
| `Severity` | str | Dirty: `sev1`/`SEV1`/`P1`/`high`/`1` |
| `Ticket_Text` | str | ~30% contain PII (emails, phones, IPs, names) |
| `Status` | str | `open`/`closed`/`in_progress` |
| `Resource_ID` | str | Affected resource |

---

## 6. `incidents.csv` — Incident Records (100 rows)

| Column | Type | Description |
|--------|------|-------------|
| `Incident_ID` | str | `INC-001`→`INC-100` |
| `Account_ID` | str | Account reference |
| `Incident_Start` | str | Dirty timestamps. ~10% null |
| `Incident_End` | str | Dirty timestamps. ~10% null |
| `Affected_Service` | str | `Compute`/`Storage`/`Database` |
| `Affected_Region` | str | Dirty regions |
| `Severity` | str | `SEV1`/`SEV2`/`SEV3` |
| `Root_Cause` | str | Brief description |
| `SLA_Breach` | str | Dirty booleans |

---

## 7. `log_events.csv` — Log Data (500 rows)

| Column | Type | Description |
|--------|------|-------------|
| `Log_ID` | str | `LOG-0001`→`LOG-0500` |
| `Source` | str | `cloudwatch`/`azure_monitor`/`gcp_logging`/`syslog`/`app_log` |
| `Timestamp` | str | Dirty, with deliberate time skew |
| `Reference_Timestamp` | str | Ground-truth time (trusted) |
| `Skew_Seconds` | float | -120 to +120. ~50% > 60s |
| `Resource_ID` | str | Resource reference |
| `Log_Level` | str | `INFO`/`WARN`/`ERROR`/`DEBUG` |
| `Message` | str | Log message |

---

## Canonical Values Reference

### Regions (15)
`us-east-1`, `eu-west-1`, `ap-south-1`, `us-west-2`, `ap-southeast-1`,
`eastus`, `westeurope`, `centralindia`, `canadacentral`, `southeastasia`,
`us-central1`, `europe-west1`, `asia-south1`, `us-west1`, `asia-southeast1`

### Dept/Project Valid Combos
| Department | Valid Projects |
|------------|---------------|
| ENGINEERING | ALPHA, BETA, PHOENIX |
| FINANCE | DELTA, EPSILON, NOVA |
| MARKETING | GAMMA, OMEGA |
| DATA_SCIENCE | ALPHA, PHOENIX, NOVA |
| SECURITY | BETA, DELTA |
| DEVOPS | ALPHA, BETA, PHOENIX, GAMMA |
| PRODUCT | OMEGA, EPSILON |
| HR | DELTA, GAMMA |
| LEGAL | EPSILON, NOVA |
| OPERATIONS | ALPHA, DELTA, GAMMA |

### FX Rates (to USD)
`USD=1.0`, `INR=0.012`, `EUR=1.08`, `GBP=1.27`
