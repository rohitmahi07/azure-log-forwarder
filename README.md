# Azure Log Forwarder

Reads Azure Monitor logs via the REST API and forwards them to an external SIEM (Splunk, Chronicle, etc.).

Useful for teams that need to keep a copy of Azure telemetry in their existing SIEM without paying for Azure Sentinel.

## Setup

```bash
pip install -r requirements.txt
python forward.py --workspace <workspace-id> --since 1h
```

## Configuration

Credentials are loaded from `.env`. The service principal needs:
- `Log Analytics Reader` role on the target workspace
- `Monitoring Reader` on the subscription (optional, for metric forwarding)

## TODO

- [ ] Move creds to Key Vault
- [ ] Batch API calls to reduce cost
- [ ] Add dead-letter queue for failed forwards
- [ ] Retry with exponential backoff
