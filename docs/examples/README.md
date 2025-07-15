# Biotope Examples

This directory contains examples and utilities for extending biotope functionality.

## Remote Validation Server

The `remote-validation-server.py` script demonstrates how to set up a remote validation server for cluster-wide metadata policies.

### Features

- **Multiple Validation Policies**: Serve different validation requirements for different use cases
- **RESTful API**: Simple HTTP endpoints for validation configuration
- **Caching Support**: Built-in caching for performance
- **Error Handling**: Graceful fallbacks and error reporting

### Usage

```bash
# Start the server
python remote-validation-server.py

# Configure biotope to use remote validation
biotope config set-remote-validation --url http://localhost:5000/validation/cluster-strict
```

### API Endpoints

- `GET /validation/cluster-strict` - Strict cluster validation requirements
- `GET /validation/storage-management` - Storage management requirements  
- `GET /validation/academic` - Academic research requirements
- `GET /validation/` - List all available policies

## Cluster Compliance Checking

The cluster compliance checker helps administrators verify that biotope projects are using appropriate validation patterns.

### Features

- **Project Scanning**: Automatically find all biotope projects in a directory
- **Compliance Checking**: Verify projects meet cluster requirements
- **Detailed Reporting**: Generate comprehensive compliance reports
- **Custom Requirements**: Define cluster-specific compliance rules

### Usage

```bash
# Check all projects in a directory
python cluster-compliance-checker.py --scan-dir /cluster/projects

# Check specific project
python cluster-compliance-checker.py --project /path/to/project

# Generate compliance report
python cluster-compliance-checker.py --scan-dir /cluster/projects --report compliance_report.txt

# Use custom requirements
python cluster-compliance-checker.py --scan-dir /cluster/projects --requirements cluster-requirements.json
```

### Example Output

```
================================================================================
BIOTOPE CLUSTER COMPLIANCE REPORT
================================================================================

SUMMARY:
  Total projects: 25
  Compliant projects: 18
  Using default pattern: 5
  Errors: 2
  Compliance rate: 72.0%

DETAILED REPORT:
--------------------------------------------------------------------------------

Project: /cluster/projects/user1/experiment
  Pattern: cluster-strict
  Status: cluster_compliant
  Remote validation: https://cluster.example.com/validation/cluster-strict
  Required fields: name, description, creator, dateCreated, distribution, license, project_id
  ✅ COMPLIANT

Project: /cluster/projects/user2/data
  Pattern: default
  Status: default_pattern
  Required fields: name, description, creator, dateCreated, distribution
  ❌ NON-COMPLIANT
    - Wrong validation pattern: default (required: cluster-strict)
    - Missing required fields: license, project_id
    - Remote validation not configured

================================================================================
RECOMMENDATIONS:
- 5 projects are using default validation pattern
  Consider configuring cluster-specific validation for these projects
- 2 projects have configuration errors
  Review these projects and fix configuration issues
- 7 projects are non-compliant
  Contact project owners to update validation configuration
```

### Configuration

Create a `cluster-requirements.json` file to define your cluster's requirements:

```json
{
  "cluster_name": "Example HPC Cluster",
  "required_pattern": "cluster-strict",
  "required_fields": [
    "name", "description", "creator", "dateCreated", 
    "distribution", "license", "project_id"
  ],
  "require_remote_validation": true
}
```

## Validation Patterns

Biotope supports different validation patterns for different use cases:

### Default Pattern
- Basic validation requirements
- Suitable for local development and simple projects
- No remote validation required

### Cluster-Strict Pattern
- Enhanced validation for cluster environments
- Requires remote validation configuration
- Additional required fields for compliance

### Storage-Management Pattern
- Validation for long-term storage systems
- Requires retention policies and backup information
- Enhanced metadata for archival purposes

### Setting Validation Patterns

```bash
# Set validation pattern for a project
biotope config set-validation-pattern --pattern cluster-strict

# Show current validation pattern
biotope config show-validation-pattern

# Show detailed validation information
biotope config show-validation
```

## Integration with Cluster Management

### Automated Compliance Checking

Set up automated compliance checking in your cluster environment:

```bash
#!/bin/bash
# /etc/cron.daily/biotope-compliance-check

# Check all user projects
python /opt/biotope/examples/cluster-compliance-checker.py \
  --scan-dir /cluster/projects \
  --requirements /etc/biotope/cluster-requirements.json \
  --report /var/log/biotope/compliance-$(date +%Y%m%d).txt

# Send report to administrators
mail -s "Biotope Compliance Report $(date +%Y-%m-%d)" \
  admin@cluster.example.com < /var/log/biotope/compliance-$(date +%Y%m%d).txt
```

### User Onboarding

Provide users with setup instructions:

```bash
# 1. Initialize biotope project
biotope init

# 2. Set cluster validation pattern
biotope config set-validation-pattern --pattern cluster-strict

# 3. Configure remote validation
biotope config set-remote-validation --url https://cluster.example.com/validation/cluster-strict

# 4. Verify configuration
biotope config show-validation-pattern
```

### Monitoring and Alerts

Monitor compliance rates and alert administrators when compliance drops:

```python
# compliance_monitor.py
import json
import subprocess
from pathlib import Path

def check_compliance_rate():
    result = subprocess.run([
        "python", "cluster-compliance-checker.py",
        "--scan-dir", "/cluster/projects",
        "--json"
    ], capture_output=True, text=True)
    
    projects = json.loads(result.stdout)
    compliant = sum(1 for p in projects if p.get("compliance_status") in ["cluster_compliant", "storage_compliant"])
    rate = compliant / len(projects) if projects else 0
    
    if rate < 0.8:  # Alert if compliance drops below 80%
        send_alert(f"Biotope compliance rate: {rate:.1%}")
    
    return rate
```

## Best Practices

### For Cluster Administrators

1. **Define Clear Requirements**: Create comprehensive requirements files
2. **Automate Checking**: Set up regular compliance monitoring
3. **Provide Documentation**: Give users clear setup instructions
4. **Monitor Trends**: Track compliance rates over time
5. **Support Users**: Help users configure their projects correctly

### For Users

1. **Set Validation Pattern**: Configure appropriate pattern for your use case
2. **Use Remote Validation**: Connect to cluster validation services
3. **Complete Metadata**: Ensure all required fields are properly filled
4. **Regular Checks**: Use `biotope config show-validation-pattern` to verify setup
5. **Seek Help**: Contact administrators if you need assistance

### For Developers

1. **Extend Patterns**: Add new validation patterns for specific use cases
2. **Custom Requirements**: Create requirements files for different environments
3. **Integration**: Integrate compliance checking into existing workflows
4. **Documentation**: Document new patterns and requirements
5. **Testing**: Test compliance checking with various project configurations 