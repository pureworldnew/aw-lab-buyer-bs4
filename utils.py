from config import checkout_form


def create_form_data(name, surname, email, shipping_address_id):
    checkout_form_data = {
        'billing[aw_store_id]': '',
        'billing[firstname]': name,
        'billing[lastname]': surname,
        'billing[email]': email,
        'billing[telephone]': checkout_form['telephone'],
        'billing[country_id]': 'IT',
        'billing[street][]': checkout_form['address'],
        'billing[city]': checkout_form['city'],
        'billing[postcode]': checkout_form['zipcode'],
        'billing[region_id]': checkout_form['region_id'],  # region code
        'billing[region]': '',
        'billing[day]': checkout_form['birth_date'].split('/')[0],
        'billing[month]': checkout_form['birth_date'].split('/')[1],
        'billing[year]': checkout_form['birth_date'].split('/')[2],
        'billing[dob]': checkout_form['birth_date'],
        'billing[gender]': checkout_form['gender'],
        'billing[customer_password]': '',
        'billing[confirm_password]': '',
        'create_account': '',
        'billing[save_in_address_book]': 1,
        'billing[use_for_shipping]': 1,
        'shipping[aw_store_id]': '',
        'shipping[firstname]': '',
        'shipping[lastname]': '',
        'shipping[telephone]': '',
        'shipping[country_id]': 'IT',
        'shipping[street][]': '',
        'shipping[city]': '',
        'shipping[postcode]': '',
        'shipping[region_id]': '',
        'shipping[region]': '',
        'shipping[company]': '',
        'shipping[fax]': '',
        'shipping[save_in_address_book]': 1,
        'shipping[address_id]': shipping_address_id,
        'shipping_method': 'tablerate_bestway',
        'payment[method]': 'cashondelivery',
        'onestepcheckout-couponcode': '',
        'agreement[1]': 1
    }
    return checkout_form_data