"""
Cloud Service Providers — Raw Dataset Generator
Generates 7 CSVs with realistic dirty data for 20 cleaning scenarios.
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'raw')
os.makedirs(OUT_DIR, exist_ok=True)

N_ROWS = 10_000
N_ACCOUNTS = 50
N_TICKETS = 200
N_INCIDENTS = 100
N_RESOURCES = 300
N_LOGS = 500
N_DUPLICATES = 550

# ═══════════════════════════════════════════════════════════════
#  REFERENCE DATA
# ═══════════════════════════════════════════════════════════════

# ── Accounts ──────────────────────────────────────────────────
ACCOUNTS_AWS   = [f"AWS-ACCT-{i:03d}" for i in range(1, 21)]    # 20
ACCOUNTS_AZ    = [f"AZ-ACCT-{i:03d}" for i in range(21, 36)]    # 15
ACCOUNTS_GCP   = [f"GCP-ACCT-{i:03d}" for i in range(36, 51)]   # 15
ALL_ACCOUNTS   = ACCOUNTS_AWS + ACCOUNTS_AZ + ACCOUNTS_GCP

CLOUD_MAP = {}
for a in ACCOUNTS_AWS:  CLOUD_MAP[a] = 'AWS'
for a in ACCOUNTS_AZ:   CLOUD_MAP[a] = 'Azure'
for a in ACCOUNTS_GCP:  CLOUD_MAP[a] = 'GCP'

ACCOUNT_NAMES = [
    "Acme Corp", "TechStart Inc", "DataWave", "CloudNine", "PixelForge",
    "NovaSoft", "OptiCore", "ByteShift", "SkyLabs", "PulseTech",
    "NeuralPath", "CodeSphere", "StackBridge", "InfraFlow", "AppVelocity",
    "MetricEdge", "ZenOps", "LogicLayer", "VaultSync", "EdgeMatrix",
    "CyberPulse", "QuantumLeap", "FlexGrid", "ShieldNet", "CoreDynamics",
    "StreamForge", "DataNest", "CloudPeak", "SynergyAI", "TitanOps",
    "MapleCode", "PineStack", "OceanData", "AlphaGrid", "BetaWorks",
    "GammaLabs", "DeltaTech", "EpsilonIO", "ZetaCloud", "EtaDigital",
    "ThetaSys", "IotaSoft", "KappaNet", "LambdaOps", "MuDevs",
    "NuTech", "XiSystems", "OmicronAI", "PiData", "RhoLabs"
]

# Parent accounts for cross-account consolidation (S15)
PARENT_ACCOUNTS = {
    "PARENT-001": ALL_ACCOUNTS[0:5],
    "PARENT-002": ALL_ACCOUNTS[5:10],
    "PARENT-003": ALL_ACCOUNTS[10:15],
    "PARENT-004": ALL_ACCOUNTS[15:20],
    "PARENT-005": ALL_ACCOUNTS[20:25],
    "PARENT-006": ALL_ACCOUNTS[25:30],
    "PARENT-007": ALL_ACCOUNTS[30:35],
    "PARENT-008": ALL_ACCOUNTS[35:40],
    "PARENT-009": ALL_ACCOUNTS[40:45],
    "PARENT-010": ALL_ACCOUNTS[45:50],
}

ACCT_TO_PARENT = {}
for parent, children in PARENT_ACCOUNTS.items():
    for child in children:
        ACCT_TO_PARENT[child] = parent

CURRENCIES = ['INR', 'USD', 'EUR', 'GBP']
ACCT_CURRENCY = {a: random.choice(CURRENCIES) for a in ALL_ACCOUNTS}

# ── SKUs ──────────────────────────────────────────────────────
SKUS = {
    'AWS': {
        'Compute':  ['EC2-t3.medium', 'EC2-t3.large', 'EC2-t3.xlarge'],
        'Storage':  ['S3-Standard', 'S3-IA'],
        'Database': ['RDS-db.m5.large'],
    },
    'Azure': {
        'Compute':  ['VM-Standard_D2s', 'VM-Standard_D4s', 'VM-Standard_D8s'],
        'Storage':  ['Blob-Hot', 'Blob-Cool'],
        'Database': ['SQLDb-S2'],
    },
    'GCP': {
        'Compute':  ['GCE-n1-standard-2', 'GCE-n1-standard-4', 'GCE-n1-standard-8'],
        'Storage':  ['GCS-Standard', 'GCS-Nearline'],
        'Database': ['CloudSQL-db.standard-2'],
    },
}

# Flat list of all canonical SKUs
ALL_SKUS = []
SKU_SERVICE = {}
SKU_CLOUD = {}
SKU_UNIT = {}
for cloud, services in SKUS.items():
    for service, skus in services.items():
        for sku in skus:
            ALL_SKUS.append(sku)
            SKU_SERVICE[sku] = service
            SKU_CLOUD[sku] = cloud
            SKU_UNIT[sku] = 'seconds' if service in ('Compute', 'Database') else 'GB'

# ── Regions ───────────────────────────────────────────────────
REGIONS = {
    'AWS':   ['us-east-1', 'eu-west-1', 'ap-south-1', 'us-west-2', 'ap-southeast-1'],
    'Azure': ['eastus', 'westeurope', 'centralindia', 'canadacentral', 'southeastasia'],
    'GCP':   ['us-central1', 'europe-west1', 'asia-south1', 'us-west1', 'asia-southeast1'],
}

CARBON_INTENSITY = {
    'us-east-1': 379.6, 'eu-west-1': 316.2, 'ap-south-1': 708.2,
    'us-west-2': 102.8, 'ap-southeast-1': 408.0,
    'eastus': 379.6, 'westeurope': 268.0, 'centralindia': 708.2,
    'canadacentral': 26.0, 'southeastasia': 408.0,
    'us-central1': 394.5, 'europe-west1': 158.0, 'asia-south1': 708.2,
    'us-west1': 54.0, 'asia-southeast1': 408.0,
}

# ── FX Rates ──────────────────────────────────────────────────
FX_TO_USD = {'USD': 1.0, 'INR': 0.012, 'EUR': 1.08, 'GBP': 1.27}

# ── Departments & Projects (S18) ─────────────────────────────
VALID_COMBOS = {
    'ENGINEERING':  ['ALPHA', 'BETA', 'PHOENIX'],
    'FINANCE':      ['DELTA', 'EPSILON', 'NOVA'],
    'MARKETING':    ['GAMMA', 'OMEGA'],
    'DATA_SCIENCE': ['ALPHA', 'PHOENIX', 'NOVA'],
    'SECURITY':     ['BETA', 'DELTA'],
    'DEVOPS':       ['ALPHA', 'BETA', 'PHOENIX', 'GAMMA'],
    'PRODUCT':      ['OMEGA', 'EPSILON'],
    'HR':           ['DELTA', 'GAMMA'],
    'LEGAL':        ['EPSILON', 'NOVA'],
    'OPERATIONS':   ['ALPHA', 'DELTA', 'GAMMA'],
}

ALL_DEPTS    = list(VALID_COMBOS.keys())
ALL_PROJECTS = list(set(p for ps in VALID_COMBOS.values() for p in ps))

# ── Price Versions (S14) ─────────────────────────────────────
PRICE_VERSIONS = {
    'v1': ('2026-01-01', '2026-01-31'),
    'v2': ('2026-02-01', '2026-02-28'),
    'v3': ('2026-03-01', '2026-03-31'),
}

# ── Tag values (S10) ─────────────────────────────────────────
TAG_OWNERS_CLEAN = ['backend', 'frontend', 'security', 'data', 'devops', 'platform']
TAG_ENVS_CLEAN   = ['production', 'development', 'staging']

# ── PII data for tickets (S12) ───────────────────────────────
PII_NAMES  = ["John Doe", "Jane Smith", "Raj Patel", "Maria Garcia", "Wei Chen",
              "Priya Sharma", "Ahmed Khan", "Sarah Johnson", "Yuki Tanaka", "Luis Rivera"]
PII_EMAILS = [f"{n.lower().replace(' ', '.')}@company.com" for n in PII_NAMES]
PII_PHONES = ["+91-9876543210", "+1-555-012-3456", "+44-7911-123456",
              "+91-8765432109", "+1-555-987-6543"]
PII_IPS    = ["192.168.1.100", "10.0.0.55", "172.16.0.1", "192.168.0.42", "10.10.10.10"]

TICKET_TEMPLATES = [
    "Instance {} is unreachable. Contact {} at {} or call {}. IP: {}",
    "Storage latency on {}. Reported by {} ({}). System IP: {}. Phone: {}",
    "Database {} timeout. Engineer {} ({}) investigating. Host: {}. Alt contact: {}",
    "High CPU on {}. {} ({}) filed this. Server: {}. Callback: {}",
    "Permission denied for {}. {} ({}) needs access. Node: {}. Contact: {}",
]

# ── Incident root causes ─────────────────────────────────────
ROOT_CAUSES = [
    "Network partition in availability zone",
    "Disk I/O saturation on storage cluster",
    "Memory exhaustion from runaway process",
    "DNS resolution failure",
    "Certificate expiry on load balancer",
    "Auto-scaling misconfiguration",
    "Database connection pool exhaustion",
    "Kernel panic on hypervisor host",
    "BGP route leak from upstream provider",
    "Deployment rollback failure",
]

# ═══════════════════════════════════════════════════════════════
#  DIRTY INJECTION HELPERS
# ═══════════════════════════════════════════════════════════════

def dirty_account(canonical):
    """S01: Inject account ID dirt."""
    r = random.random()
    if r < 0.03:   return canonical.lower()                       # lowercase
    if r < 0.06:   return f"  {canonical} "                       # whitespace
    if r < 0.09:   return canonical.replace('-', '_')             # underscores
    if r < 0.11:   return canonical.replace('-ACCT-', '--ACCT-')  # double dash
    if r < 0.13:   return canonical[4:]                           # missing prefix
    return canonical

def dirty_timestamp(dt):
    """S02: Inject timestamp format variations."""
    r = random.random()
    if r < 0.02:   return None           # null
    if r < 0.03:   return 'NULL'         # literal NULL
    if r < 0.035:  return 'N/A'          # N/A
    if r < 0.04:   return 'garbage_ts'   # garbage string
    if r < 0.045:  return '1970-01-01T00:00:00Z'   # epoch
    if r < 0.05:   return '2099-12-31T23:59:59Z'   # far future

    # Format variations
    offsets = ['+05:30', '+00:00', '-08:00', '-05:00', '+01:00']
    if r < 0.35:
        tz = random.choice(offsets)
        return dt.strftime(f'%Y-%m-%dT%H:%M:%S') + tz
    if r < 0.55:
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    if r < 0.70:
        return dt.strftime('%Y/%m/%d %H:%M')
    if r < 0.80:
        return dt.strftime('%d-%m-%Y %H:%M:%S')
    if r < 0.90:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    # Missing hyphen style
    return dt.strftime('%Y-%m%d %H:%M')

def dirty_sku(canonical):
    """S03: Inject SKU name variations."""
    r = random.random()
    if r < 0.02:   return f"UNKNOWN-SKU-{random.randint(100,999)}"
    if r < 0.10:   return canonical.lower()
    if r < 0.18:   return canonical.upper()
    if r < 0.25:   return canonical.replace('-', '_')
    if r < 0.30:   return canonical.replace('.', '_')
    return canonical

def dirty_unit(canonical_unit):
    """S04: Inject unit variations."""
    if canonical_unit == 'seconds':
        return random.choice(['sec', 'seconds', 'secs', 'second',
                               'mins', 'minutes', 'min',
                               'hrs', 'hours', 'hr', 'hour'])
    else:  # GB
        return random.choice(['gb', 'GB', 'gigabytes', 'Gb',
                               'mb', 'MB', 'megabytes'])

def dirty_cost(cost_val, currency):
    """S05: Inject cost formatting variations."""
    r = random.random()
    symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    sym = symbols.get(currency, '')

    if r < 0.01:   return str(-abs(cost_val))      # negative
    if r < 0.02:   return '0'                       # zero
    if r < 0.20:   return f"{sym}{cost_val:,.2f}"   # symbol + comma
    if r < 0.35:   return f"{cost_val:,.2f}"        # comma only
    return f"{cost_val:.2f}"                        # plain

def dirty_currency(canonical):
    """S05/S15: Inject currency name variations."""
    r = random.random()
    variants = {
        'INR': ['inr', 'Inr', 'Indian Rupee', 'INR'],
        'USD': ['usd', 'dollar', 'Us Dollar', 'USD'],
        'EUR': ['eur', 'euro', 'Euro', 'EUR'],
        'GBP': ['gbp', 'pound', 'Pound', 'GBP'],
    }
    return random.choice(variants.get(canonical, [canonical]))

def dirty_region(cloud):
    """S06: Inject region variations."""
    canonical = random.choice(REGIONS[cloud])
    r = random.random()

    if r < 0.01:   return f"unknown-region-{random.randint(1,9)}"  # unresolvable

    if cloud == 'AWS':
        if r < 0.15: return canonical.replace('-', ' ')       # us east 1
        if r < 0.25: return canonical.upper()                 # US-EAST-1
        if r < 0.30: return canonical.replace('-', '')[:4]    # usea
        return canonical
    elif cloud == 'Azure':
        if r < 0.15: return canonical.replace('east', 'East ') # East us
        if r < 0.25: return canonical.upper()                  # EASTUS
        if r < 0.30: return canonical + '2'                    # eastus2
        return canonical
    else:  # GCP
        if r < 0.15: return canonical.replace('-', ' ')
        if r < 0.25: return canonical.upper()
        return canonical

def dirty_tag_owner(clean_val):
    """S10: Inject tag owner variations."""
    abbrevs = {'backend': ['BE', 'Backend', 'BACKEND', 'back-end'],
               'frontend': ['FE', 'Frontend', 'FRONTEND', 'front-end'],
               'security': ['SEC', 'Security', 'SECURITY', 'sec-team'],
               'data': ['DATA', 'Data', 'data-team'],
               'devops': ['DEVOPS', 'DevOps', 'dev-ops'],
               'platform': ['PLATFORM', 'Platform', 'plat']}
    r = random.random()
    if r < 0.30: return random.choice(abbrevs.get(clean_val, [clean_val]))
    return clean_val

def dirty_tag_env(clean_val):
    """S10: Inject tag env variations."""
    abbrevs = {'production': ['prod', 'Prod', 'PROD', 'prd'],
               'development': ['dev', 'DEV', 'Dev', 'develop'],
               'staging': ['stg', 'STG', 'Staging', 'stage']}
    r = random.random()
    if r < 0.30: return random.choice(abbrevs.get(clean_val, [clean_val]))
    return clean_val

def dirty_charge_type():
    """S08: Inject charge type variations."""
    clean_vals = ['billable', 'billable', 'billable', 'billable',  # 70% billable
                  'free', 'credit', 'refund']
    base = random.choice(clean_vals)
    variants = {
        'billable': ['billable', 'BILLABLE', 'Billable', 'true', 'True', 'TRUE'],
        'free':     ['free', 'FREE_TIER', 'Free Tier', 'free_tier'],
        'credit':   ['credit', 'CREDIT', 'Credit'],
        'refund':   ['refund', 'REFUND', 'Refund'],
    }
    return random.choice(variants[base])

def dirty_purchase_type():
    """S17: Inject purchase type variations."""
    clean_vals = ['on-demand', 'on-demand', 'on-demand',  # 60% on-demand
                  'reserved', 'reserved', 'spot']
    base = random.choice(clean_vals)
    variants = {
        'on-demand': ['on-demand', 'On Demand', 'on_demand', 'ON-DEMAND', 'OnDemand'],
        'reserved':  ['reserved', 'Reserved', 'RESERVED', 'RI'],
        'spot':      ['spot', 'SPOT', 'Spot'],
    }
    return random.choice(variants[base])

def dirty_sla_event():
    """S19: Inject SLA event boolean variations."""
    r = random.random()
    if r < 0.80:  # 80% false
        return random.choice(['false', 'False', 'FALSE', '0', 'no', 'No', 'NO'])
    return random.choice(['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES'])

def dirty_price_version(month):
    """S14: Inject price version variations. Some rows get wrong version."""
    correct = {1: 'v1', 2: 'v2', 3: 'v3'}[month]
    r = random.random()
    if r < 0.02:   return None                     # missing
    if r < 0.06:   return correct.upper()           # V1
    if r < 0.10:   return f"version{correct[-1]}"   # version1
    if r < 0.14:   return f"ver-{correct[-1]}"      # ver-1
    if r < 0.18:   # wrong version (dirty for S14 validation)
        wrong = random.choice([v for v in ['v1', 'v2', 'v3'] if v != correct])
        return wrong
    return correct

def dirty_severity():
    """S12: Inject severity variations."""
    return random.choice(['sev1', 'SEV1', '1', 'high', 'P1',
                           'sev2', 'SEV2', '2', 'medium', 'P2',
                           'sev3', 'SEV3', '3', 'low', 'P3'])

def get_dept_project():
    """S18: Generate dept/project combos. ~7% invalid, ~5% unknown."""
    r = random.random()
    if r < 0.05:  # unknown dept or project
        if random.random() < 0.5:
            return ('UNKNOWN_DEPT', random.choice(ALL_PROJECTS))
        else:
            return (random.choice(ALL_DEPTS), 'UNKNOWN_PROJECT')
    if r < 0.12:  # invalid combo
        dept = random.choice(ALL_DEPTS)
        invalid_projects = [p for p in ALL_PROJECTS if p not in VALID_COMBOS[dept]]
        if invalid_projects:
            return (dept, random.choice(invalid_projects))
    # valid combo
    dept = random.choice(ALL_DEPTS)
    proj = random.choice(VALID_COMBOS[dept])
    # dirty formatting
    dept_out = random.choice([dept, dept.title(), dept.lower()])
    proj_out = random.choice([proj, proj.title(), proj.lower()])
    return (dept_out, proj_out)


# ═══════════════════════════════════════════════════════════════
#  1. ACCOUNT MASTER
# ═══════════════════════════════════════════════════════════════
def generate_account_master():
    print("  Generating account_master.csv ...")
    rows = []
    for i, acct in enumerate(ALL_ACCOUNTS):
        rows.append({
            'Account_ID':        acct,
            'Account_Name':      ACCOUNT_NAMES[i],
            'Cloud_Provider':    CLOUD_MAP[acct],
            'Parent_Account_ID': ACCT_TO_PARENT[acct],
            'Default_Currency':  ACCT_CURRENCY[acct],
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'account_master.csv'), index=False)
    print(f"    ✅ account_master.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  2. SKU CATALOG
# ═══════════════════════════════════════════════════════════════
def generate_sku_catalog():
    print("  Generating sku_catalog.csv ...")
    rows = []
    desc_map = {
        'EC2-t3.medium': '2 vCPU, 4 GB RAM', 'EC2-t3.large': '2 vCPU, 8 GB RAM',
        'EC2-t3.xlarge': '4 vCPU, 16 GB RAM',
        'S3-Standard': 'General purpose storage', 'S3-IA': 'Infrequent access storage',
        'RDS-db.m5.large': '2 vCPU, 8 GB RAM DB',
        'VM-Standard_D2s': '2 vCPU, 8 GB RAM', 'VM-Standard_D4s': '4 vCPU, 16 GB RAM',
        'VM-Standard_D8s': '8 vCPU, 32 GB RAM',
        'Blob-Hot': 'Frequently accessed storage', 'Blob-Cool': 'Infrequent access storage',
        'SQLDb-S2': 'Standard tier database',
        'GCE-n1-standard-2': '2 vCPU, 7.5 GB RAM', 'GCE-n1-standard-4': '4 vCPU, 15 GB RAM',
        'GCE-n1-standard-8': '8 vCPU, 30 GB RAM',
        'GCS-Standard': 'Multi-region storage', 'GCS-Nearline': 'Backup/archive storage',
        'CloudSQL-db.standard-2': '2 vCPU, 7.5 GB RAM DB',
    }
    for sku in ALL_SKUS:
        base_price = round(random.uniform(0.001, 0.05), 4)
        for ver, (eff_from, eff_to) in PRICE_VERSIONS.items():
            # Price increases ~5% per version
            multiplier = {'v1': 1.0, 'v2': 1.05, 'v3': 1.10}[ver]
            rows.append({
                'SKU_ID':          sku,
                'Service':         SKU_SERVICE[sku],
                'Cloud_Provider':  SKU_CLOUD[sku],
                'SKU_Description': desc_map.get(sku, sku),
                'Unit':            SKU_UNIT[sku],
                'Price_Per_Unit':  round(base_price * multiplier, 4),
                'Price_Currency':  'USD',
                'Price_Version':   ver,
                'Effective_From':  eff_from,
                'Effective_To':    eff_to,
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'sku_catalog.csv'), index=False)
    print(f"    ✅ sku_catalog.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  3. RESOURCE INVENTORY
# ═══════════════════════════════════════════════════════════════
def generate_resource_inventory():
    print("  Generating resource_inventory.csv ...")
    rows = []
    res_id = 1
    for acct in ALL_ACCOUNTS:
        cloud = CLOUD_MAP[acct]
        n_resources = random.randint(4, 8)
        for _ in range(n_resources):
            prefix = {'AWS': 'aws-ec2', 'Azure': 'az-vm', 'GCP': 'gcp-inst'}[cloud]
            service = random.choice(list(SKUS[cloud].keys()))
            region = random.choice(REGIONS[cloud])

            # ~10% zombie/terminated
            status = 'active'
            if random.random() < 0.07:
                status = 'zombie'
            elif random.random() < 0.05:
                status = 'terminated'

            rows.append({
                'Resource_ID':    f"{prefix}-{res_id:03d}",
                'Cloud_Provider': cloud,
                'Account_ID':     acct,
                'Service':        service,
                'Region':         region,
                'Status':         status,
                'Created_At':     (datetime(2025, 6, 1) + timedelta(days=random.randint(0, 200))).strftime('%Y-%m-%d'),
            })
            res_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'resource_inventory.csv'), index=False)
    print(f"    ✅ resource_inventory.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  4. INCIDENTS
# ═══════════════════════════════════════════════════════════════
def generate_incidents():
    print("  Generating incidents.csv ...")
    rows = []
    for i in range(1, N_INCIDENTS + 1):
        acct = random.choice(ALL_ACCOUNTS)
        cloud = CLOUD_MAP[acct]
        start_dt = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        duration = timedelta(hours=random.randint(1, 48))
        end_dt = start_dt + duration

        # ~10% null start/end
        start_str = dirty_timestamp(start_dt) if random.random() > 0.10 else None
        end_str = dirty_timestamp(end_dt) if random.random() > 0.10 else None

        rows.append({
            'Incident_ID':     f"INC-{i:03d}",
            'Account_ID':      acct,
            'Incident_Start':  start_str,
            'Incident_End':    end_str,
            'Affected_Service': random.choice(['Compute', 'Storage', 'Database']),
            'Affected_Region': dirty_region(cloud),
            'Severity':        random.choice(['SEV1', 'SEV2', 'SEV3']),
            'Root_Cause':      random.choice(ROOT_CAUSES),
            'SLA_Breach':      dirty_sla_event(),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'incidents.csv'), index=False)
    print(f"    ✅ incidents.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  5. SUPPORT TICKETS
# ═══════════════════════════════════════════════════════════════
def generate_support_tickets(resource_df):
    print("  Generating support_tickets.csv ...")
    rows = []
    resource_ids = resource_df['Resource_ID'].tolist()

    for i in range(1, N_TICKETS + 1):
        acct = random.choice(ALL_ACCOUNTS)
        cloud = CLOUD_MAP[acct]
        created = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23)
        )

        # Build ticket text — ~30% have PII
        res_id = random.choice(resource_ids)
        name = random.choice(PII_NAMES)
        email = random.choice(PII_EMAILS)
        phone = random.choice(PII_PHONES)
        ip = random.choice(PII_IPS)
        template = random.choice(TICKET_TEMPLATES)

        if random.random() < 0.30:
            text = template.format(res_id, name, email, phone, ip)
        else:
            text = f"Issue with resource {res_id}. Service degraded. Investigating."

        rows.append({
            'Ticket_ID':   f"T-{i:03d}",
            'Account_ID':  acct,
            'Created_At':  dirty_timestamp(created),
            'Severity':    dirty_severity(),
            'Ticket_Text': text,
            'Status':      random.choice(['open', 'closed', 'in_progress']),
            'Resource_ID': res_id,
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'support_tickets.csv'), index=False)
    print(f"    ✅ support_tickets.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  6. LOG EVENTS
# ═══════════════════════════════════════════════════════════════
def generate_log_events(resource_df):
    print("  Generating log_events.csv ...")
    sources = ['cloudwatch', 'azure_monitor', 'gcp_logging', 'syslog', 'app_log']
    levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    messages = [
        "Connection timeout after 30s",
        "Disk utilization exceeded 90%",
        "Health check passed successfully",
        "Auto-scaling triggered: adding 2 instances",
        "Certificate renewal completed",
        "Rate limit exceeded for API endpoint",
        "Memory allocation failure on node",
        "Backup completed successfully",
        "Failed to resolve DNS for endpoint",
        "Service restarted after crash",
    ]

    resource_ids = resource_df['Resource_ID'].tolist()
    rows = []
    for i in range(1, N_LOGS + 1):
        ref_dt = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        # Skew: -120 to +120 seconds, ~50% > 60s
        if random.random() < 0.50:
            skew = random.uniform(60, 120) * random.choice([-1, 1])
        else:
            skew = random.uniform(-60, 60)

        # ~5% null skew
        skew_val = round(skew, 1) if random.random() > 0.05 else None

        skewed_dt = ref_dt + timedelta(seconds=skew)

        rows.append({
            'Log_ID':               f"LOG-{i:04d}",
            'Source':               random.choice(sources),
            'Timestamp':            dirty_timestamp(skewed_dt),
            'Reference_Timestamp':  ref_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'Skew_Seconds':         skew_val,
            'Resource_ID':          random.choice(resource_ids),
            'Log_Level':            random.choice(levels),
            'Message':              random.choice(messages),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'log_events.csv'), index=False)
    print(f"    ✅ log_events.csv → {len(df)} rows")
    return df


# ═══════════════════════════════════════════════════════════════
#  7. USAGE BILLING (MAIN TABLE)
# ═══════════════════════════════════════════════════════════════
def generate_usage_billing(resource_df, incident_df, ticket_df):
    print("  Generating usage_billing.csv ...")

    resource_ids = resource_df['Resource_ID'].tolist()
    active_resources = resource_df[resource_df['Status'] == 'active']['Resource_ID'].tolist()
    zombie_resources = resource_df[resource_df['Status'].isin(['zombie', 'terminated'])]['Resource_ID'].tolist()
    incident_ids = incident_df['Incident_ID'].tolist()
    ticket_ids = ticket_df['Ticket_ID'].tolist()

    rows = []
    for i in range(1, N_ROWS + 1):
        # Pick account and its cloud
        acct = random.choice(ALL_ACCOUNTS)
        cloud = CLOUD_MAP[acct]

        # Pick a SKU valid for this cloud
        service = random.choice(list(SKUS[cloud].keys()))
        sku = random.choice(SKUS[cloud][service])
        unit = SKU_UNIT[sku]

        # Timestamp: Jan-Mar 2026
        ts_dt = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        month = ts_dt.month

        # Usage value
        if unit == 'seconds':
            usage_val = round(random.uniform(100, 50000), 2)
        else:  # GB
            usage_val = round(random.uniform(1, 5000), 2)

        # Cost
        cost_val = round(usage_val * random.uniform(0.001, 0.1), 2)

        # Currency & FX
        currency = ACCT_CURRENCY[acct]
        fx_rate = FX_TO_USD[currency]

        # S15: ~6.25% missing FX, some wrong direction
        fx_dirty = fx_rate
        if random.random() < 0.0625:
            fx_dirty = None
        elif random.random() < 0.02 and currency == 'INR':
            fx_dirty = 84.0  # wrong direction

        # Resource ID (S11)
        r_res = random.random()
        if r_res < 0.03:
            # prefix mismatch: use another cloud's prefix
            other_cloud = random.choice([c for c in ['AWS', 'Azure', 'GCP'] if c != cloud])
            prefix = {'AWS': 'aws-ec2', 'Azure': 'az-vm', 'GCP': 'gcp-inst'}[other_cloud]
            res_id = f"{prefix}-{random.randint(1, len(resource_ids)):03d}"
        elif r_res < 0.05:
            # ID not in inventory
            res_id = f"{'aws-ec2' if cloud == 'AWS' else 'az-vm' if cloud == 'Azure' else 'gcp-inst'}-{999}"
        elif r_res < 0.06 and zombie_resources:
            res_id = random.choice(zombie_resources)
        else:
            cloud_resources = [r for r in active_resources
                             if r.startswith({'AWS': 'aws-', 'Azure': 'az-', 'GCP': 'gcp-'}[cloud])]
            res_id = random.choice(cloud_resources) if cloud_resources else random.choice(active_resources)

        # CPU/Memory utilization (S16)
        if service == 'Compute' or service == 'Database':
            cpu = round(random.uniform(0, 100), 1)
            mem = round(random.uniform(0, 100), 1)
            # Some IDLE (both < 10)
            if random.random() < 0.08:
                cpu = round(random.uniform(0, 9.9), 1)
                mem = round(random.uniform(0, 9.9), 1)
            # Some OVERUTILIZED (>80)
            if random.random() < 0.05:
                cpu = round(random.uniform(80.1, 100), 1)
                mem = round(random.uniform(80.1, 100), 1)
        else:
            cpu = None  # Storage → no CPU/mem
            mem = None

        # Incident ID (S13): ~20% have incident
        inc_id = random.choice(incident_ids) if random.random() < 0.20 else None

        # Ticket ID (S12): ~30% have ticket
        tkt_id = random.choice(ticket_ids) if random.random() < 0.30 else None

        # Dept/Project (S18)
        dept, proj = get_dept_project()

        # Log skew (S20)
        if random.random() < 0.50:
            log_skew = round(random.uniform(60, 120) * random.choice([-1, 1]), 1)
        else:
            log_skew = round(random.uniform(-60, 60), 1)
        if random.random() < 0.03:
            log_skew = None

        # Charge type contradiction injection (S08)
        charge_type = dirty_charge_type()

        row = {
            'Usage_ID':           f"U{i:05d}",
            'Account_ID':        dirty_account(acct),
            'Timestamp':          dirty_timestamp(ts_dt),
            'Service':            random.choice([service, service.lower(), service.upper()]),
            'SKU':                dirty_sku(sku),
            'Usage_Value':        usage_val,
            'Unit':               dirty_unit(unit),
            'Cost':               dirty_cost(cost_val, currency),
            'Currency':           dirty_currency(currency),
            'FX_Rate':            fx_dirty,
            'Region':             dirty_region(cloud),
            'Resource_ID':        res_id,
            'Tag_Owner':          dirty_tag_owner(random.choice(TAG_OWNERS_CLEAN)),
            'Tag_Env':            dirty_tag_env(random.choice(TAG_ENVS_CLEAN)),
            'Charge_Type':        charge_type,
            'Purchase_Type':      dirty_purchase_type(),
            'Department':         dept,
            'Project':            proj,
            'CPU_Util':           cpu,
            'Memory_Util':        mem,
            'Incident_ID':        inc_id,
            'Ticket_ID':          tkt_id,
            'Price_Version':      dirty_price_version(month),
            'SLA_Event':          dirty_sla_event(),
            'Log_Skew_Seconds':   log_skew,
        }
        rows.append(row)

    # ── S09: Inject anomaly spikes (~500 rows) ────────────────
    spike_indices = random.sample(range(len(rows)), min(500, len(rows)))
    for idx in spike_indices:
        rows[idx]['Usage_Value'] = round(rows[idx]['Usage_Value'] * random.uniform(10, 50), 2)

    # ── S08: Inject charge type contradictions (~2%) ──────────
    contradict_indices = random.sample(range(len(rows)), min(200, len(rows)))
    for idx in contradict_indices:
        rows[idx]['Charge_Type'] = random.choice(['free', 'FREE_TIER', 'Free Tier'])
        rows[idx]['Cost'] = dirty_cost(round(random.uniform(500, 5000), 2),
                                        random.choice(CURRENCIES))

    # ── S07: Inject exact duplicates (~550 rows) ──────────────
    dup_indices = random.sample(range(len(rows)), N_DUPLICATES)
    duplicates = [rows[idx].copy() for idx in dup_indices]

    rows.extend(duplicates)

    # Shuffle
    random.shuffle(rows)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, 'usage_billing.csv'), index=False)
    print(f"    ✅ usage_billing.csv → {len(df)} rows (incl. ~{N_DUPLICATES} duplicates)")
    return df


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  Cloud Service Providers — Raw Dataset Generator")
    print("=" * 60)
    print()

    acct_df     = generate_account_master()
    sku_df      = generate_sku_catalog()
    resource_df = generate_resource_inventory()
    incident_df = generate_incidents()
    ticket_df   = generate_support_tickets(resource_df)
    log_df      = generate_log_events(resource_df)
    billing_df  = generate_usage_billing(resource_df, incident_df, ticket_df)

    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  account_master.csv     : {len(acct_df):>6} rows")
    print(f"  sku_catalog.csv        : {len(sku_df):>6} rows")
    print(f"  resource_inventory.csv : {len(resource_df):>6} rows")
    print(f"  incidents.csv          : {len(incident_df):>6} rows")
    print(f"  support_tickets.csv    : {len(ticket_df):>6} rows")
    print(f"  log_events.csv         : {len(log_df):>6} rows")
    print(f"  usage_billing.csv      : {len(billing_df):>6} rows")
    print(f"  ────────────────────────────────")
    print(f"  Output directory: {OUT_DIR}")
    print()


if __name__ == '__main__':
    main()
