odoo.define('pos_wallet_card', function (require) {
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function (model) {
                return model.model === 'res.partner';
            });
            partner_model.fields.push('wallet');
            var journal_model = _.find(this.models, function (model) {
                return model.model === 'account.journal';
            });
            journal_model.fields.push('give_wallet', 'use_wallet');
            return _super_posmodel.initialize.apply(this, arguments);
        },
        push_order: function (order, opts) {
            var self = this;
            var client = order && order.get_client();
            if (client) {
                var give_wallet_amount = 0;
                var use_wallet_amount = 0;
                for (var i = 0; i < order.paymentlines.models.length; i++) {
                    var payment_line = order.paymentlines.models[i];
                    if (payment_line.cashregister.journal['give_wallet']) {
                        give_wallet_amount += +payment_line.get_amount();
                    }
                    if (payment_line.cashregister.journal['use_wallet']) {
                        use_wallet_amount += -payment_line.get_amount();
                    }
                }/*
                if (use_wallet_amount > client['wallet']) { // we're block push order if use wallet amount bigger than wallet amount of customer
                    return this.pos.gui.show_popup('error', {
                        title: 'Warning',
                        body: client['display_name'] + ' only have wallet amount: ' + client['wallet']
                    })
                }*/
                client['wallet'] = client['wallet'] + give_wallet_amount - use_wallet_amount;

            }
            return _super_posmodel.push_order.call(this, order, opts);
        },
        get_wallet: function (client) {
            var order = this.get_order();
            if (order && order.get_client()) {
                var client = order.get_client();
                var wallet = round_pr(client.wallet, this.currency.rounding)
                return (Math.round(wallet * 100) / 100).toString()
            } else {
                return null;
            }
        }
    });
    screens.ClientListScreenWidget.include({
        rouding_client_wallet: function (client) { // return wallet amount
            var wallet = round_pr(client.wallet, this.pos.currency.rounding)
            return (Math.round(wallet * 100) / 100).toString()
        }
    });
    screens.PaymentScreenWidget.include({
        // do not allow automatic add paymentline when click numpad
        click_numpad: function (button) {
            var paymentlines = this.pos.get_order().get_paymentlines();
            var open_paymentline = false;

            for (var i = 0; i < paymentlines.length; i++) {
                if (!paymentlines[i].paid) {
                    open_paymentline = true;
                }
            }
            if (!open_paymentline) {
                return this.gui.show_popup('error', {
                    'title': _t("Error"),
                    'body': _t("Please select payment method the first"),
                });
            } else {
                return this._super(button)
            }
        },

        // render wallet for journal element
        render_paymentlines: function () {
            this._super();
            var self = this;
            var order = this.pos.get_order();
            if (!order) {
                return;
            }
            var client = order.get_client();
            var use_wallet_register = _.find(this.pos.cashregisters, function (cashregister) {
                return cashregister.journal.use_wallet;
            });
            var give_wallet_register = _.find(this.pos.cashregisters, function (cashregister) {
                return cashregister.journal.give_wallet;
            });
            // if current order have change (return money)
            // and current order have client have selected before
            // will display give journal
            // else hidden journal method element
            // hide or not give wallet journal
            var selected_paymentline = order.selected_paymentline;
            if (selected_paymentline && give_wallet_register) {
                var give_wallet_journal_id = give_wallet_register.journal.id;
                var give_wallet_journal_content = $("[data-id='" + give_wallet_journal_id + "']");
                var change_order = order.get_change(selected_paymentline);
                if (change_order && client) {
                    give_wallet_journal_content.removeClass('oe_hidden');
                } else {
                    give_wallet_journal_content.addClass('oe_hidden');
                }
            }
            if (!selected_paymentline && give_wallet_register) {
                var give_wallet_journal_id = give_wallet_register.journal.id;
                var give_wallet_journal_content = $("[data-id='" + give_wallet_journal_id + "']");
                give_wallet_journal_content.addClass('oe_hidden');
            }
            // when seller change customer, if have wallet amount > 0, auto display journal method
            // else have not customer, or customer wallet small than 0, auto hide element jourmal
            // hide or not hide use wallet journal
            if (client && use_wallet_register) { //(client && client.wallet && use_wallet_register) {
                var journal_id = use_wallet_register.journal.id;
                var journal_content = $("[data-id='" + journal_id + "']");
                journal_content.removeClass('oe_hidden');
                journal_content.html('<span class="wallet">[ ' + client.name + " ] " + this.format_currency(client.wallet) + '</span>');
            } else {
                var journal_id = use_wallet_register.journal.id;
                var journal_content = $("[data-id='" + journal_id + "']");
                journal_content.addClass('oe_hidden');
            }
        },
        set_amount: function (value) {
            this._super(value);
            var order = this.pos.get_order();
            var selected_paymentline = order.selected_paymentline;
            var client = order.get_client();
            if (selected_paymentline && selected_paymentline['journal']['use_wallet']) {
                if (-selected_paymentline['amount'] > client['wallet']) {
                    selected_paymentline.destroy();
                    this.render_paymentlines();
                }
            }
        },
        click_paymentmethods: function (journal_id) {
            var self = this;
            var journal_selected = _.find(this.pos.journals, function (journal) {
                return journal['id'] == journal_id;
            })
            var order = this.pos.get_order();
            var client = order.get_client();
            if (journal_selected['use_wallet'] == true) {
                for (var i = 0; i < order.paymentlines.models.length; i++) { // clear all payment line the same journal
                    var payment_line = order.paymentlines.models[i];
                    if (payment_line['cashregister']['journal']['use_wallet'] == true) {
                        payment_line.destroy();
                    }
                }
                this._super(journal_id);
                var due = order.get_due();
                var wallet_customer = client['wallet'];
                var selected_paymentline = order.selected_paymentline;
                if (wallet_customer >= due) {
                    selected_paymentline.set_amount(due);
                } else {
                    selected_paymentline.set_amount(due);//wallet_customer);
                }
                this.order_changes();
                this.render_paymentlines();
            }
            if (journal_selected['give_wallet'] == true) {
                for (var i = 0; i < order.paymentlines.models.length; i++) { // clear all payment line the same journal
                    var payment_line = order.paymentlines.models[i];
                    if (payment_line['cashregister']['journal']['give_wallet'] == true) {
                        payment_line.destroy();
                    }
                }
                this._super(journal_id);
                var change = order.get_change();
                var wallet_customer = client['wallet'];
                var selected_paymentline = order.selected_paymentline;
                selected_paymentline.set_amount(-change);
                this.order_changes();
                this.render_paymentlines();
            }
            if (!journal_selected['give_wallet'] && !journal_selected['use_wallet']) {
                return this._super(journal_id);
            }
        },
    })
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_client: function (client) { // remove all paymentline is give wallet if cashiers change client
            var res = _super_order.set_client.apply(this, arguments);
            var paymentlines = this.paymentlines;
            for (var i = 0; i < paymentlines.models.length; i++) {
                if (paymentlines.models[i]['cashregister']['journal']['use_wallet']) {
                    paymentlines.models[i].destroy();
                }
            }
            return res;
        },
    })

    var _super_paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        set_amount: function (value) {
            var order = this.pos.get_order();
            var client = order.get_client();
            if (value == -0 && this.cashregister['journal']['give_wallet']) { // remove set amount when pos config use iface_precompute_cash is true [prefill]
                return;
            }
            if (value == 0 && this.cashregister['journal']['use_wallet']) { // remove set amount when pos config use iface_precompute_cash is true [prefill]
                return;
            }
            if (this.cashregister['journal']['use_wallet'] && client) { // change value when choice use wallet and iface_precompute_cash is true [prefill]
                var due = order.get_due();
                if (due <= client['wallet']) {
                    return _super_paymentline.set_amount.call(this, due);
                }
                if (due > client['wallet']) {
                    return  _super_paymentline.set_amount.call(this, due);//client['wallet']);
                }
            }
            _super_paymentline.set_amount.apply(this, arguments);
        },
    })
})
