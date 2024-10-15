# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
'''Module for Creating Animal Records'''
from odoo import models, fields
from odoo import api
from odoo.exceptions import UserError, ValidationError


class AnimalDetails(models.Model):
    '''Details of Animals'''
    _name = 'animal.details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Animal Details"
    _rec_name = 'breed'

    image = fields.Binary(string='Image', tracking=True)
    ani = fields.Many2one('crop.animals')
    propietario = fields.Many2one('res.partner', string='Propietario', required=True)
    nacimiento = fields.Date(string='Fecha de Nacimiento')
    rp = fields.Char(string='RP')
    codigo = fields.Char(string='Codigo del Animal', required=True)
    codigo_taurus = fields.Char(string='RP', required=True)
    guia_movilizacion = fields.Char(string='Guía de Movilización Nro', required=True)
    pedigree = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Copia de Pedigree', required=True, tracking=True)
    fecha_llegada = fields.Datetime(string='Fecha y Hora de llegada', required=True)
    # raza = fields.Many2one('raza', string='Raza', required=False)
    puntuacion_corporal=fields.Selection(
        [('uno', '1'), ('dos', '2'), ('tres', '3'),('cuatro', '4'), ('cinco', '5')],
        default="Uno",
        string='Puntuacion Corporal 1-5', required=True, tracking=True)
    perimetro_escrotal = fields.Integer(string='Perimetro escrotal(cm)', required=True)

    motivos = fields.Text(string='Descripción del Motivo')
    examen_fisico = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Examen Fisico Normal?', required=True, tracking=True)
    certificado_vacunacion = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Certificado de vacunacion', required=True, tracking=True)
    analisis_laboratoriales = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Analisis laboratoriales', required=False, tracking=True)
    exportacion_animal = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Exportacion', required=False, tracking=True)
    examen_andrologico = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Examen Andrologico Normal?', required=True, tracking=True)
    nota_fiscal = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Nota Fiscal', required=True, tracking=True)
    registro = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Registro', required=True, tracking=True)
    enfermedades = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Brucelose', required=True, tracking=True)

    enfermedades_diarrea = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Diarrea Viral Bovina', required=True, tracking=True)

    enfermedades_tuberculosis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Tuberculose', required=True, tracking=True)
    enfermedades_campylobacteriosis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Campylobacteriosis', required=True, tracking=True)
    enfermedades_tricomaniasis = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Tricomaniasis', required=True, tracking=True)

    gta = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='GTA', required=True, tracking=True)
    contrato = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Contrato', required=True, tracking=True)
    andrologico = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],

        string='Andrologico', tracking=True)

    archivo_multimedia = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], string='Se agregó archivo multimedia?', required='True')

    name = fields.Char(string='Nombre', required=True, tracking=True)
    breed = fields.Char(string='Animal', required=True, tracking=True)
    peso = fields.Integer(string='Peso(en Kg)', required=True)
    age = fields.Char(string='Edad', required=True, tracking=True)
    country_id = fields.Many2one('res.country', string='País de Exportación', required=True, tracking=True)
    state = fields.Selection(
        [('ingresado', 'Ingresado'), ('no_ingresado', 'No ingresado')],
        default="no_ingresado",
        string='Status', required=False, tracking=True)
    note = fields.Text(string='Note', tracking=True)

    d_veterinario = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')], default=False)
    r_p = fields.Selection(
        [('ok', 'Ok'), ('no', 'No')],default=False)

    ingreso = fields.Many2one('crop.request')

    breed_id = fields.Many2one('animal.breed', string='Raza', required=True, tracking=True)
    fur_type_id = fields.Many2one('animal.fur', string='Pelaje', required=True, tracking=True)


    def copiar_a_formulario_destino(self):
        destino_obj = self.env['crop.request']

        for record in self:
            if record.state == 'ingresado':
                # Crear un nuevo registro en el modelo de destino y copiar los valores relevantes
                new_destino_record = destino_obj.create({
                    'animal_id': record.ani,  # Ajusta según tus campos

                    # Agrega más campos según sea necesario
                })

                # Actualizar el formulario_destino en el modelo de origen
                record.write({'crop.request': new_destino_record.id, 'state': 'cuarentena'})
            else:
                    print('**********************hola********************')

        return True


    def action_no_ingresado(self):
        self.state = 'no_ingresado'

    def action_sold(self):
        self.state = 'sold'

    def action_ingresado(self):
        self.state = 'ingresado'

    @api.constrains('archivo_multimedia')
    def check_multimedia(self):
        if self.archivo_multimedia != 'ok':
            raise ValidationError('Se debe adjuntar VIDEOS y FOTOS de la llegada del animal, favor adjuntar la evidencia en el chatter.')


class AnimalBreed(models.Model):
    _name = 'animal.breed'
    _description = 'Animal Breeds'

    name = fields.Char(string='Raza', required=True)
    description = fields.Text(string='Descripcion')

class AnimalFur(models.Model):
    _name = 'animal.fur'
    _description = 'Animal Fur Types'

    name = fields.Char(string='Pelaje', required=True)
    description = fields.Text(string='Descripcion')
