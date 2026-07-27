import sklearn
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import numpy as np
import pandas as pd
import os

from datetime import datetime
from sklearn.linear_model import LinearRegression
from typing import Optional, List


# ==========================================================
# AI SMART INVENTORY & POS SYSTEM
# Version 2.0 Professional
# ==========================================================

app = FastAPI(
    title="AI Smart Inventory & POS System",
    description="Machine Learning Based Inventory Management",
    version="2.0"
)

templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_FOLDER),
    name="uploads"
)


# ==========================================================
# PRODUCT STATUS
# ==========================================================

STATUS_ACTIVE = "Active"
STATUS_FROZEN = "Frozen"
STATUS_OUT = "Out Of Stock"


# ==========================================================
# USER ROLES
# ==========================================================

ROLE_ADMIN = "Admin"
ROLE_SELLER = "Seller"


# ==========================================================
# SELLERS
# ==========================================================

Sellers = [

    {
        "id":1,
        "username":"admin",
        "password":"admin123",
        "role":ROLE_ADMIN,
        "name":"Administrator"
    },

    {
        "id":2,
        "username":"seller",
        "password":"seller123",
        "role":ROLE_SELLER,
        "name":"Main Seller"
    }

]


# ==========================================================
# INVENTORY DATABASE
# ==========================================================

Inventory = [

    {
        "id":1,

        "name":"Laptop Pro 15",

        "Stock":12,

        "Price":1299.0,

        "Sales":[10,14,18],

        "image":"",

        "status":STATUS_ACTIVE,

        "barcode":"100001",

        "category":"Laptop",

        "supplier":"Default",

        "created":datetime.now().strftime("%d-%m-%Y")
    },


    {
        "id":2,

        "name":"Wireless Headphones",

        "Stock":45,

        "Price":199.0,

        "Sales":[30,35,40],

        "image":"",

        "status":STATUS_ACTIVE,

        "barcode":"100002",

        "category":"Accessories",

        "supplier":"Default",

        "created":datetime.now().strftime("%d-%m-%Y")
    },


    {
        "id":3,

        "name":"Ergonomic Office Chair",

        "Stock":5,

        "Price":299.5,

        "Sales":[8,7,9],

        "image":"",

        "status":STATUS_ACTIVE,

        "barcode":"100003",

        "category":"Furniture",

        "supplier":"Default",

        "created":datetime.now().strftime("%d-%m-%Y")
    }

]


# ==========================================================
# SALES DATABASE
# ==========================================================

Sales = []


# ==========================================================
# CUSTOMERS DATABASE
# ==========================================================

Customers = []


# ==========================================================
# SALES HISTORY
# ==========================================================

SalesHistory = []


# ==========================================================
# SHOPPING CART
# ==========================================================

Cart = []


# ==========================================================
# INVOICE NUMBER
# ==========================================================

LastInvoice = 1000


# ==========================================================
# DASHBOARD COUNTERS
# ==========================================================

Dashboard = {

    "today_sales":0,

    "today_revenue":0,

    "today_profit":0,

    "customers":0,

    "alerts":0

}
# ==========================================================
# AI DEMAND PREDICTION
# ==========================================================

def predict_demand(sales_history):

    try:

        if len(sales_history) < 3:

            while len(sales_history) < 3:
                sales_history.append(sales_history[-1] if sales_history else 0)

        x = np.array([[1], [2], [3]])

        y = np.array(sales_history[-3:])

        model = LinearRegression()

        model.fit(x, y)

        prediction = model.predict([[4]])

        return max(
            0,
            int(round(prediction[0]))
        )

    except:

        return 0


# ==========================================================
# RESTOCK LIMIT
# ==========================================================

def get_restock_limit(price):

    if price >= 1000:
        return 20

    elif price >= 300:
        return 50

    else:
        return 100


# ==========================================================
# FIND PRODUCT
# ==========================================================

def find_product(product_id):

    for item in Inventory:

        if item["id"] == product_id:

            return item

    return None


# ==========================================================
# FIND PRODUCT BY BARCODE
# ==========================================================

def find_barcode(barcode):

    for item in Inventory:

        if item["barcode"] == barcode:

            return item

    return None


# ==========================================================
# GENERATE INVOICE
# ==========================================================

def generate_invoice():

    global LastInvoice

    LastInvoice += 1

    return f"INV-{LastInvoice:06d}"


# ==========================================================
# CART TOTAL
# ==========================================================

def cart_total():

    total = 0

    for item in Cart:

        total += item["subtotal"]

    return round(total, 2)


# ==========================================================
# INVENTORY VALUE
# ==========================================================

def inventory_value():

    value = 0

    for item in Inventory:

        value += item["Price"] * item["Stock"]

    return round(value, 2)


# ==========================================================
# TOTAL ACTIVE PRODUCTS
# ==========================================================

def total_active_products():

    total = 0

    for item in Inventory:

        if item["status"] == STATUS_ACTIVE:

            total += 1

    return total


# ==========================================================
# TOTAL FROZEN PRODUCTS
# ==========================================================

def total_frozen_products():

    total = 0

    for item in Inventory:

        if item["status"] == STATUS_FROZEN:

            total += 1

    return total


# ==========================================================
# LOW STOCK ALERTS
# ==========================================================

def total_alerts():

    alerts = 0

    for item in Inventory:

        if item["Stock"] <= get_restock_limit(item["Price"]):

            alerts += 1

    return alerts


# ==========================================================
# SLOW MOVING PRODUCTS
# ==========================================================

def slow_products():

    products = []

    for item in Inventory:

        prediction = predict_demand(item["Sales"])

        if prediction <= 5:

            products.append(item)

    return products


# ==========================================================
# BEST SELLING PRODUCTS
# ==========================================================

def best_products():

    data = sorted(

        Inventory,

        key=lambda x: sum(x["Sales"]),

        reverse=True

    )

    return data[:5]


# ==========================================================
# BUILD INVENTORY
# ==========================================================

def build_enriched_inventory(search=""):

    data = []

    for item in Inventory:

        prediction = predict_demand(item["Sales"])

        limit = get_restock_limit(item["Price"])

        status = item["status"]

        ai_message = "Healthy"

        if status == STATUS_FROZEN:

            ai_message = "Frozen Product"

        elif item["Stock"] <= limit:

            ai_message = "Restock Required"

        elif prediction >= item["Stock"]:

            ai_message = "High Demand"

        elif prediction <= 5:

            ai_message = "Slow Moving"

        data.append({

            **item,

            "predicted_demand": prediction,

            "restock_limit": limit,

            "AIStatus": ai_message

        })

    if search:

        data = [

            item

            for item in data

            if search.lower() in item["name"].lower()

        ]

    return data


# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

def dashboard_summary():

    Dashboard["today_sales"] = len(Sales)

    Dashboard["today_revenue"] = round(

        sum(

            sale["total"]

            for sale in Sales

        ),

        2

    )

    Dashboard["customers"] = len(Customers)

    Dashboard["alerts"] = total_alerts()

    Dashboard["today_profit"] = round(

        Dashboard["today_revenue"] * 0.30,

        2

    )

    return Dashboard


# ==========================================================
# HOME DASHBOARD
# ==========================================================

@app.get("/")
def index(
    request: Request,
    search: Optional[str] = ""
):

    inventory = build_enriched_inventory(search)

    dashboard = dashboard_summary()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "Inventory": inventory,
            "Dashboard": dashboard,
            "search": search,
            "total_products": len(Inventory),
            "total_value": inventory_value(),
            "alerts": total_alerts(),
            "active_products": total_active_products(),
            "frozen_products": total_frozen_products(),
            "best_products": best_products(),
            "slow_products": slow_products()
        }
    )
# ==========================================================
# SEARCH
# ==========================================================

@app.get("/search")
def search_products(
    request: Request,
    keyword: str = ""
):

    inventory = build_enriched_inventory(keyword)

    return templates.TemplateResponse(

        "index.html",

        {

            "request": request,

            "Inventory": inventory,

            "Dashboard": dashboard_summary(),

            "search": keyword,

            "total_products": len(Inventory),

            "total_value": inventory_value(),

            "alerts": total_alerts(),

            "active_products": total_active_products(),

            "frozen_products": total_frozen_products(),

            "best_products": best_products(),

            "slow_products": slow_products()

        }

    )


# ==========================================================
# ADD PRODUCT
# ==========================================================

@app.post("/add")
async def add_product(

    name: str = Form(...),

    stock: int = Form(...),

    price: float = Form(...),

    category: str = Form("General"),

    supplier: str = Form("Default"),

    barcode: str = Form(""),

    image: UploadFile = File(None)

):

    image_name = ""

    if image and image.filename:

        image_name = image.filename

        with open(

            os.path.join(

                UPLOAD_FOLDER,

                image_name

            ),

            "wb"

        ) as f:

            f.write(

                await image.read()

            )

    clean_name = name.strip()

    for item in Inventory:

        if item["name"].lower() == clean_name.lower():

            item["Stock"] += stock

            item["Price"] = price

            item["category"] = category

            item["supplier"] = supplier

            if barcode:

                item["barcode"] = barcode

            if image_name:
                item["image"] = image_name

            item["Sales"].append(stock)

            item["Sales"] = item["Sales"][-3:]

            return RedirectResponse(

                "/",

                status_code=303

            )

    new_id = max(

        [

            i["id"]

            for i in Inventory

        ],

        default=0

    ) + 1

    Inventory.append(

        {

            "id": new_id,

            "name": clean_name,

            "Stock": stock,

            "Price": price,

            "Sales": [stock, stock, stock],

            "image": image_name,

            "status": STATUS_ACTIVE,

            "barcode": barcode if barcode else str(100000 + new_id),

            "category": category,

            "supplier": supplier,

            "created": datetime.now().strftime("%d-%m-%Y")

        }

    )

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# UPDATE STOCK
# ==========================================================

@app.post("/update/{item_id}")
def update_stock(

    item_id: int,

    stock: int = Form(...)

):

    product = find_product(item_id)

    if product:

        product["Stock"] = max(

            0,

            stock

        )

        product["Sales"].append(

            stock

        )

        product["Sales"] = product["Sales"][-3:]

        if product["Stock"] == 0:

            product["status"] = STATUS_OUT

        elif product["status"] != STATUS_FROZEN:

            product["status"] = STATUS_ACTIVE

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# FREEZE PRODUCT
# ==========================================================

@app.get("/freeze/{item_id}")
def freeze_product(item_id: int):

    product = find_product(item_id)

    if product:

        product["status"] = STATUS_FROZEN

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# UNFREEZE PRODUCT
# ==========================================================

@app.get("/unfreeze/{item_id}")
def unfreeze_product(item_id: int):

    product = find_product(item_id)

    if product:

        if product["Stock"] > 0:

            product["status"] = STATUS_ACTIVE

        else:

            product["status"] = STATUS_OUT

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# DELETE PRODUCT
# ==========================================================

@app.get("/delete/{item_id}")
def delete_product(item_id: int):

    global Inventory

    Inventory = [

        item

        for item in Inventory

        if item["id"] != item_id

    ]

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# IMPORT PRODUCTS (CSV / EXCEL)
# ==========================================================

@app.post("/import")
async def import_products(
    file: UploadFile = File(...)
):

    filename = file.filename.lower()

    try:

        if filename.endswith(".csv"):

            df = pd.read_csv(file.file)

        elif filename.endswith(".xlsx"):

            df = pd.read_excel(file.file)

        else:

            return RedirectResponse("/", status_code=303)

    except Exception:

        return RedirectResponse("/", status_code=303)

    for _, row in df.iterrows():

        try:

            name = str(row["name"]).strip()

            stock = int(row["stock"])

            price = float(row["price"])

        except:

            continue

        duplicate = False

        for item in Inventory:

            if item["name"].lower() == name.lower():

                item["Stock"] += stock

                item["Price"] = price

                item["Sales"].append(stock)

                item["Sales"] = item["Sales"][-3:]

                duplicate = True

                break

        if duplicate:
            continue

        new_id = max([i["id"] for i in Inventory], default=0) + 1

        Inventory.append({

            "id": new_id,

            "name": name,

            "Stock": stock,

            "Price": price,

            "Sales": [stock, stock, stock],

            "image": "",

            "status": STATUS_ACTIVE,

            "barcode": str(100000 + new_id),

            "category": "Imported",

            "supplier": "CSV Import",

            "created": datetime.now().strftime("%d-%m-%Y")

        })

    return RedirectResponse("/", status_code=303)


# ==========================================================
# SELLER DASHBOARD
# ==========================================================

@app.get("/seller")
def seller_dashboard(request: Request):

    products = [

        item

        for item in build_enriched_inventory()

        if item["status"] != STATUS_FROZEN

    ]

    return templates.TemplateResponse(
        request=request,
        name="sale.html",
        context={
            "Inventory": products,
            "error": None
        }
    )

# ==========================================================
# CUSTOMER
# ==========================================================

def add_customer(customer_name):

    customer_name = customer_name.strip()

    if customer_name == "":

        customer_name = "Walk-in Customer"

    for customer in Customers:

        if customer["name"].lower() == customer_name.lower():

            customer["visits"] += 1

            customer["last_visit"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")

            return customer

    customer = {

        "id": len(Customers) + 1,

        "name": customer_name,

        "visits": 1,

        "total_purchase": 0,

        "last_visit": datetime.now().strftime("%d-%m-%Y %I:%M %p")

    }

    Customers.append(customer)

    return customer


# ==========================================================
# ADD TO CART
# ==========================================================

def add_to_cart(product, qty):

    subtotal = round(

        product["Price"] * qty,

        2

    )

    Cart.append({

        "product_id": product["id"],

        "name": product["name"],

        "qty": qty,

        "price": product["Price"],

        "subtotal": subtotal

    })


# ==========================================================
# CLEAR CART
# ==========================================================

def clear_cart():

    Cart.clear()


# ==========================================================
# UPDATE CUSTOMER PURCHASE
# ==========================================================

def update_customer_purchase(customer, amount):

    customer["total_purchase"] += amount


# ==========================================================
# STOCK VALIDATION
# ==========================================================

def stock_available(product, qty):

    if product["status"] == STATUS_FROZEN:

        return False

    if qty <= 0:

        return False

    if qty > product["Stock"]:

        return False

    return True


# ==========================================================
# REDUCE STOCK
# ==========================================================

def reduce_stock(product, qty):

    product["Stock"] -= qty

    product["Sales"].append(qty)

    product["Sales"] = product["Sales"][-3:]

    if product["Stock"] <= 0:

        product["Stock"] = 0

        product["status"] = STATUS_OUT



# ==========================================================
# POS CHECKOUT
# Professional Billing System
# ==========================================================

@app.post("/checkout")
async def checkout(

    request: Request,

    customer_name: str = Form(...),

    seller_name: str = Form("Main Seller"),

    product_id: List[int] = Form(...),

    quantity: List[int] = Form(...)

):

    clear_cart()

    customer = add_customer(customer_name)

    warnings = []

    grand_total = 0

    sold_items = 0

    for pid, qty in zip(product_id, quantity):

        product = find_product(pid)

        if product is None:

            continue

        if not stock_available(product, qty):

            warnings.append(

                f"{product['name']} stock not available."

            )

            continue

        add_to_cart(

            product,

            qty

        )

        reduce_stock(

            product,

            qty

        )

        grand_total += round(

            product["Price"] * qty,

            2

        )

        sold_items += qty

    if len(Cart) == 0:

        inventory = build_enriched_inventory()

        return templates.TemplateResponse(

            "sale.html",

            {

                "request": request,

                "Inventory": inventory,

                "error": "No product available for checkout."

            }

        )

    invoice = generate_invoice()

    update_customer_purchase(

        customer,

        grand_total

    )

    receipt = {

        "id": len(Sales) + 1,

        "invoice": invoice,

        "customer_name": customer["name"],

        "seller": seller_name,

        "items": Cart.copy(),

        "total_items": sold_items,

        "total": round(grand_total, 2),

        "date": datetime.now().strftime(

            "%d-%m-%Y %I:%M %p"

        ),

        "warnings": warnings

    }

    Sales.append(receipt)

    SalesHistory.append(receipt)

    clear_cart()

    return RedirectResponse(

        url=f"/receipt/{receipt['id']}",

        status_code=303

    )


# ==========================================================
# RECEIPT
# ==========================================================

@app.get("/receipt/{sale_id}")
def receipt_page(

    request: Request,

    sale_id: int

):

    receipt = next(

        (

            sale

            for sale in Sales

            if sale["id"] == sale_id

        ),

        None

    )

    return templates.TemplateResponse(

        "receipt.html",

        {

            "request": request,

            "receipt": receipt

        }

    )


# ==========================================================
# PRINT RECEIPT
# ==========================================================

@app.get("/print/{sale_id}")
def print_receipt(

    request: Request,

    sale_id: int

):

    receipt = next(

        (

            sale

            for sale in Sales

            if sale["id"] == sale_id

        ),

        None

    )

    return templates.TemplateResponse(

        "print_receipt.html",

        {

            "request": request,

            "receipt": receipt

        }

    )


# ==========================================================
# SALES HISTORY
# ==========================================================

@app.get("/sales")
def sales_history(

    request: Request

):

    revenue = round(

        sum(

            sale["total"]

            for sale in SalesHistory

        ),

        2

    )

    invoices = len(

        SalesHistory

    )

    products_sold = sum(

        sale["total_items"]

        for sale in SalesHistory

    )

    return templates.TemplateResponse(

        "sales_history.html",

        {

            "request": request,

            "Sales": list(

                reversed(

                    SalesHistory

                )

            ),

            "revenue": revenue,

            "invoice_count": invoices,

            "products_sold": products_sold

        }

    )

# ==========================================================
# AI ANALYTICS
# ==========================================================

def today_revenue():

    return round(

        sum(

            sale["total"]

            for sale in SalesHistory

        ),

        2

    )


def today_profit():

    profit = 0

    for sale in SalesHistory:

        profit += sale["total"] * 0.30

    return round(

        profit,

        2

    )


def total_units_sold():

    total = 0

    for sale in SalesHistory:

        total += sale["total_items"]

    return total


def total_customers():

    return len(Customers)


# ==========================================================
# TOP SELLING PRODUCTS
# ==========================================================

def top_selling_products():

    report = {}

    for sale in SalesHistory:

        for item in sale["items"]:

            if item["name"] not in report:

                report[item["name"]] = 0

            report[item["name"]] += item["qty"]

    result = []

    for name, qty in report.items():

        result.append({

            "name": name,

            "qty": qty

        })

    result.sort(

        key=lambda x: x["qty"],

        reverse=True

    )

    return result[:10]


# ==========================================================
# SLOW MOVING PRODUCTS
# ==========================================================

def slow_moving_products():

    data = []

    for item in Inventory:

        prediction = predict_demand(

            item["Sales"]

        )

        if prediction <= 5:

            data.append({

                "name": item["name"],

                "stock": item["Stock"],

                "prediction": prediction,

                "status": "Freeze Recommended"

            })

    return data


# ==========================================================
# LOW STOCK PRODUCTS
# ==========================================================

def low_stock_products():

    data = []

    for item in Inventory:

        if item["Stock"] <= get_restock_limit(

            item["Price"]

        ):

            data.append({

                "name": item["name"],

                "stock": item["Stock"],

                "required": get_restock_limit(

                    item["Price"]

                ),

                "status": "Restock Required"

            })

    return data


# ==========================================================
# DASHBOARD REPORT
# ==========================================================

@app.get("/dashboard")
def dashboard(

    request: Request

):

    return templates.TemplateResponse(

        "dashboard.html",

        {

            "request": request,

            "Inventory": build_enriched_inventory(),

            "customers": total_customers(),

            "revenue": today_revenue(),

            "profit": today_profit(),

            "units_sold": total_units_sold(),

            "alerts": total_alerts(),

            "active_products": total_active_products(),

            "frozen_products": total_frozen_products(),

            "best_products": top_selling_products(),

            "slow_products": slow_moving_products(),

            "low_stock": low_stock_products()

        }

    )


# ==========================================================
# DAILY REPORT
# ==========================================================

@app.get("/report")
def report(

    request: Request

):

    report_data = {

        "date": datetime.now().strftime(

            "%d-%m-%Y"

        ),

        "customers": total_customers(),

        "sales": len(SalesHistory),

        "revenue": today_revenue(),

        "profit": today_profit(),

        "units": total_units_sold(),

        "alerts": total_alerts(),

        "inventory_value": inventory_value()

    }

    return templates.TemplateResponse(

        "report.html",

        {

            "request": request,

            "report": report_data,

            "best_products": top_selling_products(),

            "slow_products": slow_moving_products(),

            "low_stock": low_stock_products()

        }

    )

# ==========================================================
# CUSTOMER SEARCH
# ==========================================================

def find_customer(customer_name):

    customer_name = customer_name.strip().lower()

    for customer in Customers:

        if customer["name"].lower() == customer_name:

            return customer

    return None


# ==========================================================
# BARCODE SEARCH
# ==========================================================

@app.get("/barcode/{barcode}")
def barcode_search(barcode: str):

    product = find_barcode(barcode)

    if product:

        return {

            "success": True,

            "product": product

        }

    return {

        "success": False

    }


# ==========================================================
# SELLER ACTIVITY
# ==========================================================

SellerActivity = []


def save_seller_activity(

    seller,

    customer,

    invoice,

    amount

):

    SellerActivity.append({

        "seller": seller,

        "customer": customer,

        "invoice": invoice,

        "amount": amount,

        "date": datetime.now().strftime(

            "%d-%m-%Y %I:%M %p"

        )

    })


# ==========================================================
# DISCOUNT
# ==========================================================

def calculate_discount(

    total,

    discount_percent

):

    discount = round(

        total * (discount_percent / 100),

        2

    )

    final_total = round(

        total - discount,

        2

    )

    return discount, final_total


# ==========================================================
# CASH RETURN
# ==========================================================

def calculate_change(

    cash,

    total

):

    if cash < total:

        return 0

    return round(

        cash - total,

        2

    )


# ==========================================================
# AI RESTOCK SUGGESTION
# ==========================================================

def ai_restock_recommendation():

    recommendations = []

    for product in Inventory:

        prediction = predict_demand(

            product["Sales"]

        )

        if prediction >= product["Stock"]:

            recommendations.append({

                "product": product["name"],

                "current_stock": product["Stock"],

                "expected_demand": prediction,

                "recommendation": max(

                    prediction * 2,

                    get_restock_limit(

                        product["Price"]

                    )

                )

            })

    return recommendations


# ==========================================================
# CUSTOMER HISTORY
# ==========================================================

@app.get("/customers")
def customer_history(

    request: Request

):

    return templates.TemplateResponse(

        "customers.html",

        {

            "request": request,

            "Customers": Customers

        }

    )


# ==========================================================
# SELLER HISTORY
# ==========================================================

@app.get("/seller/history")
def seller_history(

    request: Request

):

    return templates.TemplateResponse(

        "seller_history.html",

        {

            "request": request,

            "history": SellerActivity

        }

    )


# ==========================================================
# INVENTORY ANALYTICS
# ==========================================================

@app.get("/inventory/analytics")
def inventory_analytics(

    request: Request

):

    return templates.TemplateResponse(

        "inventory_analytics.html",

        {

            "request": request,

            "Inventory": build_enriched_inventory(),

            "recommendations": ai_restock_recommendation(),

            "low_stock": low_stock_products(),

            "slow_products": slow_moving_products(),

            "best_products": top_selling_products()

        }

    )


# ==========================================================
# EXPORT SALES (CSV)
# ==========================================================

@app.get("/export/sales")
def export_sales():

    df = pd.DataFrame(

        [

            {

                "Invoice": sale["invoice"],

                "Customer": sale["customer_name"],

                "Seller": sale["seller"],

                "Items": sale["total_items"],

                "Total": sale["total"],

                "Date": sale["date"]

            }

            for sale in SalesHistory

        ]

    )

    os.makedirs(

        "exports",

        exist_ok=True

    )

    filename = os.path.join(

        "exports",

        "sales_report.csv"

    )

    df.to_csv(

        filename,

        index=False

    )

    return RedirectResponse(

        "/sales",

        status_code=303

    )

# ==========================================================
# PRODUCT EDIT
# ==========================================================

@app.post("/product/edit/{item_id}")
async def edit_product(

    item_id: int,

    name: str = Form(...),

    stock: int = Form(...),

    price: float = Form(...),

    category: str = Form(...),

    supplier: str = Form(...),

    barcode: str = Form(...),

    image: UploadFile = File(None)

):

    product = find_product(item_id)

    if product is None:

        return RedirectResponse("/", status_code=303)

    product["name"] = name.strip()

    product["Stock"] = max(0, stock)

    product["Price"] = max(0, price)

    product["category"] = category.strip()

    product["supplier"] = supplier.strip()

    product["barcode"] = barcode.strip()

    if image and image.filename:

        filename = image.filename

        filepath = os.path.join(

            UPLOAD_FOLDER,

            filename

        )

        with open(filepath, "wb") as buffer:

            buffer.write(

                await image.read()

            )

        product["image"] = filename

    if product["Stock"] <= 0:

        product["status"] = STATUS_OUT

    elif product["status"] != STATUS_FROZEN:

        product["status"] = STATUS_ACTIVE

    return RedirectResponse("/", status_code=303)


# ==========================================================
# SUPPLIERS
# ==========================================================

Suppliers = [

    {

        "id":1,

        "name":"Default Supplier",

        "phone":"",

        "email":""

    }

]


@app.get("/suppliers")
def supplier_page(request: Request):

    return templates.TemplateResponse(

        "suppliers.html",

        {

            "request":request,

            "suppliers":Suppliers

        }

    )


@app.post("/supplier/add")
def add_supplier(

    name:str=Form(...),

    phone:str=Form(""),

    email:str=Form("")

):

    Suppliers.append(

        {

            "id":len(Suppliers)+1,

            "name":name,

            "phone":phone,

            "email":email

        }

    )

    return RedirectResponse(

        "/suppliers",

        status_code=303

    )


# ==========================================================
# CATEGORIES
# ==========================================================

def category_summary():

    summary={}

    for product in Inventory:

        cat=product["category"]

        summary.setdefault(cat,0)

        summary[cat]+=1

    return summary


@app.get("/categories")
def categories(request:Request):

    return templates.TemplateResponse(

        "categories.html",

        {

            "request":request,

            "categories":category_summary()

        }

    )


# ==========================================================
# MONTHLY SALES REPORT
# ==========================================================

@app.get("/monthly-report")
def monthly_report(request:Request):

    revenue=today_revenue()

    profit=today_profit()

    units=total_units_sold()

    return templates.TemplateResponse(

        "monthly_report.html",

        {

            "request":request,

            "revenue":revenue,

            "profit":profit,

            "units":units,

            "customers":total_customers(),

            "best_products":top_selling_products(),

            "slow_products":slow_moving_products()

        }

    )


# ==========================================================
# AI BUSINESS INSIGHTS
# ==========================================================

def ai_business_insights():

    insights=[]

    if total_alerts()>0:

        insights.append(

            "Restock low-stock products."

        )

    if len(

        slow_moving_products()

    )>0:

        insights.append(

            "Discount or Freeze slow moving products."

        )

    if today_revenue()>10000:

        insights.append(

            "Excellent sales performance today."

        )

    if total_customers()>50:

        insights.append(

            "Customer growth is increasing."

        )

    if len(insights)==0:

        insights.append(

            "Inventory is healthy."

        )

    return insights


@app.get("/ai")
def ai_page(request:Request):

    return templates.TemplateResponse(

        "ai.html",

        {

            "request":request,

            "insights":ai_business_insights(),

            "recommendations":ai_restock_recommendation(),

            "best_products":top_selling_products(),

            "slow_products":slow_moving_products()

        }

    )


# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

@app.get("/system")
def system_info():

    return {

        "application":"AI Smart Inventory & POS",

        "version":"2.0",

        "products":len(Inventory),

        "customers":len(Customers),

        "sales":len(SalesHistory),

        "suppliers":len(Suppliers),

        "inventory_value":inventory_value(),

        "revenue":today_revenue(),

        "profit":today_profit()

    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():

    return {

        "status":"Running",

        "server_time":datetime.now().strftime(

            "%d-%m-%Y %I:%M:%S %p"

        )

    }


# ==========================================================
# END OF APP
# ==========================================================

# ==========================================================
# FINAL PRODUCTION FIXES
# ADD THIS AT THE END OF app.py
# ==========================================================


# ==========================================================
# AUTO INVENTORY STATUS UPDATE
# ==========================================================

def refresh_inventory():

    for product in Inventory:

        if product["status"] == STATUS_FROZEN:
            continue

        if product["Stock"] <= 0:

            product["status"] = STATUS_OUT

        else:

            product["status"] = STATUS_ACTIVE


# ==========================================================
# AUTO AI UPDATE
# ==========================================================

def refresh_ai():

    refresh_inventory()

    dashboard_summary()


# ==========================================================
# PRODUCT STATISTICS
# ==========================================================

def inventory_statistics():

    total_stock = 0

    total_value = 0

    total_prediction = 0

    for product in Inventory:

        total_stock += product["Stock"]

        total_value += product["Stock"] * product["Price"]

        total_prediction += predict_demand(

            product["Sales"]

        )

    return {

        "products": len(Inventory),

        "stock": total_stock,

        "inventory_value": round(total_value, 2),

        "expected_sales": total_prediction

    }


# ==========================================================
# DAILY SALES SUMMARY
# ==========================================================

def sales_summary():

    invoices = len(SalesHistory)

    revenue = today_revenue()

    profit = today_profit()

    units = total_units_sold()

    avg = 0

    if invoices > 0:

        avg = round(

            revenue / invoices,

            2

        )

    return {

        "invoices": invoices,

        "revenue": revenue,

        "profit": profit,

        "units": units,

        "average_invoice": avg

    }


# ==========================================================
# AI HEALTH SCORE
# ==========================================================

def ai_health_score():

    score = 100

    score -= total_alerts() * 5

    score -= len(

        slow_moving_products()

    ) * 3

    if score < 0:

        score = 0

    return score


# ==========================================================
# SYSTEM ANALYTICS
# ==========================================================

@app.get("/analytics")
def analytics(request: Request):

    return templates.TemplateResponse(

        "analytics.html",

        {

            "request": request,

            "dashboard": dashboard_summary(),

            "inventory": inventory_statistics(),

            "sales": sales_summary(),

            "health": ai_health_score(),

            "recommendations": ai_restock_recommendation(),

            "best_products": top_selling_products(),

            "slow_products": slow_moving_products(),

            "low_stock": low_stock_products()

        }

    )


# ==========================================================
# RESET CART
# ==========================================================

@app.get("/cart/reset")
def reset_cart():

    clear_cart()

    return RedirectResponse(

        "/seller",

        status_code=303

    )


# ==========================================================
# RESET DEMO DATA
# ==========================================================

@app.get("/demo/reset")
def reset_demo():

    global Sales
    global SalesHistory
    global Customers
    global Cart

    Sales.clear()

    SalesHistory.clear()

    Customers.clear()

    Cart.clear()

    refresh_ai()

    return RedirectResponse(

        "/",

        status_code=303

    )


# ==========================================================
# APPLICATION STARTUP
# ==========================================================

@app.on_event("startup")
async def startup_event():

    refresh_ai()

    print("=" * 60)
    print(" AI SMART INVENTORY & POS SYSTEM")
    print("=" * 60)
    print(" Server Started Successfully")
    print(" Machine Learning Loaded")
    print(" Inventory Loaded :", len(Inventory))
    print(" Products Ready")
    print("=" * 60)


# ==========================================================
# APPLICATION SHUTDOWN
# ==========================================================

@app.on_event("shutdown")
async def shutdown_event():

    print("Saving Inventory...")

    print("Closing Application...")


# ==========================================================
# ROOT API STATUS
# ==========================================================

@app.get("/api/status")
def api_status():

    return {

        "success": True,

        "application": "AI Smart Inventory & POS",

        "version": "2.0 Professional",

        "machine_learning": True,

        "products": len(Inventory),

        "customers": len(Customers),

        "sales": len(SalesHistory),

        "health_score": ai_health_score()

    }


# ==========================================================
# END OF FILE
# ==========================================================
