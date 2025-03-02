from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import os
import re
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tiknew-real-estate-app-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# دالة مساعدة لتنسيق الأرقام والأسعار
@app.template_filter('format_price')
def format_price(value):
    try:
        value = float(value)
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value

# Load data from JSON files
def load_data(filename='db.json'):
    """Cargar datos desde un archivo JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Asegurar que todas las estructuras necesarias estén presentes
        if 'users' not in data:
            data['users'] = []
        if 'properties' not in data:
            data['properties'] = []
        if 'agents' not in data:
            data['agents'] = []
        if 'companies' not in data:
            data['companies'] = []
        if 'appointments' not in data:
            data['appointments'] = []
        if 'reviews' not in data:
            data['reviews'] = []
        if 'messages' not in data:
            data['messages'] = []
            
        # Asegurar que cada usuario tenga una lista de propiedades guardadas
        for user in data['users']:
            if 'saved_properties' not in user:
                user['saved_properties'] = []
                
        # Asegurar que cada mensaje tenga un campo is_read
        for message in data['messages']:
            if 'is_read' not in message:
                message['is_read'] = False
                
        return data
    except FileNotFoundError:
        # Si el archivo no existe, crear una estructura básica
        return {
            'users': [],
            'properties': [],
            'agents': [],
            'companies': [],
            'appointments': [],
            'reviews': [],
            'messages': []
        }
    except json.JSONDecodeError:
        # Si hay un error al decodificar el JSON, devolver una estructura básica
        return {
            'users': [],
            'properties': [],
            'agents': [],
            'companies': [],
            'appointments': [],
            'reviews': [],
            'messages': []
        }

# Save data to JSON files
def save_data(data, filename='db.json'):
    """Guardar datos en un archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Funciones auxiliares para cargar datos específicos
def load_users():
    """Cargar usuarios desde la base de datos"""
    data = load_data()
    return data.get('users', [])

def load_properties():
    """Cargar propiedades desde la base de datos"""
    data = load_data()
    return data.get('properties', [])

def load_agents():
    """Cargar agentes desde la base de datos"""
    data = load_data()
    return data.get('agents', [])

def load_companies():
    """Cargar compañías desde la base de datos"""
    data = load_data()
    return data.get('companies', [])

def load_appointments():
    """Cargar citas desde la base de datos"""
    data = load_data()
    return data.get('appointments', [])

def load_reviews():
    """Cargar reseñas desde la base de datos"""
    data = load_data()
    return data.get('reviews', [])

def load_messages():
    """Cargar mensajes desde la base de datos"""
    data = load_data()
    return data.get('messages', [])

# توفير متغير JavaScript لحالة تسجيل الدخول
@app.context_processor
def inject_user_status():
    return {
        'user_logged_in': True if g.user else False
    }

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Función para verificar si una solicitud es XHR (AJAX)
@app.before_request
def before_request():
    request.is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    g.user = session.get('user', None)

# تعديل الإعدادات لتجنب مشكلة "The message port closed before a response was received"
@app.after_request
def add_header(response):
    """
    إضافة headers لمنع مشاكل الكاش والاتصال
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Routes
@app.route('/')
def splash():
    if g.user:
        return redirect(url_for('index'))
    return render_template('splash.html')

@app.route('/home')
def index():
    properties = load_properties()
    agents = load_agents()
    return render_template('index.html', properties=properties, agents=agents)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # طباعة تصحيحية
        print(f"محاولة تسجيل دخول: {email}, تذكرني: {remember}")
        
        users = load_users()
        user_found = None
        
        for user in users:
            if user['email'] == email:
                user_found = user
                print(f"تم العثور على المستخدم: {user['name']}")
                break
        
        if not user_found:
            print("لم يتم العثور على المستخدم")
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة')
            return render_template('login.html')
            
        try:
            # للتجربة، نتحقق من كلمة المرور بطريقتين
            # 1. إذا كانت مخزنة بدون تشفير (للاختبار فقط)
            # 2. أو باستخدام check_password_hash للكلمات المشفرة
            
            password_matches = False
            
            # للحسابات الثلاثة المعروفة
            if (user_found['email'] == 'ahmed@example.com' and password == '123456') or \
               (user_found['email'] == 'sara@example.com' and password == '123456') or \
               (user_found['email'] == 'basem@hh.com' and password == '123456'):
                password_matches = True
            # للمسوق وشركة التطوير (كلمات مرور غير مشفرة)
            elif user_found['password'] == password:
                password_matches = True
            # للكلمات المشفرة
            elif check_password_hash(user_found['password'], password):
                password_matches = True
                
            if password_matches:
                # نسخة من المستخدم بدون كلمة المرور للجلسة
                session_user = user_found.copy()
                # التأكد من وجود saved_properties
                if 'saved_properties' not in session_user:
                    session_user['saved_properties'] = []
                session['user'] = session_user
                
                # إذا كان المستخدم اختار "تذكرني"، نضبط مدة صلاحية الجلسة إلى 30 يوم
                if remember:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=30)
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                print(f"كلمة المرور غير صحيحة للمستخدم: {user_found['email']}")
                flash('البريد الإلكتروني أو كلمة المرور غير صحيحة')
        except Exception as e:
            app.logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
            print(f"استثناء: {str(e)}")
            flash('حدث خطأ أثناء تسجيل الدخول. يرجى المحاولة مرة أخرى.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not name or not email or not password or not confirm_password:
            flash('جميع الحقول مطلوبة')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة')
            return render_template('register.html')
            
        # Check if email already exists
        users = load_users()
        for user in users:
            if user['email'] == email:
                flash('البريد الإلكتروني مستخدم بالفعل')
                return render_template('register.html')
        
        # Create new user
        data = load_data('db.json')
        users_data = data.get('users', [])
        
        # Generate unique ID
        user_id = str(len(users_data) + 1)
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create new user data
        new_user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': 'client',
            'saved_properties': []
        }
        
        # Add user to database
        users_data.append(new_user_data)
        data['users'] = users_data
        save_data(data, 'db.json')
        
        # Create User object and login
        session['user'] = new_user_data
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    properties = load_properties()
    
    # Filter properties based on search query
    if query:
        filtered_properties = []
        for property in properties:
            if (query.lower() in property['title'].lower() or 
                query.lower() in property['location'].lower() or
                query.lower() in property['description'].lower()):
                filtered_properties.append(property)
        properties = filtered_properties
    
    # Apply additional filters if provided
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    property_type = request.args.getlist('type')
    bedrooms = request.args.getlist('bedrooms')
    location = request.args.getlist('location')
    
    if min_price or max_price or property_type or bedrooms or location:
        filtered_properties = []
        for property in properties:
            include = True
            
            if min_price and int(property['price']) < int(min_price):
                include = False
            
            if max_price and int(property['price']) > int(max_price):
                include = False
            
            if property_type and property['type'] not in property_type:
                include = False
            
            if bedrooms and str(property['bedrooms']) not in bedrooms:
                include = False
            
            if location and property['location'] not in location:
                include = False
            
            if include:
                filtered_properties.append(property)
        
        properties = filtered_properties
    
    return render_template('search.html', properties=properties, query=query)

@app.route('/property/<property_id>')
def property_details(property_id):
    properties = load_properties()
    agents = load_agents()
    
    # Find property by ID
    property = None
    for p in properties:
        if p['id'] == property_id:
            property = p
            break
    
    if not property:
        flash('العقار غير موجود')
        return redirect(url_for('index'))
    
    # Find agent for this property
    agent = None
    for a in agents:
        if a['id'] == property['agent_id']:
            agent = a
            break
    
    return render_template('property_details.html', property=property, agent=agent)

@app.route('/book-appointment/<property_id>', methods=['GET', 'POST'])
def book_appointment_route(property_id):
    # التحقق من تسجيل الدخول
    if not g.user:
        # حفظ الصفحة المقصودة للعودة إليها بعد تسجيل الدخول
        session['next'] = url_for('book_appointment_route', property_id=property_id)
        flash('يرجى تسجيل الدخول أولاً لحجز موعد')
        return redirect(url_for('login'))
    
    # استكمال وظيفة حجز الموعد
    return book_appointment(property_id)

def book_appointment(property_id):
    if not g.user:
        flash('يرجى تسجيل الدخول لحجز موعد', 'error')
        return redirect(url_for('login'))
    
    properties = load_properties()
    property_data = next((p for p in properties if p['id'] == property_id), None)
    
    if not property_data:
        flash('العقار غير موجود', 'error')
        return redirect(url_for('index'))
    
    agents = load_agents()
    agent_data = next((a for a in agents if a['id'] == property_data['agent_id']), None)
    
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']
        
        # تحميل بيانات المواعيد
        db_data = load_data('db.json')
        appointments = db_data.get('appointments', [])
        
        # إنشاء معرف جديد
        appointment_ids = [a['id'] for a in appointments]
        new_id = 'appt' + str(len(appointments) + 1)
        while new_id in appointment_ids:
            # إذا كان المعرف موجودًا بالفعل، زد الرقم
            current_num = int(new_id.replace('appt', ''))
            new_id = 'appt' + str(current_num + 1)
        
        # إنشاء موعد جديد
        new_appointment = {
            'id': new_id,
            'client_name': g.user['name'],
            'client_phone': g.user.get('phone', ''),
            'property_id': property_id,
            'agent_id': property_data['agent_id'],
            'date': date,
            'time': time,
            'status': 'pending',
            'notes': notes,
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        
        # إضافة الموعد الجديد إلى قائمة المواعيد
        appointments.append(new_appointment)
        db_data['appointments'] = appointments
        
        # حفظ البيانات
        save_data(db_data, 'db.json')
        
        flash('تم حجز الموعد بنجاح، سيتم التواصل معك قريباً', 'success')
        return redirect(url_for('index'))
    
    # إضافة متغيرات التاريخ والوقت للقالب
    now = datetime.now()
    return render_template('book_appointment.html', property=property_data, agent=agent_data, now=now, timedelta=timedelta)

@app.route('/review-visit/<appointment_id>', methods=['GET', 'POST'])
@login_required
def review_visit(appointment_id):
    # تحميل بيانات المواعيد
    db_data = load_data('db.json')
    appointments = db_data.get('appointments', [])
    
    # البحث عن الموعد
    appointment_data = next((a for a in appointments if a['id'] == appointment_id), None)
    
    if not appointment_data:
        flash('الموعد غير موجود', 'error')
        return redirect(url_for('appointments'))
    
    # التحقق من أن الموعد يخص المستخدم الحالي
    if appointment_data['client_name'] != g.user['name']:
        flash('لا يمكنك الوصول إلى هذا الموعد', 'error')
        return redirect(url_for('appointments'))
    
    # تحميل بيانات العقار والمسوق
    properties = load_properties()
    property_data = next((p for p in properties if p['id'] == appointment_data['property_id']), None)
    
    agents = load_agents()
    agent_data = next((a for a in agents if a['id'] == appointment_data['agent_id']), None)
    
    # إعداد بيانات الموعد لعرضها في القالب
    appointment = {
        'id': appointment_data['id'],
        'date': appointment_data['date'],
        'time': appointment_data['time'],
        'status': appointment_data['status'],
        'property': property_data,
        'agent': agent_data
    }
    
    if request.method == 'POST':
        rating = float(request.form['rating'])
        comment = request.form['comment']
        public_review = 'public_review' in request.form
        
        # تحميل بيانات التقييمات
        reviews = db_data.get('reviews', [])
        
        # إنشاء معرف جديد
        new_id = str(int(reviews[-1]['id']) + 1) if reviews else "1"
        
        # إنشاء تقييم جديد
        new_review = {
            'id': new_id,
            'property_id': property_data['id'],
            'client_name': g.user['name'],
            'agent_id': agent_data['id'],
            'appointment_id': appointment_id,
            'rating': rating,
            'comment': comment,
            'public': public_review,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # إضافة التقييم الجديد إلى قائمة التقييمات
        reviews.append(new_review)
        db_data['reviews'] = reviews
        
        # تحديث حالة الموعد إلى "تم التقييم"
        for appt in appointments:
            if appt['id'] == appointment_id:
                appt['status'] = 'reviewed'
                break
        
        db_data['appointments'] = appointments
        
        # حفظ البيانات
        save_data(db_data, 'db.json')
        
        flash('تم إرسال تقييمك بنجاح، شكراً لمشاركة رأيك', 'success')
        return redirect(url_for('appointments'))
    
    return render_template('review_visit.html', appointment=appointment)

@app.route('/appointments')
@login_required
def appointments():
    # تحميل بيانات المواعيد
    db_data = load_data('db.json')
    appointments_data = db_data.get('appointments', [])
    
    # تصفية المواعيد حسب المستخدم الحالي
    user_appointments = [a for a in appointments_data if a.get('client_name') == g.user.get('name')]
    
    # تحميل بيانات العقارات والمسوقين
    properties = load_properties()
    agents = load_agents()
    
    # إعداد بيانات المواعيد لعرضها في القالب
    appointments = []
    for appointment in user_appointments:
        property_data = next((p for p in properties if p['id'] == appointment.get('property_id')), None)
        agent_data = next((a for a in agents if a['id'] == appointment.get('agent_id')), None)
        
        if property_data and agent_data:
            appointments.append({
                'id': appointment.get('id'),
                'date': appointment.get('date'),
                'status': appointment.get('status'),
                'property': property_data,
                'agent': agent_data
            })
    
    # ترتيب المواعيد حسب التاريخ (الأحدث أولاً)
    appointments.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('appointments.html', appointments=appointments)

@app.route('/cancel-appointment/<appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    # تحميل بيانات المواعيد
    db_data = load_data('db.json')
    appointments = db_data.get('appointments', [])
    
    # البحث عن الموعد
    appointment = next((a for a in appointments if a['id'] == appointment_id), None)
    
    if not appointment:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'الموعد غير موجود'})
        flash('الموعد غير موجود', 'error')
        return redirect(url_for('appointments'))
    
    # التحقق من أن الموعد يخص المستخدم الحالي
    if appointment['client_name'] != g.user['name']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'لا يمكنك إلغاء هذا الموعد'})
        flash('لا يمكنك إلغاء هذا الموعد', 'error')
        return redirect(url_for('appointments'))
    
    # تحديث حالة الموعد إلى "ملغي"
    for appt in appointments:
        if appt['id'] == appointment_id:
            appt['status'] = 'cancelled'
            property_id = appt['property_id']
            break
    
    db_data['appointments'] = appointments
    
    # حفظ البيانات
    save_data(db_data, 'db.json')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'تم إلغاء الموعد بنجاح', 'property_id': property_id})
    
    flash('تم إلغاء الموعد بنجاح', 'success')
    return redirect(url_for('appointments'))

@app.route('/messages')
@login_required
def messages():
    # Cargar datos
    data = load_data('db.json')
    current_user = g.user
    
    # Obtener todos los mensajes relacionados con el usuario actual
    user_messages = [m for m in data['messages'] if 
                     m['sender_id'] == current_user['id'] or 
                     m['receiver_id'] == current_user['id']]
    
    # Agrupar mensajes por conversación
    conversations = {}
    for message in user_messages:
        # Determinar el ID del otro usuario en la conversación
        other_user_id = message['sender_id'] if message['receiver_id'] == current_user['id'] else message['receiver_id']
        
        # Si esta conversación no existe en el diccionario, crearla
        if other_user_id not in conversations:
            conversations[other_user_id] = {
                'messages': [],
                'unread_count': 0
            }
        
        # Añadir mensaje a la conversación
        conversations[other_user_id]['messages'].append(message)
        
        # Contar mensajes no leídos
        if message['receiver_id'] == current_user['id'] and not message.get('is_read', False):
            conversations[other_user_id]['unread_count'] += 1
    
    # Obtener información de usuarios para cada conversación
    formatted_conversations = []
    for user_id, conv in conversations.items():
        # Buscar información del usuario
        other_user = next((u for u in data['users'] if u['id'] == user_id), None)
        if not other_user:
            continue
        
        # Ordenar mensajes por fecha y hora
        if conv['messages']:
            for message in conv['messages']:
                if 'timestamp' not in message:
                    # Si no existe timestamp, crear uno a partir de date y time
                    if 'date' in message and 'time' in message:
                        message['timestamp'] = f"{message['date']} {message['time']}"
                    else:
                        # Si no hay date o time, usar la fecha actual
                        message['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Asegurar que todos los campos necesarios estén presentes
                if 'sender_id' not in message:
                    message['sender_id'] = current_user['id']
                if 'text' not in message and 'image' not in message and 'location' not in message:
                    message['text'] = ""
            
            # Ahora ordenar los mensajes
            conv['messages'].sort(key=lambda x: x['timestamp'])
        
        # Obtener el último mensaje
        last_message = conv['messages'][-1] if conv['messages'] else None
        
        # Formatear la hora del último mensaje
        last_message_time = ""
        if last_message:
            try:
                timestamp = datetime.strptime(last_message['timestamp'], '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                
                # Si es hoy, mostrar solo la hora
                if timestamp.date() == now.date():
                    last_message_time = timestamp.strftime('%H:%M')
                # Si es ayer, mostrar "أمس"
                elif timestamp.date() == (now - timedelta(days=1)).date():
                    last_message_time = "أمس"
                # De lo contrario, mostrar la fecha
                else:
                    last_message_time = timestamp.strftime('%Y/%m/%d')
            except:
                last_message_time = last_message['timestamp']
        
        # Añadir conversación formateada
        formatted_conversations.append({
            'user': {
                'id': user_id,
                'name': other_user['name'],
                'image': other_user.get('image', ''),
                'online': False  # En una aplicación real, esto se determinaría dinámicamente
            },
            'last_message': {
                'text': last_message.get('text', ''),
                'image': last_message.get('image', None),
                'location': last_message.get('location', None),
                'time': last_message_time,
                'is_sent': last_message['sender_id'] == current_user['id'] if last_message else False
            },
            'unread_count': conv['unread_count']
        })
    
    # Ordenar conversaciones por la hora del último mensaje (más reciente primero)
    formatted_conversations.sort(key=lambda x: x['last_message']['time'], reverse=True)
    
    return render_template('messages.html', conversations=formatted_conversations)

@app.route('/favorites')
@login_required
def favorites():
    # Cargar propiedades guardadas por el usuario
    properties = load_properties()
    saved_properties = []
    
    # Filtrar propiedades guardadas por el usuario actual
    for property in properties:
        if int(property['id']) in g.user['saved_properties']:
            saved_properties.append(property)
    
    return render_template('favorites.html', properties=saved_properties)

@app.route('/profile')
@login_required
def profile():
    # Obtener información del usuario actual
    
    # Contar las citas del usuario
    db_data = load_data('db.json')
    appointments_data = db_data.get('appointments', [])
    user_appointments = [a for a in appointments_data if a.get('client_name') == g.user.get('name')]
    appointments_count = len(user_appointments)
    
    # Contar las reseñas del usuario
    reviews_data = db_data.get('reviews', [])
    user_reviews = [r for r in reviews_data if r.get('client_name') == g.user.get('name')]
    reviews_count = len(user_reviews)
    
    return render_template('profile.html', user=g.user, appointments_count=appointments_count, reviews_count=reviews_count)

@app.route('/transactions')
@login_required
def transactions():
    # تحميل بيانات قاعدة البيانات
    db_data = load_data('db.json')
    
    # تحميل بيانات المواعيد والتقييمات والعقارات والمسوقين
    appointments_data = db_data.get('appointments', [])
    reviews_data = db_data.get('reviews', [])
    properties = load_properties()
    agents = load_agents()
    
    # تصفية المواعيد والتقييمات حسب المستخدم الحالي
    user_appointments = [a for a in appointments_data if a['client_name'] == g.user['name']]
    user_reviews = [r for r in reviews_data if r['client_name'] == g.user['name']]
    
    # إنشاء قائمة بالعقارات التي تفاعل معها المستخدم
    property_interactions = {}
    
    # إضافة العقارات المحفوظة
    for prop_id in g.user['saved_properties']:
        property_id = str(prop_id)  # تحويل إلى نص إذا كان رقمًا
        if property_id not in property_interactions:
            property_interactions[property_id] = {
                'status': 'saved',
                'last_action_date': '',  # سيتم تحديثه لاحقًا
                'actions': [],
                'is_reviewed': False,
                'appointment_id': None
            }
    
    # إضافة المواعيد
    for appointment in user_appointments:
        property_id = appointment['property_id']
        appointment_date = appointment['date']
        
        if property_id not in property_interactions:
            property_interactions[property_id] = {
                'status': 'viewed',
                'last_action_date': appointment_date,
                'actions': [],
                'is_reviewed': False,
                'appointment_id': None
            }
        
        # تحديث الحالة بناءً على حالة الموعد
        if appointment['status'] == 'pending' or appointment['status'] == 'confirmed':
            property_interactions[property_id]['status'] = 'contacted'
        elif appointment['status'] == 'completed':
            property_interactions[property_id]['status'] = 'visited'
        elif appointment['status'] == 'reviewed':
            property_interactions[property_id]['status'] = 'reviewed'
            property_interactions[property_id]['is_reviewed'] = True
        
        # تحديث معرف الموعد للعقار
        property_interactions[property_id]['appointment_id'] = appointment['id']
        
        # إضافة إجراء للجدول الزمني
        action_text = ''
        if appointment['status'] == 'pending':
            action_text = 'تم حجز موعد لزيارة العقار'
        elif appointment['status'] == 'confirmed':
            action_text = 'تم تأكيد موعد الزيارة'
        elif appointment['status'] == 'completed':
            action_text = 'تمت زيارة العقار'
        elif appointment['status'] == 'reviewed':
            action_text = 'تم تقييم الزيارة'
        elif appointment['status'] == 'cancelled':
            action_text = 'تم إلغاء موعد الزيارة'
        
        if action_text:
            property_interactions[property_id]['actions'].append({
                'date': appointment_date,
                'text': action_text
            })
            
            # تحديث تاريخ آخر إجراء
            if not property_interactions[property_id]['last_action_date'] or appointment_date > property_interactions[property_id]['last_action_date']:
                property_interactions[property_id]['last_action_date'] = appointment_date
    
    # إضافة التقييمات
    for review in user_reviews:
        property_id = review['property_id']
        review_date = review['date']
        
        if property_id in property_interactions:
            # تحديث الحالة إلى "تم التقييم"
            property_interactions[property_id]['status'] = 'reviewed'
            property_interactions[property_id]['is_reviewed'] = True
            
            # إضافة إجراء للجدول الزمني
            property_interactions[property_id]['actions'].append({
                'date': review_date,
                'text': f'تم تقييم العقار بتقييم {review["rating"]} نجوم'
            })
            
            # تحديث تاريخ آخر إجراء
            if not property_interactions[property_id]['last_action_date'] or review_date > property_interactions[property_id]['last_action_date']:
                property_interactions[property_id]['last_action_date'] = review_date
    
    # إنشاء قائمة بالصفقات النهائية
    transactions = []
    
    for property_id, interaction in property_interactions.items():
        property_data = next((p for p in properties if p['id'] == property_id), None)
        
        if property_data:
            agent_id = property_data.get('agent_id')
            agent_data = next((a for a in agents if a['id'] == agent_id), None) if agent_id else None
            
            # إضافة العقار إلى القائمة
            transactions.append({
                'property': property_data,
                'agent': agent_data or {'name': 'غير معروف'},
                'status': interaction['status'],
                'last_action_date': interaction['last_action_date'],
                'actions': interaction['actions'],
                'is_reviewed': interaction['is_reviewed'],
                'appointment_id': interaction['appointment_id']
            })
    
    # ترتيب الصفقات حسب تاريخ آخر إجراء (الأحدث أولاً)
    transactions.sort(key=lambda x: x['last_action_date'], reverse=True)
    
    return render_template('transactions.html', transactions=transactions)

@app.route('/chat/<user_id>')
def chat(user_id):
    # التحقق من تسجيل الدخول
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # الحصول على بيانات المستخدم الحالي
    current_user = next((u for u in load_users() if u['id'] == session['user_id']), None)
    if not current_user:
        return redirect(url_for('login'))
    
    # الحصول على بيانات المستخدم الآخر
    receiver = next((u for u in load_users() if u['id'] == user_id), None)
    if not receiver:
        return redirect(url_for('messages'))
    
    # الحصول على المحادثة بين المستخدمين
    conversation_key = f"{current_user['id']}_{user_id}"
    alt_conversation_key = f"{user_id}_{current_user['id']}"
    
    # البحث عن المحادثة في قاعدة البيانات
    messages = []
    
    # فلترة الرسائل بين المستخدمين
    for message in load_messages():
        # التحقق من أن الرسالة بين المستخدمين المعنيين
        if ((message['sender_id'] == current_user['id'] and message['receiver_id'] == user_id) or
            (message['sender_id'] == user_id and message['receiver_id'] == current_user['id'])):
            
            # التأكد من وجود جميع الحقول المطلوبة
            if 'timestamp' not in message:
                if 'date' in message and 'time' in message:
                    message['timestamp'] = f"{message['date']} {message['time']}"
                else:
                    message['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            messages.append(message)
    
    # ترتيب الرسائل حسب التاريخ والوقت
    messages.sort(key=lambda x: x.get('timestamp', ''))
    
    # تحديث حالة قراءة الرسائل
    for message in messages:
        if message['sender_id'] == user_id and message.get('read', False) == False:
            message['read'] = True
    
    # حفظ التغييرات في قاعدة البيانات
    save_data(load_data(), 'db.json')
    
    # تنسيق الوقت الحالي للعرض
    now = datetime.now().strftime('%H:%M')
    
    return render_template('chat.html', receiver=receiver, messages=messages, now=now)

@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    if not request.is_xhr:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    data = load_data('db.json')
    current_user = g.user
    
    # Obtener datos del formulario
    chat_id = request.json.get('chat_id')
    message_text = request.json.get('message')
    image_data = request.json.get('image')
    location = request.json.get('location')
    
    if not chat_id:
        return jsonify({'success': False, 'message': 'Missing chat ID'})
    
    # Extraer IDs de usuario del chat_id
    user_ids = chat_id.split('-')
    if len(user_ids) != 2:
        return jsonify({'success': False, 'message': 'Invalid chat ID format'})
    
    try:
        user1_id = int(user_ids[0])
        user2_id = int(user_ids[1])
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid user IDs'})
    
    # Determinar el ID del destinatario
    receiver_id = user1_id if current_user['id'] == user2_id else user2_id
    
    # Verificar que el destinatario existe
    receiver = next((u for u in data['users'] if u['id'] == receiver_id), None)
    if not receiver:
        return jsonify({'success': False, 'message': 'Recipient not found'})
    
    # Crear nuevo mensaje
    new_message = {
        'id': max([m['id'] for m in data['messages']], default=0) + 1,
        'sender_id': current_user['id'],
        'receiver_id': receiver_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': False
    }
    
    # Agregar el contenido del mensaje según el tipo
    if message_text:
        new_message['text'] = message_text
    
    if image_data:
        new_message['image'] = image_data
    
    if location:
        new_message['location'] = location
    
    # Agregar el mensaje a la base de datos
    data['messages'].append(new_message)
    save_data(data, 'db.json')
    
    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/start-chat/<int:user_id>')
@login_required
def start_chat(user_id):
    # Redirigir a la página de chat con el ID proporcionado
    return redirect(url_for('chat', user_id=user_id))

@app.route('/api/send-message', methods=['POST'])
@login_required
def api_send_message():
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Se esperaba JSON'}), 400
    
    data = load_data('db.json')
    current_user = g.user
    
    # Obtener datos del formulario
    receiver_id = request.json.get('receiver_id')
    message_text = request.json.get('message')
    image_data = request.json.get('image')
    location = request.json.get('location')
    
    if not receiver_id or not message_text:
        return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400
    
    # Verificar que el destinatario existe
    receiver = next((u for u in data['users'] if u['id'] == receiver_id), None)
    if not receiver:
        return jsonify({'success': False, 'error': 'Recipient not found'}), 400
    
    # Crear nuevo mensaje
    new_message = {
        'id': max([m['id'] for m in data['messages']], default=0) + 1,
        'sender_id': current_user['id'],
        'receiver_id': receiver_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': False
    }
    
    # Agregar el contenido del mensaje según el tipo
    if message_text:
        new_message['text'] = message_text
    
    if image_data:
        new_message['image'] = image_data
    
    if location:
        new_message['location'] = location
    
    # Agregar el mensaje a la base de datos
    data['messages'].append(new_message)
    save_data(data, 'db.json')
    
    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/save-property/<property_id>', methods=['POST'])
@login_required
def save_property(property_id):
    if request.is_xhr:
        data = load_data('db.json')
        current_user = g.user
        
        # Buscar al usuario en la base de datos
        user_index = next((i for i, u in enumerate(data['users']) if u['id'] == current_user['id']), None)
        
        if user_index is None:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
        
        # Asegurarse de que el usuario tiene una lista de propiedades guardadas
        if 'saved_properties' not in data['users'][user_index]:
            data['users'][user_index]['saved_properties'] = []
        
        # Verificar si la propiedad ya está guardada
        saved_properties = data['users'][user_index]['saved_properties']
        property_id_int = int(property_id)
        
        if property_id_int in saved_properties:
            # Si ya está guardada, eliminarla
            data['users'][user_index]['saved_properties'].remove(property_id_int)
            is_saved = False
        else:
            # Si no está guardada, añadirla
            data['users'][user_index]['saved_properties'].append(property_id_int)
            is_saved = True
        
        # Actualizar la sesión del usuario
        session['user'] = data['users'][user_index]
        
        # Guardar cambios en la base de datos
        save_data(data, 'db.json')
        
        return jsonify({'success': True, 'is_saved': is_saved})
    
    return jsonify({'success': False, 'message': 'Solicitud inválida'})

@app.route('/property-management')
@login_required
def property_management():
    # Verificar si el usuario es un agente inmobiliario
    if g.user.get('role') != 'agent':
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # Cargar datos
    data = load_data()
    
    # Filtrar propiedades del agente actual
    agent_properties = [prop for prop in data['properties'] if prop.get('agent_id') == g.user.get('id')]
    
    # Calcular estadísticas
    active_properties = len([p for p in agent_properties if p.get('status') == 'active'])
    total_views = sum(p.get('views', 0) for p in agent_properties)
    total_inquiries = sum(p.get('inquiries', 0) for p in agent_properties)
    
    # Ordenar propiedades por fecha de creación (más recientes primero)
    agent_properties.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('property_management.html', 
                          properties=agent_properties,
                          active_properties=active_properties,
                          total_views=total_views,
                          total_inquiries=total_inquiries)

@app.route('/new_ad', methods=['GET', 'POST'])
def new_ad():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'agent':
        flash('يجب تسجيل الدخول كمسوق للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # استخراج بيانات النموذج
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        location = request.form.get('location')
        area = request.form.get('area')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        garages = request.form.get('garages')
        property_type = request.form.get('type')
        status = request.form.get('status')
        features = request.form.getlist('features')
        
        # التحقق من البيانات المطلوبة
        if not title or not description or not price or not location or not area:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('new_ad'))
        
        # قراءة ملف قاعدة البيانات
        with open('db.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # إنشاء معرف جديد للعقار
        new_id = str(int(max([int(prop['id']) for prop in data['properties']])) + 1)
        
        # إنشاء كائن العقار الجديد
        new_property = {
            "id": new_id,
            "title": title,
            "description": description,
            "price": int(price),
            "location": location,
            "area": int(area),
            "bedrooms": int(bedrooms) if bedrooms else 0,
            "bathrooms": int(bathrooms) if bathrooms else 0,
            "garages": int(garages) if garages else 0,
            "type": property_type,
            "status": status,
            "agent_id": g.user['id'],
            "views": 0,
            "inquiries": 0,
            "created_at": datetime.now().strftime('%Y-%m-%d'),
            "videos": [],
            "images": [],
            "features": features,
            "likes": 0,
            "comments": []
        }
        
        # إضافة العقار الجديد إلى قاعدة البيانات
        data['properties'].append(new_property)
        
        # حفظ التغييرات في ملف قاعدة البيانات
        with open('db.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        flash('تم إضافة العقار بنجاح', 'success')
        return redirect(url_for('agent_properties'))
    
    return render_template('new_ad.html')

@app.route('/analytics')
def analytics():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'agent':
        flash('يجب تسجيل الدخول كمسوق للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # فلترة العقارات التي يملكها المسوق الحالي
    agent_properties = [prop for prop in data['properties'] if prop['agent_id'] == g.user['id']]
    
    # إحصائيات عامة
    total_properties = len(agent_properties)
    total_views = sum(prop.get('views', 0) for prop in agent_properties)
    total_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties)
    
    # بيانات للرسوم البيانية
    property_views = [{'name': prop['title'], 'views': prop.get('views', 0)} for prop in agent_properties]
    property_inquiries = [{'name': prop['title'], 'inquiries': prop.get('inquiries', 0)} for prop in agent_properties]
    
    # تحليل الأداء حسب نوع العقار
    property_types = {}
    for prop in agent_properties:
        prop_type = prop['type']
        if prop_type not in property_types:
            property_types[prop_type] = {'count': 0, 'views': 0, 'inquiries': 0}
        property_types[prop_type]['count'] += 1
        property_types[prop_type]['views'] += prop.get('views', 0)
        property_types[prop_type]['inquiries'] += prop.get('inquiries', 0)
    
    return render_template('analytics.html', 
                           total_properties=total_properties,
                           total_views=total_views,
                           total_inquiries=total_inquiries,
                           property_views=property_views,
                           property_inquiries=property_inquiries,
                           property_types=property_types,
                           properties=agent_properties)

@app.route('/inquiries')
def inquiries():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'agent':
        flash('يجب تسجيل الدخول كمسوق للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # فلترة العقارات التي يملكها المسوق الحالي
    agent_properties = [prop for prop in data['properties'] if prop['agent_id'] == g.user['id']]
    
    # جمع جميع التعليقات والاستفسارات
    all_inquiries = []
    for prop in agent_properties:
        for comment in prop['comments']:
            # البحث عن معلومات المستخدم
            user_info = next((user for user in data['users'] if user['id'] == comment['user_id']), None)
            
            all_inquiries.append({
                'property_id': prop['id'],
                'property_title': prop['title'],
                'user_id': comment['user_id'],
                'user_name': user_info['name'] if user_info else 'مستخدم غير معروف',
                'text': comment['text'],
                'date': comment['date']
            })
    
    # ترتيب الاستفسارات حسب التاريخ (الأحدث أولاً)
    all_inquiries.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('inquiries.html', inquiries=all_inquiries)

@app.route('/availability_schedule', methods=['GET', 'POST'])
def availability_schedule():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'agent':
        flash('يجب تسجيل الدخول كمسوق للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # البحث عن المسوق الحالي
    agent = next((agent for agent in data['agents'] if agent['id'] == g.user['id']), None)
    
    if request.method == 'POST':
        # تحديث جدول التوفر
        availability_data = request.form.get('availability_data')
        
        if agent:
            # إضافة أو تحديث بيانات التوفر
            agent['availability'] = json.loads(availability_data)
            
            # حفظ التغييرات في ملف قاعدة البيانات
            with open('db.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            flash('تم تحديث جدول التوفر بنجاح', 'success')
        
        return redirect(url_for('availability_schedule'))
    
    # استخراج بيانات التوفر الحالية
    current_availability = agent.get('availability', {}) if agent else {}
    
    return render_template('availability_schedule.html', availability=current_availability)

@app.route('/performance_evaluation')
def performance_evaluation():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'agent':
        flash('يجب تسجيل الدخول كمسوق للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # فلترة العقارات التي يملكها المسوق الحالي
    agent_properties = [prop for prop in data['properties'] if prop['agent_id'] == g.user['id']]
    
    # حساب متوسط المشاهدات والاستفسارات
    avg_views = sum(prop.get('views', 0) for prop in agent_properties) / len(agent_properties) if agent_properties else 0
    avg_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties) / len(agent_properties) if agent_properties else 0
    
    # حساب معدل التحويل (نسبة مئوية من 100%)
    total_views = sum(prop.get('views', 0) for prop in agent_properties)
    total_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties)
    conversion_rate = (total_inquiries / total_views * 100) if total_views > 0 else 0
    
    # حساب متوسط الإعجابات
    avg_likes = sum(prop.get('likes', 0) for prop in agent_properties) / len(agent_properties) if agent_properties else 0
    
    # حساب عدد العقارات حسب الحالة
    status_counts = {}
    for prop in agent_properties:
        status = prop['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # تحليل الأداء حسب نوع العقار
    property_types = {}
    for prop in agent_properties:
        prop_type = prop['type']
        if prop_type not in property_types:
            property_types[prop_type] = {'count': 0, 'views': 0, 'inquiries': 0}
        property_types[prop_type]['count'] += 1
        property_types[prop_type]['views'] += prop.get('views', 0)
        property_types[prop_type]['inquiries'] += prop.get('inquiries', 0)
    
    # تحليل الأداء حسب المنطقة
    regions = {}
    for prop in agent_properties:
        region = prop['location']
        if region not in regions:
            regions[region] = {'count': 0, 'views': 0, 'inquiries': 0}
        regions[region]['count'] += 1
        regions[region]['views'] += prop.get('views', 0)
        regions[region]['inquiries'] += prop.get('inquiries', 0)
    
    return render_template('performance_evaluation.html', 
                           agent_properties=agent_properties,
                           avg_views=avg_views,
                           avg_inquiries=avg_inquiries,
                           conversion_rate=conversion_rate,
                           avg_likes=avg_likes,
                           status_counts=status_counts,
                           property_types=property_types,
                           regions=regions)

@app.route('/company/agents')
def company_agents():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'company':
        flash('يجب تسجيل الدخول كشركة تطوير عقاري للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # الحصول على معرف الشركة الحالية
    company_id = g.user['id']
    
    # الحصول على معلومات الشركة
    company = next((c for c in data['companies'] if c['id'] == company_id), None)
    
    if not company:
        flash('لم يتم العثور على معلومات الشركة', 'error')
        return redirect(url_for('index'))
    
    # الحصول على قائمة المسوقين التابعين للشركة
    company_agents = []
    for agent_id in company.get('agents', []):
        agent = next((a for a in data['agents'] if a['id'] == agent_id), None)
        if agent:
            # حساب مؤشر الأداء (نسبة مئوية من 100%)
            performance = 0
            agent_properties = [p for p in data['properties'] if p.get('agent_id') == agent_id]
            if agent_properties:
                total_views = sum(prop.get('views', 0) for prop in agent_properties)
                total_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties)
                # حساب تقريبي للأداء بناءً على المشاهدات والاستفسارات
                if total_views > 0:
                    performance = min(int((total_inquiries / total_views) * 1000), 100)
            
            # إضافة حالة المسوق (افتراضياً نشط)
            agent_data = {**agent, 'performance': performance, 'status': 'active'}
            company_agents.append(agent_data)
    
    # إحصائيات عامة
    total_agents = len(company_agents)
    active_agents = sum(1 for agent in company_agents if agent.get('status') == 'active')
    
    # حساب إجمالي العقارات
    total_properties = sum(len([p for p in data['properties'] if p.get('agent_id') == agent['id']]) for agent in company_agents)
    
    # حساب متوسط تقييم المسوقين
    avg_rating = 0
    if total_agents > 0:
        avg_rating = round(sum(agent.get('rating', 0) for agent in company_agents) / total_agents, 1)
    
    # تحويل بيانات المسوقين إلى تنسيق JSON للاستخدام في JavaScript
    agents_data = json.dumps(company_agents)
    
    return render_template('company_agents.html', 
                          company=company,
                          agents=company_agents,
                          agents_data=agents_data,
                          total_agents=total_agents,
                          active_agents=active_agents,
                          total_properties=total_properties,
                          avg_rating=avg_rating)

@app.route('/company/ads')
def company_ads():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'company':
        flash('يجب تسجيل الدخول كشركة تطوير عقاري للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # الحصول على معرف الشركة الحالية
    company_id = g.user['id']
    
    # الحصول على معلومات الشركة
    company = next((c for c in data['companies'] if c['id'] == company_id), None)
    
    if not company:
        flash('لم يتم العثور على معلومات الشركة', 'error')
        return redirect(url_for('index'))
    
    # الحصول على قائمة المسوقين التابعين للشركة
    company_agents_ids = company.get('agents', [])
    
    # جمع كل العقارات التي يديرها مسوقو الشركة
    company_properties = []
    total_views = 0
    total_inquiries = 0
    
    for agent_id in company_agents_ids:
        agent_properties = [p for p in data['properties'] if p['agent_id'] == agent_id]
        
        for prop in agent_properties:
            # إضافة العقار إلى القائمة
            prop_data = prop.copy()
            
            # إضافة التسميات العربية للنوع والحالة
            prop_data['type_label'] = {
                'villa': 'فيلا',
                'apartment': 'شقة',
                'penthouse': 'بنتهاوس',
                'land': 'أرض',
                'office': 'مكتب',
                'retail': 'محل تجاري'
            }.get(prop.get('type', ''), prop.get('type', ''))
            
            prop_data['status_label'] = {
                'active': 'نشط',
                'pending': 'قيد المراجعة',
                'sold': 'تم البيع'
            }.get(prop.get('status', ''), prop.get('status', ''))
            
            # حساب معدل التحويل لكل عقار
            prop_views = prop.get('views', 0)
            prop_inquiries = prop.get('inquiries', 0)
            prop_data['conversion_rate'] = round((prop_inquiries / prop_views * 100) if prop_views > 0 else 0, 1)
            
            # تجميع المشاهدات والاستفسارات
            total_views += prop_views
            total_inquiries += prop_inquiries
            
            company_properties.append(prop_data)
    
    # ترتيب العقارات حسب المشاهدات (تنازلياً)
    company_properties.sort(key=lambda x: x.get('views', 0), reverse=True)
    
    # حساب إجمالي العقارات
    total_properties = len(company_properties)
    
    # حساب معدل التحويل الإجمالي
    conversion_rate = round((total_inquiries / total_views * 100) if total_views > 0 else 0, 1)
    
    # إعداد بيانات الرسم البياني على مدار الأسبوع الماضي
    # في هذا المثال، سنقوم بإنشاء بيانات تجريبية
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14, -1, -1)]
    
    # بيانات مصطنعة للمشاهدات والاستفسارات
    views_data = {
        'labels': dates,
        'data': [random.randint(50, 200) for _ in range(15)]
    }
    
    inquiries_data = {
        'labels': dates,
        'data': [random.randint(5, 30) for _ in range(15)]
    }
    
    # تحويل كل البيانات إلى JSON للاستخدام في JavaScript
    property_data = json.dumps(company_properties)
    views_data = json.dumps(views_data)
    inquiries_data = json.dumps(inquiries_data)
    
    return render_template('company_ads.html', 
                           company=company,
                           properties=company_properties,
                           property_data=property_data,
                           total_properties=total_properties,
                           total_views=total_views,
                           total_inquiries=total_inquiries,
                           conversion_rate=conversion_rate,
                           views_data=views_data,
                           inquiries_data=inquiries_data)

@app.route('/company/reports')
def company_reports():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'company':
        flash('يجب تسجيل الدخول كشركة تطوير عقاري للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # الحصول على معرف الشركة الحالية
    company_id = g.user['id']
    
    # الحصول على معلومات الشركة
    company = next((c for c in data['companies'] if c['id'] == company_id), None)
    
    if not company:
        flash('لم يتم العثور على معلومات الشركة', 'error')
        return redirect(url_for('index'))
    
    # الحصول على قائمة المسوقين التابعين للشركة
    company_agents_ids = company.get('agents', [])
    
    # جمع جميع العقارات التي يديرها مسوقو الشركة
    company_properties = []
    total_views = 0
    total_inquiries = 0
    total_sales = 0
    
    for agent_id in company_agents_ids:
        agent_properties = [p for p in data['properties'] if p['agent_id'] == agent_id]
        
        # إضافة العقارات للقائمة المجمعة
        company_properties.extend(agent_properties)
        
        # تجميع المشاهدات والاستفسارات
        total_views += sum(prop.get('views', 0) for prop in agent_properties)
        total_inquiries += sum(prop.get('inquiries', 0) for prop in agent_properties)
        
        # حساب المبيعات (العقارات المباعة)
        sold_properties = [p for p in agent_properties if p.get('status') == 'sold']
        total_sales += sum(float(prop.get('price', 0)) for prop in sold_properties)
    
    # إحصائيات إضافية
    total_properties = len(company_properties)
    
    # حساب نسب النمو (قيم افتراضية)
    property_growth = round(random.uniform(5, 15), 1)
    sales_growth = round(random.uniform(-2, 20), 1)
    views_growth = round(random.uniform(10, 30), 1)
    inquiries_growth = round(random.uniform(-5, 15), 1)
    
    # تحليل الأداء حسب نوع العقار
    property_types = {}
    for prop in company_properties:
        prop_type = prop['type']
        if prop_type not in property_types:
            property_types[prop_type] = {'count': 0, 'views': 0, 'inquiries': 0, 'sales': 0}
        property_types[prop_type]['count'] += 1
        property_types[prop_type]['views'] += prop.get('views', 0)
        property_types[prop_type]['inquiries'] += prop.get('inquiries', 0)
        if prop.get('status') == 'sold':
            property_types[prop_type]['sales'] += 1
    
    # تحليل الأداء حسب المنطقة
    regions = {}
    for prop in company_properties:
        region = prop['location']
        if region not in regions:
            regions[region] = {'count': 0, 'views': 0, 'inquiries': 0, 'sales': 0}
        regions[region]['count'] += 1
        regions[region]['views'] += prop.get('views', 0)
        regions[region]['inquiries'] += prop.get('inquiries', 0)
        if prop.get('status') == 'sold':
            regions[region]['sales'] += 1
    
    # تحليل الأداء حسب المسوقين
    agents_performance = {}
    for agent_id in company_agents_ids:
        agent_properties = [p for p in data['properties'] if p['agent_id'] == agent_id]
        agent_views = sum(prop.get('views', 0) for prop in agent_properties)
        agent_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties)
        agent_sales = len([p for p in agent_properties if p.get('status') == 'sold'])
        
        agents_performance[agent_id] = {
            'views': agent_views,
            'inquiries': agent_inquiries,
            'sales': agent_sales
        }
    
    # تحويل البيانات إلى JSON للاستخدام في JavaScript
    market_trends = json.dumps({
        'labels': ['property_growth', 'sales_growth', 'views_growth', 'inquiries_growth'],
        'data': [property_growth, sales_growth, views_growth, inquiries_growth]
    })
    category_sales = json.dumps({
        'labels': list(property_types.keys()),
        'data': [property_types[prop_type]['sales'] for prop_type in property_types]
    })
    agent_performance = json.dumps({
        'labels': list(agents_performance.keys()),
        'data': [agents_performance[agent_id]['sales'] for agent_id in agents_performance]
    })
    heatmap_data = json.dumps({
        'labels': list(regions.keys()),
        'data': [regions[region]['sales'] for region in regions]
    })
    
    return render_template('company_reports.html', 
                           company=company,
                           total_properties=total_properties,
                           total_views=total_views,
                           total_inquiries=total_inquiries,
                           total_sales=total_sales,
                           property_growth=property_growth,
                           sales_growth=sales_growth,
                           views_growth=views_growth,
                           inquiries_growth=inquiries_growth,
                           market_trends=market_trends,
                           category_sales=category_sales,
                           agent_performance=agent_performance,
                           heatmap_data=heatmap_data)

@app.route('/company/appointments')
def company_appointments():
    if g.user is None or 'role' not in g.user or g.user['role'] != 'company':
        flash('يجب تسجيل الدخول كشركة تطوير عقاري للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('login'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # الحصول على معرف الشركة الحالية
    company_id = g.user['id']
    
    # الحصول على معلومات الشركة
    company = next((c for c in data['companies'] if c['id'] == company_id), None)
    
    if not company:
        flash('لم يتم العثور على معلومات الشركة', 'error')
        return redirect(url_for('index'))
    
    # الحصول على قائمة المسوقين التابعين للشركة
    company_agents_ids = company.get('agents', [])
    agents = []
    
    for agent_id in company_agents_ids:
        agent = next((a for a in data['agents'] if a['id'] == agent_id), None)
        if agent:
            agents.append(agent)
    
    # إنشاء قائمة بكل المواعيد المرتبطة بمسوقي الشركة
    appointments = []
    for appointment in data.get('appointments', []):
        if appointment.get('agent_id') in company_agents_ids:
            # الحصول على معلومات العقار والعميل
            property_info = None
            client_info = None
            
            for prop in data['properties']:
                if prop['id'] == appointment.get('property_id'):
                    property_info = {
                        'id': prop['id'],
                        'title': prop['title'],
                        'location': prop['location']
                    }
                    break
            
            for user in data['users']:
                if user['id'] == appointment.get('client_id'):
                    client_info = {
                        'id': user['id'],
                        'name': user['name'],
                        'phone': user.get('phone', '')
                    }
                elif user['id'] == appointment.get('agent_id'):
                    agent_info = {
                        'id': user['id'],
                        'name': user['name'],
                        'phone': user.get('phone', '')
                    }
            
            appointment_data = {
                'id': appointment.get('id'),
                'date': appointment.get('date'),
                'time': appointment.get('time'),
                'status': appointment.get('status'),
                'property': property_info,
                'client': client_info,
                'notes': appointment.get('notes', '')
            }
            
            # تحديد لون الموعد حسب حالته
            if appointment.get('status') == 'completed':
                appointment_data['color'] = '#4CAF50'  # أخضر
            elif appointment.get('status') == 'cancelled':
                appointment_data['color'] = '#F44336'  # أحمر
            else:
                appointment_data['color'] = '#2196F3'  # أزرق
            
            appointments.append(appointment_data)
    
    # تحويل بيانات المواعيد والمسوقين إلى JSON لاستخدامها في JavaScript
    appointments_data = json.dumps(appointments)
    agents_data = json.dumps(agents)
    
    return render_template('company_appointments.html', 
                          company=company,
                          appointments=appointments,
                          appointments_data=appointments_data,
                          agents=agents,
                          agents_data=agents_data)

@app.route('/api/appointments/create', methods=['POST'])
def create_appointment():
    if g.user is None or 'role' not in g.user:
        return jsonify({'status': 'error', 'message': 'يجب تسجيل الدخول لإنشاء موعد'}), 401
    
    # التحقق من صحة البيانات المرسلة
    data = request.get_json()
    
    required_fields = ['agent_id', 'property_id', 'date', 'client_name', 'client_phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'حقل {field} مطلوب'}), 400
    
    appointment_id = data.get('appointment_id')
    new_status = data.get('status')
    
    # التحقق من صحة الحالة
    if new_status not in ['scheduled', 'completed', 'cancelled']:
        return jsonify({'status': 'error', 'message': 'حالة غير صحيحة'})
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # إنشاء معرف جديد للموعد
    appointment_id = f"appt{len(db_data.get('appointments', [])) + 1}"
    
    # إنشاء الموعد الجديد
    new_appointment = {
        'id': appointment_id,
        'agent_id': data['agent_id'],
        'property_id': data['property_id'],
        'date': data['date'],
        'client_name': data['client_name'],
        'client_phone': data['client_phone'],
        'status': 'scheduled',
        'notes': data.get('notes', '')
    }
    
    # إضافة الموعد إلى قاعدة البيانات
    if 'appointments' not in db_data:
        db_data['appointments'] = []
    
    db_data['appointments'].append(new_appointment)
    
    # حفظ التغييرات في ملف قاعدة البيانات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)
    
    return jsonify({'status': 'success', 'message': 'تم إنشاء الموعد بنجاح', 'appointment': new_appointment})

# Route removed to avoid duplication - use get_agent_properties_api instead
def get_agent_properties(agent_id):
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # البحث عن جميع العقارات المرتبطة بالمسوق
    agent_properties = []
    for property_data in data.get('properties', []):
        if property_data.get('agent_id') == agent_id:
            # إضافة معلومات العقار
            agent_properties.append({
                'id': property_data.get('id'),
                'title': property_data.get('title'),
                'type': property_data.get('type'),
                'price': property_data.get('price'),
                'location': property_data.get('location')
            })
    
    return jsonify({'status': 'success', 'properties': agent_properties})

@app.route('/api/appointments/update-status', methods=['POST'])
def update_appointment_status():
    # التحقق من المستخدم وصلاحيته للوصول للصفحة
    if g.user is None or 'role' not in g.user or g.user['role'] not in ['company', 'admin', 'agent']:
        return jsonify({'status': 'error', 'message': 'غير مصرح لك بتعديل المواعيد'})
    
    # جلب بيانات الطلب
    data = request.get_json()
    
    # التحقق من وجود جميع البيانات المطلوبة
    if not data or 'appointment_id' not in data or 'status' not in data:
        return jsonify({'status': 'error', 'message': 'بيانات غير كاملة'})
    
    appointment_id = data.get('appointment_id')
    new_status = data.get('status')
    
    # التحقق من صحة الحالة
    if new_status not in ['scheduled', 'completed', 'cancelled']:
        return jsonify({'status': 'error', 'message': 'حالة غير صحيحة'})
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # البحث عن الموعد وتحديث حالته
    appointment_found = False
    for appointment in db_data.get('appointments', []):
        if appointment.get('id') == appointment_id:
            appointment['status'] = new_status
            appointment_found = True
            updated_appointment = appointment
            break
    
    if not appointment_found:
        return jsonify({'status': 'error', 'message': 'الموعد غير موجود'})
    
    # حفظ التغييرات في قاعدة البيانات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)
    
    return jsonify({'status': 'success', 'message': 'تم تحديث حالة الموعد بنجاح', 'appointment': updated_appointment})

@app.route('/api/agents/<agent_id>/performance', methods=['GET'])
def get_agent_performance(agent_id):
    if not g.user:
        return jsonify({'status': 'error', 'message': 'يرجى تسجيل الدخول'}), 401
    
    # التحقق من صلاحيات المستخدم
    if g.user.get('role') not in ['admin', 'company']:
        return jsonify({'status': 'error', 'message': 'ليس لديك صلاحيات كافية'}), 403
    
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # البحث عن المسوق
    agent = None
    for user in db.get('users', []):
        if user.get('id') == agent_id and user.get('role') == 'agent':
            # التحقق من صلاحية الوصول للمسوق إذا كان المستخدم من نوع شركة
            if g.user.get('role') == 'company' and user.get('company_id') != g.user.get('id'):
                return jsonify({'status': 'error', 'message': 'هذا المسوق ليس تابعاً لشركتك'}), 403
            
            agent = user
            break
    
    if not agent:
        return jsonify({'status': 'error', 'message': 'المسوق غير موجود'}), 404
    
    # جمع العقارات الخاصة بالمسوق
    agent_properties = [p for p in db.get('properties', []) if p.get('agent_id') == agent_id]
    
    # جمع المواعيد الخاصة بالمسوق
    agent_appointments = [a for a in db.get('appointments', []) if a.get('agent_id') == agent_id]
    
    # توزيع أنواع العقارات
    property_types = {}
    for prop in agent_properties:
        prop_type = prop.get('type', 'أخرى')
        property_types[prop_type] = property_types.get(prop_type, 0) + 1
    
    # توزيع المواعيد حسب الشهور (آخر 6 أشهر)
    months_data = {}
    today = datetime.now()
    for i in range(6):
        month = (today - timedelta(days=30 * i)).strftime('%Y-%m')
        months_data[month] = 0
    
    for appointment in agent_appointments:
        try:
            appointment_date = datetime.strptime(appointment.get('date', ''), '%Y-%m-%d')
            month_key = appointment_date.strftime('%Y-%m')
            if month_key in months_data:
                months_data[month_key] += 1
        except:
            continue
    
    # ترتيب بيانات الأشهر تصاعدياً
    monthly_appointments = []
    for month in sorted(months_data.keys()):
        month_name = datetime.strptime(month, '%Y-%m').strftime('%m/%Y')
        monthly_appointments.append({
            'month': month_name,
            'count': months_data[month]
        })
    
    # توزيع المواعيد حسب الحالة
    appointment_status = {
        'pending': 0,
        'confirmed': 0,
        'completed': 0,
        'cancelled': 0
    }
    
    for appointment in agent_appointments:
        status = appointment.get('status', 'pending')
        appointment_status[status] = appointment_status.get(status, 0) + 1
    
    # حساب معدل التحويل
    conversion_rate = 0
    if len(agent_appointments) > 0:
        conversion_rate = (appointment_status.get('completed', 0) / len(agent_appointments)) * 100
    
    # تجهيز البيانات للإرجاع
    performance_data = {
        'agent': {
            'id': agent.get('id'),
            'name': agent.get('name'),
            'email': agent.get('email'),
            'phone': agent.get('phone')
        },
        'stats': {
            'properties_count': len(agent_properties),
            'appointments_count': len(agent_appointments),
            'conversion_rate': round(conversion_rate, 1),
            'completed_deals': appointment_status.get('completed', 0)
        },
        'charts': {
            'property_types': [{'type': k, 'count': v} for k, v in property_types.items()],
            'monthly_appointments': monthly_appointments,
            'appointment_status': [{'status': k, 'count': v} for k, v in appointment_status.items()]
        }
    }
    
    return jsonify({
        'status': 'success',
        'data': performance_data
    })

@app.route('/api/agents/<agent_id>/assign-properties', methods=['POST'])
def assign_properties_to_agent(agent_id):
    if not g.user:
        return jsonify({'status': 'error', 'message': 'يرجى تسجيل الدخول'}), 401
    
    # التحقق من صلاحيات المستخدم
    if g.user.get('role') not in ['admin', 'company']:
        return jsonify({'status': 'error', 'message': 'ليس لديك صلاحيات كافية'}), 403
    
    # التحقق من وجود بيانات
    data = request.get_json()
    
    required_fields = ['property_ids']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'حقل {field} مطلوب'}), 400
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # البحث عن المسوق
    agent = None
    for user in db.get('users', []):
        if user.get('id') == agent_id and user.get('role') == 'agent':
            # التحقق من صلاحية الوصول للمسوق إذا كان المستخدم من نوع شركة
            if g.user.get('role') == 'company' and user.get('company_id') != g.user.get('id'):
                return jsonify({'status': 'error', 'message': 'هذا المسوق ليس تابعاً لشركتك'}), 403
            
            agent = user
            break
    
    if not agent:
        return jsonify({'status': 'error', 'message': 'المسوق غير موجود'}), 404
    
    # التحقق من وجود العقارات وإمكانية الوصول إليها
    property_ids = data['property_ids']
    property_access_error = False
    
    for prop_id in property_ids:
        property_found = False
        for prop in db.get('properties', []):
            if prop.get('id') == prop_id:
                # إذا كان المستخدم شركة، يجب أن تكون العقارات تابعة للشركة
                if g.user.get('role') == 'company' and prop.get('company_id') != g.user.get('id'):
                    property_access_error = True
                property_found = True
                break
        
        if not property_found:
            return jsonify({'status': 'error', 'message': f'العقار برقم {prop_id} غير موجود'}), 404
    
    if property_access_error:
        return jsonify({'status': 'error', 'message': 'بعض العقارات ليست تابعة لشركتك'}), 403
    
    # تعيين العقارات للمسوق
    for prop in db.get('properties', []):
        if prop.get('id') in property_ids:
            prop['agent_id'] = agent_id
    
    # حفظ التغييرات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    return jsonify({
        'status': 'success',
        'message': f'تم تعيين {len(property_ids)} عقار للمسوق بنجاح'
    })

@app.route('/api/agents/<agent_id>/properties', methods=['GET'])
def get_agent_properties_api(agent_id):
    """الحصول على قائمة العقارات الخاصة بمسوق معين"""
    try:
        properties = load_properties()
        
        # تصفية العقارات الخاصة بالمسوق المحدد
        agent_properties = [prop for prop in properties if prop.get('agent_id') == agent_id]
        
        # تصفية حسب الحالة إذا تم تحديدها
        status = request.args.get('status')
        if status:
            agent_properties = [prop for prop in agent_properties if prop.get('status') == status]
        
        # معلومات المسوق
        agents = load_agents()
        agent_info = next((agent for agent in agents if agent.get('id') == agent_id), None)
        
        if not agent_info:
            return jsonify({
                'status': 'error',
                'message': 'المسوق غير موجود'
            }), 404
        
        return jsonify({
            'status': 'success',
            'agent': {
                'id': agent_info.get('id'),
                'name': agent_info.get('name'),
                'email': agent_info.get('email'),
                'phone': agent_info.get('phone')
            },
            'count': len(agent_properties),
            'properties': agent_properties
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/appointments', methods=['GET'])
def get_agent_appointments_api():
    """الحصول على قائمة المواعيد الخاصة بمسوق معين"""
    try:
        appointments = load_appointments()
        
        # تصفية المواعيد الخاصة بالمسوق المحدد
        agent_appointments = [appt for appt in appointments if appt.get('agent_id') == agent_id]
        
        # تصفية حسب الحالة إذا تم تحديدها
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if status:
            agent_appointments = [appt for appt in agent_appointments if appt.get('status') == status]
        
        # تصفية حسب التاريخ
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                agent_appointments = [
                    appt for appt in agent_appointments 
                    if datetime.strptime(appt.get('date'), '%Y-%m-%d') >= date_from_obj
                ]
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                agent_appointments = [
                    appt for appt in agent_appointments 
                    if datetime.strptime(appt.get('date'), '%Y-%m-%d') <= date_to_obj
                ]
            except ValueError:
                pass
        
        # إضافة معلومات العقار والعميل لكل موعد
        properties = load_properties()
        users = load_users()
        
        detailed_appointments = []
        for appt in agent_appointments:
            property_info = next((prop for prop in properties if prop.get('id') == appt.get('property_id')), {})
            client_info = next((user for user in users if user.get('id') == appt.get('client_id')), {})
            
            detailed_appointment = appt.copy()
            detailed_appointment['property'] = {
                'id': property_info.get('id'),
                'title': property_info.get('title'),
                'location': property_info.get('location'),
                'price': property_info.get('price')
            }
            detailed_appointment['client'] = {
                'id': client_info.get('id'),
                'name': client_info.get('name'),
                'email': client_info.get('email'),
                'phone': client_info.get('phone')
            }
            
            detailed_appointments.append(detailed_appointment)
        
        return jsonify({
            'status': 'success',
            'count': len(detailed_appointments),
            'appointments': detailed_appointments
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Route removed to avoid duplication - use get_agent_properties_api instead
def get_agent_properties_legacy(agent_id):
    # هذه الوظيفة مكررة وتم استبدالها بـ get_agent_properties_api
    # تحويل الطلب إلى الوظيفة الجديدة
    return get_agent_properties_api(agent_id)

# تم إزالة هذا المسار لتجنب التكرار
def get_agent_properties_api(agent_id):
    """الحصول على قائمة العقارات الخاصة بمسوق معين"""
    try:
        # التحقق من وجود المسوق
        agent = get_agent_by_id(agent_id)
        if not agent:
            return jsonify({
                'status': 'error',
                'message': 'المسوق غير موجود'
            }), 404
        
        # التحقق من الصلاحيات
        if g.user.get('role') == 'agent' and g.user.get('id') != agent_id:
            return jsonify({
                'status': 'error',
                'message': 'ليس لديك صلاحية الوصول إلى عقارات مسوق آخر'
            }), 403
        
        if g.user.get('role') == 'company' and agent.get('company_id') != g.user.get('id'):
            return jsonify({
                'status': 'error',
                'message': 'هذا المسوق ليس تابع لشركتك'
            }), 403
        
        # الحصول على العقارات الخاصة بالمسوق
        properties = load_properties()
        status = request.args.get('status')
        
        agent_properties = []
        for prop in properties:
            if prop.get('agent_id') == agent_id:
                # فلترة حسب الحالة إذا تم تحديدها
                if status and prop.get('status') != status:
                    continue
                
                # إضافة العقار إلى القائمة
                agent_properties.append({
                    'id': prop.get('id'),
                    'title': prop.get('title'),
                    'type': prop.get('type'),
                    'price': prop.get('price'),
                    'location': prop.get('location')
                })
        
        return jsonify({'status': 'success', 'properties': agent_properties})
    except Exception as e:
        # تسجيل الخطأ
        app.logger.error(f"Error in get_agent_properties_api: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/settings')
@login_required
def settings():
    """صفحة إعدادات المستخدم والنظام"""
    if g.user.get('role') not in ['admin', 'company']:
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # تحميل إعدادات النظام من قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # استخراج إعدادات النظام أو إنشاء إعدادات افتراضية إذا لم تكن موجودة
    settings_data = db.get('settings', {})
    
    # تعيين القيم الافتراضية إذا لم تكن موجودة
    if not settings_data:
        settings_data = {
            'site_title': 'تيك توك العقاري',
            'contact_email': '',
            'google_maps_api': '',
            'currency': 'SAR',
            'language': 'ar',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d',
            'layout_style': 'default',
            'font_size': 'medium',
            'email_new_property': False,
            'email_appointment': False,
            'email_price_change': False,
            'app_messages': False,
            'app_appointment_reminder': False,
            'reminder_time': '1h'
        }
    
    return render_template('settings.html', settings=settings_data)

@app.route('/agents')
@login_required
def agents():
    """صفحة إدارة المسوقين"""
    if g.user.get('role') not in ['admin', 'company']:
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # قراءة ملف قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # الحصول على معرف الشركة الحالية
    company_id = g.user['id']
    
    # الحصول على معلومات الشركة
    company = next((c for c in data['companies'] if c['id'] == company_id), None)
    
    if not company:
        flash('لم يتم العثور على معلومات الشركة', 'error')
        return redirect(url_for('index'))
    
    # الحصول على قائمة المسوقين التابعين للشركة
    company_agents = []
    for agent_id in company.get('agents', []):
        agent = next((a for a in data['agents'] if a['id'] == agent_id), None)
        if agent:
            # حساب مؤشر الأداء (نسبة مئوية من 100%)
            performance = 0
            agent_properties = [p for p in data['properties'] if p['agent_id'] == agent_id]
            if agent_properties:
                total_views = sum(prop.get('views', 0) for prop in agent_properties)
                total_inquiries = sum(prop.get('inquiries', 0) for prop in agent_properties)
                # حساب تقريبي للأداء بناءً على المشاهدات والاستفسارات
                if total_views > 0:
                    performance = min(int((total_inquiries / total_views) * 1000), 100)
            
            # إضافة حالة المسوق (افتراضياً نشط)
            agent_data = {**agent, 'performance': performance, 'status': agent.get('status', 'active')}
            company_agents.append(agent_data)
    
    # إحصائيات عامة
    total_agents = len(company_agents)
    active_agents = sum(1 for agent in company_agents if agent.get('status') == 'active')
    
    # حساب إجمالي العقارات
    total_properties = sum(len([p for p in data['properties'] if p.get('agent_id') == agent['id']]) for agent in company_agents)
    
    # حساب متوسط تقييم المسوقين
    avg_rating = 0
    if total_agents > 0:
        avg_rating = round(sum(agent.get('rating', 0) for agent in company_agents) / total_agents, 1)
    
    # تحويل بيانات المسوقين إلى تنسيق JSON للاستخدام في JavaScript
    agents_data = json.dumps(company_agents)
    
    return render_template('company_agents.html', 
                          company=company,
                          agents=company_agents,
                          agents_data=agents_data,
                          total_agents=total_agents,
                          active_agents=active_agents,
                          total_properties=total_properties,
                          avg_rating=avg_rating)

@app.route('/save_system_settings', methods=['POST'])
@login_required
def save_system_settings():
    """حفظ إعدادات النظام"""
    if g.user.get('role') not in ['admin', 'company']:
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # تحديث الإعدادات
    if 'settings' not in db:
        db['settings'] = {}
    
    # تحديث إعدادات النظام
    db['settings']['site_title'] = request.form.get('site_title', 'تيك توك العقاري')
    db['settings']['contact_email'] = request.form.get('contact_email', '')
    db['settings']['google_maps_api'] = request.form.get('google_maps_api', '')
    db['settings']['currency'] = request.form.get('currency', 'SAR')
    db['settings']['language'] = request.form.get('language', 'ar')
    
    # حفظ التغييرات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    flash('تم حفظ إعدادات النظام بنجاح', 'success')
    return redirect(url_for('settings'))

@app.route('/save_ui_settings', methods=['POST'])
@login_required
def save_ui_settings():
    """حفظ إعدادات واجهة المستخدم"""
    if g.user.get('role') not in ['admin', 'company']:
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # تحديث الإعدادات
    if 'settings' not in db:
        db['settings'] = {}
    
    # تحديث إعدادات واجهة المستخدم
    db['settings']['primary_color'] = request.form.get('primary_color', '#0d6efd')
    db['settings']['secondary_color'] = request.form.get('secondary_color', '#6c757d')
    db['settings']['layout_style'] = request.form.get('layout_style', 'default')
    db['settings']['font_size'] = request.form.get('font_size', 'medium')
    
    # حفظ التغييرات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    flash('تم حفظ إعدادات واجهة المستخدم بنجاح', 'success')
    return redirect(url_for('settings'))

@app.route('/save_notification_settings', methods=['POST'])
@login_required
def save_notification_settings():
    """حفظ إعدادات الإشعارات"""
    if g.user.get('role') not in ['admin', 'company']:
        flash('لا تملك صلاحيات للوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # تحديث الإعدادات
    if 'settings' not in db:
        db['settings'] = {}
    
    # تحديث إعدادات الإشعارات
    db['settings']['email_new_property'] = 'email_new_property' in request.form
    db['settings']['email_appointment'] = 'email_appointment' in request.form
    db['settings']['email_price_change'] = 'email_price_change' in request.form
    db['settings']['app_messages'] = 'app_messages' in request.form
    db['settings']['app_appointment_reminder'] = 'app_appointment_reminder' in request.form
    db['settings']['reminder_time'] = request.form.get('reminder_time', '1h')
    
    # حفظ التغييرات
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    flash('تم حفظ إعدادات الإشعارات بنجاح', 'success')
    return redirect(url_for('settings'))

@app.route('/get_users')
@login_required
def get_users():
    """الحصول على قائمة المستخدمين"""
    if g.user.get('role') not in ['admin', 'company']:
        return jsonify({'status': 'error', 'message': 'لا تملك صلاحيات كافية'}), 403
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    users = []
    
    # تجميع المستخدمين من جميع الأنواع
    for role in ['admin', 'company', 'agent', 'client']:
        for user in db.get(role + 's', []):
            users.append({
                'id': user.get('id'),
                'name': user.get('name'),
                'username': user.get('username', ''),
                'email': user.get('email', ''),
                'role': role,
                'active': user.get('active', True)
            })
    
    return jsonify({
        'status': 'success',
        'users': users
    })

@app.route('/toggle_user_status/<user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """تغيير حالة المستخدم (نشط/غير نشط)"""
    if g.user.get('role') not in ['admin', 'company']:
        return jsonify({'status': 'error', 'message': 'لا تملك صلاحيات كافية'}), 403
    
    # تحميل قاعدة البيانات
    with open('db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # البحث عن المستخدم في جميع الأنواع
    user_found = False
    for role in ['admin', 'company', 'agent', 'client']:
        role_plural = role + 's'
        for user in db.get(role_plural, []):
            if user.get('id') == user_id:
                # تغيير حالة المستخدم
                current_status = user.get('active', True)
                user['active'] = not current_status
                user_found = True
                
                # حفظ التغييرات
                with open('db.json', 'w', encoding='utf-8') as f:
                    json.dump(db, f, ensure_ascii=False, indent=4)
                
                return jsonify({
                    'status': 'success',
                    'message': f'تم {("تعطيل" if current_status else "تفعيل")} المستخدم بنجاح'
                })
    
    if not user_found:
        return jsonify({
            'status': 'error',
            'message': 'المستخدم غير موجود'
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
