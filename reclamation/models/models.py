# -*- coding: utf-8 -*- 

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from datetime import date, timedelta
from odoo import _
import logging

# Create a logger
_logger = logging.getLogger(__name__)

class Reclamation(models.Model):
    _name = 'reclamation'
    _description = 'Réclamation'
    objet = fields.Char(string="Objet de la réclamation", required=True) 
    nom_reclament = fields.Char(string="Nom du reclament", required=True)
    prenom_reclament = fields.Char(string="Prenom du reclament", required=True)
    adresse_mail = fields.Char(string="Adresse E-mail", required=False)
    nom_entreprise = fields.Char(string="Nom de l'entreprise", required=False)
    numero_tel = fields.Char(string="Numero de telephone du reclament", required=True)
    contact_id = fields.Many2one('contact', string='Contact')
    description = fields.Text(string="Description de la réclamation", required=True) 
    date = fields.Datetime(string="Date de la réclamation", default=fields.Datetime.now)
    file = fields.Binary(string="Fichiers justificatifs", required=False)
    treated = fields.Boolean(string="Traitée?", required=True, default=False)
    archived = fields.Boolean(string="Archivée?", required=True, default=False)
    active = fields.Boolean(required=False, default=True)
    
    
     
 
    priority = fields.Selection(
    [
     ('Urgente', 'Une réclamation urgente'),
     ('Non urgente', 'Une réclamation non urgente')],
    string="Priorité de la réclamation",
    required=False,
    default=''  
    )
    type2 = fields.Selection(
    [  
     ('technical', 'Une réclamation technique'),
     ('commercial', 'Une réclamation commerciale'),
     ('Other', 'Une réclamationnon non typé')],
    string="Type de la réclamation",
    required=False,
    default=''  
    )

    origin = fields.Selection(
        [('Cellule', 'Cellule de veille'),
         ('Présence', 'Présentielle'),
         ('tel', 'Appel téléphonique'),
         ('site', 'SiteWeb')],
        string="Origine de la réclamation",
        required=True,
        default=''  
    )
   
    source = fields.Selection(
        [('Citoyen', 'Un/Une Citoyen(ne)'),
         ('Entreprise', 'Une entreprise')],
        string="Source de la réclamation",
        required=True,
        default=''  
    )
    def action_archive(self):
        # Mettre à jour le champ `active` à False pour archiver l'enregistrement
        self.write({'archived': True})


    
    @api.onchange('type2')
    def _onchange_type2(self):
       
        if self.type2 == 'technical':
           
            self.env['project.project'].create({
              'reclamation_id': self.id,
              'name': self.objet,  # Le nom du projet sera celui de la réclamation
              'description': self.description,  # La description du projet sera celle de la réclamation
              'date_start': date.today(),
              'numero_tel': self.numero_tel, #a checker men 3nd chaima
              'type2': 'technical',
              'priority': self.priority,
              'objet': self.objet,
              'nom_reclament': self.nom_reclament,
              'prenom_reclament': self.prenom_reclament,
            })
              #reclamation_id = fields.Many2one('reclamation', string="Réclamation", required=True)

        if self.type2 == 'commercial':
           
            self.env['project.project'].create({
              'reclamation_id': self.id,
              'name': self.objet,  # Le nom du projet sera celui de la réclamation
              'description': self.description,  # La description du projet sera celle de la réclamation
              'date_start': date.today(),
              'numero_tel': self.numero_tel, #a checker men 3nd chaima
              'type2': 'commercial',
              'priority': self.priority,
              'objet': self.objet,
              'nom_reclament': self.nom_reclament,
              'prenom_reclament': self.prenom_reclament,
            })
  

   
        
    



    #Traitement de la réclamation 
class ReclamationProject(models.Model):
    _inherit = 'project.project'

    # Champs ajoutés pour les réclamations
    reclamation_id = fields.Many2one('reclamation', string="Réclamation", required=False)
    objet = fields.Char(string="Objet de la réclamation", required=True)
    nom_reclament = fields.Char(string="Nom du réclamant", required=False)
    prenom_reclament = fields.Char(string="Prénom du réclamant", required=False)
    adresse_mail = fields.Char(string="Adresse E-mail")
    nom_entreprise = fields.Char(string="Nom de l'entreprise")
    numero_tel = fields.Char(string="Numéro de téléphone du réclamant", required=True)
    date_reclamation = fields.Datetime(string="Date de la réclamation", default=fields.Datetime.now)
    file = fields.Binary(string="Fichiers justificatifs")
    treated = fields.Boolean(string="Traitée ?", default=False)
    users_id = fields.Many2one(
        'res.users', 
        string='Membres de l équipe',
    )
    cheffe = fields.Many2one('res.users', string='Project Manager', default=False) #pas d'heritage car par defaut doit etre a faux
  

    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved')
    ], string="Status", default='in_progress')

    # Champs supplémentaires
    priority = fields.Selection(
        [
            ('Urgente', 'Une réclamation urgente'),
            ('Non urgente', 'Une réclamation non urgente')
        ],
        string="Priorité de la réclamation",
        default=''
    )
    type2 = fields.Selection(
        [
            ('technical', 'Une réclamation technique'),
            ('commercial', 'Une réclamation commerciale'),
            ('Other', 'Une réclamation non typée')
        ],
        string="Type de la réclamation",
        default=''
    )
    origin = fields.Selection(
        [
            ('Cellule', 'Cellule de veille'),
            ('Présence', 'Présentielle'),
            ('tel', 'Appel téléphonique'),
            ('site', 'Site Web')
        ],
        string="Origine de la réclamation",
        required=False,
        default=''
    )
    source = fields.Selection(
        [
            ('Citoyen', 'Un/Une Citoyen(ne)'),
            ('Entreprise', 'Une entreprise')
        ],
        string="Source de la réclamation",
        required=False,
        default=''
    )
    resolved_count = fields.Integer(string="Count", compute="_compute_resolved_count", store=False)

    @api.model
    def _compute_resolved_count(self):
        # Compter les enregistrements de chaque type
        total_reclamations = self.search_count()  
        resolved_reclamations = self.search_count([('treated', '=', True)]) 
        # Calcul des pourcentages
        if total_reclamations > 0:
            resolved_percentage = (resolved_reclamations / total_reclamations) * 100
            not_resoleved_percentage = ((total_reclamations-resolved_reclamations) / total_reclamations) * 100

        else:
            resolved_percentage = not_resoleved_percentage = 0

        return {
            'type_1': resolved_percentage,
            'not_resoleved_percentage': not_resoleved_percentage,

        }
    pv = fields.Text(string="Pv de commission", default='')
    @api.onchange('treated')
    def _onchange_treated(self):
       
        if self.treated:
            template = self.env.ref('agence.email_template_satisfaction_reclamation', raise_if_not_found=False)
            if template and self.adresse_mail:
                template.write({
                    'email_to': self.adresse_mail,  #
                })
                template.send_mail(self.id, force_send=True)
    
   

#Interventions d'un projet


class Intervention(models.Model):
    _inherit = 'project.task'
    reclamant_name = fields.Char(string="Reclamant Name")
    #Chef/fe de l'equipe de l'intervention 
    cheffe = fields.Many2one('res.users', string='Project Manager', default=False) #pas d'heritage car par defaut doit etre a faux


    planned_date = fields.Datetime(string="Date de l'Intervention")
    
    # Statut de l'Intervention
    status = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En Cours'),
        ('completed', 'Terminée')
    ], string="Statut de l'Intervention", default='planned')


    
    # Description de l'Intervention
    description = fields.Text(string="Description de l'Intervention")


    # Documents justificatifs
    attachment_ids = fields.Many2many('ir.attachment', string="Documents Justificatifs")

    # Compte-rendu de l'Intervention
    report = fields.Text(string="Compte-rendu de l'Intervention")

    # Commentaires supplémentaires
    additional_comments = fields.Text(string="Commentaires Supplémentaires")
    @api.model
    def _update_task_status(self):
        """Cron method to update task status based on planned date."""
        # Get the current datetime
        now = fields.Datetime.now()
        # Define a tolerance window (e.g., ±1 minute)
        window_start = now - timedelta(minutes=1)
        window_end = now + timedelta(minutes=1)

        # Search for tasks within the tolerance window
        tasks = self.search([
            ('planned_date', '>=', window_start), #pour une meilleure comparaison
            ('planned_date', '<=', window_end),
            ('status', '=', 'planned')
        ])

        for task in tasks:
            task.status = 'in_progress'
            
            # Notifier l'équipe de l'intervention
            partner_ids = task.user_ids.mapped('partner_id').ids
    
            # Ajouter le chef d'intervention à la liste des notifications
            if task.cheffe:
                partner_ids.append(task.cheffe.partner_id.id)
    
            # Construire le message
            message = _(
                "Ceci est un rappel pour '%s'. commencer lintervention."
            ) % task.name
    
            # Envoyer la notification
            task.message_post(
                body=message,
                partner_ids=list(set(partner_ids))  # Éliminer les doublons
            )
from odoo import models, fields

class SatisfactionSurvey(models.Model):
    _name = 'satisfaction.survey'
    _description = 'Survey for Customer Satisfaction on Reclamation Resolution'
    
    ref = fields.Char(string='Référence de la réclamation')
    prenom_reclament = fields.Char(string = 'Prenom du réclament')
    nom_reclament = fields.Char(string = 'Nom du réclament')
    satisfaction_rating = fields.Selection([
        ('5', '⭐⭐⭐⭐⭐ - Très satisfait'),
        ('4', '⭐⭐⭐⭐ - Satisfait'),
        ('3', '⭐⭐⭐ - Neutre'),
        ('2', '⭐⭐ - Insatisfait'),
        ('1', '⭐ - Très insatisfait'),
    ], string="Satisfaction Globale", required=True)
    
    treatment_time = fields.Selection([
        ('very_fast', 'Très rapide (moins de 24h)'),
        ('fast', 'Rapide (1-3 jours)'),
        ('acceptable', 'Acceptable (3-7 jours)'),
        ('slow', 'Long (plus d\'une semaine)'),
        ('very_slow', 'Très long (plus de 2 semaines)'),
    ], string="Délai de Traitement", required=True)

    clarity = fields.Selection([
        ('5', 'Très clair'),
        ('4', 'Clair'),
        ('3', 'Acceptable'),
        ('2', 'Peu clair'),
        ('1', 'Pas du tout clair'),
    ], string="Clarté des Explications", required=True)

    solution_quality = fields.Selection([
        ('very_satisfied', 'Très satisfait'),
        ('satisfied', 'Satisfait'),
        ('neutral', 'Neutre'),
        ('dissatisfied', 'Insatisfait'),
        ('very_dissatisfied', 'Très insatisfait'),
    ], string="Qualité de la Solution", required=True)

    professionalism = fields.Selection([
        ('5', '⭐⭐⭐⭐⭐ - Excellent'),
        ('4', '⭐⭐⭐⭐ - Bon'),
        ('3', '⭐⭐⭐ - Moyen'),
        ('2', '⭐⭐ - À améliorer'),
        ('1', '⭐ - Mauvais'),
    ], string="Amabilité et Professionnalisme", required=True)

    recommend = fields.Selection([
        ('yes', 'Oui'),
        ('maybe', 'Peut-être'),
        ('no', 'Non'),
    ], string="Recommanderiez-vous notre service ?", required=True)

    comments = fields.Text(string="Suggestions d'Amélioration")
    consent = fields.Boolean(string="Acceptez-vous que votre retour soit utilisé anonymement ?", default=True)


class ReclamationStats(models.Model):
    _name = 'reclamation.dashboard'
    _description = 'Statistiques des réclamations'

    type2 = fields.Selection([
        ('technical', 'Technique'),
        ('commercial', 'Commercial'),
        ('other', 'Autre')
    ], string='Type de réclamation')
 
    archived = fields.Boolean(string="Archivée?", required=False, default=False)

    origin = fields.Selection([
        ('cellule', 'Cellule de veille'),
        ('presence', 'Présence'),
        ('tel', 'Téléphone'),
        ('site', 'Site Web')
    ], string='Origine de la réclamation')

    countnb = fields.Integer(string='Nombre de réclamations', default=0)
    count_archived = fields.Integer(string='Nombre de réclamations', default=0)
    dynamic_row = fields.Char(string='Dynamic Row', compute='_compute_dynamic_fields')
    dynamic_measure = fields.Char(string='Dynamic Measure', compute='_compute_dynamic_fields')
    view_mode = fields.Selection(
        [('archived', 'Archived'), ('type2', 'Type')],
        default='archived',
        string='View Mode'
    )

    def toggle_view_mode(self):
        """Toggle between Archived and Type view."""
        for record in self:
            record.view_mode = 'type2' if record.view_mode == 'archived' else 'archived'

    @api.depends('view_mode', 'archived', 'count_archived', 'type2', 'countnb')
    def _compute_dynamic_fields(self):
        for record in self:
            if record.view_mode == 'archived':
                record.dynamic_row = record.archived
                record.dynamic_measure = record.count_archived
            else:
                record.dynamic_row = record.type
                record.dynamic_measure = record.countnb


    @api.model
    def get_reclamation_stats(self):
        stats = {
            'origin': {
                'cellule': 0,
                'site': 0,
                'tel': 0,
                'presence': 0
            },
            'type2': {
                'technical': 0,
                'commercial': 0,
                'other': 0
            },
            'archived': {
                False: 0,
                True: 0,

            }

        }

        # Récupérer les réclamations par origine
        reclamations_by_origin = self.env['reclamation'].read_group(
            [('active', '=', True)],  # Assurez-vous que le champ 'active' est filtré
            ['origin'],                # Récupérer uniquement le champ 'origin'
            ['origin']                 # Grouper uniquement par 'origin'
        )
        for record in reclamations_by_origin:
            stats['origin'][record['origin']] = record['__count']

        # Récupérer les réclamations par type2
        reclamations_by_type = self.env['reclamation'].read_group(
            [('active', '=', True)],  # Assurez-vous que le champ 'active' est filtré
            ['type2'],                 # Récupérer uniquement le champ 'type2'
            ['type2']                  # Grouper uniquement par 'type2'
        )
        for record in reclamations_by_type:
            stats['type2'][record['type2']] = record['__count']

        reclamations_by_archived = self.env['reclamation'].read_group(
            [('active', '=', True)],  # Assurez-vous que le champ 'active' est filtré
            ['archived'],                 # Récupérer uniquement le champ 'type2'
            ['archived']                  # Grouper uniquement par 'type2'
        )
        for record in reclamations_by_type:
            stats['archived'][record['archived']] = record['__count']


        return stats





