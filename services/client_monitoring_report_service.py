from services.monitoring_service import ScanComparison
class ClientMonitoringReportService:
    def print_summary(
        self,
        comparison: ScanComparison,
    ) -> None:
        print()
        print("CLIENT MONITORING UPDATE")
        print("-" * 60)
        if comparison.current_score is None:
            print(
                "Commercial Website Score: "
                "Not Assessed"
            )
            print()
            print(
                "The latest scan was not complete "
                "enough for a commercial comparison."
            )
            return
        print(
            "Commercial Website Score: "
            f"{comparison.current_score}"
        )
        if not comparison.has_previous_scan:
            print()
            print(
                "This is the first recorded "
                "commercial monitoring baseline."
            )
            print(
                "Future complete scans will be "
                "compared against this assessment."
            )
        else:
            print(
                "Previous Commercial Score: "
                f"{comparison.previous_score}"
            )
            if comparison.score_change is not None:
                change = comparison.score_change
                change_text = (
                    f"+{change}"
                    if change > 0
                    else str(change)
                )
                print(
                    f"Score Change: {change_text}"
                )
        print()
        print("NEW ISSUES")
        print("-" * 60)
        if comparison.new_issues:
            for issue in comparison.new_issues:
                print(
                    f"- {issue}"
                )
        else:
            print(
                "None"
            )
        print()
        print("RESOLVED ISSUES")
        print("-" * 60)
        if comparison.resolved_issues:
            for issue in comparison.resolved_issues:
                print(
                    f"- {issue}"
                )
        else:
            print(
                "None"
            )