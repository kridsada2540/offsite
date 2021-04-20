# -*- coding: utf-8 -*-
from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model, by default partners are not
    # instructors
    instructor = fields.Boolean(
        'instructor',
        default=False)

    expense_ids = fields.Many2many(
        'openacademy.expense',
        string='Attended expenses',
        readonly=True
    )
