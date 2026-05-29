from odoo import models, fields, api, exceptions
from odoo.tools.translate import _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    team_id = fields.Many2one(
        'nexyor.team',
        string='Assigned Team',
        help='The operational team assigned to this task',
        tracking=True
    )

    @api.onchange('team_id')
    def _onchange_team_id(self):
        """
        Auto-populate user_ids with linked user accounts of team leader and members.
        Maps employees to their corresponding res.users records.
        """
        if self.team_id:
            users_to_assign = self.env['res.users']
            
            # Add team leader's user
            if self.team_id.leader_id and self.team_id.leader_id.user_id:
                users_to_assign |= self.team_id.leader_id.user_id
            
            # Add team members' users
            for member in self.team_id.member_ids:
                if member.user_id:
                    users_to_assign |= member.user_id
            
            # Assign to user_ids (native many2many field)
            self.user_ids = [(6, 0, users_to_assign.ids)]
        else:
            self.user_ids = [(5, 0, 0)]

    @api.constrains('team_id', 'planned_date_begin', 'planned_date_end', 'state')
    def _check_schedule_conflict(self):
        """
        Strict validation to prevent schedule overlaps for team members.
        
        Checks if any employee (leader or member) of the assigned team
        is already assigned to another active task that overlaps
        with the current task's scheduled timeframe.
        """
        for task in self:
            # Skip if no team or no dates set
            if not task.team_id or not task.planned_date_begin or not task.planned_date_end:
                continue
            
            # Skip if task is in a terminal state (done, cancelled)
            if task.state in ['done', 'cancel']:
                continue
            
            # Get all employees from the team (leader + members)
            employees = self.env['hr.employee']
            if task.team_id.leader_id:
                employees |= task.team_id.leader_id
            employees |= task.team_id.member_ids
            
            if not employees:
                continue
            
            # Find all tasks with overlapping schedules that have teams assigned
            # Exclude the current task and terminal state tasks
            overlapping_domain = [
                ('id', '!=', task.id),
                ('state', 'not in', ['done', 'cancel']),
                ('team_id', '!=', False),
                ('planned_date_begin', '!=', False),
                ('planned_date_end', '!=', False),
                # Overlap condition: existing task overlaps with current task
                ('planned_date_begin', '<', task.planned_date_end),
                ('planned_date_end', '>', task.planned_date_begin),
            ]
            
            overlapping_tasks = self.search(overlapping_domain)
            
            # Check each overlapping task for employee conflicts
            for other_task in overlapping_tasks:
                if not other_task.team_id:
                    continue
                
                # Get employees from the other task's team
                other_employees = self.env['hr.employee']
                if other_task.team_id.leader_id:
                    other_employees |= other_task.team_id.leader_id
                other_employees |= other_task.team_id.member_ids
                
                # Find intersection of employees
                conflicting_employees = employees & other_employees
                
                if conflicting_employees:
                    # Raise error with first conflicting employee's name
                    employee = conflicting_employees[0]
                    raise exceptions.ValidationError(_(
                        "Conflict Detected: Employee %(name)s is already assigned to "
                        "another task during this period.",
                        name=employee.name
                    ))
