# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import logging
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
_logger = logging.getLogger(__name__)


class AgenceController(http.Controller):

    # Route to the success page after final submission
    @http.route('/reclamation/success', auth='public', website=True)
    def reclamation_success(self, **kwargs):
        return request.render('agence.reclamation_succes_template')

    @http.route('/reclamation', auth='public', website=True)
    def reclamation_form(self, **kwargs):
        current_section = kwargs.get('current_section', '1')
        return request.render('agence.reclamation_form_template', {
            'current_section': current_section,
            'form_data': kwargs  # Pass all the details as form_data
        })

    # Handle form submission (next, previous, or final submit)
    @http.route('/reclamation/next', auth='public', website=True, type='http', methods=['GET'])
    def next_section(self, **kwargs):
        nom_reclament = kwargs.get('nom_reclament', '')
        prenom_reclament = kwargs.get('prenom_reclament', '')
        numero_tel = kwargs.get('numero_tel', '')
        source = kwargs.get('source', '')
        adresse_mail = kwargs.get('adresse_mail', '')
        reclamation_id = kwargs.get('reclamation_id', '')  # Ensure reclamation_id is passed

        # Pass the form data to the template for Section 2
        return request.render('agence.reclamation_form_template', {
            'current_section': '2',
            'form_data': {
                'nom_reclament': nom_reclament,
                'prenom_reclament': prenom_reclament,
                'numero_tel': numero_tel,
                'source': source,
                'adresse_mail': adresse_mail,
                'reclamation_id': reclamation_id  # Include reclamation_id
            }
        })

    @http.route('/reclamation/previous', auth='public', website=True, type='http', methods=['GET'])
    def previous_section(self, **kwargs):
        # Retrieve the form data passed from Section 1
        nom_reclament = kwargs.get('nom_reclament', '')
        prenom_reclament = kwargs.get('prenom_reclament', '')
        numero_tel = kwargs.get('numero_tel', '')
        source = kwargs.get('source', '')
        adresse_mail = kwargs.get('adresse_mail', '')
        reclamation_id = kwargs.get('reclamation_id', '')  # Ensure reclamation_id is passed

        # Pass the form data to the template for Section 1
        return request.render('agence.reclamation_form_template', {
            'current_section': '1',
            'form_data': {
                'nom_reclament': nom_reclament,
                'prenom_reclament': prenom_reclament,
                'numero_tel': numero_tel,
                'source': source,
                'adresse_mail': adresse_mail,
                'reclamation_id': reclamation_id  # Include reclamation_id
            }
        })

    @http.route('/reclamation/route', auth='public', website=True, type='http', methods=['POST'], csrf=True)
    def test_reclamation(self, **kwargs):
        # Retrieve form data from section 1
        nom_reclament = kwargs.get('nom_reclament', '')
        prenom_reclament = kwargs.get('prenom_reclament', '')
        numero_tel = kwargs.get('numero_tel', '')
        source = kwargs.get('source', '')
        adresse_mail = kwargs.get('email', '')
        objet = kwargs.get('objet', 'objet')
        reclamation_id = kwargs.get('reclamation_id', '')  # Ensure reclamation_id is passed

        # Check which section we are in and navigate accordingly
        if kwargs.get('current_section') == '1':
            # Navigate to the next section (Section 2)
            return request.redirect('/reclamation/next?nom_reclament=%s&prenom_reclament=%s&numero_tel=%s&source=%s&adresse_mail=%s&reclamation_id=%s' % (
                nom_reclament, prenom_reclament, numero_tel, source, adresse_mail, reclamation_id
            ))
        if kwargs.get('current_section') == '2':
            # Go to final submission or processing
            return self.submit_reclamation(**kwargs)
        elif kwargs.get('current_section') == '3':
            # Go to page B (final submission or processing)
            return request.redirect('/reclamation/download_report?nom_reclament=%s&prenom_reclament=%s&numero_tel=%s&source=%s&adresse_mail=%s&objet=%s&reclamation_id=%s' % (
                nom_reclament, prenom_reclament, numero_tel, source, adresse_mail, objet, reclamation_id
            ))
    @http.route('/reclamation/satisfaction', auth='public', website=True, type='http', methods=['GET'], csrf=True)
    def satisfaction_reclamation(self, **kwargs):
    # Return the rendered template with the reclamation data
     return request.render('agence.reclamation_satisfaction_template', {
     })
    @http.route('/satisfaction/submit', auth='public', website=True, type='http', methods=['POST'], csrf=False)
    def satisfaction_sbmit_reclamation(self, **kwargs):
    # Return the rendered template with the reclamation data
     request.env['satisfaction.survey'].create({
            'ref': kwargs.get('reference_reclamation'),
            'prenom_reclament': kwargs.get('prenom_reclament'),
            'nom_reclament': kwargs.get('nom_reclament'),
            'satisfaction_rating': kwargs.get('clarity'),
            'solution_quality': kwargs.get('solution_quality'),
            'professionalism': kwargs.get('professionalism'),
            'recommend': kwargs.get('recommend'),
            'treatment_time': kwargs.get('treatment_time'),
            'clarity': kwargs.get('clarity'),
            'comments': kwargs.get('comments'),
            'consent': kwargs.get('consent') == 'on',  # Checkbox
        })
     return request.render('agence.satisfaction_succes_template')
    @http.route('/reclamation/submit', auth='public', website=True, type='http', methods=['POST'], csrf=True)
    def submit_reclamation(self, **kwargs):
    # Create the reclamation record
     reclamation = request.env['reclamation'].create({
        'objet': kwargs.get('objet'),
        'prenom_reclament': kwargs.get('prenom_reclament'),
        'nom_reclament': kwargs.get('nom_reclament'),
        'numero_tel': kwargs.get('numero_tel'),
        'description': kwargs.get('description'),
        'source': kwargs.get('source'),
        'adresse_mail': kwargs.get('email'),
        'origin': 'site',
     })

    # Get the uploaded file from the form
     uploaded_file = kwargs.get('file')

    # If a file was uploaded, save it in the reclamation record
     if uploaded_file:
        # Save the file data in the 'file' field and the file name in 'file_name'
        reclamation.write({
            'file': uploaded_file.read(),
        })

    # Return the rendered template with the reclamation data
     return request.render('agence.reclamation_form_template', {
        'current_section': '3',
        'form_data': {
            'nom_reclament': kwargs.get('nom_reclament'),
            'prenom_reclament': kwargs.get('prenom_reclament'),
            'numero_tel': kwargs.get('numero_tel'),
            'source': kwargs.get('source'),
            'adresse_mail': kwargs.get('email'),
            'reclamation_id': reclamation.id, 
        }
     })


    @http.route('/reclamation/download_report', auth='public', type='http', website=True)
    def download_reclamation_report(self, **kwargs):
        # Create PDF buffer
        pdf_buffer = io.BytesIO()

        # Define styles and positions
        inch = 72  # 1 inch = 72 points
        line_height = 14
        margin = 1 * inch
        page_width = 6 * inch  # Fixed width
        total_lines = 8  # Estimate total lines for content
        required_height = (total_lines * line_height) + (3 * line_height) + (2 * margin)
        page_height = max(required_height, 4 * inch)  # Ensure minimum height
        y_position = page_height - margin  # Start at the top minus margin
        x_position = margin  # Align everything to the left margin

        # Create canvas with dynamic height
        p = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))

        # Fetch data from kwargs
        nom_reclament = kwargs.get('nom_reclament', 'Non spécifié')
        prenom_reclament = kwargs.get('prenom_reclament', 'Non spécifié')
        reclamation_id = kwargs.get('reclamation_id', 'Non spécifié')
        objet = kwargs.get('objet', 'Non spécifié')

        # Add title
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.darkblue)
        p.drawString(x_position, y_position, "Accusé de la Réclamation")
        y_position -= 1.5 * line_height

        # Add agency information
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.black)
        p.drawString(x_position, y_position, "Agence : Alger Centre")
        y_position -= line_height
        p.drawString(x_position, y_position, "Agent de clientèle : FADEL NESRINE")
        y_position -= line_height
        p.drawString(x_position, y_position, "Numéro de l'agent : 0770453221")
        y_position -= 1.5 * line_height 

        # Add a line separator
        p.setStrokeColor(colors.black)
        p.setLineWidth(1)
        p.line(x_position, y_position, page_width - margin, y_position)
        y_position -= line_height

        # Add reclamation details
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_position, y_position, f"Identifiant de Réclamation: {reclamation_id}")
        y_position -= 1.5 * line_height


        # Add another separator
        p.setStrokeColor(colors.grey)
        p.line(x_position, y_position, page_width - margin, y_position)
        y_position -= line_height

        # Add detailed information
        p.setFont("Helvetica", 10)
        for label, value in [
            ("Prénom du réclament", prenom_reclament),
            ("Nom du réclament", nom_reclament),
        ]:
            p.drawString(x_position, y_position, f"{label}: {value}")
            y_position -= line_height

        # Add footer with date
        p.setFont("Helvetica", 8)
        p.setFillColor(colors.grey)
        footer_text = f"Accusé généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
        p.drawString(x_position, margin / 2, footer_text)

        # Save and return the PDF
        p.save()
        pdf_data = pdf_buffer.getvalue()
        pdf_buffer.close()

        return request.make_response(
            pdf_data,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="reclamation_report.pdf"'),
                ('Content-Length', len(pdf_data))
            ]
        )