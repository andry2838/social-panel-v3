import os
from datetime import datetime
from fpdf import FPDF

class PremiumPDFReport(FPDF):
    def __init__(self, agency_name="BoostPanel Agency"):
        super().__init__()
        self.agency_name = agency_name
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Logo placeholder or Agency Name
        self.set_font('Arial', 'B', 20)
        self.set_text_color(139, 92, 246) # Primary Purple
        self.cell(0, 15, self.agency_name, 0, 1, 'L')
        
        # Line break and separator
        self.set_draw_color(236, 72, 153) # Secondary Pink
        self.set_line_width(1)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Rapport généré le {datetime.now().strftime("%d/%m/%Y")} par {self.agency_name}', 0, 0, 'C')

def generate_campaign_report(campaign_name: str, stats: dict, agency_name: str = "BoostPanel Agency") -> str:
    """
    Génère un rapport PDF Marque Blanche pour une campagne donnée.
    Retourne le chemin absolu du fichier PDF généré.
    """
    pdf = PremiumPDFReport(agency_name)
    pdf.add_page()
    
    # Titre du rapport
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(30, 41, 59) # Slate 800
    pdf.cell(0, 20, "RAPPORT DE PERFORMANCE", 0, 1, 'C')
    
    pdf.set_font('Arial', 'I', 14)
    pdf.set_text_color(100, 116, 139) # Slate 500
    pdf.cell(0, 10, f"Campagne : {campaign_name}", 0, 1, 'C')
    pdf.ln(10)
    
    # Section Résumé
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "1. Résumé des Actions Automatisées", 0, 1, 'L')
    pdf.ln(5)
    
    # Métriques (Tableau basique)
    pdf.set_font('Arial', '', 12)
    pdf.set_fill_color(248, 250, 252) # Slate 50
    
    metrics = [
        ("Nouveaux Abonnés Estimés", f"+{stats.get('new_followers', 0)}"),
        ("Stories Visionnées (Mass Look)", f"{stats.get('stories_viewed', 0)}"),
        ("Interactions Sondages & Sliders", f"{stats.get('polls_voted', 0)}"),
        ("Commentaires IA Générés", f"{stats.get('ai_comments', 0)}"),
        ("Likes Multi-Niveaux", f"{stats.get('comment_likes', 0)}")
    ]
    
    for label, value in metrics:
        pdf.cell(120, 10, label, 1, 0, 'L', fill=True)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(139, 92, 246)
        pdf.cell(70, 10, str(value), 1, 1, 'R', fill=True)
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(15, 23, 42)
        
    pdf.ln(15)
    
    # Section Source Tracking
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "2. Analyse des Sources (Source Tracking)", 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, "Ce module identifie précisément quels comptes concurrents ont généré le meilleur taux de conversion durant cette campagne.")
    pdf.ln(5)
    
    sources = stats.get('top_sources', [])
    if not sources:
        pdf.cell(0, 10, "Aucune donnée de source disponible pour le moment.", 0, 1, 'L')
    else:
        for idx, source in enumerate(sources, 1):
            pdf.cell(0, 8, f"{idx}. @{source['username']} - {source['conversions']} conversions", 0, 1, 'L')
            
    pdf.ln(20)
    
    # Conclusion
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(236, 72, 153) # Pink
    pdf.cell(0, 10, "Objectifs de croissance atteints. Protection algorithmique activée.", 0, 1, 'C')
    
    # Sauvegarde
    output_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"Report_{campaign_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath
