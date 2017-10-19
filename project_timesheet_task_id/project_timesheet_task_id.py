# -*- coding: utf-8 -*-
# © 2016-2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class ProjectWork(models.Model):
    _inherit = 'project.task.work'

    @api.model
    def create(self, vals):
        """
        When create a new record, modify the timesheet task_id field
        :param vals:
        :return:
        """
        res = super(ProjectWork, self).create(vals)
        time_sheet = res.hr_analytic_timesheet_id
        if time_sheet:
            time_sheet.task_id = vals.get('task_id', False)

        return res

    @api.multi
    def write(self, vals):
        if 'task_id' in vals:
            task_id = vals['task_id']
            for record in self:
                time_sheet = record.hr_analytic_timesheet_id
                if time_sheet:
                    time_sheet.task_id = task_id
        return super(ProjectWork, self).write(vals)


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    task_id = fields.Many2one('project.task', 'Task')

    @api.model
    def create(self, vals):
        """When create a new record, create the project.task.work record
        """
        res = super(HrAnalyticTimesheet, self).create(vals)
        if res.task_id.exists():
            # Disable creation of analytic_entry when creating
            # project.task.work as there is already created
            task_work_obj = self.env['project.task.work'].with_context(
                no_analytic_entry=True,
            )
            task_work = task_work_obj.create({
                'name': res.name,
                'hours': res.unit_amount,
                'date': res.date,
                'user_id': res.user_id.id,
                'task_id': res.task_id.id,
                'hr_analytic_timesheet_id': res.id,
            })

        return res

    @api.multi
    def unlink(self):
        """When deleting a record, delete related project.task.work record"""
        to_delete = self.env['project.task.work'].search([
            ('hr_analytic_timesheet_id', 'in', self.mapped('id')),
        ])

        super(HrAnalyticTimesheet, self).unlink()
        to_delete.unlink()
