import os
import io
import base64
import random
import string
from datetime import datetime, date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gowisata-uas-rpl-2026-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'gowisata.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

QR_DIR = os.path.join(BASE_DIR, 'static', 'qrcodes')
os.makedirs(QR_DIR, exist_ok=True)


# ------------------------------------------------------------------
# MODELS
# ------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, admin, owner
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(150), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    quota_per_day = db.Column(db.Integer, default=200)
    is_active = db.Column(db.Boolean, default=True)

    def bookings_count(self):
        return Booking.query.filter_by(destination_id=self.id).filter(Booking.status != 'pending').count()


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, used, cancelled
    qr_token = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    used_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='bookings')
    destination = db.relationship('Destination', backref='bookings')


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def gen_code(prefix='GW'):
    return prefix + '-' + ''.join(random.choices(string.digits, k=6))


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('login', next=request.path))
            if role and user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


@app.context_processor
def inject_user():
    return dict(current_user=current_user())


def make_qr(data, filename):
    img = qrcode.make(data, border=2)
    path = os.path.join(QR_DIR, filename)
    img.save(path)
    return filename


def rupiah(value):
    try:
        return 'Rp ' + f'{int(value):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return value


app.jinja_env.filters['rupiah'] = rupiah


# ------------------------------------------------------------------
# PUBLIC ROUTES
# ------------------------------------------------------------------
@app.route('/')
def index():
    featured = Destination.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', featured=featured)


@app.route('/destinasi')
def destinations():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    query = Destination.query.filter_by(is_active=True)
    if q:
        query = query.filter(Destination.name.ilike(f'%{q}%'))
    if category:
        query = query.filter_by(category=category)
    items = query.all()
    categories = sorted({d.category for d in Destination.query.all()})
    return render_template('destinations.html', items=items, categories=categories, q=q, category=category)


@app.route('/destinasi/<int:dest_id>')
def destination_detail(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    related = Destination.query.filter(Destination.id != dest.id, Destination.category == dest.category).limit(3).all()
    return render_template('destination_detail.html', dest=dest, related=related, today=date.today().isoformat())


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not name or not email or not password:
            flash('Semua field wajib diisi.', 'danger')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Konfirmasi kata sandi tidak cocok.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar. Silakan login.', 'danger')
            return redirect(url_for('register'))

        user = User(name=name, email=email, phone=phone, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Selamat datang, {user.name}!', 'success')
            nxt = request.args.get('next')
            if nxt:
                return redirect(nxt)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user.role == 'owner':
                return redirect(url_for('owner_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Email atau kata sandi salah.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('index'))


# ------------------------------------------------------------------
# BOOKING FLOW (user)
# ------------------------------------------------------------------
@app.route('/destinasi/<int:dest_id>/pesan', methods=['POST'])
@login_required(role='user')
def create_booking(dest_id):
    dest = Destination.query.get_or_404(dest_id)
    visit_date_str = request.form.get('visit_date')
    qty = int(request.form.get('qty', 1))
    try:
        visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Tanggal kunjungan tidak valid.', 'danger')
        return redirect(url_for('destination_detail', dest_id=dest_id))

    if visit_date < date.today():
        flash('Tanggal kunjungan tidak boleh di masa lalu.', 'danger')
        return redirect(url_for('destination_detail', dest_id=dest_id))
    if qty < 1 or qty > 20:
        flash('Jumlah tiket tidak valid (maks. 20).', 'danger')
        return redirect(url_for('destination_detail', dest_id=dest_id))

    booking = Booking(
        code=gen_code(),
        user_id=current_user().id,
        destination_id=dest.id,
        visit_date=visit_date,
        qty=qty,
        total_price=dest.price * qty,
        status='pending',
    )
    db.session.add(booking)
    db.session.commit()
    return redirect(url_for('payment', booking_id=booking.id))


@app.route('/pembayaran/<int:booking_id>', methods=['GET', 'POST'])
@login_required(role='user')
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user().id:
        abort(403)
    if request.method == 'POST':
        if booking.status == 'pending':
            booking.status = 'paid'
            booking.paid_at = datetime.utcnow()
            booking.qr_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))
            qr_payload = f'GOWISATA|{booking.code}|{booking.qr_token}'
            fname = f'{booking.code}.png'
            make_qr(qr_payload, fname)
            db.session.commit()
        flash('Pembayaran (simulasi) berhasil! E-tiket QR Code telah diterbitkan.', 'success')
        return redirect(url_for('ticket', booking_id=booking.id))
    return render_template('payment.html', booking=booking)


@app.route('/tiket/<int:booking_id>')
@login_required(role='user')
def ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user().id:
        abort(403)
    if booking.status not in ('paid', 'used'):
        flash('Tiket belum dibayar.', 'warning')
        return redirect(url_for('payment', booking_id=booking.id))
    return render_template('ticket.html', booking=booking)


@app.route('/dashboard')
@login_required(role='user')
def user_dashboard():
    user = current_user()
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    stats = {
        'total': len(bookings),
        'paid': len([b for b in bookings if b.status in ('paid', 'used')]),
        'used': len([b for b in bookings if b.status == 'used']),
        'pending': len([b for b in bookings if b.status == 'pending']),
    }
    return render_template('user_dashboard.html', bookings=bookings, stats=stats)


# ------------------------------------------------------------------
# ADMIN
# ------------------------------------------------------------------
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    total_dest = Destination.query.count()
    total_bookings = Booking.query.filter(Booking.status != 'pending').count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(Booking.status.in_(['paid', 'used'])).scalar() or 0
    pending_verif = Booking.query.filter_by(status='paid').count()
    recent = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()
    return render_template('admin_dashboard.html', total_dest=total_dest, total_bookings=total_bookings,
                            total_revenue=total_revenue, pending_verif=pending_verif, recent=recent)


@app.route('/admin/destinasi')
@login_required(role='admin')
def admin_destinations():
    items = Destination.query.all()
    return render_template('admin_destinations.html', items=items)


@app.route('/admin/destinasi/tambah', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_destination_add():
    if request.method == 'POST':
        d = Destination(
            name=request.form.get('name'),
            category=request.form.get('category'),
            location=request.form.get('location'),
            price=int(request.form.get('price', 0)),
            description=request.form.get('description'),
            image=request.form.get('image') or 'default.png',
            latitude=float(request.form.get('latitude', -7.6)),
            longitude=float(request.form.get('longitude', 110.4)),
            quota_per_day=int(request.form.get('quota_per_day', 200)),
        )
        db.session.add(d)
        db.session.commit()
        flash('Destinasi berhasil ditambahkan.', 'success')
        return redirect(url_for('admin_destinations'))
    return render_template('admin_destination_form.html', dest=None)


@app.route('/admin/destinasi/<int:dest_id>/edit', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_destination_edit(dest_id):
    d = Destination.query.get_or_404(dest_id)
    if request.method == 'POST':
        d.name = request.form.get('name')
        d.category = request.form.get('category')
        d.location = request.form.get('location')
        d.price = int(request.form.get('price', 0))
        d.description = request.form.get('description')
        d.quota_per_day = int(request.form.get('quota_per_day', 200))
        d.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('Destinasi berhasil diperbarui.', 'success')
        return redirect(url_for('admin_destinations'))
    return render_template('admin_destination_form.html', dest=d)


@app.route('/admin/destinasi/<int:dest_id>/hapus', methods=['POST'])
@login_required(role='admin')
def admin_destination_delete(dest_id):
    d = Destination.query.get_or_404(dest_id)
    db.session.delete(d)
    db.session.commit()
    flash('Destinasi dihapus.', 'info')
    return redirect(url_for('admin_destinations'))


@app.route('/admin/verifikasi', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_verify():
    result = None
    if request.method == 'POST':
        raw = request.form.get('qr_payload', '').strip()
        parts = raw.split('|')
        booking = None
        if len(parts) == 3 and parts[0] == 'GOWISATA':
            booking = Booking.query.filter_by(code=parts[1], qr_token=parts[2]).first()
        else:
            booking = Booking.query.filter_by(code=raw).first()

        if not booking:
            result = {'valid': False, 'message': 'Kode tiket tidak ditemukan.'}
        elif booking.status == 'used':
            result = {'valid': False, 'message': f'Tiket sudah digunakan pada {booking.used_at.strftime("%d-%m-%Y %H:%M")}.', 'booking': booking}
        elif booking.status != 'paid':
            result = {'valid': False, 'message': 'Tiket belum dibayar / tidak valid.', 'booking': booking}
        else:
            booking.status = 'used'
            booking.used_at = datetime.utcnow()
            db.session.commit()
            result = {'valid': True, 'message': 'Tiket VALID. Selamat berwisata!', 'booking': booking}
    return render_template('admin_verify.html', result=result)


@app.route('/admin/transaksi')
@login_required(role='admin')
def admin_transactions():
    status = request.args.get('status', '')
    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin_transactions.html', items=items, status=status)


# ------------------------------------------------------------------
# OWNER
# ------------------------------------------------------------------
@app.route('/owner')
@login_required(role='owner')
def owner_dashboard():
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(Booking.status.in_(['paid', 'used'])).scalar() or 0
    total_visitors = db.session.query(db.func.sum(Booking.qty)).filter(Booking.status.in_(['paid', 'used'])).scalar() or 0
    total_bookings = Booking.query.filter(Booking.status.in_(['paid', 'used'])).count()

    dest_stats = []
    for d in Destination.query.all():
        rev = db.session.query(db.func.sum(Booking.total_price)).filter(
            Booking.destination_id == d.id, Booking.status.in_(['paid', 'used'])).scalar() or 0
        visitors = db.session.query(db.func.sum(Booking.qty)).filter(
            Booking.destination_id == d.id, Booking.status.in_(['paid', 'used'])).scalar() or 0
        dest_stats.append({'name': d.name, 'revenue': rev, 'visitors': visitors})
    dest_stats.sort(key=lambda x: x['revenue'], reverse=True)

    # monthly trend (based on paid_at month)
    monthly = {}
    paid_bookings = Booking.query.filter(Booking.status.in_(['paid', 'used'])).all()
    for b in paid_bookings:
        if b.paid_at:
            key = b.paid_at.strftime('%Y-%m')
            monthly.setdefault(key, {'revenue': 0, 'visitors': 0})
            monthly[key]['revenue'] += b.total_price
            monthly[key]['visitors'] += b.qty
    monthly_sorted = sorted(monthly.items())

    return render_template('owner_dashboard.html', total_revenue=total_revenue, total_visitors=total_visitors,
                            total_bookings=total_bookings, dest_stats=dest_stats, monthly=monthly_sorted)


# ------------------------------------------------------------------
# ERROR HANDLERS
# ------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Anda tidak memiliki akses ke halaman ini.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Halaman tidak ditemukan.'), 404


# ------------------------------------------------------------------
# SEED DATA
# ------------------------------------------------------------------
def seed_data():
    db.create_all()
    if User.query.count() > 0:
        return

    admin = User(name='Admin GoWisata', email='admin@gowisata.id', role='admin', phone='081200000001')
    admin.set_password('admin123')
    owner = User(name='Owner Dinas Pariwisata', email='owner@gowisata.id', role='owner', phone='081200000002')
    owner.set_password('owner123')
    demo = User(name='yoga pratama', email='yoga@gowisata.id', role='user', phone='081200000003')
    demo.set_password('user123')
    db.session.add_all([admin, owner, demo])

    destinations = [
        dict(name='Kaliurang', category='Pegunungan', location='Kaliurang, Sleman',
             price=15000, image='kaliurang.png', latitude=-7.5975, longitude=110.4306,
             description='Kawasan wisata pegunungan sejuk di lereng Gunung Merapi dengan udara segar, taman rekreasi keluarga, dan area outbound.'),
        dict(name='Lava Tour Merapi (Kaliadem)', category='Petualangan', location='Kaliadem, Cangkringan, Sleman',
             price=150000, image='lava_tour.png', latitude=-7.5766, longitude=110.4453,
             description='Petualangan menyusuri jalur lahar Gunung Merapi menggunakan jeep, melintasi Bunker Kaliadem dan Museum Sisa Hartaku.'),
        dict(name='Tlogo Putri Kaliurang', category='Pegunungan', location='Kaliurang, Sleman',
             price=10000, image='tlogo_putri.png', latitude=-7.5989, longitude=110.4288,
             description='Danau kecil yang asri di kaki Merapi, cocok untuk piknik keluarga, berperahu santai, dan menikmati suasana pegunungan.'),
        dict(name='Museum Ullen Sentalu', category='Budaya', location='Kaliurang, Sleman',
             price=50000, image='ullen_sentalu.png', latitude=-7.5981, longitude=110.4262,
             description='Museum budaya Jawa yang menyimpan koleksi kesenian dan sejarah keraton Mataram, dengan arsitektur unik dan suasana teduh.'),
        dict(name='Candi Prambanan', category='Budaya', location='Prambanan, Sleman',
             price=50000, image='prambanan.png', latitude=-7.7520, longitude=110.4914,
             description='Kompleks candi Hindu terbesar di Indonesia, warisan dunia UNESCO dengan arsitektur menjulang yang megah.'),
        dict(name='Candi Ratu Boko', category='Budaya', location='Bokoharjo, Prambanan, Sleman',
             price=40000, image='ratu_boko.png', latitude=-7.7706, longitude=110.4899,
             description='Situs keraton kuno di atas bukit, terkenal dengan pemandangan matahari terbenam yang memukau.'),
        dict(name='Tebing Breksi', category='Alam Buatan', location='Sambirejo, Prambanan, Sleman',
             price=10000, image='tebing_breksi.png', latitude=-7.7649, longitude=110.5069,
             description='Bekas tambang batu kapur yang disulap menjadi destinasi wisata dengan ukiran relief raksasa dan spot foto ikonik.'),
        dict(name='Kalikuning Adventure Park', category='Petualangan', location='Umbulharjo, Cangkringan, Sleman',
             price=20000, image='kalikuning.png', latitude=-7.6084, longitude=110.4491,
             description='Taman hutan pinus di lereng Merapi dengan jalur tracking, spot foto alam, dan udara sejuk pegunungan.'),
    ]
    for item in destinations:
        db.session.add(Destination(**item))

    db.session.commit()

    # seed some historical bookings for owner/admin analytics demo
    import calendar
    dests = Destination.query.all()
    demo_user = User.query.filter_by(email='budi@gowisata.id').first()
    rnd = random.Random(42)
    months = ['2026-04', '2026-05', '2026-06', '2026-07']
    for m in months:
        year, month = map(int, m.split('-'))
        for _ in range(rnd.randint(6, 12)):
            d = rnd.choice(dests)
            qty = rnd.randint(1, 5)
            day = rnd.randint(1, 27)
            visit_dt = date(year, month, day)
            b = Booking(
                code=gen_code(),
                user_id=demo_user.id,
                destination_id=d.id,
                visit_date=visit_dt,
                qty=qty,
                total_price=d.price * qty,
                status=rnd.choice(['paid', 'used', 'used']),
                qr_token=''.join(rnd.choices(string.ascii_uppercase + string.digits, k=24)),
                created_at=datetime(year, month, day, rnd.randint(8, 20), rnd.randint(0, 59)),
            )
            b.paid_at = b.created_at
            if b.status == 'used':
                b.used_at = b.created_at
            db.session.add(b)
    db.session.commit()


with app.app_context():
    seed_data()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
