from services.batch_scan_service import BatchScanResult
class BatchReportService:
    def print_report(
        self,
        batch: BatchScanResult,
    ) -> None:
        print()
        print("=" * 80)
        print("RK MONITOR - PROSPECT BATCH RESULTS")
        print("=" * 80)
        successful = (
            batch.successful_items
        )
        failed = (
            batch.failed_items
        )
        def ranking_key(item):
            result = item.result
            if result is None:
                return (3, 999)
            if (
                not result.scan_result.successful
                and result.prospect.strength == "STRONG"
            ):
                return (0, 0)
            if not result.scan_result.successful:
                return (2, 999)
            return (
                1,
                result.commercial_score.commercial_score,
            )
        ranked = sorted(
            successful,
            key=ranking_key,
        )
        print()
        print(
            f"Sites Scanned: "
            f"{len(batch.items)}"
        )
        print(
            f"Successful:    "
            f"{len(successful)}"
        )
        print(
            f"Failed:        "
            f"{len(failed)}"
        )
        print()
        print("RANKED PROSPECTS")
        print("-" * 80)
        for index, item in enumerate(
            ranked,
            start=1,
        ):
            result = item.result
            if result is None:
                continue
            print()
            print(
                f"{index}. "
                f"{result.scan_result.url}"
            )
            if not result.scan_result.successful:
                print(
                    "   Commercial Score: N/A"
                )
                print(
                    "   Technical: "
                    f"{result.score.overall}"
                )
                print(
                    "   Hospitality: N/A"
                )
                print(
                    "   Content: N/A"
                )
            else:
                print(
                    "   Commercial Score: "
                    f"{result.commercial_score.commercial_score} / 100"
                )
                print(
                    "   Technical: "
                    f"{result.commercial_score.technical_score}"
                )
                print(
                    "   Hospitality: "
                    f"{result.commercial_score.site_quality_score}"
                )
                print(
                    "   Content: "
                    f"{result.commercial_score.content_quality_score}"
                )
            print(
                f"   Strength: "
                f"{result.prospect.strength}"
            )
            print(
                f"   Review Priority: "
                f"{result.prospect.review_priority}"
            )
            print(
                f"   Manual Review: "
                f"{'Yes' if result.prospect.manual_review_needed else 'No'}"
            )
            print(
                f"   Recommended: "
                f"{result.prospect.recommended_service}"
            )
            print(
                f"   Primary Problem: "
                f"{result.prospect.primary_problem}"
            )
            print(
                f"   Outreach Angle: "
                f"{result.prospect.outreach_angle}"
            )
            print(
                f"   High Issues: "
                f"{result.score.high_issues}"
            )
            print(
                f"   Medium Issues: "
                f"{result.score.medium_issues}"
            )
            if result.prospect.supporting_reasons:
                print(
                    "   Reasons: "
                    + " | ".join(
                        result.prospect.supporting_reasons
                    )
                )
        if failed:
            print()
            print("FAILED SCANS")
            print("-" * 80)
            for item in failed:
                print(
                    f"{item.url}"
                )
                print(
                    f"  Error: "
                    f"{item.error_message}"
                )
        print()
        print("=" * 80)