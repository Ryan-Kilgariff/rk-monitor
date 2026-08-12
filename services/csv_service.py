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
            "URL",
            "Score",
            "Strength",
            "Recommended Service",
            "High Issues",
            "Medium Issues",
            "Low Issues",
            "Booking Provider",
            "Booking Links",
            "Top Problem",
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
                    top_problem = ""
                    if result.issues:
                        top_problem = (
                            result.issues[0].title
                        )
                    writer.writerow(
                        {
                            "URL": (
                                result.scan_result.url
                            ),
                            "Score": (
                                result.score.overall
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
                            "Top Problem": (
                                top_problem
                            ),
                            "Scan Successful": (
                                "Yes"
                            ),
                            "Error": "",
                        }
                    )
                else:
                    writer.writerow(
                        {
                            "URL": item.url,
                            "Score": "",
                            "Strength": "",
                            "Recommended Service": "",
                            "High Issues": "",
                            "Medium Issues": "",
                            "Low Issues": "",
                            "Booking Provider": "",
                            "Booking Links": "",
                            "Top Problem": "",
                            "Scan Successful": "No",
                            "Error": (
                                item.error_message
                                or ""
                            ),
                        }
                    )