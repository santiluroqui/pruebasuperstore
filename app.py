# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import pandas as pd # Importar pandas para manipulación de datos
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy import func as sa_func # Importar func de SQLAlchemy para funciones SQL
from collections import defaultdict # Para agrupar datos

# --- Configuración de la aplicación Flask ---
app = Flask(__name__)
  
# Configuración de la base de datos para Flask-SQLAlchemy
# Considera usar variables de entorno para las credenciales en un entorno de producción
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123456@localhost:5432/superstore"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SUPERSTORE_SECRET_KEY_CAMBIAR_EN_PRODUCCION' # ¡ADVERTENCIA: Cambia esto por una clave segura en producción!

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # La vista a la que redirigir si no está autenticado

# --- Modelos ---
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Tamaño aumentado para hashes de contraseña

    def __repr__(self):
        return '<Usuario %r>' % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class SuperstoreSale(db.Model):
    __tablename__ = 'superstore_sales'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # autoincrement=True por defecto para PK Integer
    order_id = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.DateTime)
    ship_date = db.Column(db.DateTime)
    ship_mode = db.Column(db.String(50))
    customer_id = db.Column(db.String(50))
    customer_name = db.Column(db.String(100))
    segment = db.Column(db.String(50))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.Integer) 
    region = db.Column(db.String(50))
    product_id = db.Column(db.String(50))
    category = db.Column(db.String(50))
    sub_category = db.Column(db.String(50))
    product_name = db.Column(db.String(255))
    sales = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    discount = db.Column(db.Float)
    profit = db.Column(db.Float)

    def __repr__(self):
        return f"<SuperstoreSale Order: {self.order_id}, Product: {self.product_name}>"


# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# --- Rutas de Autenticación ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            flash('Ese nombre de usuario ya existe. Por favor, elige otro.', 'danger')
        else:
            new_user = Usuario(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))


# --- Dashboard General ---
@app.route('/dashboard')
@login_required
def dashboard():
    total_sales = db.session.query(sa_func.sum(SuperstoreSale.sales)).scalar()
    total_profit = db.session.query(sa_func.sum(SuperstoreSale.profit)).scalar()
    num_orders = db.session.query(sa_func.count(SuperstoreSale.order_id.distinct())).scalar()
    num_unique_customers = db.session.query(sa_func.count(SuperstoreSale.customer_id.distinct())).scalar()

    # Aunque el dashboard.html tiene un bloque de ventas recientes,
    # la idea es que las tablas en secciones específicas sean más interactivas.
    # Por ahora, mantenemos un ejemplo simple aquí.
    recent_sales = SuperstoreSale.query.order_by(SuperstoreSale.order_date.desc()).limit(10).all()

    return render_template('dashboard.html', 
                           total_sales=total_sales, 
                           total_profit=total_profit,
                           num_orders=num_orders,
                           num_unique_customers=num_unique_customers,
                           recent_sales=recent_sales)

# --- Rutas API para Gráficos del Dashboard General ---

@app.route('/api/sales_by_region')
@login_required
def api_sales_by_region():
    sales_data = db.session.query(
        SuperstoreSale.region,
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by(SuperstoreSale.region).order_by(sa_func.sum(SuperstoreSale.sales).desc()).all()
    
    data = [{'region': row.region, 'total_sales': float(row.total_sales)} for row in sales_data]
    return jsonify(data)

@app.route('/api/sales_trend')
@login_required
def api_sales_trend():
    sales_data = db.session.query(
        sa_func.to_char(SuperstoreSale.order_date, 'YYYY-MM').label('month'),
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by('month').order_by('month').all()

    data = [{'month': row.month, 'total_sales': float(row.total_sales)} for row in sales_data]
    return jsonify(data)

@app.route('/api/top_products')
@login_required
def api_top_products():
    top_10_products = db.session.query(
        SuperstoreSale.product_name,
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by(SuperstoreSale.product_name).order_by(sa_func.sum(SuperstoreSale.sales).desc()).limit(10).all()

    data = [{'product_name': row.product_name, 'total_sales': float(row.total_sales)} for row in top_10_products]
    return jsonify(data)

@app.route('/api/category_subcategory_sales')
@login_required
def api_category_subcategory_sales():
    sales_data = db.session.query(
        SuperstoreSale.category,
        SuperstoreSale.sub_category,
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by(SuperstoreSale.category, SuperstoreSale.sub_category).all()
    
    data = [{'category': row.category, 'sub_category': row.sub_category, 'total_sales': float(row.total_sales)} for row in sales_data]
    return jsonify(data)

# --- Nuevas Rutas para Secciones Específicas ---

@app.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html')

@app.route('/api/customers_data')
@login_required
def api_customers_data():
    # Datos para la tabla de clientes
    # Limitamos para no cargar una tabla enorme si hay muchos clientes
    customers = db.session.query(
        SuperstoreSale.customer_id,
        SuperstoreSale.customer_name,
        SuperstoreSale.segment,
        sa_func.count(SuperstoreSale.order_id.distinct()).label('total_orders'),
        sa_func.sum(SuperstoreSale.sales).label('total_sales'),
        sa_func.sum(SuperstoreSale.profit).label('total_profit')
    ).group_by(
        SuperstoreSale.customer_id,
        SuperstoreSale.customer_name,
        SuperstoreSale.segment
    ).order_by(sa_func.sum(SuperstoreSale.sales).desc()).limit(100).all() # Limitamos a 100 clientes

    data = [{
        'customer_id': c.customer_id,
        'customer_name': c.customer_name,
        'segment': c.segment,
        'total_orders': c.total_orders,
        'total_sales': float(c.total_sales),
        'total_profit': float(c.total_profit)
    } for c in customers]
    return jsonify({'data': data}) # DataTables espera un objeto con clave 'data'

@app.route('/api/orders_by_segment')
@login_required
def api_orders_by_segment():
    orders_by_segment = db.session.query(
        SuperstoreSale.segment,
        sa_func.count(SuperstoreSale.order_id.distinct()).label('order_count')
    ).group_by(SuperstoreSale.segment).all()

    data = [{'segment': row.segment, 'order_count': row.order_count} for row in orders_by_segment]
    return jsonify(data)

@app.route('/api/top_customers_by_sales')
@login_required
def api_top_customers_by_sales():
    top_customers = db.session.query(
        SuperstoreSale.customer_name,
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by(SuperstoreSale.customer_name).order_by(sa_func.sum(SuperstoreSale.sales).desc()).limit(10).all()

    data = [{'customer_name': row.customer_name, 'total_sales': float(row.total_sales)} for row in top_customers]
    return jsonify(data)


@app.route('/productos')
@login_required
def productos():
    return render_template('productos.html')

@app.route('/api/products_data')
@login_required
def api_products_data():
    products_data = db.session.query(
        SuperstoreSale.product_id,
        SuperstoreSale.product_name,
        SuperstoreSale.category,
        SuperstoreSale.sub_category,
        sa_func.sum(SuperstoreSale.quantity).label('total_quantity'),
        sa_func.sum(SuperstoreSale.sales).label('total_sales'),
        sa_func.sum(SuperstoreSale.profit).label('total_profit')
    ).group_by(
        SuperstoreSale.product_id,
        SuperstoreSale.product_name,
        SuperstoreSale.category,
        SuperstoreSale.sub_category
    ).order_by(sa_func.sum(SuperstoreSale.sales).desc()).limit(200).all() # Limitar por si hay muchos productos

    data = [{
        'product_id': p.product_id,
        'product_name': p.product_name,
        'category': p.category,
        'sub_category': p.sub_category,
        'total_quantity': p.total_quantity,
        'total_sales': float(p.total_sales),
        'total_profit': float(p.total_profit)
    } for p in products_data]
    return jsonify({'data': data})

@app.route('/api/profit_vs_sales_by_category')
@login_required
def api_profit_vs_sales_by_category():
    data = db.session.query(
        SuperstoreSale.category,
        sa_func.sum(SuperstoreSale.sales).label('total_sales'),
        sa_func.sum(SuperstoreSale.profit).label('total_profit')
    ).group_by(SuperstoreSale.category).all()
    
    result = [{'category': r.category, 'sales': float(r.total_sales), 'profit': float(r.total_profit)} for r in data]
    return jsonify(result)


@app.route('/regiones')
@login_required
def regiones():
    return render_template('regiones.html')

@app.route('/api/sales_profit_by_state')
@login_required
def api_sales_profit_by_state():
    data = db.session.query(
        SuperstoreSale.state,
        sa_func.sum(SuperstoreSale.sales).label('total_sales'),
        sa_func.sum(SuperstoreSale.profit).label('total_profit')
    ).group_by(SuperstoreSale.state).order_by(sa_func.sum(SuperstoreSale.sales).desc()).all()
    
    result = [{'state': r.state, 'sales': float(r.total_sales), 'profit': float(r.total_profit)} for r in data]
    return jsonify(result)

@app.route('/api/top_cities_by_sales')
@login_required
def api_top_cities_by_sales():
    data = db.session.query(
        SuperstoreSale.city,
        SuperstoreSale.state,
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by(SuperstoreSale.city, SuperstoreSale.state).order_by(sa_func.sum(SuperstoreSale.sales).desc()).limit(20).all()
    
    result = [{'city': r.city, 'state': r.state, 'sales': float(r.total_sales)} for r in data]
    return jsonify(result)


@app.route('/tiempo')
@login_required
def tiempo():
    return render_template('tiempo.html')

@app.route('/api/sales_by_year_month')
@login_required
def api_sales_by_year_month():
    sales_data = db.session.query(
        sa_func.extract('year', SuperstoreSale.order_date).label('year'),
        sa_func.extract('month', SuperstoreSale.order_date).label('month'),
        sa_func.to_char(SuperstoreSale.order_date, 'YYYY-MM').label('year_month'),
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by('year', 'month', 'year_month').order_by('year', 'month').all()

    data = [{'year': int(s.year), 'month': int(s.month), 'year_month': s.year_month, 'total_sales': float(s.total_sales)} for s in sales_data]
    return jsonify(data)

@app.route('/api/sales_by_day_of_week')
@login_required
def api_sales_by_day_of_week():
    sales_data = db.session.query(
        sa_func.extract('dow', SuperstoreSale.order_date).label('day_of_week'), # 0=Sunday, 1=Monday...
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by('day_of_week').order_by('day_of_week').all()

    # Mapear números a nombres de días
    day_names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    data = [{'day': day_names[int(s.day_of_week)], 'total_sales': float(s.total_sales)} for s in sales_data]
    return jsonify(data)

@app.route('/api/sales_heatmap')
@login_required
def api_sales_heatmap():
    # Datos para un heatmap de ventas por día de la semana y hora del día (si tu base de datos tiene datos de hora)
    # Por ahora, solo día del mes y mes
    sales_data = db.session.query(
        sa_func.extract('month', SuperstoreSale.order_date).label('month'),
        sa_func.extract('day', SuperstoreSale.order_date).label('day_of_month'),
        sa_func.sum(SuperstoreSale.sales).label('total_sales')
    ).group_by('month', 'day_of_month').order_by('month', 'day_of_month').all()

    # Formatear para un heatmap (ej. array de objetos {x, y, value})
    heatmap_data = []
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    for row in sales_data:
        heatmap_data.append({
            'month': month_names[int(row.month)-1],
            'day': int(row.day_of_month),
            'value': float(row.total_sales)
        })
    return jsonify(heatmap_data)


# --- Comandos CLI ---
@app.cli.command('create-admin')
def create_admin_command():
    """Crea un usuario administrador por defecto si no existe."""
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123') 

    with app.app_context(): 
        user = Usuario.query.filter_by(username=username).first()
        if not user:
            new_user = Usuario(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuario '{username}' creado con contraseña '{password}'.")
            print("¡ADVERTENCIA: Cambia la contraseña por defecto en producción!")
        else:
            print(f"Usuario '{username}' ya existe.")

# Para crear las tablas de la base de datos si no existen
@app.cli.command('create-db')
def create_db_command():
    """Crea las tablas de la base de datos."""
    with app.app_context():
        db.create_all()
        print("Tablas de la base de datos creadas.")


if __name__ == '__main__':
    # Es recomendable desactivar debug=True en producción
    app.run(debug=True)