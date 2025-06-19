import re
from pathlib import Path
import pandas as pd
import json
from typing import Optional, List, Dict, Any

from .client import IQServerClient, Application, ReportInfo
from .config import Config
from .utils import logger, resolve_path


class RawReportFetcher:
    """🎯 Fetches and saves IQ Server reports as CSV files and consolidates them."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.iq = IQServerClient(
            str(config.iq_server_url), config.iq_username, config.iq_password
        )
        self.output_path = Path(resolve_path(config.output_dir))
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _extract_report_id(self, info: ReportInfo) -> Optional[str]:
        """Extract report ID from report info."""
        if info.reportDataUrl:
            try:
                return info.reportDataUrl.split("/reports/")[1].split("/")[0]
            except Exception:
                pass
        return info.scanId or info.reportId

    def _fetch_app_report(
        self, app: Application, idx: int, total: int
    ) -> Optional[str]:
        """Fetch report for a single application, save as JSON, and return the file path."""
        try:
            logger.info(f"🔍 [{idx}/{total}] Processing {app.name}...")

            info = self.iq.get_latest_report_info(app.id)
            if not info:
                logger.warning(f"⚠️  [{idx}/{total}] No reports found for {app.name}")
                return None

            report_id = self._extract_report_id(info)
            if not report_id:
                logger.warning(f"⚠️  [{idx}/{total}] No report ID for {app.name}")
                return None

            data = self.iq.get_policy_violations(app.publicId, report_id)
            if not data:
                logger.warning(f"⚠️  [{idx}/{total}] No report data for {app.name}")
                return None

            # Save JSON to disk
            json_filename = f"{app.publicId}_{report_id}.json"
            json_path = self.output_path / json_filename
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ [{idx}/{total}] Saved JSON: {json_filename}")
            return str(json_path)
        except Exception as e:
            logger.error(f"❌ [{idx}/{total}] Error processing {app.name}: {e}")
            return None

    def get_applications(self) -> List[Application]:
        """Fetch and display applications."""
        logger.info("🔍 Fetching applications from IQ Server...")
        apps = self.iq.get_applications(self.config.organization_id)

        if not apps:
            logger.error("❌ Failed to fetch applications or no applications found")
            return []

        logger.info(f"🎯 Found {len(apps)} applications!")

        if apps:
            logger.info("📋 Applications preview:")
            for i, app in enumerate(apps[:5], 1):
                logger.info(f"   {i}. {app.name} ({app.publicId})")
            if len(apps) > 5:
                logger.info(f"   ... and {len(apps) - 5} more! 🚀")

        return apps

    def fetch_all_reports(self) -> None:
        """Main method to fetch all reports and consolidate them."""
        logger.info("🚀 Starting raw report fetch process...")
        logger.info(f"📁 Output directory: {self.output_path.absolute()}")

        apps = self.get_applications()
        if not apps:
            logger.warning("😞 No applications to process")
            return

        total = len(apps)
        success_count = 0
        json_files = []

        logger.info(f"⚡ Processing {total} applications...")

        for i, app in enumerate(apps, 1):
            json_path = self._fetch_app_report(app, i, total)
            if json_path:
                json_files.append(json_path)
                success_count += 1

        # Final summary with emojis
        logger.info("=" * 50)
        logger.info("🎉 Processing completed!")
        logger.info(f"✅ Successfully processed: {success_count}/{total}")

        if success_count == total:
            logger.info("🏆 Perfect! All reports fetched successfully! 🎊")
        elif success_count > 0:
            failed = total - success_count
            logger.info(f"⚠️  {failed} reports failed to fetch")
        else:
            logger.error("😞 No reports were successfully fetched")

        # Load all JSON files and consolidate
        report_data_list = []
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    report_data_list.append(json.load(f))
            except Exception as e:
                logger.error(f"❌ Failed to load {json_file}: {e}")

        # Save consolidated CSV to OUTPUT_DIR
        consolidated_csv = self.output_path / "consolidated_security_report.csv"
        self.consolidate_reports_to_csv(report_data_list, consolidated_csv)

        # Delete JSON files after consolidation
        for json_file in json_files:
            try:
                Path(json_file).unlink()
                logger.info(f"🗑️  Deleted {json_file}")
            except Exception as e:
                logger.warning(f"⚠️  Could not delete {json_file}: {e}")

    def consolidate_reports_to_csv(
        self, report_data_list: List[Dict[str, Any]], output_csv_path: Path
    ) -> None:
        """Consolidate all report data into a single CSV as specified."""
        if not report_data_list:
            logger.warning("❌ No report data found to consolidate!")
            return
        logger.info(
            f"🔍 Found {len(report_data_list)} reports to process for consolidation."
        )
        # First pass: aggregate all violations per application
        app_severity_counts = {}
        app_rows = []
        for data in report_data_list:
            try:
                app = data.get("application", {})
                app_id = app.get("publicId", "unknown")
                org_id = app.get("organizationId", "unknown")
                components = data.get("components", [])
                if app_id not in app_severity_counts:
                    app_severity_counts[app_id] = {
                        "Critical": 0,
                        "Severe": 0,
                        "Moderate": 0,
                    }
                for c in components:
                    violations = c.get("violations", [])
                    for violation in violations:
                        threat_level = violation.get("policyThreatLevel", 0)
                        if threat_level >= 7:
                            app_severity_counts[app_id]["Critical"] += 1
                        elif threat_level >= 4:
                            app_severity_counts[app_id]["Severe"] += 1
                        elif threat_level >= 1:
                            app_severity_counts[app_id]["Moderate"] += 1
                app_rows.append((app_id, org_id, components))
            except Exception as e:
                logger.error(f"   ❌ Error processing report data: {e}")

        # Second pass: build rows with total counts for each app
        consolidated_data = []
        for app_id, org_id, components in app_rows:
            for c in components:
                component_name = c.get("displayName", "")
                violations = c.get("violations", [])
                if not violations:
                    continue  # skip rows with no policy violations
                for violation in violations:
                    threat_level = violation.get("policyThreatLevel", 0)

                    def extract_cve_info(constraints):
                        cve_info = {
                            "cve_id": "",
                            "condition": "",
                            "constraint_name": "",
                        }
                        for constraint in constraints:
                            constraint_name = constraint.get("constraintName", "")
                            conditions = constraint.get("conditions", [])
                            cve_info["constraint_name"] = constraint_name
                            cve_ids = []
                            condition_parts = []
                            for condition in conditions:
                                condition_summary = condition.get(
                                    "conditionSummary", ""
                                )
                                condition_reason = condition.get("conditionReason", "")
                                cve_match = re.search(
                                    r"CVE-\d{4}-\d+",
                                    condition_summary + " " + condition_reason,
                                )
                                if cve_match and cve_match.group(0) not in cve_ids:
                                    cve_ids.append(cve_match.group(0))
                                if condition_reason:
                                    condition_parts.append(condition_reason)
                                elif condition_summary:
                                    condition_parts.append(condition_summary)
                            cve_info["cve_id"] = ", ".join(cve_ids) if cve_ids else ""
                            cve_info["condition"] = (
                                " | ".join(condition_parts) if condition_parts else ""
                            )
                        return cve_info

                    cve_info = extract_cve_info(violation.get("constraints", []))
                    policy_action = ""
                    if violation.get("policyThreatCategory", "").upper() == "SECURITY":
                        if threat_level >= 7:
                            policy_action = "Security-Critical"
                        elif threat_level >= 4:
                            policy_action = "Security-CVSS score than or equals 7"
                        else:
                            policy_action = "Security-Moderate"
                    else:
                        sev = (
                            "Critical"
                            if threat_level >= 7
                            else "Severe"
                            if threat_level >= 4
                            else "Moderate"
                            if threat_level >= 1
                            else "Low"
                        )
                        policy_action = (
                            f"{violation.get('policyThreatCategory', '')}-{sev}"
                            if violation.get("policyThreatCategory", "")
                            else sev
                        )
                    consolidated_row = {
                        "No.": len(consolidated_data) + 1,
                        "Application": app_id,
                        "Organization": org_id,
                        "time": "10 hours ago",
                        "Critical (7-10)": app_severity_counts[app_id]["Critical"],
                        "Severe (4-6)": app_severity_counts[app_id]["Severe"],
                        "Moderate (1-3)": app_severity_counts[app_id]["Moderate"],
                        "Policy": violation.get("policyName", ""),
                        "Component": component_name,
                        "Threat": threat_level,
                        "Policy/Action": policy_action,
                        "Constraint Name": cve_info["constraint_name"],
                        "Condition": cve_info["condition"],
                        "CVE": cve_info["cve_id"],
                    }
                    consolidated_data.append(consolidated_row)

        if consolidated_data:
            df_consolidated = pd.DataFrame(consolidated_data)
            output_csv_path.parent.mkdir(parents=True, exist_ok=True)
            df_consolidated.to_csv(output_csv_path, index=False)
            logger.info(f"💾 Consolidated CSV saved to: {output_csv_path}")
            logger.info(f"📊 Generated {len(consolidated_data)} consolidated rows.")
        else:
            logger.warning("❌ No data was consolidated!")
