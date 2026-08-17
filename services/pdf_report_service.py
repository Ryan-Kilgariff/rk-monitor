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
                "Area",
                "Score",
            ],
            [
                "Technical Health",
                f"{result.score.technical_health} / 100",
            ],
            [
                "Booking Journey",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else f"{result.score.booking_journey} / 100"
                ),
            ],
            [
                "Mobile Experience",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else f"{result.score.mobile_experience} / 100"
                ),
            ],
            [
                "Room Presentation",
                (
                    f"{result.score.room_presentation} / 100"
                    if result.site_quality.has_rooms
                    else "Not Assessed"
                ),
            ],
            [
                "Guest Information",
                (
                    f"{result.score.guest_information} / 100"
                    if result.site_quality.has_guest_information
                    else "Not Assessed"
                ),
            ],
            [
                "Analytics",
                (
                    "Not Assessed"
                    if scan_incomplete
                    else f"{result.score.analytics} / 100"
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
        story.append(
            PageBreak()
        )
        story.append(
            Paragraph(
                "Verified Findings",
                heading_style,
            )
        )
        if not client_issues:
            story.append(
                Paragraph(
                    (
                        "No verified priority issues "
                        "were identified."
                    ),
                    body_style,
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