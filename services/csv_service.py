import csv
from pathlib import Path
from services.batch_scan_service import BatchScanResult
class CsvService:
    def load_urls(
        self,
        file_path: str,
    ) -> list[str]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )
        urls = []
        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                raise ValueError(
                    "CSV file has no headings."
                )
            url_column = None
            possible_names = (
                "url",
                "website",
                "website url",
                "website_url",
                "site",
            )
            for heading in reader.fieldnames:
                if heading.lower().strip() in possible_names:
                    url_column = heading
                    break
            if url_column is None:
                raise ValueError(
                    "Could not find a URL column. "
                    "Use a heading such as URL or Website."
                )
            for row in reader:
                url = (
                    row.get(url_column, "")
                    .strip()
                )
                if url:
                    urls.append(url)
        return urls
    def export_results(
        self,
        batch: BatchScanResult,
        file_path: str,
    ) -> None:
        path = Path(file_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        headings = [
            "Priority",
            "Manual Review",
            "URL",
            "Strength",
            "Recommended Service",
            "Commercial Score",
            "Technical Score",
            "Site Quality Score",
            "Content Quality Score",
            "Primary Problem",
            "Outreach Angle",
            "Supporting Reasons",
            "High Issues",
            "Medium Issues",
            "Low Issues",
            "Booking Provider",
            "Booking Links",
            "Scan Successful",
            "Error",
        ]
        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=headings,
            )
            writer.writeheader()
            for item in batch.items:
                if (
                    item.successful
                    and item.result
                ):
                    result = item.result
                    limited_analysis = (
                        not result.scan_result.successful
                        or (
                            result.scan_result.status_code is not None
                            and result.scan_result.status_code >= 400
                        )
                        or (
                            result.domain_identity is not None
                            and result.domain_identity.mismatch_detected
                        )
                    )
                    if limited_analysis:
                        commercial_score = ""
                        hospitality_score = ""
                        content_score = ""
                    else:
                        commercial_score = (
                            result.commercial_score.commercial_score
                        )
                        hospitality_score = (
                            result.commercial_score.site_quality_score
                        )
                        content_score = (
                            result.commercial_score.content_quality_score
                        )
                    if result.prospect.strength == "STRONG":
                        priority = 1
                    elif result.prospect.strength == "GOOD":
                        priority = 2
                    elif result.prospect.strength == "POSSIBLE":
                        priority = 3
                    else:
                        priority = 4
                    writer.writerow(
                        {
                            "Priority": priority,
                            "Manual Review": (
                                "Yes"
                                if result.prospect.manual_review_needed
                                else "No"
                            ),
                            "URL": (
                                result.scan_result.url
                            ),
                            "Strength": (
                                result.prospect.strength
                            ),
                            "Recommended Service": (
                                result.prospect
                                .recommended_service
                            ),
                            "High Issues": (
                                result.score.high_issues
                            ),
                            "Medium Issues": (
                                result.score.medium_issues
                            ),
                            "Low Issues": (
                                result.score.low_issues
                            ),
                            "Booking Provider": (
                                result.booking_provider
                                or ""
                            ),
                            "Booking Links": (
                                len(
                                    result.booking_links
                                )
                            ),
                            "Scan Successful": (
                                "Limited"
                                if limited_analysis
                                else "Yes"
                            ),
                            "Error": (
                                result.scan_result.error_message
                                or ""
                            ),
                            "Commercial Score": (
                                commercial_score
                            ),
                            "Technical Score": (
                                result.score.overall
                            ),
                            "Site Quality Score": (
                                hospitality_score
                            ),
                            "Content Quality Score": (
                                content_score
                            ),
                            "Primary Problem": (
                                result.prospect
                                .primary_problem
                            ),
                            "Outreach Angle": (
                                result.prospect
                                .outreach_angle
                            ),
                            "Supporting Reasons": (
                                " | ".join(
                                    result.prospect
                                    .supporting_reasons
                                )
                            ),
                        }
                    )
                else:
                    writer.writerow(
                        {
                            "Priority": "",
                            "Manual Review": "",
                            "URL": item.url,
                            "Strength": "",
                            "Recommended Service": "",
                            "High Issues": "",
                            "Medium Issues": "",
                            "Low Issues": "",
                            "Booking Provider": "",
                            "Booking Links": "",
                            "Scan Successful": "No",
                            "Error": (
                                item.error_message
                                or ""
                            ),
                            "Commercial Score": "",
                            "Site Quality Score": "",
                            "Content Quality Score": "",
                            "Primary Problem": "",
                            "Outreach Angle": "",
                            "Supporting Reasons": "",
                            "Technical Score": "",
                        }
                    )