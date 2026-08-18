from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from services.scan_service import FullScanResult
class PdfReportService:
    def _draw_footer(
        self,
        canvas,
        document,
    ) -> None:
        canvas.saveState()
        page_width, _ = A4
        canvas.setFont(
            "Helvetica",
            8,
        )
        canvas.drawString(
            18 * mm,
            10 * mm,
            "RK Hospitality Studio",
        )
        canvas.drawRightString(
            page_width - (18 * mm),
            10 * mm,
            f"Page {document.page}",
        )
        canvas.restoreState()
    def export_client_report(
        self,
        result: FullScanResult,
        output_path: str,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        document = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "RKTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        )
        heading_style = ParagraphStyle(
            "RKHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=16,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "RKBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14.5,
            spaceAfter=3,
            textColor=colors.black,
        )
        story = []
        story.append(
            Paragraph(
                "RK MONITOR WEBSITE REVIEW",
                title_style,
            )
        )
        prepared_style = ParagraphStyle(
            "RKPrepared",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=8.5,
            leading=11,
            spaceAfter=4,
        )
        story.append(
            Paragraph(
                "Prepared by RK Hospitality Studio",
                prepared_style,
            )
        )
        url_style = ParagraphStyle(
            "RKUrl",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=9,
            leading=12,
            spaceAfter=4,
        )
        story.append(
            Paragraph(
                result.scan_result.url,
                url_style,
            )
        )
        story.append(
            Spacer(1, 8 * mm)
        )
        score_style = ParagraphStyle(
            "RKScore",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=26,
            leading=30,
            spaceBefore=4,
            spaceAfter=2,
        )
        score_label_style = ParagraphStyle(
            "RKScoreLabel",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=10,
            leading=13,
            spaceAfter=6,
        )
        scan_incomplete = (
            result.assessment_status == "PARTIAL"
        )
        commercial_score_display = (
            "Not Fully Assessed"
            if scan_incomplete
            else (
                f"{result.commercial_score.commercial_score} / 100"
            )
        )
        story.append(
            Paragraph(
                "Commercial Website Score",
                score_label_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>{commercial_score_display}</b>",
                score_style,
            )
        )
        story.append(
            Spacer(
                1,
                3 * mm,
            )
        )
        assessment_status_display = (
            "Partial"
            if result.assessment_status == "PARTIAL"
            else "Complete"
        )
        story.append(
            Paragraph(
                "Assessment Status",
                heading_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>{assessment_status_display}</b>",
                body_style,
            )
        )
        client_issues = [
            issue
            for issue in result.issues
            if (
                not issue.requires_review
                or issue.review_status == "CONFIRMED"
            )
        ]
        commercial_score_value = (
            result.commercial_score.commercial_score
        )
        if scan_incomplete:
            summary_text = (
                "The website could not be fully assessed because "
                "RK Monitor encountered a technical connection issue. "
                "The findings below reflect the areas that could be "
                "verified during the scan."
                )
        elif commercial_score_value < 70:
            summary_text = (
                "The website is technically accessible, "
                "but the review identified commercial "
                "weaknesses that may affect the guest "
                "journey and direct-booking experience."
            )
        elif commercial_score_value < 85:
            summary_text = (
                "The website has a generally functional "
                "foundation, but several opportunities "
                "were identified to improve the guest "
                "journey, website structure or booking "
                "experience."
            )
        else:
            summary_text = (
                "The website performs strongly overall, "
                "with no major commercial weaknesses "
                "identified during this review."
            )
        story.append(
            Paragraph(
                "Website Review Summary",
                heading_style,
            )
        )
        story.append(
            Paragraph(
                summary_text,
                body_style,
            )
        )
        story.append(
            Paragraph(
                (
                    f"<b>Verified Findings:</b> "
                    f"{len(client_issues)}"
                ),
                body_style,
            )
        )
        https_status = (
            "Yes"
            if (
                result.scan_result.has_https
                and not result.scan_result.ssl_verification_failed
                and not result.scan_result.connection_failed
            )
            else "No"
        )
        story.append(
            Paragraph(
                "Website Snapshot",
                heading_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>HTTPS:</b> {https_status}",
                body_style,
            )
        )
        mobile_status = (
            "Not Assessed"
            if scan_incomplete
            else (
                "Yes"
                if result.scan_result.has_mobile_viewport
                else "No"
            )
        )
        analytics_status = (
            "Not Assessed"
            if scan_incomplete
            else (
                "Detected"
                if result.scan_result.has_google_analytics
                else "Not detected"
            )
        )
        booking_status = (
            "Not Assessed"
            if scan_incomplete
            else (
                "Detected"
                if result.booking_links
                else "Not detected"
            )
        )
        rooms_status = (
            "Not Assessed"
            if scan_incomplete
            else (
                "Detected"
                if result.site_quality.has_rooms
                else "Not detected"
            )
        )
        story.append(
            Paragraph(
                f"<b>Mobile Viewport:</b> {mobile_status}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Analytics:</b> {analytics_status}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Booking Route:</b> {booking_status}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Rooms / Accommodation:</b> {rooms_status}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                "Score Breakdown",
                heading_style,
            )
        )
        score_data = [
            [
                "Commercial Area",
                "Score",
            ],
            [
                "Technical Performance",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else (
                        f"{result.commercial_score.technical_score} / 100"
                    )
                ),
            ],
            [
                "Hospitality Structure",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else (
                        f"{result.commercial_score.site_quality_score} / 100"
                    )
                ),
            ],
            [
                "Content Quality",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else (
                        f"{result.commercial_score.content_quality_score} / 100"
                    )
                ),
            ],
            [
                "Commercial Website Score",
                (
                    "Not Fully Assessed"
                    if scan_incomplete
                    else (
                        f"{result.commercial_score.commercial_score} / 100"
                    )
                ),
            ],
        ]
        score_table = Table(
            score_data,
            colWidths=[
                115 * mm,
                40 * mm,
            ],
        )
        score_table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (0, -1),
                        "Helvetica",
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (1, -1),
                        "RIGHT",
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, 0),
                        0.75,
                        colors.grey,
                    ),
                    (
                        "LINEBELOW",
                        (0, 1),
                        (-1, -2),
                        0.25,
                        colors.lightgrey,
                    ),
                ]
            )
        )
        story.append(score_table)
        strengths = []
        if (
            result.scan_result.has_https
            and not result.scan_result.ssl_verification_failed
            and not result.scan_result.connection_failed
        ):
            strengths.append("Secure HTTPS connection")
        if result.scan_result.has_mobile_viewport:
            strengths.append(
                "Mobile viewport configured"
            )
        if result.booking_links:
            strengths.append(
                "Direct booking route detected"
            )
        if result.site_quality.has_rooms:
            strengths.append(
                "Rooms or accommodation content detected"
            )
        if result.site_quality.has_guest_information:
            strengths.append(
                "Guest information available"
            )
        if strengths:
            story.append(
                Paragraph(
                    "Strengths",
                    heading_style,
                )
            )

            for strength in strengths:
                story.append(
                    Paragraph(
                        f"- {strength}",
                        body_style,
                    )
                )
        if client_issues:
            story.append(
                PageBreak()
            )
        if not client_issues:
            story.append(
                KeepTogether(
                    [
                        Paragraph(
                            "Verified Findings",
                            heading_style,
                        ),
                        Paragraph(
                            (
                                "No verified priority issues "
                                "were identified."
                            ),
                            body_style,
                        ),
                    ]
                )
            )
        else:
            story.append(
                Paragraph(
                    "Verified Findings",
                    heading_style,
                )
            )
        for issue in client_issues:
            story.append(
                Paragraph(
                    (
                        f"<b>[{issue.severity}] "
                        f"{issue.title}</b>"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    (
                        f"<b>Category:</b> "
                        f"{issue.category}"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    (
                        f"<b>Evidence:</b> "
                        f"{issue.evidence}"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    (
                        f"<b>Commercial Impact:</b> "
                        f"{issue.commercial_impact}"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(
                    (
                        f"<b>Recommended Action:</b> "
                        f"{issue.recommended_action}"
                    ),
                    body_style,
                )
            )
            story.append(
                Spacer(1, 5 * mm)
            )
        story.append(
            Paragraph(
                "Recommended Next Step",
                heading_style,
            )
        )
        if client_issues:
            recommendation = (
                "Review and address the verified "
                "findings above, prioritising issues "
                "that may affect the guest journey "
                "or direct booking experience."
            )
        else:
            recommendation = (
                "No verified priority issues were "
                "identified in this review. Continue "
                "monitoring the website for technical, "
                "content and booking journey changes."
            )
        story.append(
            Paragraph(
                recommendation,
                body_style,
            )
        )
        document.build(
            story,
            onFirstPage=self._draw_footer,
            onLaterPages=self._draw_footer,
        )
        return str(output)
    def export_monitoring_update(
        self,
        website_url: str,
        comparison,
        escalation,
        output_path: str,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        document = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "RKMonitoringTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "RKMonitoringBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14.5,
            spaceAfter=3,
            textColor=colors.black,
        )
        heading_style = ParagraphStyle(
            "RKMonitoringHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=16,
            spaceAfter=8,
        )
        prepared_style = ParagraphStyle(
            "RKMonitoringPrepared",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=8.5,
            leading=11,
            spaceAfter=4,
        )
        url_style = ParagraphStyle(
            "RKMonitoringUrl",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=9,
            leading=12,
            spaceAfter=4,
        )
        score_style = ParagraphStyle(
            "RKMonitoringScore",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=26,
            leading=30,
            spaceBefore=4,
            spaceAfter=2,
        )
        score_label_style = ParagraphStyle(
            "RKMonitoringScoreLabel",
            parent=body_style,
            alignment=TA_CENTER,
            fontSize=10,
            leading=13,
            spaceAfter=6,
        )
        story = []
        story.append(
            Paragraph(
                "RK MONITOR WEBSITE MONITORING UPDATE",
                title_style,
            )
        )
        story.append(
            Paragraph(
                "Prepared by RK Hospitality Studio",
                prepared_style,
            )
        )
        story.append(
            Paragraph(
                website_url,
                url_style,
            )
        )
        story.append(
            Spacer(
                1,
                8 * mm,
            )
        )
        current_score_display = (
            "Not Assessed"
            if comparison.current_score is None
            else f"{comparison.current_score} / 100"
        )
        story.append(
            Paragraph(
                "Commercial Website Score",
                score_label_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>{current_score_display}</b>",
                score_style,
            )
        )
        if comparison.current_score is None:
            summary_text = (
                "The latest monitoring scan was not "
                "complete enough to produce a reliable "
                "commercial website score."
            )
        elif not comparison.has_previous_scan:
            summary_text = (
                "This assessment establishes the first "
                "recorded commercial monitoring baseline. "
                "Future complete scans will be compared "
                "against this result."
            )
        elif comparison.score_change is None:
            summary_text = (
                "A previous monitoring baseline exists, "
                "but a reliable score comparison could "
                "not be calculated."
            )
        elif comparison.score_change > 0:
            summary_text = (
                "The commercial website score has improved "
                f"by {comparison.score_change} point(s) "
                "since the previous monitored assessment."
            )
        elif comparison.score_change < 0:
            summary_text = (
                "The commercial website score has decreased "
                f"by {abs(comparison.score_change)} point(s) "
                "since the previous monitored assessment."
            )
        else:
            summary_text = (
                "The commercial website score is unchanged "
                "since the previous monitored assessment."
            )
        story.append(
            Paragraph(
                "Monitoring Summary",
                heading_style,
            )
        )
        story.append(
            Paragraph(
                summary_text,
                body_style,
            )
        )
        story.append(
            Paragraph(
                "Escalation Status",
                heading_style,
            )
        )
        story.append(
            Paragraph(
                (
                    f"<b>Level:</b> "
                    f"{escalation.level}"
                ),
                body_style,
            )
        )
        story.append(
            Paragraph(
                (
                    "<b>Client Contact Required:</b> "
                    f"{'Yes' if escalation.requires_contact else 'No'}"
                ),
                body_style,
            )
        )
        for reason in escalation.reasons:
            story.append(
                Paragraph(
                    f"- {reason}",
                    body_style,
                )
            )
        if comparison.has_previous_scan:
            previous_display = (
                "Not Assessed"
                if comparison.previous_score is None
                else f"{comparison.previous_score} / 100"
            )
            change_display = (
                "Not Available"
                if comparison.score_change is None
                else (
                    f"+{comparison.score_change}"
                    if comparison.score_change > 0
                    else str(comparison.score_change)
                )
            )
            comparison_data = [
                [
                    "Monitoring Measure",
                    "Result",
                ],
                [
                    "Previous Commercial Score",
                    previous_display,
                ],
                [
                    "Current Commercial Score",
                    current_score_display,
                ],
                [
                    "Score Change",
                    change_display,
                ],
            ]
            comparison_table = Table(
                comparison_data,
                colWidths=[
                    115 * mm,
                    40 * mm,
                ],
            )
            comparison_table.setStyle(
                TableStyle(
                    [
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "ALIGN",
                            (1, 0),
                            (1, -1),
                            "RIGHT",
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "LINEBELOW",
                            (0, 0),
                            (-1, 0),
                            0.75,
                            colors.grey,
                        ),
                        (
                            "LINEBELOW",
                            (0, 1),
                            (-1, -2),
                            0.25,
                            colors.lightgrey,
                        ),
                    ]
                )
            )
            story.append(
                Spacer(
                    1,
                    3 * mm,
                )
            )
            story.append(
                comparison_table
            )
        story.append(
            Paragraph(
                "New Issues",
                heading_style,
            )
        )
        if comparison.new_issues:
            for issue in comparison.new_issues:
                story.append(
                    Paragraph(
                        f"- {issue}",
                        body_style,
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No new monitored issues were identified.",
                    body_style,
                )
            )
        story.append(
            Paragraph(
                "Resolved Issues",
                heading_style,
            )
        )
        if comparison.resolved_issues:
            for issue in comparison.resolved_issues:
                story.append(
                    Paragraph(
                        f"- {issue}",
                        body_style,
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No previously monitored issues were resolved.",
                    body_style,
                )
            )
        story.append(
            Paragraph(
                "Recommended Next Step",
                heading_style,
            )
        )
        if comparison.current_score is None:
            recommendation = (
                "Repeat the monitoring scan when the website "
                "can be fully assessed."
            )
        elif comparison.new_issues:
            recommendation = (
                "Review the new monitored issues above and "
                "prioritise any changes that may affect the "
                "guest journey or direct booking experience."
            )
        else:
            recommendation = (
                "Continue scheduled website monitoring and "
                "review any material changes identified in "
                "future assessments."
            )
        story.append(
            Paragraph(
                recommendation,
                body_style,
            )
        )
        document.build(
            story,
            onFirstPage=self._draw_footer,
            onLaterPages=self._draw_footer,
        )
        return str(output)