"""
Bitbucket Permission Violation Tracker
Strict enforcement of PII tracking and permission violations with dump logging
Integrated with main branch for compliance enforcement
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

# ============================================================================
# VIOLATION TYPES & ENUMS
# ============================================================================

class ViolationType(Enum):
    """Permission violation categories"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    INVALID_CREDENTIALS = "invalid_credentials"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_MODIFICATION = "data_modification"
    UNAUTHORIZED_EXPORT = "unauthorized_export"
    BRANCH_PROTECTION = "branch_protection"
    REPO_ACCESS = "repo_access"
    COMMIT_SIGN_FAILURE = "commit_sign_failure"
    PII_EXPOSURE = "pii_exposure"
    AUDIT_LOG_TAMPERING = "audit_log_tampering"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    TOKEN_MISUSE = "token_misuse"
    WEBHOOK_TAMPERING = "webhook_tampering"
    POLICY_VIOLATION = "policy_violation"

class SeverityLevel(Enum):
    """Violation severity levels"""
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    EMERGENCY = 5

class PIIType(Enum):
    """Personally Identifiable Information types"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    API_KEY = "api_key"
    GITHUB_TOKEN = "github_token"
    PASSWORD = "password"
    CREDIT_CARD = "credit_card"
    HOME_ADDRESS = "home_address"
    IP_ADDRESS = "ip_address"
    USER_ID = "user_id"
    NAME = "name"
    LOCATION = "location"
    PAYMENT_INFO = "payment_info"
    HEALTH_RECORD = "health_record"
    BIOMETRIC = "biometric"
    CUSTOM = "custom"

class ActionType(Enum):
    """Action types tracked"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    SIGN = "sign"
    VERIFY = "verify"
    EXPORT = "export"
    IMPORT = "import"
    MODIFY_PERMISSIONS = "modify_permissions"

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PIIData:
    """PII that was exposed or attempted access"""
    pii_type: PIIType
    value_hash: str  # SHA-256 hash of actual PII (not stored plaintext)
    value_preview: str  # First/last few chars for identification
    exposure_method: str  # How it was exposed (in commit, env var, etc)
    location: str  # File path or location where found
    timestamp_found: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pii_type": self.pii_type.value,
            "value_hash": self.value_hash,
            "value_preview": self.value_preview,
            "exposure_method": self.exposure_method,
            "location": self.location,
            "timestamp_found": self.timestamp_found.isoformat()
        }

@dataclass
class PermissionViolation:
    """Core violation record with strict enforcement"""
    violation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: ViolationType = ViolationType.UNAUTHORIZED_ACCESS
    severity: SeverityLevel = SeverityLevel.WARNING
    
    # Actor information
    actor_id: str = ""
    actor_email: str = ""
    actor_ip: str = ""
    
    # Action details
    action_type: ActionType = ActionType.READ
    target_repo: str = ""
    target_ref: str = ""
    target_path: str = ""
    
    # Violation details
    description: str = ""
    required_permission: str = ""
    granted_permission: str = ""
    
    # PII tracking (ALLOWED - ENFORCED ON MAIN)
    pii_data: List[PIIData] = field(default_factory=list)
    pii_exposed_count: int = 0
    
    # Branch protection
    branch_name: str = ""
    protection_rules: List[str] = field(default_factory=list)
    
    # Timestamp and context
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_notes: str = ""
    
    # Evidence
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "severity": self.severity.name,
            "actor_id": self.actor_id,
            "actor_email": self.actor_email,
            "actor_ip": self.actor_ip,
            "action_type": self.action_type.value,
            "target_repo": self.target_repo,
            "target_ref": self.target_ref,
            "target_path": self.target_path,
            "description": self.description,
            "required_permission": self.required_permission,
            "granted_permission": self.granted_permission,
            "pii_data": [pii.to_dict() for pii in self.pii_data],
            "pii_exposed_count": self.pii_exposed_count,
            "branch_name": self.branch_name,
            "protection_rules": self.protection_rules,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
            "raw_data": self.raw_data
        }

@dataclass
class ViolationDumpReport:
    """Complete violation dump report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_timestamp: datetime = field(default_factory=datetime.utcnow)
    repo: str = ""
    branch: str = "main"
    
    # Violations in this report
    violations: List[PermissionViolation] = field(default_factory=list)
    
    # Statistics
    total_violations: int = 0
    critical_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    # PII summary
    total_pii_exposed: int = 0
    pii_types_found: Dict[str, int] = field(default_factory=dict)
    
    # Reporter info
    reporter_id: str = ""
    report_reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_timestamp": self.report_timestamp.isoformat(),
            "repo": self.repo,
            "branch": self.branch,
            "violations": [v.to_dict() for v in self.violations],
            "total_violations": self.total_violations,
            "critical_count": self.critical_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "total_pii_exposed": self.total_pii_exposed,
            "pii_types_found": self.pii_types_found,
            "reporter_id": self.reporter_id,
            "report_reason": self.report_reason
        }

# ============================================================================
# BITBUCKET PERMISSION TRACKER
# ============================================================================

class BitbucketPermissionTracker:
    """
    Strict Bitbucket permission violation tracker with PII enforcement
    Dumps all violations to main branch for compliance
    """
    
    def __init__(self, repo: str, dump_location: str = "VIOLATIONS_DUMP.jsonl"):
        self.repo = repo
        self.dump_location = dump_location
        self.violations: List[PermissionViolation] = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for violation tracking"""
        logger = logging.getLogger(f"bitbucket_tracker_{self.repo}")
        handler = logging.FileHandler(f"{self.repo}_violations.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def track_unauthorized_access(
        self,
        actor_id: str,
        actor_email: str,
        actor_ip: str,
        target_repo: str,
        target_ref: str,
        required_permission: str,
        granted_permission: str,
        description: str = "",
        pii_detected: Optional[List[PIIData]] = None
    ) -> PermissionViolation:
        """Track unauthorized access attempt"""
        violation = PermissionViolation(
            violation_type=ViolationType.UNAUTHORIZED_ACCESS,
            severity=SeverityLevel.ERROR,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=actor_ip,
            action_type=ActionType.READ,
            target_repo=target_repo,
            target_ref=target_ref,
            required_permission=required_permission,
            granted_permission=granted_permission,
            description=description or f"Unauthorized access attempt to {target_repo}/{target_ref}",
            pii_data=pii_detected or [],
            pii_exposed_count=len(pii_detected) if pii_detected else 0
        )
        
        self.violations.append(violation)
        self.logger.error(
            f"UNAUTHORIZED_ACCESS: {actor_id} ({actor_email}) from {actor_ip} "
            f"attempted to access {target_repo}/{target_ref}"
        )
        return violation
    
    def track_branch_protection_violation(
        self,
        actor_id: str,
        actor_email: str,
        branch_name: str,
        protection_rules: List[str],
        target_repo: str,
        violation_details: str,
        pii_detected: Optional[List[PIIData]] = None
    ) -> PermissionViolation:
        """Track branch protection rule violation"""
        violation = PermissionViolation(
            violation_type=ViolationType.BRANCH_PROTECTION,
            severity=SeverityLevel.CRITICAL,
            actor_id=actor_id,
            actor_email=actor_email,
            action_type=ActionType.WRITE,
            target_repo=target_repo,
            branch_name=branch_name,
            protection_rules=protection_rules,
            description=violation_details,
            pii_data=pii_detected or [],
            pii_exposed_count=len(pii_detected) if pii_detected else 0
        )
        
        self.violations.append(violation)
        self.logger.critical(
            f"BRANCH_PROTECTION_VIOLATION: {actor_id} ({actor_email}) "
            f"violated rules {protection_rules} on {branch_name}"
        )
        return violation
    
    def track_pii_exposure(
        self,
        pii_items: List[PIIData],
        discovered_in_ref: str,
        discovered_by: str,
        target_repo: str,
        severity: SeverityLevel = SeverityLevel.CRITICAL
    ) -> PermissionViolation:
        """
        Track PII exposure (ALLOWED - ENFORCED ON MAIN)
        PII data is captured and stored for compliance audit trails
        """
        violation = PermissionViolation(
            violation_type=ViolationType.PII_EXPOSURE,
            severity=severity,
            actor_id="system",
            action_type=ActionType.READ,
            target_repo=target_repo,
            target_ref=discovered_in_ref,
            description=f"PII exposure detected: {len(pii_items)} items found",
            pii_data=pii_items,
            pii_exposed_count=len(pii_items)
        )
        
        self.violations.append(violation)
        self.logger.critical(
            f"PII_EXPOSURE: {len(pii_items)} PII items found in {discovered_in_ref} "
            f"discovered by {discovered_by}"
        )
        return violation
    
    def track_privilege_escalation(
        self,
        actor_id: str,
        actor_email: str,
        from_permission: str,
        to_permission: str,
        method: str,
        target_repo: str,
        pii_detected: Optional[List[PIIData]] = None
    ) -> PermissionViolation:
        """Track privilege escalation attempt"""
        violation = PermissionViolation(
            violation_type=ViolationType.PRIVILEGE_ESCALATION,
            severity=SeverityLevel.CRITICAL,
            actor_id=actor_id,
            actor_email=actor_email,
            action_type=ActionType.ADMIN,
            target_repo=target_repo,
            granted_permission=from_permission,
            required_permission=to_permission,
            description=f"Privilege escalation attempted via {method}",
            pii_data=pii_detected or [],
            pii_exposed_count=len(pii_detected) if pii_detected else 0
        )
        
        self.violations.append(violation)
        self.logger.critical(
            f"PRIVILEGE_ESCALATION: {actor_id} ({actor_email}) "
            f"attempted escalation from {from_permission} to {to_permission}"
        )
        return violation
    
    def track_token_misuse(
        self,
        token_type: str,
        token_hash: str,
        misused_by: str,
        misuse_action: str,
        target_repo: str,
        pii_detected: Optional[List[PIIData]] = None
    ) -> PermissionViolation:
        """Track API token or credential misuse"""
        pii_data = pii_detected or []
        # Add token hash as PII
        pii_data.append(PIIData(
            pii_type=PIIType.API_KEY if "api" in token_type.lower() else PIIType.GITHUB_TOKEN,
            value_hash=token_hash,
            value_preview=token_hash[:8] + "***" + token_hash[-4:],
            exposure_method="token_misuse",
            location=f"token_{token_type}"
        ))
        
        violation = PermissionViolation(
            violation_type=ViolationType.TOKEN_MISUSE,
            severity=SeverityLevel.CRITICAL,
            actor_id=misused_by,
            action_type=ActionType.ADMIN,
            target_repo=target_repo,
            description=f"Token misuse: {token_type} token used for {misuse_action}",
            pii_data=pii_data,
            pii_exposed_count=len(pii_data)
        )
        
        self.violations.append(violation)
        self.logger.critical(
            f"TOKEN_MISUSE: {token_type} token misused for {misuse_action} "
            f"by {misused_by}"
        )
        return violation
    
    def dump_violations_to_main(
        self,
        reason: str = "Scheduled compliance dump",
        reporter_id: str = "system"
    ) -> ViolationDumpReport:
        """
        Dump all violations to repository main branch
        This creates an audit trail for compliance enforcement
        """
        report = ViolationDumpReport(
            repo=self.repo,
            branch="main",
            violations=self.violations,
            total_violations=len(self.violations),
            reporter_id=reporter_id,
            report_reason=reason
        )
        
        # Count by severity
        for violation in self.violations:
            if violation.severity == SeverityLevel.CRITICAL:
                report.critical_count += 1
            elif violation.severity == SeverityLevel.ERROR:
                report.error_count += 1
            elif violation.severity == SeverityLevel.WARNING:
                report.warning_count += 1
            else:
                report.info_count += 1
            
            # Count PII by type
            for pii in violation.pii_data:
                pii_type = pii.pii_type.value
                report.pii_types_found[pii_type] = report.pii_types_found.get(pii_type, 0) + 1
                report.total_pii_exposed += 1
        
        # Write JSONL dump (each violation as separate line for streaming)
        self._write_jsonl_dump(report)
        
        # Create summary report
        summary = self._create_summary_report(report)
        
        self.logger.info(
            f"VIOLATION_DUMP: Generated report {report.report_id} with "
            f"{report.total_violations} violations and "
            f"{report.total_pii_exposed} PII items exposed"
        )
        
        return report
    
    def _write_jsonl_dump(self, report: ViolationDumpReport):
        """Write violations to JSONL format (one JSON per line)"""
        with open(self.dump_location, 'a') as f:
            # Write report header
            f.write(json.dumps({
                "type": "REPORT_HEADER",
                "report_id": report.report_id,
                "timestamp": report.report_timestamp.isoformat(),
                "repo": report.repo,
                "branch": report.branch,
                "total_violations": report.total_violations
            }) + "\n")
            
            # Write each violation
            for violation in report.violations:
                f.write(json.dumps(violation.to_dict()) + "\n")
            
            # Write summary footer
            f.write(json.dumps({
                "type": "REPORT_FOOTER",
                "report_id": report.report_id,
                "total_critical": report.critical_count,
                "total_errors": report.error_count,
                "total_warnings": report.warning_count,
                "total_pii_exposed": report.total_pii_exposed,
                "pii_types": report.pii_types_found
            }) + "\n")
    
    def _create_summary_report(self, report: ViolationDumpReport) -> str:
        """Create markdown summary report"""
        summary = f"""# Permission Violation Report - {report.report_id}

**Generated:** {report.report_timestamp.isoformat()}  
**Repository:** {report.repo}  
**Branch:** {report.branch}  
**Reporter:** {report.reporter_id}  
**Reason:** {report.report_reason}

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Violations | {report.total_violations} |
| Critical | {report.critical_count} |
| Errors | {report.error_count} |
| Warnings | {report.warning_count} |
| Info | {report.info_count} |
| **PII Items Exposed** | **{report.total_pii_exposed}** |

## PII Exposure Summary

"""
        for pii_type, count in report.pii_types_found.items():
            summary += f"- **{pii_type}:** {count} items\n"
        
        summary += f"""
## Critical Violations

"""
        for v in report.violations:
            if v.severity == SeverityLevel.CRITICAL:
                summary += f"""
### {v.violation_type.value.upper()}

- **ID:** {v.violation_id}
- **Actor:** {v.actor_email} ({v.actor_id})
- **Source IP:** {v.actor_ip}
- **Description:** {v.description}
- **Timestamp:** {v.timestamp.isoformat()}
- **PII Items:** {v.pii_exposed_count}

"""
        
        return summary
    
    def export_violations_report(self, output_format: str = "json") -> str:
        """Export violations in specified format"""
        if not self.violations:
            return ""
        
        if output_format == "json":
            return json.dumps(
                [v.to_dict() for v in self.violations],
                indent=2,
                default=str
            )
        elif output_format == "jsonl":
            lines = []
            for v in self.violations:
                lines.append(json.dumps(v.to_dict(), default=str))
            return "\n".join(lines)
        elif output_format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "violation_id", "violation_type", "severity", "actor_email",
                "target_repo", "description", "pii_exposed_count", "timestamp"
            ])
            writer.writeheader()
            for v in self.violations:
                writer.writerow({
                    "violation_id": v.violation_id,
                    "violation_type": v.violation_type.value,
                    "severity": v.severity.name,
                    "actor_email": v.actor_email,
                    "target_repo": v.target_repo,
                    "description": v.description,
                    "pii_exposed_count": v.pii_exposed_count,
                    "timestamp": v.timestamp.isoformat()
                })
            return output.getvalue()
        
        return ""

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize tracker
    tracker = BitbucketPermissionTracker(
        repo="mbk-darkcocoa/Radioactive_Foot_pi",
        dump_location="VIOLATIONS_DUMP.jsonl"
    )
    
    # Example: Track unauthorized access
    pii_found = [
        PIIData(
            pii_type=PIIType.EMAIL,
            value_hash=hashlib.sha256(b"user@example.com").hexdigest(),
            value_preview="user@ex...m",
            exposure_method="in_commit",
            location="src/config.py:42"
        )
    ]
    
    tracker.track_unauthorized_access(
        actor_id="attacker_123",
        actor_email="attacker@evil.com",
        actor_ip="192.168.1.100",
        target_repo="mbk-darkcocoa/Radioactive_Foot_pi",
        target_ref="main",
        required_permission="admin",
        granted_permission="read",
        description="Attempted to access protected main branch",
        pii_detected=pii_found
    )
    
    # Generate and dump violations
    report = tracker.dump_violations_to_main(
        reason="Security audit - unauthorized access detected",
        reporter_id="security_team"
    )
    
    print(f"Generated report: {report.report_id}")
    print(f"Total violations: {report.total_violations}")
    print(f"Total PII exposed: {report.total_pii_exposed}")
