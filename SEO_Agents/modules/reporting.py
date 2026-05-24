"""
Professional PDF Report Generator for SEO Automation
Creates beautiful, comprehensive PDF reports with charts and styling
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import pandas as pd
import json

class SEOPDFReport:
    """Professional PDF Report Generator"""
    
    def __init__(self, output_filename="seo_master_report.pdf"):
        self.filename = output_filename
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.width, self.height = A4
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#3949ab'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#212121'),
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Highlight box
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#1b5e20'),
            backColor=colors.HexColor('#e8f5e9'),
            borderPadding=10,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))

        # Table text
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['BodyText'],
            fontSize=8,
            textColor=colors.HexColor('#212121'),
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=10
        ))
    
    def add_cover_page(self, site_url="", date_range=""):
        """Add professional cover page"""
        
        # Title
        title = Paragraph(
            "SEO MASTER AUTOMATION<br/>COMPREHENSIVE REPORT",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Website info
        if site_url:
            site_info = Paragraph(
                f"<b>Website:</b> {site_url}",
                self.styles['CustomHeading']
            )
            self.story.append(site_info)
            self.story.append(Spacer(1, 0.2*inch))
        
        # Date
        report_date = Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['CustomBody']
        )
        self.story.append(report_date)
        self.story.append(Spacer(1, 0.2*inch))
        
        if date_range:
            period = Paragraph(
                f"<b>Analysis Period:</b> {date_range}",
                self.styles['CustomBody']
            )
            self.story.append(period)
        
        self.story.append(Spacer(1, 1*inch))
        
        # Summary box
        summary_text = """
        <b>This report contains:</b><br/>
        ✓ Complete keyword research with AI clustering<br/>
        ✓ AI-generated content briefs and strategy<br/>
        ✓ Technical SEO audit results<br/>
        ✓ Backlink strategy and recommendations<br/>
        ✓ Performance analytics and insights<br/>
        ✓ Actionable next steps
        """
        summary = Paragraph(summary_text, self.styles['HighlightBox'])
        self.story.append(summary)
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, summary_data):
        """Add executive summary section"""
        
        # Section title
        title = Paragraph("EXECUTIVE SUMMARY", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Create summary table
        data = [
            [Paragraph('Metric', self.styles['CustomSubHeading']), Paragraph('Value', self.styles['CustomSubHeading'])],
            [Paragraph('Total Keywords Discovered', self.styles['TableText']), Paragraph(str(summary_data.get('total_keywords', 0)), self.styles['TableText'])],
            [Paragraph('Average Ranking Position', self.styles['TableText']), Paragraph(f"{summary_data.get('avg_position', 0):.2f}", self.styles['TableText'])],
            [Paragraph('Top Performing Keyword', self.styles['TableText']), Paragraph(summary_data.get('top_keyword', 'N/A'), self.styles['TableText'])],
            [Paragraph('Content Briefs Generated', self.styles['TableText']), Paragraph(str(summary_data.get('content_briefs', 0)), self.styles['TableText'])],
            [Paragraph('Technical Issues Found', self.styles['TableText']), Paragraph(str(summary_data.get('technical_issues', 0)), self.styles['TableText'])],
            [Paragraph('Backlink Opportunities', self.styles['TableText']), Paragraph(str(summary_data.get('backlink_opportunities', 0)), self.styles['TableText'])],
            [Paragraph('Total Organic Sessions', self.styles['TableText']), Paragraph(str(summary_data.get('total_sessions', 0)), self.styles['TableText'])]
        ]
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_keyword_research_section(self, keywords_df):
        """Add keyword research section"""
        
        # Section title
        title = Paragraph("KEYWORD RESEARCH ANALYSIS", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Overview
        overview = Paragraph(
            f"Discovered <b>{len(keywords_df)}</b> keywords with AI-powered semantic clustering. "
            f"Keywords are prioritized based on search volume, intent, and ranking position.",
            self.styles['CustomBody']
        )
        self.story.append(overview)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Top 20 keywords table
        subtitle = Paragraph("Top 20 Priority Keywords", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        top_keywords = keywords_df.nlargest(20, 'priority_score') if 'priority_score' in keywords_df.columns else keywords_df.head(20)
        
        table_data = [['Keyword', 'Intent', 'Position', 'Priority']]
        
        for _, row in top_keywords.iterrows():
            table_data.append([
                Paragraph(str(row.get('keyword', 'N/A')), self.styles['TableText']),
                Paragraph(str(row.get('intent', 'N/A')), self.styles['TableText']),
                Paragraph(f"{row.get('position', 0):.1f}", self.styles['TableText']),
                Paragraph(f"{row.get('priority_score', 0):.1f}", self.styles['TableText'])
            ])
        
        table = Table(table_data, colWidths=[3*inch, 1.2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Intent distribution
        if 'intent' in keywords_df.columns:
            intent_counts = keywords_df['intent'].value_counts()
            
            subtitle2 = Paragraph("Keyword Intent Distribution", self.styles['CustomSubHeading'])
            self.story.append(subtitle2)
            
            intent_data = [[
                Paragraph('Intent Type', self.styles['CustomSubHeading']),
                Paragraph('Count', self.styles['CustomSubHeading']),
                Paragraph('Percentage', self.styles['CustomSubHeading'])
            ]]
            for intent, count in intent_counts.items():
                percentage = (count / len(keywords_df)) * 100
                intent_data.append([
                    Paragraph(intent.title(), self.styles['TableText']),
                    Paragraph(str(count), self.styles['TableText']),
                    Paragraph(f"{percentage:.1f}%", self.styles['TableText'])
                ])
            
            intent_table = Table(intent_data, colWidths=[2.2*inch, 1*inch, 1*inch])
            intent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            
            self.story.append(intent_table)
        
        self.story.append(PageBreak())
    
    def add_content_briefs_section(self, briefs_data):
        """Add content briefs section"""
        
        title = Paragraph("CONTENT STRATEGY & BRIEFS", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        overview = Paragraph(
            f"Generated <b>{len(briefs_data)}</b> AI-powered SEO content briefs. "
            "Each brief includes keyword targeting, heading structure, and optimization guidelines.",
            self.styles['CustomBody']
        )
        self.story.append(overview)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Show top 5 briefs
        num_briefs = min(len(briefs_data), 5)
        for i, brief in enumerate(briefs_data[:5], 1):
            # Brief title
            brief_title = Paragraph(
                f"<b>Content Brief #{i}: {brief.get('primary_keyword', 'N/A')}</b>",
                self.styles['CustomSubHeading']
            )
            self.story.append(brief_title)
            
            # Brief details
            details = f"""<b>Content Type:</b> {brief.get('content_type', 'N/A')}<br/>
<b>Search Intent:</b> {brief.get('search_intent', 'N/A')}<br/>
<b>Target Word Count:</b> {brief.get('target_word_count', 0)} words<br/>
<b>Target URL:</b> {brief.get('target_url', 'N/A')}<br/>
<b>Meta Title:</b> {brief.get('meta_title', 'N/A')}<br/>
<b>Secondary Keywords:</b> {', '.join(brief.get('secondary_keywords', [])[:3])}"""
            
            details_para = Paragraph(details, self.styles['CustomBody'])
            self.story.append(details_para)
            
            # Add spacer only between briefs, not after the last one
            if i < num_briefs:
                self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(PageBreak())
    
    def add_technical_audit_section(self, audit_data):
        """Add technical SEO audit section"""
        
        title = Paragraph("TECHNICAL SEO AUDIT", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        checks = audit_data.get('checks', {})
        
        # Technical checks table
        check_data = [['Check', 'Status', 'Action Required']]
        
        checks_list = [
            ('HTTPS Enabled', checks.get('https', False), 'Enable HTTPS' if not checks.get('https') else 'None'),
            ('robots.txt Found', checks.get('robots_txt', False), 'Create robots.txt' if not checks.get('robots_txt') else 'None'),
            ('Sitemap.xml Found', checks.get('sitemap', False), 'Create sitemap' if not checks.get('sitemap') else 'None'),
            ('Mobile Friendly', checks.get('mobile_friendly', False), 'Add viewport meta tag' if not checks.get('mobile_friendly') else 'None'),
            ('Fast Loading', checks.get('page_speed', {}).get('fast', False), 'Optimize page speed' if not checks.get('page_speed', {}).get('fast') else 'None')
        ]
        
        for check_name, status, action in checks_list:
            status_text = '✓ Pass' if status else '✗ Fail'
            check_data.append([
                Paragraph(check_name, self.styles['TableText']),
                Paragraph(status_text, self.styles['TableText']),
                Paragraph(action, self.styles['TableText'])
            ])
        
        table = Table(check_data, colWidths=[2.5*inch, 1.2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Broken links
        broken_links = checks.get('broken_links', [])
        if broken_links:
            subtitle = Paragraph(f"Broken Links Found: {len(broken_links)}", self.styles['CustomSubHeading'])
            self.story.append(subtitle)
            
            for link in broken_links[:10]:
                link_para = Paragraph(f"• {link}", self.styles['CustomBody'])
                self.story.append(link_para)
        
        self.story.append(PageBreak())
    
    def add_backlink_strategy_section(self, strategy_data):
        """Add backlink strategy section"""
        
        title = Paragraph("BACKLINK ACQUISITION STRATEGY", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        # High priority pages
        high_priority = strategy_data.get('high_priority_pages', [])
        
        subtitle = Paragraph(f"High Priority Pages ({len(high_priority)} pages)", self.styles['CustomSubHeading'])
        self.story.append(subtitle)
        
        if high_priority:
            table_data = [['Keyword', 'Target URL', 'Backlinks Needed']]
            
            for page in high_priority[:10]:
                table_data.append([
                    Paragraph(str(page.get('keyword', 'N/A')), self.styles['TableText']),
                    Paragraph(str(page.get('target_url', 'N/A')), self.styles['TableText']),
                    Paragraph(str(page.get('required_backlinks', 0)), self.styles['TableText'])
                ])
            
            table = Table(table_data, colWidths=[2.5*inch, 2.8*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            
            self.story.append(table)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Anchor text distribution
        subtitle2 = Paragraph("Recommended Anchor Text Distribution", self.styles['CustomSubHeading'])
        self.story.append(subtitle2)
        
        anchor_data = [
        [Paragraph('Anchor Type', self.styles['CustomSubHeading']),
         Paragraph('Percentage', self.styles['CustomSubHeading']),
         Paragraph('Example', self.styles['CustomSubHeading'])],
        [Paragraph('Brand', self.styles['TableText']), Paragraph('40%', self.styles['TableText']), Paragraph('Decentrawood', self.styles['TableText'])],
        [Paragraph('Generic', self.styles['TableText']), Paragraph('30%', self.styles['TableText']), Paragraph('click here, learn more', self.styles['TableText'])],
        [Paragraph('Partial Match', self.styles['TableText']), Paragraph('20%', self.styles['TableText']), Paragraph('AI automation tools', self.styles['TableText'])],
        [Paragraph('Exact Match', self.styles['TableText']), Paragraph('10%', self.styles['TableText']), Paragraph('exact keyword', self.styles['TableText'])]
    ]
        
        anchor_table = Table(anchor_data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
        anchor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        
        self.story.append(anchor_table)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Free platforms
        subtitle3 = Paragraph("Free Backlink Platforms (20+ Opportunities)", self.styles['CustomSubHeading'])
        self.story.append(subtitle3)
        
        platforms_text = """
        <b>Content Publishing:</b> Medium, Dev.to, Hashnode, Hackernoon<br/>
        <b>Web3/Crypto:</b> Publish0x, Mirror.xyz, Hive.blog, Steemit<br/>
        <b>Q&A Platforms:</b> Quora, Reddit, StackOverflow<br/>
        <b>Directories:</b> Product Hunt, AlternativeTo, IndieHackers
        """
        
        platforms = Paragraph(platforms_text, self.styles['CustomBody'])
        self.story.append(platforms)
        
        self.story.append(PageBreak())

    def add_performance_section(self, traffic_df):
        """Add traffic performance section"""
        
        title = Paragraph("PERFORMANCE & TRAFFIC ANALYSIS", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        if traffic_df is not None and not traffic_df.empty:
            # Overview
            total_sessions = traffic_df['sessions'].sum()
            total_users = traffic_df['users'].sum()
            
            overview = Paragraph(
                f"Website received <b>{total_sessions}</b> sessions from <b>{total_users}</b> unique users in the last 30 days.",
                self.styles['CustomBody']
            )
            self.story.append(overview)
            self.story.append(Spacer(1, 0.3*inch))
            
            # Top Pages Table
            subtitle = Paragraph("Top Performing Landing Pages", self.styles['CustomSubHeading'])
            self.story.append(subtitle)
            
            # Group and clean names
            traffic_clean = traffic_df[traffic_df['page'] != '(not set)'].copy()
            traffic_clean['page'] = traffic_clean['page'].apply(
                lambda x: x.strip('/').replace('/', ' > ').title() if x != '/' else 'Homepage'
            )
            top_pages = traffic_clean.groupby("page")["sessions"].sum().nlargest(10).reset_index()
            
            table_data = [['Landing Page', 'Sessions']]
            for _, row in top_pages.iterrows():
                table_data.append([
                    Paragraph(str(row['page']), self.styles['TableText']),
                    Paragraph(str(row['sessions']), self.styles['TableText'])
                ])
            
            table = Table(table_data, colWidths=[5*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            
            self.story.append(table)
        else:
            self.story.append(Paragraph("No traffic data available for the analysis period.", self.styles['CustomBody']))
            
        self.story.append(PageBreak())
    
    def add_recommendations_section(self):
        """Add actionable recommendations"""
        
        title = Paragraph("ACTIONABLE RECOMMENDATIONS", self.styles['CustomHeading'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
        
        recommendations = [
            ("Immediate Actions (This Week)", [
                "Fix critical technical issues identified in the audit",
                "Create content for top 5 priority keywords",
                "Set up daily monitoring automation",
                "Claim and optimize free directory listings"
            ]),
            ("Short-term Goals (This Month)", [
                "Publish 5-10 content pieces from generated briefs",
                "Build 10-20 backlinks on free platforms",
                "Optimize existing pages for top keywords",
                "Monitor and respond to ranking changes"
            ]),
            ("Long-term Strategy (3-6 Months)", [
                "Scale content production to 20+ pieces",
                "Build 50+ quality backlinks",
                "Achieve top 10 rankings for 50+ keywords",
                "Establish automated SEO workflow"
            ])
        ]
        
        for section_title, items in recommendations:
            subtitle = Paragraph(section_title, self.styles['CustomSubHeading'])
            self.story.append(subtitle)
            
            for item in items:
                item_para = Paragraph(f"• {item}", self.styles['CustomBody'])
                self.story.append(item_para)
            
            self.story.append(Spacer(1, 0.2*inch))
    
    def add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        
        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(A4[0] - 50, 30, text)
        
        # Report info
        canvas.drawString(50, 30, "SEO Master Automation Report")
        
        canvas.restoreState()
    
    def generate(self, keywords_df=None, briefs_data=None, audit_data=None, 
                 strategy_data=None, summary_data=None, traffic_df=None, site_url=""):
        """Generate complete PDF report"""
        
        # Cover page
        self.add_cover_page(site_url=site_url, date_range="Last 30 Days")
        
        # Executive summary
        if summary_data:
            self.add_executive_summary(summary_data)
            self.story.append(PageBreak())
        
        # Keyword research
        if keywords_df is not None and not keywords_df.empty:
            self.add_keyword_research_section(keywords_df)
        
        # Content briefs
        if briefs_data:
            self.add_content_briefs_section(briefs_data)
        
        # Technical audit
        if audit_data:
            self.add_technical_audit_section(audit_data)
        
        # Backlink strategy
        if strategy_data:
            self.add_backlink_strategy_section(strategy_data)
        
        # Performance analysis (NEW)
        if traffic_df is not None:
            self.add_performance_section(traffic_df)
        
        # Recommendations
        self.add_recommendations_section()
        
        # Build PDF
        self.doc.build(self.story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
        
        return self.filename


def generate_complete_report(output_filename="seo_master_report.pdf"):
    """Generate complete SEO report from available data files"""
    
    # Use absolute import from the package
    try:
        from modules.seo_engine import SEOConfig
    except ImportError:
        # Resolve the package path dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir) # Should be SEO_Agents dir
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        try:
            from modules.seo_engine import SEOConfig
        except ImportError:
            # Last resort: try direct import if in the same folder
            if current_dir not in sys.path:
                sys.path.append(current_dir)
            from seo_engine import SEOConfig
    
    # Ensure PDF is saved in reports/pdf directory
    os.makedirs(SEOConfig.PDF_DIR, exist_ok=True)
    if not output_filename.startswith(SEOConfig.PDF_DIR):
        output_filename = os.path.join(SEOConfig.PDF_DIR, output_filename)
        
    report = SEOPDFReport(output_filename)
    
    # Load data from reports directory
    keywords_df = None
    briefs_data = None
    audit_data = None
    strategy_data = None
    traffic_df = None
    summary_data = {}
    
    # Load keywords with error handling
    if os.path.exists(SEOConfig.KEYWORDS_FILE):
        try:
            keywords_df = pd.read_csv(SEOConfig.KEYWORDS_FILE)
            if not keywords_df.empty:
                summary_data['total_keywords'] = len(keywords_df)
                summary_data['avg_position'] = keywords_df['position'].mean() if 'position' in keywords_df.columns else 0
                if 'keyword' in keywords_df.columns:
                    summary_data['top_keyword'] = keywords_df.iloc[0]['keyword']
            else:
                keywords_df = None
        except Exception as e:
            print(f"⚠️ Could not load keywords: {e}")
            keywords_df = None
    
    # Load content briefs with error handling
    if os.path.exists(SEOConfig.CONTENT_BRIEF_FILE):
        try:
            with open(SEOConfig.CONTENT_BRIEF_FILE, 'r') as f:
                briefs_data = json.load(f)
                if briefs_data:
                    summary_data['content_briefs'] = len(briefs_data)
                else:
                    briefs_data = None
        except Exception as e:
            print(f"⚠️ Could not load content briefs: {e}")
            briefs_data = None
    
    # Load technical audit with error handling
    if os.path.exists(SEOConfig.TECHNICAL_AUDIT_FILE):
        try:
            with open(SEOConfig.TECHNICAL_AUDIT_FILE, 'r') as f:
                audit_data = json.load(f)
                if audit_data:
                    checks = audit_data.get('checks', {})
                    summary_data['technical_issues'] = sum(1 for v in checks.values() if not v)
                else:
                    audit_data = None
        except Exception as e:
            print(f"⚠️ Could not load technical audit: {e}")
            audit_data = None
    
    # Load backlink strategy with error handling
    backlink_json = os.path.join(SEOConfig.JSON_DIR, "backlink_strategy.json")
    if os.path.exists(backlink_json):
        try:
            with open(backlink_json, 'r') as f:
                strategy_data = json.load(f)
                if strategy_data:
                    summary_data['backlink_opportunities'] = len(strategy_data.get('high_priority_pages', []))
                else:
                    strategy_data = None
        except Exception as e:
            print(f"⚠️ Could not load backlink strategy: {e}")
            strategy_data = None
    
    # Load traffic data with error handling
    try:
        if os.path.exists(SEOConfig.TRAFFIC_FILE):
            traffic_df = pd.read_csv(SEOConfig.TRAFFIC_FILE)
            if not traffic_df.empty and 'sessions' in traffic_df.columns:
                summary_data['total_sessions'] = traffic_df['sessions'].sum()
    except Exception as e:
        pass
    
    # Check if we have any data to generate report
    has_data = any([
        keywords_df is not None and not keywords_df.empty,
        briefs_data is not None and len(briefs_data) > 0,
        audit_data is not None,
        strategy_data is not None
    ])
    
    if not has_data:
        raise ValueError(
            "No data available to generate PDF report. "
            "Please run the SEO automation first."
        )
    
    # Get site URL from config
    try:
        from dotenv import load_dotenv
        load_dotenv()
        site_url = os.getenv("GSC_SITE_URL", "").replace("sc-domain:", "")
    except Exception as e:
        site_url = "Website"
    
    # Generate report
    try:
        filename = report.generate(
            keywords_df=keywords_df,
            briefs_data=briefs_data,
            audit_data=audit_data,
            strategy_data=strategy_data,
            summary_data=summary_data,
            traffic_df=traffic_df,
            site_url=site_url
        )
        return filename
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


if __name__ == "__main__":
    generate_complete_report()
