from datetime import timedelta
from odoo import _, api, exceptions, fields, models

class Permission(models.Model):
    _name = 'offsite.permission'
    _description = "Offsite Permissions"

    name = fields.Char(
        string='ขอไปราชการเพื่อ (วัตถุประสงค์/ลักษณะงาน)'
    )
    responsible_id = fields.Many2one(
        'res.users',
        ondelete='set null',
        string='ผู้ขอทำเรื่อง',
        index=True,
        readonly=True,
        default=lambda self: self.env.user
    )

    fuculty = fields.Selection(
        selection=[
            ('education','คณะครุศาสตร์'),
            ('science','คณะวิทยาศาสตร์'),
            ('agricultural','คณะเทคโนโลยีการเกษตร'),
            ('management','คณะวิทยาการจัดการ'),
            ('humanities','คณะมนุษย์ศาสตร์และสังคมศาสตร์'),
            ('industrial','คณะเทคโนโลยีอุตสาหกรรม'),
            ('nursing','คณะพยาบาลศาสตร์ '),
            ('graduate','บัณฑิตวิทยาลัย'),
            ('research','สถาบันวิจัยและพัฒนา'),
            ('arit','สำนักวิทยบริการและเทคโนโลยีสารสนเทศ')
        ],
        string='ส่วนราชการ'
    )
    department = fields.Many2one(
        'hr.department',
        ondelete='set null',
        string="สังกัด",
        index=True
    )
    date_rec = fields.Date(
        string='วันที่',
        default=fields.Date.today
    )
    position = fields.Char(
        string='ตำแหน่ง'
    )
    number = fields.Char(
        string='พร้อมด้วยคณะ รวม'
    )
    departure_as = fields.Selection(
        selection=[
            ('executive','ผู้บริหาร'),
            ('instructor','ผู้สอน'),
            ('supporter','ผู้สนับสนุนการสอน'),
        ],
        string='ขอไปราชการฐานะ'
    )
    date_departure = fields.Datetime(
        string="วันเวลาเดินไปราชการ",
        default=fields.Date.today
    )

    date_arrival = fields.Datetime(
        string='วันเวลากลับถึง',
        store=True,
        compute='_get_date_arrival',
        inverse='_set_date_arrival'
    )
    duration = fields.Float(
        digits=(6, 2),
        help='จำนวนวัน'
    )
    days = fields.Float(
        digits=(6, 2),
        string='จำนวนวัน'
    )
    hours = fields.Float(
        digits=(6, 2),
        string='จำนวนชั่วโมง'
    )
    place = fields.Char(
        string='สถานที่ไปราชการ ชื่อหน่วยงาน'
    )
    amphur = fields.Char(
        string='อำเภอ'
    )
    province = fields.Many2one(
        'res.country.state',
        ondelete='set null',
        string='จังหวัด',
        index=True
    )

    budget1 = fields.Float(
        string='งบประมาณ (บาท)'
    )
    budget2 = fields.Selection(
        selection=[
            ('pay1','เบิกค่าใช้จ่าย / ตามสิทธิ์'),
            ('pay2','เบิกค่าใช้จ่าย / เหมาจ่าย'),
            ('pay3','ไม่เบิกค่าใช้จ่าย')
        ],
        string='งบประมาณ')
    budget_type	 = fields.Selection(
        selection=[
            ('budget1','งบแผ่นดิน'),
            ('budget2','งบเงินรายได้'),
            ('budget3','งบอื่น ๆ'),
        ],
        string='โดยใช้งบประมาณ')
    amount = fields.Float(
        string='ในวงเงิน'
    )
    vehicle = fields.Selection(
        selection=[
            ('Vehicles1','ยานพาหนะประจำทาง'),
            ('Vehicles2','ขอใช้รถราชการ'),
            ('Vehicles3','ขอใช้รถส่วนตัว'),
        ],
        string='การเดินทาง'
    )
    license_plate = fields.Char(
        string='ทะเบียนรถ'
    )
    assignment = fields.Text(
        string='การมอบหมายระหว่างเดินทางไปราชการ'
    )
       
    expense_ids = fields.One2many(
        'offsite.expense',
        'permission_id',
        string='expenses'
    )

    attachment_ids = fields.Binary(
        'ไฟล์แนบ'
    )
    
    field1 = fields.Many2one(
        'hr.department',
        String='First field'
    )
    check = fields.Boolean(
        compute='_get_value'
    )
    field2 = fields.Char(
        String='Second field'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'ร่างบันทึกขออนุมัติ'),
            ('reported', 'ส่งบันทึกรอการอนุมัติ'),
            ('approved', 'อนุมัติ'),
            ('refused', 'ไม่อนุมัติ')
        ],
        string='Status',
        copy=False,
        index=True,
        readonly=True,
        store=True,
        default='draft',
        help='Status of the offsite'
    )
    amount_total = fields.Monetary(
        readonly=True,
        string='รวมค่าใช้จ่ายทั้งหมด'
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )


    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_reported(self):
        for rec in self:
            rec.state = 'reported'

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

    def action_refused(self):
        for rec in self:
            rec.state = 'refused'
    

    @api.depends('field1')
    def _get_value(self):
         if self.field1.name == "Any_String":
             self.check = True
         else:
             self.check = False

    @api.depends('date_departure', 'duration')
    def _get_date_arrival(self):
        for r in self:
            if not (r.date_departure and r.duration):
                r.date_arrival = r.date_departure
                continue

            # Add duration to date_departure, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.date_arrival = r.date_departure + duration

    def _set_date_arrival(self):
        for r in self:
            if not (r.date_departure and r.date_arrival):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.date_arrival - r.date_departure).days +1
            

    @api.onchange('date_departure', 'date_arrival')
    def _onchange_date(self):
        # set auto-changing field

        durations = ( self.date_arrival - self.date_departure )
        years = ((durations.total_seconds())/(365.242*24*3600))
        yearsInt = int(years)

        months = (years - yearsInt)*12
        monthsInt = int(months)
     
        days = (months - monthsInt)*(365.242/12)
        daysInt = int(days)
          
        hours = (days - daysInt)*24
        hoursInt = int(hours)

        minutes = (hours - hoursInt)*60
        minutesInt = int(minutes)

        seconds = (minutes - minutes)*60
        secondsInt = int(seconds)

        # if (minutesInt > 30) :
        #     hoursInt = hoursInt + 1
        # if (hoursInt > 12) :
        #     daysInt = daysInt + 1
        #     hoursInt = 0
        # elif (hoursInt > 6) & (daysInt == 0):
        #     daysInt = 0.5
        #     hoursInt = 0
 

        self.days = ( daysInt)
        self.hours = ( hoursInt )
        #self.duration = ' days  hours'.format(daysInt,hoursInt)
    # def _calculate_total_hours(self, cr, uid, ids, field_name, arg, context):
    #     for obj in self.pool.get('xxxxxx').browse(cr,uid,ids,context=context)
    #         date_from = datetime.strptime(obj.date_from, DEFAULT_SERVER_DATE_FORMAT) # change the format of the date if require
    #         date_to = datetime.strptime(obj.date_to, DEFAULT_SERVER_DATE_FORMAT) # change the format of the date if required
    #         difference = date_to - date_from
    #         res[obj.id] = difference.seconds / 3600 # float in hours
    #     return res
    # @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    # def _compute_state(self):
    #     for expense in self:
    #         if not expense.sheet_id or expense.sheet_id.state == 'draft':
    #             expense.state = "draft"
    #         elif expense.sheet_id.state == "cancel":
    #             expense.state = "refused"
    #         elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
    #             expense.state = "approved"
    #         elif not expense.sheet_id.account_move_id:
    #             expense.state = "reported"
    #         else:
    #             expense.state = "done"

class Expense(models.Model):
    _name = 'offsite.expense'
    _description = "offsite expenses"

    name = fields.Many2one(
        'res.users',
        ondelete='set null',
        string='ชื่อ-สกุล',
        index=True
    )

    allowance = fields.Float(
        string='เบี้ยเลี้ยง'
    )
    accommodation_fee = fields.Float(
        string='ค่าที่พัก'
    )
    vehicle_fee = fields.Float(
        string='ค่ายานพาหนะ'
    )
    other_expenses = fields.Float(
        string='ค่าใช้จ่ายอื่นๆ'
    )

    permission_id = fields.Many2one(
        'offsite.permission',
        ondelete='cascade',
        string='Permission',
        required=True
    )
    attendee_ids = fields.Many2many(
        'res.partner',
        string='Attendees'
    )

    attendees_count = fields.Integer(
        string='Attendees count',
        compute='_get_attendees_count',
        store=True
    )


class Estimate(models.Model):
    _name = 'offsite.estimate'
    _description = "offsite estimate"

    name = fields.Char(
        string='ขอไปราชการเพื่อ (วัตถุประสงค์/ลักษณะงาน)'
    )
    responsible_id = fields.Many2one(
        'res.users',
        ondelete='set null',
        string='ผู้ขอทำเรื่อง',
        index=True
    )

    fuculty = fields.Selection(
        selection=[
            ('education','	คณะครุศาสตร์'),
            ('science','	คณะวิทยาศาสตร์'),
            ('agricultural','คณะเทคโนโลยีการเกษตร'),
            ('management','	คณะวิทยาการจัดการ'),
            ('humanities',' คณะมนุษย์ศาสตร์และสังคมศาสตร์'),
            ('industrial',' คณะเทคโนโลยีอุตสาหกรรม'),
            ('nursing','	คณะพยาบาลศาสตร์ '),
            ('graduate','	บัณฑิตวิทยาลัย'),
            ('research','	สถาบันวิจัยและพัฒนา'),
            ('arit','สำนักวิทยบริการและเทคโนโลยีสารสนเทศ')
        ],
        string='ส่วนราชการ'
    )
    department = fields.Many2one(
        'hr.department',
        ondelete='set null',
        string='สังกัด',
        index=True
    )
    date_rec = fields.Date(
        string='วันที่',
        default=fields.Date.today
    )
    position = fields.Char(
        string='ตำแหน่ง'
    )
    number = fields.Char(
        string='พร้อมด้วยคณะ รวม'
    )
    departure_as = fields.Selection(
        selection=[
            ('executive', 'ผู้บริหาร'),
            ('instructor', 'ผู้สอน'),
            ('supporter', 'ผู้สนับสนุนการสอน'),
        ],
        string='ขอไปราชการฐานะ'
    )
    date_departure = fields.Datetime(
        string="วันเวลาเดินไปราชการ"
    )
    date_arrival = fields.Datetime(
        string="วันเวลากลับถึง"
    )
    place = fields.Char(
        string='สถานที่ไปราชการ ชื่อหน่วยงาน'
    )
    amphur = fields.Char(
        string="อำเภอ"
    )
    province = fields.Many2one(
        'res.country.state',
        ondelete='set null',
        string="จังหวัด",
        index=True)

    budget1 = fields.Float(
        string='งบประมาณ (บาท)'
    )
    budget2 = fields.Selection(
        selection=[
            ('1','เบิกค่าใช้จ่าย'),
            ('2','ไม่เบิกค่าใช้จ่าย'),
            ('3','ตามสิทธิ์'),
            ('4','เหมาจ่าย')
        ],
        string='งบประมาณ'
    )
    budget_type	= fields.Selection(
        selection=[
            ('1','งบแผ่นดิน'),
            ('2','งบเงินรายได้'),
            ('3','งบอื่น ๆ')
        ],
        string='โดยใช้งบประมาณ'
    )
    amount = fields.Float(
        string="ในวงเงิน"
    )
    vehicle = fields.Selection(
        selection=[
            ('1','ยานพาหนะประจำทาง'),
            ('2','ขอใช้รถราชการ'),
            ('3','ขอใช้รถส่วนตัว')
        ],
        string='การเดินทาง'
    )
    assignment = fields.Text(
        string="การมอบหมายระหว่างเดินทางไปราชการ"
    )

    expense_ids = fields.One2many(
        'offsite.expense',
        'permission_id',
        string='Expenses'
    )

    attachment_ids = fields.Binary(
        'ไฟล์แนบ'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'ร่างบันทึกขออนุญาต'),
            ('reported', 'ส่งบันทึกแล้ว'),
            ('approved', 'อนุมัติแล้ว'),
            ('refused', 'ไม่อนุญาต')
        ],
        string='Status',
        copy=False,
        index=True,
        readonly=True,
        store=True,
        default='draft',
        help='Status of the offsite.'
    )

