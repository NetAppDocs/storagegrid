# Copilot instructions for StorageGRID software documentation

## Repository overview

Product: StorageGRID software (current version: 12.0)

NetApp StorageGRID is a software-defined object storage suite that supports a wide range of use cases across public, private, and hybrid multicloud environments. It offers native support for the Amazon S3 API and automated lifecycle management to store, secure, protect, and preserve unstructured data cost effectively over long periods.

## Repository structure

- `admin/` – Grid administration: users, groups, identity federation, load balancer, security certificates, and Grid Management API settings
- `audit/` – Audit log message reference and audit share configuration
- `expand/` – Procedures for adding Storage Nodes, Admin Nodes, Gateway Nodes, or sites to an existing grid
- `fabricpool/` – Configuring StorageGRID as a FabricPool capacity tier for ONTAP
- `harden/` – System hardening guidelines for securing a StorageGRID deployment
- `ilm/` – Information Lifecycle Management: creating and managing ILM rules, policies, storage pools, and erasure-coding profiles
- `landing-*/` – Navigation landing pages for each major doc section (not standalone content)
- `maintain/` – Grid maintenance: node recovery, decommission, rename, reboot, hotfix, and site removal procedures
- `media/` – Images and screenshots referenced across all topics
- `monitor/` – Monitoring: alerts, metrics, AutoSupport, SNMP, and audit logs
- `network/` – Networking guidelines, topology, and port reference
- `primer/` – Introductory concepts and quick-start content
- `redirect/` – URL redirects for pages that have moved
- `release-notes/` – What's new and removed or deprecated features for each release
- `rhel/` – Installing StorageGRID on Red Hat Enterprise Linux
- `s3/` – S3 REST API operations, authentication, and usage reference
- `swift/` – Swift REST API reference (end of life)
- `swnodes/` – Installing StorageGRID on software-based nodes (RHEL, Ubuntu, VMware)
- `tenant/` – Tenant account management: buckets, groups, users, S3 keys, and platform services
- `troubleshoot/` – Troubleshooting procedures and error reference
- `ubuntu/` – Installing StorageGRID on Ubuntu
- `upgrade/` – Upgrading StorageGRID to a new release
- `vmware/` – Installing StorageGRID on VMware
- `_include/` – Shared AsciiDoc fragments included (via `include::`) in multiple topics

## Product-specific context

- **Grid / site / node hierarchy:** A StorageGRID deployment is called a grid. A grid contains one or more sites, and each site contains nodes. Always use these terms precisely.
- **Node types:** Admin Nodes, Storage Nodes, and Gateway Nodes. Admin Nodes host management services; Storage Nodes store object data and metadata; Gateway Nodes provide a load-balanced S3/Swift interface.
- **Software-based vs. appliance nodes:** Nodes can run on NetApp hardware appliances or on customer-supplied servers and VMs (RHEL, Ubuntu, VMware). Installation content differs by platform.
- **ILM (Information Lifecycle Management):** The StorageGRID policy engine that controls how objects are placed, replicated, or erasure-coded over time. ILM rules combine together into an ILM policy.
- **S3 as primary API:** The Amazon S3 REST API is the primary interface for object storage clients. The Swift API is end of life.
- **Tenant accounts:** Object storage clients operate within isolated tenant accounts. Tenants manage their own buckets, groups, users, and S3 access keys.
- **ADC quorum:** The Administrative Domain Controller (ADC) service must maintain quorum across Storage Nodes. This constraint affects decommission and recovery procedures.
- **Version specificity:** Always include the StorageGRID version number (e.g., 12.0) when content is version-specific. The current release is 12.0.