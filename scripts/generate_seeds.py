"""Generate deterministic synthetic source-shaped fixtures; never reads source rows."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "metadata/source_contract.json").read_text())
AS_OF = CONTRACT["as_of_date"]
UTC = f"{AS_OF} 12:00:00+00:00"
LOCAL = f"{AS_OF} 12:00:00"
SCENARIOS = [
    ("Northstar Demo Labs", "eligible", True),
    ("Cedar Demo Manufacturing", "overdue_invoice", False),
    ("Harbor Demo Analytics", "unsubscribed", False),
    ("Summit Demo Systems", "stale_engagement", False),
    ("Juniper Demo Works", "no_closed_won", False),
    ("Atlas Demo Services", "missing_finance_match", False),
    ("Willow Demo Software", "held_subscriber", False),
    ("Beacon Demo Logistics", "no_engagement", False),
    ("Orchard Demo Industries", "current_unpaid_invoice", True),
    ("Pine Demo Networks", "inactive_finance_customer", False),
    ("River Demo Research", "unsubscribe_event", False),
    ("Aspen Demo Ventures", "closed_lost", False),
    ("Elm Demo Technologies", "unknown_subscription_status", False),
    ("Cobalt Demo Studio", "complaint_event", False),
    ("Maple Demo Partners", "already_has_expansion_product", False),
]


def sfid(prefix: str, number: int) -> str:
    """A structurally valid Salesforce 18-character ID, with a case checksum."""
    short = prefix + f"{number:012d}"
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    suffix = "".join(
        alphabet[sum(1 << j for j, c in enumerate(short[i:i + 5]) if c.isupper())]
        for i in range(0, 15, 5)
    )
    return short + suffix


def generate() -> dict[str, list[dict]]:
    rows = {t["seed"]: [] for t in CONTRACT["tables"]}
    items = [
        {"ID": 501, "ITEMID": "CORE-ANNUAL", "DISPLAYNAME": "Core Platform Annual", "ITEMTYPE": "Service", "ISINACTIVE": "F"},
        {"ID": 502, "ITEMID": "SUPPORT-ANNUAL", "DISPLAYNAME": "Support Annual", "ITEMTYPE": "Service", "ISINACTIVE": "F"},
        {"ID": 503, "ITEMID": "ANALYTICS-ADDON", "DISPLAYNAME": "Analytics Expansion", "ITEMTYPE": "Service", "ISINACTIVE": "F"},
    ]
    rows["netsuite_item"] = items
    for i, (company, scenario, eligible) in enumerate(SCENARIOS, 1):
        key, aid, nid, sub = f"CUST-{i:03d}", sfid("001", i), 1000 + i, f"demo-contact-{i:03d}"
        email = f"contact{i:03d}@example.com"
        account = dict(ID=aid, NAME=company, ACCOUNTNUMBER=f"DEMO-{i:03d}",
                       INDUSTRY="Technology" if i % 2 else "Manufacturing",
                       TYPE="Prospect" if i == 5 else "Customer - Direct",
                       ANNUALREVENUE=1000000 + i * 100000, NUMBEROFEMPLOYEES=50 + i * 10,
                       WEBSITE=f"https://demo-{i:03d}.example.com", ISDELETED=False,
                       CREATEDDATE="2025-10-01 00:00:00+00:00", LASTMODIFIEDDATE=UTC,
                       SYSTEMMODSTAMP=UTC, DESCRIPTION="Synthetic demo account; no real customer data.")
        rows["salesforce_account"].append(account)
        won = i not in (5, 12)
        opportunity = dict(ID=sfid("006", i), ACCOUNTID=aid, NAME=f"{company} - Core Platform",
                           AMOUNT=12000 + i * 100, CLOSEDATE="2026-08-01",
                           STAGENAME="Closed Won" if won else "Prospecting" if i == 5 else "Closed Lost",
                           ISWON=won, ISCLOSED=i != 5, ISDELETED=False,
                           PROBABILITY=100 if won else 20 if i == 5 else 0,
                           CREATEDDATE="2026-07-01 00:00:00+00:00", LASTMODIFIEDDATE=UTC,
                           SYSTEMMODSTAMP=UTC, TYPE="New Customer")
        rows["salesforce_opportunity"].append(opportunity)
        # Two won opportunities deliberately expose accidental fan-out in future joins.
        if i in (1, 9):
            rows["salesforce_opportunity"].append({**opportunity, "ID": sfid("006", 100 + i),
                "NAME": f"{company} - Prior Renewal", "AMOUNT": 6000, "CLOSEDATE": "2025-08-01"})
        if i != 6:
            rows["netsuite_customer"].append(dict(ID=nid, ENTITYID=f"DEMO-{i:03d}",
                COMPANYNAME=company, EMAIL=email, ISINACTIVE="T" if i == 10 else "F",
                CURRENCY=1, LASTMODIFIEDDATE=LOCAL))
        rows["customer_identity"].append(dict(CUSTOMER_KEY=key, SALESFORCE_ACCOUNT_ID=aid,
            NETSUITE_CUSTOMER_ID=nid if i != 6 else None, SFMC_SUBSCRIBER_KEY=sub))
        rows["demo_scenarios"].append(dict(CUSTOMER_KEY=key, SCENARIO=scenario,
            EXPECTED_ELIGIBLE=eligible, EXPECTED_REASON="eligible" if eligible else scenario,
            AS_OF_DATE=AS_OF))
        if i not in (5, 6):
            for invoice_no in (1, 2):
                tid = 10000 + i * 10 + invoice_no
                total = 6000 + i * 100
                unpaid = 2000 if invoice_no == 2 and i in (2, 9) else 0
                due = "2026-09-15" if i == 2 else "2026-11-15" if i == 9 and invoice_no == 2 else "2026-09-30"
                rows["netsuite_transaction"].append(dict(ID=tid, ENTITY=nid,
                    TRANID=f"DEMO-INV-{i:03d}-{invoice_no}", TYPE="CustInvc",
                    STATUS="A" if unpaid else "B", TRANDATE="2026-08-15", DUEDATE=due,
                    CURRENCY=1, FOREIGNTOTAL=total, FOREIGNAMOUNTPAID=total-unpaid,
                    FOREIGNAMOUNTUNPAID=unpaid, VOIDED="F", LASTMODIFIEDDATE=LOCAL))
                # Include mainline and detail rows; never sum header totals after a line join.
                for line, item, amount, main in ((0, None, total, "T"),
                                                (1, 501, -(total - 1000), "F"),
                                                (2, 503 if i == 15 else 502, -1000, "F")):
                    rows["netsuite_transactionline"].append(dict(ID=line, TRANSACTION=tid,
                        UNIQUEKEY=tid * 10 + line, ITEM=item, MAINLINE=main, TAXLINE="F",
                        QUANTITY=-1 if line else None, NETAMOUNT=amount))
        # A voided invoice with an unpaid balance must not suppress this eligible account.
        if i == 1:
            rows["netsuite_transaction"].append(dict(ID=19001, ENTITY=nid, TRANID="DEMO-VOID-001",
                TYPE="CustInvc", STATUS="A", TRANDATE="2026-07-01", DUEDATE="2026-07-31",
                CURRENCY=1, FOREIGNTOTAL=500, FOREIGNAMOUNTPAID=0, FOREIGNAMOUNTUNPAID=500,
                VOIDED="T", LASTMODIFIEDDATE=LOCAL))
        status = "Unsubscribed" if i == 3 else "Held" if i == 7 else None if i == 13 else "Active"
        rows["sfmc_subscribers"].append(dict(ID=str(2000 + i), SubscriberKey=sub,
            EmailAddress=email, Status=status, EmailTypePreference="HTML",
            CreatedDate="2026-01-01 00:00:00+00:00",
            UnsubscribedDate="2026-10-10 09:00:00+00:00" if i == 3 else None))
        if i != 8:
            date = "2026-07-01" if i == 4 else "2026-10-10"
            for n, event in enumerate(("sent", "click"), 1):
                rows["sfmc_event"].append(dict(id=f"{event}_7001_{sub}_{date.replace('-', '')}09000{n}",
                    event_type=event, AccountID=900001, BatchID=1, JobID=7001, ListID=100,
                    SubscriberID=2000+i, SubscriberKey=sub, EventDate=f"{date} 09:00:0{n}+00:00",
                    IsUnique=True, Domain="example.com",
                    URL="https://www.supa-flow.io/demo" if event == "click" else None))
            if i in (3, 11, 14):
                event = "complaint" if i == 14 else "unsubscribe"
                rows["sfmc_event"].append(dict(id=f"{event}_7001_{sub}_20261012100000",
                    event_type=event, AccountID=900001, BatchID=1, JobID=7001, ListID=100,
                    SubscriberID=2000+i, SubscriberKey=sub, EventDate="2026-10-12 10:00:00+00:00",
                    IsUnique=True, Domain="example.com"))
    # Match physical, unquoted Snowflake column names while preserving source names in metadata.
    return {seed: [{k.upper(): v for k, v in row.items()} for row in data] for seed, data in rows.items()}


def main() -> None:
    rows = generate()
    manifest = {"synthetic_only": True, "as_of_date": AS_OF, "tables": []}
    config = {"name": "supaflow_customer_demo", "version": "1.0.0", "config-version": 2,
        "profile": "supaflow_customer_demo", "require-dbt-version": [">=1.10.0", "<2.0.0"],
        "model-paths": ["models"], "seed-paths": ["seeds"], "test-paths": ["tests"],
        "macro-paths": ["macros"], "analysis-paths": ["analyses"],
        "snapshot-paths": ["snapshots"],
        "models": {"supaflow_customer_demo": {
            "staging": {"+materialized": "view", "+schema": "STAGING"},
            "intermediate": {"+materialized": "view", "+schema": "INTERMEDIATE"},
            "marts": {"+materialized": "table"}}},
        "vars": {"demo_as_of_date": AS_OF}, "on-run-start": ["{{ assert_demo_target() }}"],
        "seeds": {"supaflow_customer_demo": {"+quote_columns": False}}}
    sources = []
    for suffix in ("SALESFORCE", "NETSUITE", "SFMC", "REFERENCE"):
        ts = [t for t in CONTRACT["tables"] if t["schema_suffix"] == suffix]
        sources.append({"name": suffix.lower(), "database": "{{ target.database }}",
            "schema": "{{ target.schema }}_" + suffix,
            "tables": [{"name": t["table"].lower(), "identifier": t["table"],
                "description": t["provenance"],
                "config": {"freshness": {"warn_after": {"count": 24, "period": "hour"},
                    "error_after": {"count": 48, "period": "hour"}},
                    "loaded_at_query": "select max(last_altered) from {{ target.database }}.information_schema.tables where table_schema = upper('{{ target.schema }}_" + suffix + "') and table_name = '" + t["table"] + "'"}} for t in ts]})
    verification = ["-- Generated from synthetic CSV payloads; reads only the isolated demo tables."]
    for t in CONTRACT["tables"]:
        seed, data = t["seed"], rows[t["seed"]]
        path = ROOT / "seeds" / t["source"] / f"{seed}.csv"
        columns = [c["name"] for c in t["columns"]]
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=columns, extrasaction="raise", lineterminator="\n")
            w.writeheader()
            for row in data:
                w.writerow({k: str(v).lower() if isinstance(v, bool) else v for k, v in row.items()})
        config["seeds"]["supaflow_customer_demo"].setdefault(t["source"], {})[seed] = {"+schema": t["schema_suffix"],
            "+alias": t["table"], "+column_types": {c["name"]: c["snowflake_type"] for c in t["columns"]}}
        manifest["tables"].append({"seed": seed, "relation": f"SUPA_DB.SUPAFLOW_DEMO_{t['schema_suffix']}.{t['table']}",
            "rows": len(data), "columns": len(columns), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        # Text VALUES plus explicit casts avoid Snowflake's mixed-literal coercion.
        def literal(value):
            if value is None:
                return "null"
            value = str(value).lower() if isinstance(value, bool) else str(value)
            return "'" + value.replace("'", "''") + "'"
        values = ",\n".join("(" + ",".join(literal(row.get(col)) for col in columns) + ")" for row in data)
        casts = ",\n".join(f"column{i}::{col['snowflake_type']} as {col['name']}" for i, col in enumerate(t['columns'], 1))
        relation = manifest["tables"][-1]["relation"]
        names = ",".join(columns)
        verification.append(f"""with expected as (
select {casts} from values {values}
), missing as (
select {names} from expected minus select {names} from {relation}
), unexpected as (
select {names} from {relation} minus select {names} from expected
)
select '{relation}' as relation_name,
 (select count(*) from {relation}) as actual_rows,
 {len(data)} as expected_rows,
 (select count(*) from missing) as missing_rows,
 (select count(*) from unexpected) as unexpected_rows;""")
    (ROOT / "dbt_project.yml").write_text(yaml.safe_dump(config, sort_keys=False))
    (ROOT / "models/sources.yml").write_text(yaml.safe_dump({"version": 2, "sources": sources}, sort_keys=False))
    (ROOT / "metadata/seed_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (ROOT / "scripts/verify_seed_values.sql").write_text("\n\n".join(verification) + "\n")
    print(f"Generated {sum(t['rows'] for t in manifest['tables'])} synthetic rows across {len(manifest['tables'])} tables.")


if __name__ == "__main__":
    main()
