"""Forward Azure Monitor logs to an external SIEM via HTTP POST."""

import os
import sys
import argparse
import json
from datetime import timedelta
from dotenv import load_dotenv
import requests
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--workspace", required=True, help="Log Analytics workspace ID")
parser.add_argument("--since", default="1h", help="Lookback window (e.g. 1h, 30m, 1d)")
parser.add_argument("--table", default="AzureActivity", help="Table to query")
args = parser.parse_args()

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
)

siem_url = os.getenv("SIEM_ENDPOINT")
siem_token = os.getenv("SIEM_TOKEN")


def parse_window(s):
    """Convert '1h', '30m', '1d' into timedelta."""
    unit = s[-1]
    val = int(s[:-1])
    return {"h": timedelta(hours=val), "m": timedelta(minutes=val), "d": timedelta(days=val)}[unit]


def main():
    client = LogsQueryClient(credential)
    query = f"{args.table} | order by TimeGenerated desc"

    response = client.query_workspace(
        workspace_id=args.workspace,
        query=query,
        timespan=parse_window(args.since),
    )

    if response.status != LogsQueryStatus.SUCCESS:
        print(f"Query failed: {response.partial_error}", file=sys.stderr)
        sys.exit(1)

    forwarded = 0
    for row in response.tables[0].rows:
        payload = dict(zip(response.tables[0].columns, row))
        r = requests.post(
            siem_url,
            headers={"Authorization": f"Bearer {siem_token}"},
            json=payload,
            timeout=10,
        )
        if r.ok:
            forwarded += 1
        else:
            print(f"Forward failed: {r.status_code} {r.text}", file=sys.stderr)

    print(f"Forwarded {forwarded} events.")


if __name__ == "__main__":
    main()
