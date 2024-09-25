from flask import Flask, jsonify, request, render_template
from datetime import date
import json

app = Flask(__name__)

FROM = " from "

class Product:

    def __init__(self, name, category):
        self.name = name.upper()
        self.category = category.upper()
        
        self.units = {'unit' : 1}
        self.purchase_history = []
        self.price = 0
        self.average_price = 0
        self.best_price = 0
        self.best_merchant = None

    def set_units(self, units):
        self.units.update(units)
    
    def add_unit(self, unit, size):
        self.units.update({unit : size})
    
    def adjust_price(self, new_price, merchant):
        self.price = new_price
        self.average_price = (self.average_price * (len(self.purchase_history) - 1) + new_price) / len(self.purchase_history)

        if new_price < self.best_price or self.best_price == 0:
            self.best_price = new_price
            self.best_merchant = merchant

    def __str__(self):
        return self.name
    
    def price_display(self):
        if len(self.purchase_history) == 0: return "NO HISTORY"
        return (str(self) + "\n\tBEST: $" + "{:>6.2f}".format(self.best_price) + FROM + str(self.best_merchant) +
                            "\n\tLAST: $" + "{:>6.2f}".format(self.price) + FROM + str(self.purchase_history[-1].merchant) +
                            "\n\tAVER: $" + "{:>6.2f}".format(self.average_price))

class Package(Product):

    def __init__(self, product, packname, size):
        super().__init__(product.name, product.category)
        self.product = product
        self.packname = packname.upper()
        self.size = size
    
    def adjust_price(self, new_price, merchant):
        self.price = new_price
        self.average_price = (self.average_price * (len(self.purchase_history) - 1) + new_price) / len(self.purchase_history)

        if new_price < self.best_price or self.best_price == 0:
            self.best_price = new_price
            self.best_merchant = merchant
        
        self.product.price = new_price / self.size
        self.product.average_price = (self.product.average_price * (len(self.product.purchase_history) - 1) + (new_price / self.size)) / len(self.product.purchase_history)

        if new_price / self.size < self.product.best_price or self.product.best_price == 0:
            self.product.best_price = new_price / self.size
            self.product.best_merchant = merchant
    
    def __str__(self):
        return self.packname+ " OF " + self.name + "S (" + str(self.size) + ")"

    def unit(self):
        return self.packname+ " OF " + self.name + "S (UNIT)"

    def price_display(self):
        if len(self.purchase_history) == 0: return "NO HISTORY"
        return (str(self) + "\n\tBEST: $" + "{:>6.2f}".format(self.best_price) + FROM + str(self.best_merchant) +
                            "\n\tLAST: $" + "{:>6.2f}".format(self.price) + FROM + str(self.purchase_history[-1].merchant) +
                            "\n\tAVER: $" + "{:>6.2f}".format(self.average_price))
    
    def unit_price_display(self):
        if len(self.purchase_history) == 0: return "NO HISTORY"
        return (self.unit() + "\n\tBEST: $" + "{:>6.2f}".format(self.best_price / self.size) + FROM + str(self.best_merchant) +
                              "\n\tLAST: $" + "{:>6.2f}".format(self.price / self.size) + FROM + str(self.purchase_history[-1].merchant) +
                              "\n\tAVER: $" + "{:>6.2f}".format(self.average_price / self.size))


class Merchant:

    def __init__(self, name, category='RETAIL'):
        self.name = name.upper()
        self.category = category.upper()

        self.catalog = {}
        self.transactions = []
    
    def __str__(self):
        return self.name

class Purchase:

    def __init__(self, product, merchant, price, quantity=1, unit='piece', variety='standard'):
        self.product = product
        self.merchant = merchant
        self.price = price
        self.quantity = quantity
        
        product.purchase_history.append(self)
        product.adjust_price(price / quantity, merchant)
        merchant.catalog[product] = price / quantity

        if type(product) is Package: 
            product.product.purchase_history.append(self)
            merchant.catalog[product.product] = (price / quantity) / product.size

    def __str__(self):
        return str(self.product) + " bought for $" + "{:>6.2f}".format(self.price / self.quantity) + FROM + str(self.merchant)
    
    def unit(self):
        if type(self.product) is Package: 
            return str(self.product.product) + " bought for $" + "{:>6.2f}".format((self.price / self.quantity) / self.product.size) + FROM + str(self.merchant) 
        else: 
            return str(self.product) + " bought for $" + "{:>6.2f}".format(self.price / self.quantity) + FROM + str(self.merchant)

class Transaction:

    def __init__(self, merchant, summary):
        self.merchant = merchant
        
        if isinstance(summary, list):
            self.add_up(summary)
        else:
            self.purchases = None
            self.total = summary
        merchant.transactions.append(self)

    def add_up(self, summary):
        self.total = 0
        self.purchases = summary
        for purchase in summary:
            self.total += purchase.price

@app.route('/add_transaction', methods=['GET'])
def add_transaction():
    prods = [p.lower() for p in products]
    merchs = [str(m) for m in merchants]
    units = {u : list(products[u].units.keys())[1:] for u in products}
    cats = [c for c in categories]
    cats_map = {u : products[u].category for u in products}
    return render_template('transaction.html', existing_product_names=prods, merchants=merchs, today=date.today(), units_map = units, categories=cats, cats_map=cats_map)

@app.route('/add_transaction', methods=['POST'])
def process_transaction():
    product_names = request.form.getlist('product_name[]')
    if product_names[0] != '':
        merchant = request.form['merchant']
        if merchant != "new":
            merchant = int(request.form['merchant'])
        else:
            merchants.append(Merchant(request.form['new_merchant_name'], request.form['new_merchant_category']))
            merchant = 0
        date = request.form['date']
        product_names = request.form.getlist('product_name[]')
        quantities = request.form.getlist('quantity[]')
        total_prices = request.form.getlist('total_price[]')
        units = request.form.getlist('unit[]')
        new_unit_names = request.form.getlist('new_unit_name[]')
        new_unit_sizes = request.form.getlist('new_unit_size[]')
        new_unit_defaults = request.form.getlist('new_unit_default[]')
        print('test', new_unit_defaults)
        cats = request.form.getlist('cat[]')
        purchases = []
        j = 0
        for i in range(len(product_names)):
            p = product_names[i].upper()
            q = int(quantities[i])
            t = float(total_prices[i])
            c = cats[i].upper()
            d = new_unit_defaults[i]
            if c == 'i':
                c = merchants[merchant].category
            if p in products:
                pass
            elif p[:-1] in products:
                p = p[:-1]
            elif p[:-2] in products:
                p = p[:-2]
            elif p + 'S' in products:
                products[p] = products[p + 'S']
                del products[p + 's']
            elif p + 'ES' in products:
                products[p] = products[p + 'ES']
                del products[p + 'ES']
            else:
                products.update({p: Product(p, c)})
            u = units[i].lower()
            if u == "new":
                u = new_unit_names[i].lower()
                if new_unit_sizes[i] == '':
                    curr = products[p]
                    if d == "1":
                        if('unit' in curr.units.keys()):
                            curr.set_units({u : 1})
                            del curr.units['unit']
                        else:
                            p1 = p + " " + u.upper()
                            products.update({p1: Product(p1, c)})
                            p2 = p + " " + list(curr.units.keys())[0]
                            products.update({p2: Product(p2, c)})
                            del curr
                    else: 
                        p = p + " " + u.upper()
                        products.update({p: Product(p, c)})
                        u = "unit"
                else:
                    products[p].add_unit(u, int(new_unit_sizes[i]))
            m = products[p].units[u]
            print(q, m)
            purchases.append(Purchase(products[p], merchants[merchant - 1], t, q * m))

    save_all()

    prods = [{'name':p, 'price':"{:.2f}".format(products[p].average_price),'category': products[p].category} for p in products]
    return render_template('products.html', products=prods)

def save_all():
    with open('products.csv', 'w') as f1:
        for p in products:
            f1.write(p.lower() + "," + products[p].category)
            for unit, size in products[p].units.items():
                f1.write("," + unit + "," + str(size))
            f1.write("\n")
        f1.close()
    
    with open('merchants.csv', 'w') as f2:
        for m in merchants:
            f2.write(m.name.lower() + "," + m.category.upper() + "\n")
        f2.close()

    with open('./static/products.json', 'w') as f3:
        f3.write(json.dumps(list(products.keys())))
        f3.close()

def extract_all():
    try:
        with open('products.csv', 'r') as f1:
            lines = f1.readlines()
            for l in lines:
                l = l.strip().split(',')
                name = l[0].strip().upper()
                category = l[1].strip().upper()
                categories.add(category)
                products[name.upper()] = Product(name, category)
                if len(l) > 2:
                    units = {l[i].strip().lower() : int(l[i+1].strip()) for i in range(2, len(l), 2)}
                    products[name].set_units(units)
            f1.close()

        with open('merchants.csv', 'r') as f2:
            lines = f2.readlines()
            for l in lines:
                l = l.strip().split(',')
                name = l[0].strip().upper()
                category = l[1].strip().upper()
                merchants.append(Merchant(name, category))
            f2.close()
    except:
        return

products = {}
merchants = []
categories = set()
if __name__ == '__main__':
    extract_all()
    print(products)
    print(merchants)
    print(categories)
    app.run(debug=False)