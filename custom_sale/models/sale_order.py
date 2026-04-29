from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Logistics notes (internal use only)
    notes_logistiques = fields.Html(
        string='Logistics Notes',
        sanitize=True,
        translate=True,
    )

    # Approval workflow fields
    x_is_dg_approved = fields.Boolean(
        string='Approved by General Director',
        default=False,
        readonly=True,
        help='Indicates if the General Director has approved this quotation',
    )
    
    x_dg_approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        help='User who approved this quotation',
    )
    
    x_dg_approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        help='Date and time of approval',
    )

    x_deposit_paid = fields.Boolean(
        string='Deposit Paid',
        compute='_compute_deposit_paid',
        store=True,
        help='Indicates if the 50% deposit has been paid',
    )

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.amount_total')
    def _compute_deposit_paid(self):
        """
        Compute if 50% deposit has been paid by checking down payment invoices.
        """
        for order in self:
            # Get down payment invoices linked to this order
            # Down payments are identified by having invoice lines with product 'Down payment'
            down_payment_invoices = order.invoice_ids.filtered(
                lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted' and 
                           any(line.product_id.name == 'Down payment' for line in inv.invoice_line_ids)
            )
            
            if not down_payment_invoices:
                order.x_deposit_paid = False
                continue
            
            # Calculate total paid amount from down payments
            total_paid = sum(inv.amount_total for inv in down_payment_invoices)
            # Check if paid amount is at least 50% of order total
            order.x_deposit_paid = total_paid >= (order.amount_total * 0.5)

    def action_approve_by_dg(self):
        """
        Action for General Director to approve a quotation.
        """
        for order in self:
            if order.state != 'draft':
                raise UserError('Only draft quotations can be approved.')
            
            order.write({
                'x_is_dg_approved': True,
                'x_dg_approved_by': self.env.user.id,
                'x_dg_approved_date': fields.Datetime.now(),
            })
        
        return True

    def action_confirm(self):
        """
        Override confirm action to enforce approval and deposit validation.
        """
        for order in self:
            if not order.x_is_dg_approved:
                raise UserError(
                    'The General Director must approve this quotation before confirmation.'
                )
            if not order.x_deposit_paid:
                raise UserError(
                    'A 50% deposit must be paid before confirming this quotation.'
                )
        
        return super().action_confirm()
