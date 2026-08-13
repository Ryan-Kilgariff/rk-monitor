from services.scan_service import FullScanResult
class ReportService:
    def print_report(
        self,
        result: FullScanResult,
    ) -> None:
        scan = result.scan_result
        score = result.score
        prospect = result.prospect
        comparison = result.comparison
        print()
        print("=" * 60)
        print("RK MONITOR REPORT")
        print("=" * 60)
        print()
        print("WEBSITE")
        print("-" * 60)
        print(
            f"URL: {scan.url}"
        )
        print(
            f"Page Title: "
            f"{scan.page_title}"
        )
        print(
            f"HTTP Status: "
            f"{scan.status_code}"
        )
        if scan.response_time is not None:
            print(
                f"Response Time: "
                f"{scan.response_time:.2f}s"
            )
        print(
            f"HTTPS: "
            f"{'Yes' if scan.has_https else 'No'}"
        )
        print(
            f"SSL Verification: "
            f"{'FAILED' if scan.ssl_verification_failed else 'Passed'}"
        )
        print(
            f"Mobile Viewport: "
            f"{'Yes' if scan.has_mobile_viewport else 'No'}"
        )
        print(
            f"Google Analytics: "
            f"{'Detected' if scan.has_google_analytics else 'Not detected'}"
        )
        print()
        print("BOOKING")
        print("-" * 60)
        print(
            f"Booking Provider: "
            f"{result.booking_provider or 'Unknown'}"
        )
        print(
            f"Booking Links Found: "
            f"{len(result.booking_links)}"
        )
        for link in result.booking_links:
            print(
                f" - {link}"
            )
        print()
        print("IMPORTANT PAGES")
        print("-" * 60)
        if not result.crawled_pages:
            print(
                "No important hospitality "
                "pages detected."
            )
        for page in result.crawled_pages:
            print()
            print(
                f"{page.page_type.upper()}"
            )
            print(
                f"Status: "
                f"{page.status_code}"
            )
            print(
                f"URL: "
                f"{page.url}"
            )
            if page.successful:
                print(
                    f"Images: "
                    f"{page.image_count}"
                )
                print(
                    f"Headings: "
                    f"{page.heading_count}"
                )
                print(
                    f"Links: "
                    f"{page.link_count}"
                )
        print()
        print("ISSUES")
        print("-" * 60)
        if not result.issues:
            print(
                "No significant issues detected."
            )
        for issue in result.issues:
            print()
            print(
                f"[{issue.severity}] "
                f"{issue.title}"
            )
            print(
                f"Category: "
                f"{issue.category}"
            )
            print(
                f"Evidence: "
                f"{issue.evidence}"
            )
            print(
                f"Commercial Impact: "
                f"{issue.commercial_impact}"
            )
            print(
                f"Recommended Action: "
                f"{issue.recommended_action}"
            )
        print()
        print("RK MONITOR SCORE")
        print("-" * 60)
        print(
            f"Technical Health:      "
            f"{score.technical_health} / 100"
        )
        print(
            f"Booking Journey:       "
            f"{score.booking_journey} / 100"
        )
        print(
            f"Mobile Experience:     "
            f"{score.mobile_experience} / 100"
        )
        print(
            f"Room Presentation:     "
            f"{score.room_presentation} / 100"
        )
        print(
            f"Guest Information:     "
            f"{score.guest_information} / 100"
        )
        print(
            f"Analytics:             "
            f"{score.analytics} / 100"
        )
        print("-" * 60)
        print(
            f"OVERALL:               "
            f"{score.overall} / 100"
        )
        print()
        print(
            f"High Issues:   "
            f"{score.high_issues}"
        )
        print(
            f"Medium Issues: "
            f"{score.medium_issues}"
        )
        print(
            f"Low Issues:    "
            f"{score.low_issues}"
        )
        print()
        print("COMMERCIAL WEBSITE SCORE")
        print()
        if not result.scan_result.successful:
            print(
                "COMMERCIAL SCORE:      N/A"
            )
            print(
                "Reason: Full website analysis "
                "could not be completed."
            )
        else:
            commercial = result.commercial_score
            print(
                f"Technical Score:       "
                f"{commercial.technical_score} / 100"
            )
            print(
                f"Hospitality Quality:   "
                f"{commercial.site_quality_score} / 100"
            )
            print(
                f"Content Quality:       "
                f"{commercial.content_quality_score} / 100"
            )
            print("-" * 60)
            print(
                f"COMMERCIAL SCORE:      "
                f"{commercial.commercial_score} / 100"
            )
            print()
        print()
        print("## PROSPECT QUALIFICATION")
        print()
        prospect = result.prospect
        print(
            f"Strength: "
            f"{prospect.strength}"
        )
        print(
            f"Recommended Service: "
            f"{prospect.recommended_service}"
        )
        print(
            f"Reason: "
            f"{prospect.reason}"
        )
        print(
            f"Primary Problem: "
            f"{prospect.primary_problem}"
        )
        print(
            f"Outreach Angle: "
            f"{prospect.outreach_angle}"
        )
        if prospect.supporting_reasons:
            print()
            print("Why this prospect:")
            for reason in prospect.supporting_reasons:
                print(
                    f" - {reason}"
                )
        print()
        print("MONITORING")
        print("-" * 60)
        if not comparison.has_previous_scan:
            print(
                "First recorded scan."
            )
            print(
                "Future scans will be "
                "compared against this baseline."
            )
        else:
            print(
                f"Previous Score: "
                f"{comparison.previous_score}"
            )
            print(
                f"Current Score: "
                f"{comparison.current_score}"
            )
            if comparison.score_change is not None:
                if comparison.score_change > 0:
                    change = (
                        f"+{comparison.score_change}"
                    )
                else:
                    change = str(
                        comparison.score_change
                    )
                print(
                    f"Score Change: "
                    f"{change}"
                )
            if comparison.new_issues:
                print()
                print("NEW ISSUES")
                for issue in comparison.new_issues:
                    print(
                        f" + {issue}"
                    )
            if comparison.resolved_issues:
                print()
                print("RESOLVED ISSUES")
                for issue in comparison.resolved_issues:
                    print(
                        f" - {issue}"
                    )
            if (
                not comparison.new_issues
                and not comparison.resolved_issues
                and comparison.score_change == 0
            ):
                print()
                print(
                    "No significant change "
                    "since the previous scan."
                )
        print()
        print(
            f"Scan saved successfully. "
            f"Scan ID: {result.scan_id}"
        )
        print()
        print("## SITE QUALITY")
        print()
        if not result.scan_result.successful:
            print(
                "Not available - website content "
                "could not be retrieved."
            )
        else:
            quality = result.site_quality
            print(
                f"Important Page Types: "
                f"{quality.important_page_count}"
            )
            print(
                f"Rooms / Accommodation: "
                f"{'Yes' if quality.has_rooms else 'No'}"
            )
            print(
                f"Room Pages Detected: "
                f"{quality.room_page_count}"
            )
            print(
                f"Room Images Detected: "
                f"{quality.room_image_count}"
            )
            print(
                f"Booking Route: "
                f"{'Yes' if quality.has_booking_route else 'No'}"
            )
            print(
                f"Guest Information: "
                f"{'Yes' if quality.has_guest_information else 'No'}"
            )
            print(
                f"Dedicated Contact Page: "
                f"{'Yes' if quality.has_contact_page else 'No'}"
            )
            print()
            print(
                "ADDITIONAL HOSPITALITY FEATURES"
            )
            print(
                f"Dining: "
                f"{'Yes' if quality.has_dining else 'No'}"
            )
            print(
                f"Events: "
                f"{'Yes' if quality.has_events else 'No'}"
            )
            print(
                f"Offers: "
                f"{'Yes' if quality.has_offers else 'No'}"
            )
            print()
            print(
                f"Site Quality Score: "
                f"{quality.quality_score} / 100"
            )
        print()
        print("## CONTENT QUALITY")
        print()
        if not result.scan_result.successful:
            print(
                "Not available - no pages "
                "could be analysed."
            )
        else:
            content = result.content_quality
            print(
                f"Pages Analysed: "
                f"{content.pages_checked}"
            )
            print(
                f"Average Word Count: "
                f"{content.average_word_count}"
            )
            print(
                f"Thin Pages: "
                f"{len(content.thin_pages)}"
            )
            print(
                f"Duplicate Page Pairs: "
                f"{len(content.duplicate_pairs)}"
            )
            print(
                f"Content Depth Score: "
                f"{content.content_depth_score} / 100"
            )
            print(
                f"Site Pages Discovered: "
                f"{len(result.general_pages)}"
            )
            if content.thin_pages:
                print()
                print("THIN PAGES")
                for url in content.thin_pages:
                    print(
                        f" - {url}"
                    )
            if content.duplicate_pairs:
                print()
                print("POSSIBLE DUPLICATE CONTENT")
                for pair in content.duplicate_pairs:
                    overlap_percent = round(
                        pair.overlap * 100
                    )
                    print(
                        f" - {overlap_percent}% content overlap"
                    )
                    print(
                        f"   {pair.first_url}"
                    )
                    print(
                        f"   {pair.second_url}"
                    )
        if (
                result.scan_result.successful
                and result.general_pages
            ):
            print()
            print("DISCOVERED PAGES")
            for page in result.general_pages:
                print(
                    f" - {page.url} "
                    f"({page.word_count} words)"
                )
        print()
        print("=" * 60)