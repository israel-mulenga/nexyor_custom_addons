from odoo import models, fields


class NexyorTeam(models.Model):
    _name = 'nexyor.team'
    _description = 'Nexyor Operational Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Team Name',
        required=True,
        help='Name of the operational team (e.g., "Sound Engineering Team A")',
        track_visibility='onchange'  # Ajoutez ceci pour le suivi
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        readonly=True)
    
    leader_id = fields.Many2one(
        'hr.employee',
        string='Team Leader',
        required=True,
        help='The designated Team Leader for this operational team',
        track_visibility='onchange'  # Ajoutez ceci pour le suivi
    )
    
    member_ids = fields.Many2many(
        'hr.employee',
        'nexyor_team_hr_employee_rel',
        'team_id',
        'employee_id',
        string='Team Members',
        help='The logistics personnel belonging to this team'
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Assigned Project',
        help='The specific event project this team is currently built for',
        track_visibility='onchange'  # Ajoutez ceci pour le suivi
    )
    
    active = fields.Boolean(default=True)
    
   
    
    def _compute_display_name(self):
        for team in self:
            name = team.name
            if team.project_id:
                name += f' ({team.project_id.name})'
            team.display_name = name