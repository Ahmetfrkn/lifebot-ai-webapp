from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime # datetime'ı burada da import etmeyi unutmayın

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Bir kullanıcıya ait birden fazla sohbet olabileceği için relationship kuruyoruz
    sohbetler = db.relationship('Sohbet', backref='user', lazy=True, cascade="all, delete-orphan") # cascade ile sohbet silinince mesajları da silinir

class Sohbet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    baslik = db.Column(db.String(100), nullable=False, default="Yeni Sohbet") # Sohbetin adı
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow) # Sohbetin oluşturulma tarihi
    # Bir sohbete ait birden fazla mesaj olabileceği için relationship kuruyoruz
    mesajlar = db.relationship('Mesaj', backref='sohbet', lazy=True, cascade="all, delete-orphan") # cascade ile sohbet silinince mesajları da silinir

class Mesaj(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sohbet_id = db.Column(db.Integer, db.ForeignKey('sohbet.id'), nullable=False) # Hangi sohbete ait olduğunu belirttik
    kim = db.Column(db.String(10), nullable=False)  # "user" veya "bot"
    mesaj = db.Column(db.Text, nullable=False)
    zaman = db.Column(db.String(20), nullable=False) # Veya db.DateTime kullanıp Jinja'da formatlayabiliriz