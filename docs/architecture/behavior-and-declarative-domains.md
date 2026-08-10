# Behavioral intelligence and declarative domains

## Behavioral PDCA

The infrastructure domain samples persisted Zabbix snapshots and calculates recurring availability by host, component, local hour and observed day. Calculations are deterministic and auditable; Claude may explain a result but does not calculate confidence or classify observations by itself.

The cycle is:

1. **Plan** — define the expected availability window and minimum evidence.
2. **Do** — collect snapshots through the installed infrastructure domain.
3. **Check** — compare out-of-hours and business-hours rates for every host/component pair.
4. **Act** — recommend validation, maintenance windows or a deviation alert. No automatic remediation is performed from a statistical hypothesis.

A scheduled-availability pattern requires observations on at least three days, enough samples in both windows, more than 55% unavailability outside business hours, at most 30% during business hours and a separation of at least 40 percentage points. Results expose rates, sample counts, confidence, evidence and the rule that should detect deviations.

The analyzer runs at most once per hour. PostgreSQL performs temporal sampling before returning large JSON snapshots, reducing memory and network use. A result with zero patterns is valid and must not be replaced by an LLM inference.

## Declarative domain installer

Administrators can install domains such as medicine, finance, inventory or HR from the Knowledge screen. The form produces a safe manifest rather than executable code. Each installation declares:

- identifier, version, name, description and purpose;
- entities and metrics;
- read/manage permissions and role grants;
- status, search and manifest endpoints;
- an isolated knowledge collection;
- an optional allow-listed documentation source;
- provisioning and health state.

Routes are available immediately through the generic runtime contract:

- `GET /domains/{domain_id}`
- `GET /domains/{domain_id}/status`
- `GET /domains/{domain_id}/search?query=...`

Creating or disabling a domain requires `platform.manage`; reading and searching require `knowledge.search`. Domain IDs are validated and reserved platform names cannot be installed. This is intentionally not a code generator: connectors with credentials, clinical decision support, financial transactions or write actions still require a reviewed adapter and domain-specific validation.
