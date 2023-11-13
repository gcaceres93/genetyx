# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words
# from odoo.tools import float_round, round

class factura (models.Model):
    _inherit = "account.move"

    seccion = fields.Boolean(string="Seccion")
    isrucinternacional = fields.Boolean(string='Imprimir Ruc Internacional',
                                        help="ANTES DE IMPRIMIR DEBE VERIFICAR SI ESTA CARGADO EL RUC INTERNACIONAL EN LA FICHA DEL CLIENTE")
    isredondeo = fields.Boolean(string='Redondeo', help="SE APLICA SOLO AL BANCO CENTRAL DEL PARAGUAY")
    comercial = fields.Many2one('res.partner',string="Comercial")
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',default=lambda self: self.env.user, copy=False)

    def action_post(self):
        res = super(factura, self).action_post()

        # for rec in self:
        #
        #     if rec.move_type in ('in_invoice', 'out_invoice', 'in_refund', 'out_refund'):
        #         lineas_impuesto = rec.line_ids.filtered(lambda r: r.tax_line_id)
        #         # Se calcula la cotizacion en caso de ser diferente a GS, si es guaranies la cotizacion es 1
        #         if rec.currency_id != rec.env.company.currency_id:
        #             currency_rate = rec.env['res.currency.rate'].search(
        #                 [('name', '=', rec.invoice_date), ('currency_id', '=', rec.currency_id.id)])
        #             if currency_rate:
        #                 rate = currency_rate[0].set_venta
        #         else:
        #             rate = 1
        #         for lineas_imp in lineas_impuesto.mapped('tax_line_id'):
        #             gravadas_con_imp = sum(
        #                 rec.line_ids.filtered(lambda r: r.tax_ids == lineas_imp).mapped('amount_currency'))
        #             for gravadas in rec.line_ids.filtered(lambda r: r.tax_ids == lineas_imp):
        #                 _logger.info('price_unit %s ' % gravadas.price_unit)
        #
        #             monto_imp = lineas_imp.amount
        #             if monto_imp != 0:
        #                 total_imp = gravadas_con_imp / monto_imp
        #             else:
        #                 total_imp = 0
        #             linea_to_up = lineas_impuesto.filtered(lambda r: r.tax_line_id == lineas_imp)
        #
        #             _logger.info('total_imp %s' % total_imp)
        #             linea_to_up.amount_currency = total_imp
        #
        #             if total_imp > 0:
        #
        #                 linea_to_up.debit = total_imp * rate
        #                 linea_to_up.balance = total_imp * rate
        #             else:
        #                 linea_to_up.credit = abs(total_imp) * rate
        #                 linea_to_up.balance = total_imp * rate
        #         total_currency = sum(
        #             rec.line_ids.filtered(lambda r: r.account_internal_type not in ('receivable', 'payable')).mapped(
        #                 'amount_currency'))
        #
        #         due_lines = rec.line_ids.filtered(lambda r: r.account_internal_type in ('receivable', 'payable'))
        #         if len(due_lines) == 1:
        #             due_lines.amount_currency = -1 * total_currency
        #             due_lines.amount_residual_currency = -1 * total_currency
        #
        #             if total_currency > 0:
        #                 total_credit = sum(rec.line_ids.filtered(
        #                     lambda r: r.account_internal_type not in ('receivable', 'payable')).mapped(
        #                     'credit'))
        #                 total_debit = sum(rec.line_ids.filtered(
        #                     lambda r: r.account_internal_type not in ('receivable', 'payable')).mapped(
        #                     'debit'))
        #                 due_lines.credit = abs(total_credit - total_debit)
        #                 due_lines.balance = total_credit - total_debit
        #                 due_lines.amount_residual = total_credit - total_debit
        #             else:
        #                 total_credit = sum(rec.line_ids.filtered(
        #                     lambda r: r.account_internal_type not in ('receivable', 'payable')).mapped(
        #                     'credit'))
        #                 total_debit = sum(rec.line_ids.filtered(
        #                     lambda r: r.account_internal_type not in ('receivable', 'payable')).mapped(
        #                     'debit'))
        #                 due_lines.debit = abs(total_debit - total_credit)
        #                 due_lines.balance = abs(total_debit - total_credit)
        #                 due_lines.amount_residual = abs(total_debit - total_credit)
        #
        #         rec.amount_residual = abs(total_currency)

        print(f"Junior Factura {self.name}")
        cant_dias = sum(l.days for l in self.invoice_payment_term_id.line_ids)
        # Verificar
        tiene_cuotas = False
        if any(l.value == 'instalment' for l in self.invoice_payment_term_id.line_ids):
            tiene_cuotas = True
        # DESCOMENTAR PARA TRASLADAR EL CODIGO A OTRO CLIENTE QUE POSEA FACTURAS A CUAOTA
        # if cant_dias == 0 and not tiene_cuotas:
        #     if self.amount_total != self.amount_residual:
        #         query = """
        #             update account_move_line set price_unit = - (Select amount_total from account_move where id = move_id),
        #             amount_currency = (Select amount_total from account_move where id = move_id),
        #             price_subtotal = - (Select amount_total from account_move where id = move_id),
        #             price_total = - (Select amount_total from account_move where id = move_id),
        #             amount_residual_currency = (Select amount_total from account_move where id = move_id)
        #             where move_id = %s and account_id in (select id from account_account where user_type_id = (select id from account_account_type where "name" = 'Receivable' and "type" = 'receivable'))
        #         """
        #         params = [self.id]
        #         second_query = """
        #         update account_move set amount_residual = amount_total where id %s
        #         """
        #         self.env.cr.execute(query, params)
        #         self.env.cr.execute(second_query, params)
        if self.amount_total != self.amount_residual and self.move_type != 'entry':
            query = """
                    UPDATE account_move_line SET 
                        price_unit = - (SELECT amount_total FROM account_move WHERE id = move_id),
                        amount_currency = (SELECT CASE 
                                               WHEN account_move.move_type IN ('out_invoice', 'in_refund') THEN amount_total 
                                               WHEN account_move.move_type IN ('in_invoice', 'out_refund') THEN - amount_total 
                                           END 
                                           FROM account_move WHERE id = move_id),
                        price_subtotal = - (SELECT amount_total FROM account_move WHERE id = move_id),
                        price_total = - (SELECT amount_total FROM account_move WHERE id = move_id),
                        amount_residual_currency = (SELECT CASE 
                                                        WHEN account_move.currency_id = account_move.company_currency_id THEN amount_total
                                                        WHEN account_move.move_type IN ('out_invoice', 'in_refund') THEN amount_total
                                                        WHEN account_move.move_type IN ('in_invoice', 'out_refund') THEN - amount_total
                                                    END 
                                                    FROM account_move WHERE id = move_id)
                    WHERE move_id = %s AND account_id IN (
                        SELECT id FROM account_account 
                        WHERE user_type_id IN (
                            SELECT id FROM account_account_type 
                            WHERE "name" IN ('Receivable', 'Payable') AND "type" IN ('receivable', 'payable')
                        )
                    )
            """
            params = [self.id]
            second_query = """
                UPDATE account_move SET amount_residual = amount_total WHERE id = %s
            """
            self.env.cr.execute(query, params)
            self.env.cr.execute(second_query, params)

        return res

    @api.onchange('date', 'currency_id')
    def _onchange_currency(self):
        currency = self.currency_id or self.company_id.currency_id

        if self.is_invoice(include_receipts=False):
            for line in self._get_lines_onchange_currency():
                line.currency_id = currency
                line._onchange_currency()
        else:
            for line in self.line_ids:
                line._onchange_currency()

        self._recompute_dynamic_lines(recompute_tax_base_amount=True)
    
    def calcular_rate(self):
            tasas = self.env['res.currency.rate'].search([('rate','=',1)])
            for t in tasas:
                t.rate = 1 / t.set_venta

    
    def get_seccion(self, seccion):
        seleccion = 0
        if (seccion):
            seleccion = 1
        else:
            seleccion = 0

        return seleccion

    # FUNCION PARA EVALUAR LA LONGITUD DE LAS LINEAS DE PRODUCTOS
    
    def get_procesar_producto(self, lista_producto):
        longitud = len(lista_producto)
        print("Londitud: " + str(longitud))
        return longitud

    # FUNCION PARA EVALUAR SI EN LA LINEA DE PRODUCTO INGRESA UNA DECRIPCION DE SECCION
    
    def get_descripcion(self, producto):
        descripcion = ''
        if (type(producto.display_type) is str):
            descripcion = producto.name
        return descripcion

    # LA SECCION ES DE TIPO BOOLEAN Y EL NAME ES STR ESO EVALUAMOS PARA ACUMULAR EL PRECIO
    
    def get_prueba(self, tipo):
        tipo = type(tipo)
        bandera = 0
        if (tipo is str):
            bandera = 1
        elif (tipo is True):
            bandera = 0
        elif (tipo is False):
            bandera = 0
        # print(tipo)
        print(bandera)
        return bandera

    def get_tipo(self, tipo):
        bandera = 0
        if 'line_section' in tipo:
            bandera = 1
        elif 'line_nota' in tipo:
            bandera = 0
        return bandera

    
    def get_total_precio(self, cantidad, precio_unitario):
        if cantidad > 0:
            cant_entero = int(cantidad)
            # precio_total = cant_entero * precio_unitario
            precio_total = cantidad * precio_unitario
            return precio_total
        else:
            precio_total = cantidad * precio_unitario
            return precio_total

    
    def get_redondeo_iva(self, iva, moneda):
        if 'PYG' in moneda:
            # redondeo_parcial = round(iva, 1)
            redondeo_total = round(iva)
            return redondeo_total
        elif 'USD' in moneda:
            return iva

    
    def get_redondeo(self, acumulador_impuesto, moneda):
        if 'PYG' in moneda:
            # redondeo_parcial = round(acumulador_impuesto,1)
            # redondeo_total = round(redondeo_parcial)
            redondeo = round(acumulador_impuesto, 1)
            return redondeo
        elif 'USD' in moneda:
            redondeo = acumulador_impuesto
            # redondeo = round(acumulador_impuesto,2)
            return redondeo

    
    def get_pos(self):
        pos = self.env['pos.order'].search([('name', '=', self.reference)])
        return pos

    
    def get_monto(self, impuesto):
        i = 0
        j = 0
        entero = 0
        if (self.currency_id.id == 3):
            impuesto_letra = str(impuesto)
            while i < len(impuesto_letra):
                if (impuesto_letra[i] == "."):
                    j = i + 3
                    break;
                i += 1
            return impuesto_letra[:j]
        else:
            entero = int(impuesto)
        return entero

    # termino_pago=fields.Integer(compute="_get_termino_pago")
    #
    # @api.depends
    # def _get_termino_pago(self):
    #     fecha_factura=int(self.date_invoice)
    #     fecha_vencimiento=int(self.date_due)
    #     return fecha_factura - fecha_vencimiento

    def get_invoice_data(self):
        invoice = self
        datos = list()
        print(invoice)
        dato_final = 'None'
        for orden in invoice:
            datos.append(orden.nro_factura)
            datos.append(orden.talonario_factura.name)
            datos.append(orden.talonario_factura.fecha_inicio)
            datos.append(orden.talonario_factura.fecha_final)
            dato_final = orden.talonario_factura.name
            print(orden.talonario_factura.name)
            print(datos)

        return datos

    def sacacoma(self, n):
        return int(n)

    
    def tipofactura(self, n):
        if (n == '2'):
            return 'Credito'
        elif (n == '1'):
            return 'Contado'

    
    def calcular_letras(self, numero):
        letras =  num2words(numero, lang='es').upper()
        letras = '--' + 'GUARANIES ' + letras + '--'
        return letras

    
    def calcular_letras_dolar(self, numero):
        nuevo_numero = str(numero).split('.')
        entero = num2words(int(nuevo_numero[0]), lang='es').upper()
        # if len(nuevo_numero[1] == 1):
        if len(nuevo_numero[1]) == 1:
            if nuevo_numero[1] == '0':
                decimal = num2words(int(nuevo_numero[1]), lang='es').upper()
            else:
                decimal = num2words(int(nuevo_numero[1] + '0'), lang='es').upper()
        else:
            decimal = num2words(int(nuevo_numero[1]), lang='es').upper()
        letras = entero + ' DOLARES ' + ' CON ' + decimal + ' CENTAVOS '
        return letras

    
    # def agregar_punto_de_miles(self, numero):
    #     numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(numero))), 3)])[::-1]
    #     return numero_con_punto

    def agregar_punto_de_miles(self, numero, moneda):
        entero = int(numero)
        if 'USD' in moneda:

            decimal = '{0:.2f}'.format(numero - entero)
            entero_string = '.'.join([str(int(entero))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                            ::-1]
            if decimal == '0.00':
                numero_con_punto = entero_string + ',00'
            else:
                decimal_string = str(decimal).split('.')
                numero_con_punto = entero_string + ',' + decimal_string[1]
        elif 'PYG' in moneda:
            numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(numero))), 3)])[
                               ::-1]
            return numero_con_punto
        else:
            numero_con_punto = '.'.join([str(int(numero))[::-1][i:i + 3] for i in range(0, len(str(int(entero))), 3)])[
                               ::-1]
        num_return = numero_con_punto
        return num_return

    def calcula_moneda(self, moneda):
        if 'USD' in moneda:
            return '$'
        elif 'PYG' in moneda:
            return 'Gs.'

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    @api.onchange('currency_id')
    def _onchange_currency(self):
        for line in self:
            company = line.move_id.company_id
            if line.move_id.move_type != 'in_receipt':
                if line.move_id.is_invoice(include_receipts=True):
                    line._onchange_price_subtotal()
                elif not line.move_id.reversed_entry_id:
                    balance = line.currency_id._convert(line.amount_currency, company.currency_id, company,
                                                        line.move_id.date or fields.Date.context_today(line))
                    line.debit = balance if balance > 0.0 else 0.0
                    line.credit = -balance if balance < 0.0 else 0.0



