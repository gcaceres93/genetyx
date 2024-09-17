from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CropRequests(models.Model):
    '''Details to create Crop Requests'''
    _name = 'crop.requests'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Taurus"
    _rec_name = 'ref'

    ref = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, tracking=True,
                      default=lambda self: _('New'))

    produccion_ids = fields.One2many('crop.production', 'cro', string='Producción')

    nombre = fields.Char(string="Nombre")
    
    insumos_ids = fields.One2many('crop.insumos', 'pro', string='Insumos')

    price = fields.Float(string='Precio', related='insumos_ids.product_id.list_price', store=True)

    animal_id = fields.Many2one(related='animal_ids.animal_id', string='Animal', store=True)

    veterinario_id = fields.Many2one('vet.details', string='Veterinario', required=False, tracking=True)

    location_id = fields.Many2one('location.details', string='Location',domain=lambda self: self._domain_campo_relacionado(),
                                  required=False, tracking=True)
    request_date = fields.Date(string='Fecha de Ingreso', required=True,
                               tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cuarentena', 'Cuarentena'), ('s_cuarentena', 'Salida de Cuarentena'),
         ('residente', 'Residente'), ('enfermeria', 'Enfermeria'),
         ('cancel', 'Cancel')],
        string='Status', default='draft', tracking=True,
        group_expand='_group_expand_states')
    note = fields.Text(string='Note', tracking=True)

    # machinery_ids = fields.One2many('crop.machinery', 'des', string=   'Machinery',
    #                                tracking=True)
    animal_ids = fields.One2many('crop.animals', 'dec', string='Animals', required=True,
                                 tracking=True)
    tags_id = fields.Many2many('agr.tag', string='Tags', tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible User',
                              default=lambda self: self.env.user)
    gta = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')])
    nota_fiscal = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')])
    rp = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')])
    guia_senacsa = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Guía Senacsa')
    guia_senacsa_cuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Guía Senacsa')
    enfermedades_scuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string="Enfermedades")
    analisis_cuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string="Enfermedades")
    fecha_analisis_cuarentena = fields.Date(string='Fecha de último analisis')
    enfermedades_cuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string="Enfermedades", required=True)
    d_veterinario = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')])

    examen_fisico_cuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Examen Fisico Normal?',  tracking=True)
    examen_andrologico_cuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],
        string='Examen Andrologico', tracking=True)

    examen_fisico_scuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Examen Fisico Normal?', tracking=True, required=True)
    pedigree = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Pedigree', tracking=True, required=True)
    analisis_laboratorio = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Analisis de laboratorio', tracking=True, required=True)
    examen_andrologico_scuarentena = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],
        string='Examen Andrologico',tracking=True, required=True)

    enfermedades_diarrea = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Diarrea Viral Bovina', tracking=True)
    fecha_analisis_dv = fields.Date(string='Fecha de Analisis')
    enfermedades_tuberculosis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Tuberculose',  tracking=True)
    study_ids = fields.One2many('crop.request.studies', 'request_id', string="Estudios en Cuarentena")
    fecha_analisis_tb = fields.Date(string='Fecha de Analisis')
    enfermedades_campylobacteriosis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Campylobacteriosis',tracking=True)
    fecha_analisis_camp = fields.Date(string='Fecha de Analisis')
    enfermedades_tricomaniasis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Tricomaniasis', tracking=True)
    fecha_analisis_trico = fields.Date(string='Fecha de Analisis')
    def _domain_campo_relacionado(self):
        asignados = self.env['location.details'].search([('location_name', '!=', False)])
        ids_asignados = asignados.mapped('location_name')
        return [('id', 'not in', ids_asignados)]

    @api.model
    def _create_analysis_activity(self, record_id):
        record = self.env['crop.requests'].browse(record_id)
        if record.fecha_analisis_cuarentena:
            # Calcula la fecha de la actividad en función de la fecha de cuarentena (por ejemplo, 7 días después).
            activity_date = record.fecha_analisis_cuarentena + timedelta(days=180)
            activity = self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'Ultimo analisis hecho en cuarentena el {record.fecha_analisis_cuarentena.strftime("%d-%m-%Y")} el siguiente a realizar {activity_date.strftime("%d-%m-%Y")}',
                'date_deadline': activity_date,
                'res_id': record_id,
                'res_model_id': self.env['ir.model']._get('crop.requests').id,
            })
            return activity
        return False

    @api.onchange('animal_id')
    def _onchange_animal_id(self):
        if self.animal_id:
            self.gta = self.animal_id.gta

    def _update_request_date(self):
        self.request_date = date.today()  # Se actualiza la fecha de ingreso cada vez que se cambia de estado

    @api.model
    def create(self, values):
        if values.get('ref', _('New')) == _('New'):
            values['ref'] = self.env['ir.sequence'].next_by_code(
                'crop.requests') or _('New')
        res = super(CropRequests, self).create(values)
        return res

    def _check_deseases(self):
        animal = self.animal_ids
        for a in animal:
            if a.animal_id.enfermedades == 'ok':
                raise ValidationError('No se puede salir de cuarentena si el toro tiene positivo a enfermedades')
            return True


    def action_draft(self):
        self.state = 'draft'
        self._update_request_date()

    def action_cuarentena(self):
        # if self._check_documentacion_cuarentena():
        #     print(...)


        self.state = 'cuarentena'
        self._update_request_date()


    def action_s_cuarentena(self):
        if self._check_deseases():
            print('...')

        self.state = 's_cuarentena'
        self._update_request_date()

    def action_residente(self):
        if self.guia_senacsa != 'ok':
            raise ValidationError('No puedes pasar al estado "Residente" sin la guía SENACSA.')
        else:
            self.state = 'residente'
            # Llama a la función para crear la actividad basada en la fecha de cuarentena
            activity = self._create_analysis_activity(self.id)

    def action_enfermeria(self):
        self.state = 'enfermeria'
        self._update_request_date()

    def action_cancel(self):
        self.state = 'cancel'
        self._update_request_date()

    def action_storage(self):
        self.state = 'storage'

    def _group_expand_states(self, states, domain, order):
        return [key for
                key, val in type(self).state.selection]

    def estadosMayus(self):
        estado = ''
        if self.state == 'enfermeria':
            estado = 'Enfermeria'
        elif self.state == 's_cuarentena':
            estado = 'Salida de Cuarentena'
        elif self.state == 'residente':
            estado = 'Residente'
        elif self.state == 'cuarentena':
            estado = 'Cuarentena'

        return estado


class CropProdutcion(models.Model):
    _name = 'crop.production'

    cod_toro = fields.Char(string='Cod. Toro')
    cro = fields.Many2one(string='Produccion')
    salto = fields.Char(string='Salto')
    codigo_coletador = fields.Char(string='Código Coletador')
    metodo_coleta = fields.Char(string='Método Coleta')
    lote = fields.Char(string='Lote')
    vol_ml = fields.Char(string='Vol ML')
    conc = fields.Char(string='Conc')
    con_total = fields.Char(string='Con Total')
    motil = fields.Char(string='Motil')
    vigor = fields.Char(string='Vigor')
    sptz = fields.Char(string='Sptz')
    def_mayores = fields.Char(string='Def Mayores')
    def_totales = fields.Char(string='Def Totales')
    calc_paletas = fields.Char(string='Calc Paletas')
    vol_inicial = fields.Char(string='Vol Inicial')
    vol_final = fields.Char(string='Vol Final')
    vol_agregar = fields.Char(string='Vol Agregar')
    paletas_envasadas = fields.Char(string='Paletas Envasadas')
    paletas_producidas = fields.Char(string='Paletas Producidas')
    resultado_final = fields.Char(string='Resultado Final')
    country_id = fields.Many2one('res.country', string="País")

class CropMachinery(models.Model):
    '''Model For Attaching Vehicles'''
    _name = 'crop.machinery'

    des = fields.Many2one('crop.requests')
    vehicle_id = fields.Many2one('vehicle.details', string='Vehicle',
                                 tracking=True)
    qty = fields.Integer(string='Quantity')


class CropAnimals(models.Model):
    '''Model For Attaching Animals'''
    _name = 'crop.animals'

    dec = fields.Many2one('crop.requests')
    animal_id = fields.Many2one('animal.details', string='Animal', tracking=True, required=True)
    animal_ids = fields.One2many('animal.details', 'ani', string='Animal', tracking=True)
    qty = fields.Integer(string='Quantity')


class ProductExtention(models.Model):
    _name = 'crop.insumos'

    pro = fields.Many2one('crop.requests')
    product_id = fields.Many2one('product.product', string="Medicamentos")
    qty = fields.Integer(string='Cantidad')
    motivo_uso = fields.Many2one('crop.uso')
    price = fields.Float(string='Precio', compute='_compute_product_price')
    fecha = fields.Date(string='Fecha de Uso', default=date.today())

    @api.depends('product_id')
    def _compute_product_price(self):
        for record in self:
            record.price = record.product_id.list_price




class Eventos(models.Model):
    _name = 'crop.eventos'

    sintomas = fields.Char(string='Sintomas')
    tratamiento = fields.Char(string='Tratamientos')
    motivo_uso = fields.Char(string='Motivo de Uso')
    reacciones_alergicas = fields.Char(string='Reacciones Alergicas')

class Tratamiento(models.Model):
    _name = 'crop.tratamiento'

    tratamiento = fields.Char(string='Tratamientos')


class MotivoUso(models.Model):
    _name = 'crop.uso'

    motivo_uso = fields.Char(string='Motivo de Uso')

class Reacciones(models.Model):
    _name = 'crop.reacciones'

    reacciones_alergicas = fields.Char(string='Reacciones Alergicas')

class CropRequestStudies(models.Model):
    _name = 'crop.request.studies'
    _description = 'Estudios en Cuarentena'

    request_id = fields.Many2one('crop.requests', string="Solicitud de Cuarentena")
    country_id = fields.Many2one('res.country', string="País")
    study_name = fields.Char(string="Nombre del Estudio")
    result = fields.Selection([('pending', 'Pendiente'), ('done', 'Realizado')], string="Resultado")
