from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import ollama
from datetime import datetime
from models import db, Mesaj, User, Sohbet
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifeBot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sizin_gizli_anahtarınız_buraya_gelecek'
db.init_app(app)

app.jinja_env.globals.update(datetime=datetime)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("Kullanıcı adı ve şifre boş bırakılamaz.", 'error')
            return render_template("register.html")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Bu kullanıcı adı zaten alınmış. Lütfen farklı bir tane deneyin.", 'error')
            return render_template("register.html")

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Kaydınız başarıyla tamamlandı! Giriş yapabilirsiniz.", 'success')
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Başarıyla giriş yaptınız!", 'success')
            return redirect(url_for('index'))
        else:
            flash("Yanlış kullanıcı adı veya şifre.", 'error')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Çıkış yaptınız.", 'info')
    return redirect(url_for('login'))

@app.route("/", defaults={'chat_id': None}, methods=["GET", "POST"])
@app.route("/chat/<int:chat_id>", methods=["GET", "POST"])
@login_required
def index(chat_id):
    uyari = None
    secili_sohbet = None
    
    sohbetler = Sohbet.query.filter_by(user_id=current_user.id).order_by(Sohbet.olusturma_tarihi.desc()).all()

    if not sohbetler or chat_id is None:
        if not sohbetler:
            yeni_sohbet = Sohbet(user_id=current_user.id, baslik="İlk Sohbet")
            db.session.add(yeni_sohbet)
            db.session.commit()
            secili_sohbet = yeni_sohbet
            ilk_bot_mesaji = Mesaj(
                sohbet_id=secili_sohbet.id,
                kim="bot",
                mesaj="Merhaba! Ben LifeBot AF.AI 🤖\nBugün nasıl hissediyorsun? Dertleşmek istersen buradayım... 💙",
                zaman=datetime.now().strftime("%H:%M")
            )
            db.session.add(ilk_bot_mesaji)
            db.session.commit()
            flash("Hoş geldin! İlk sohbetin oluşturuldu.", 'info')
            return redirect(url_for('index', chat_id=secili_sohbet.id))

        elif chat_id is None:
            secili_sohbet = sohbetler[0]
            return redirect(url_for('index', chat_id=secili_sohbet.id))

    else:
        secili_sohbet = Sohbet.query.filter_by(id=chat_id, user_id=current_user.id).first()
        if not secili_sohbet:
            flash("Böyle bir sohbet bulunamadı veya erişim izniniz yok.", 'error')
            return redirect(url_for('index'))

    mesajlar = Mesaj.query.filter_by(sohbet_id=secili_sohbet.id).order_by(Mesaj.id).all() if secili_sohbet else []

    return render_template(
        "index.html",
        mesajlar=mesajlar,
        sohbetler=sohbetler,
        secili_sohbet_id=secili_sohbet.id if secili_sohbet else None
    )

# ✅ ✅ ✅ YENİ AJAX API ENDPOINT ✅ ✅ ✅
@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    try:
        veri = request.get_json()
        mesaj = veri.get("mesaj", "").strip()
        sohbet_id = veri.get("sohbet_id")

        if not mesaj:
            return jsonify({"hata": "Boş mesaj gönderilemez."}), 400

        sohbet = Sohbet.query.filter_by(id=sohbet_id, user_id=current_user.id).first()
        if not sohbet:
            return jsonify({"hata": "Geçersiz sohbet ID."}), 404

        yeni_mesaj = Mesaj(
            sohbet_id=sohbet.id,
            kim="user",
            mesaj=mesaj,
            zaman=datetime.now().strftime("%H:%M")
        )
        db.session.add(yeni_mesaj)
        db.session.commit()

        sohbet_gecmisi = Mesaj.query.filter_by(sohbet_id=sohbet.id).order_by(Mesaj.id).all()
        ollama_mesajlari = [{"role": "system", "content": "Senin adın AF.AI. Samimi, anlayışlı ve pozitif cevaplar ver."}]
        for c in sohbet_gecmisi:
            rol = "user" if c.kim == "user" else "assistant"
            ollama_mesajlari.append({"role": rol, "content": c.mesaj})

        try:
            yanit = ollama.chat(model="llama3", messages=ollama_mesajlari)
            bot_cevabi = yanit["message"]["content"]
        except Exception as ollama_err:
            hata_mesaji = str(ollama_err)
            bot_cevabi = (
                "Merhaba! Ben LifeBot AF.AI. 🤖\n\n"
                "Şu anda yerel yapay zeka servisime (Ollama) bağlanamıyorum. "
                "Sizinle sohbet edebilmem için lütfen Ollama uygulamasının arka planda çalıştığından "
                "ve `llama3` modelinin yüklü olduğundan emin olun.\n\n"
                "**Nasıl Düzeltilir?**\n"
                "1. Bilgisayarınızda Ollama uygulamasını başlatın.\n"
                "2. Terminalinizden `ollama run llama3` komutunu çalıştırarak Llama3 modelini indirin.\n\n"
                f"*(Bağlantı Hatası: {hata_mesaji})*"
            )

        yeni_bot_mesaji = Mesaj(
            sohbet_id=sohbet.id,
            kim="bot",
            mesaj=bot_cevabi,
            zaman=datetime.now().strftime("%H:%M")
        )
        db.session.add(yeni_bot_mesaji)
        db.session.commit()

        return jsonify({"cevap": bot_cevabi})

    except Exception as e:
        return jsonify({"hata": f"Beklenmeyen bir hata oluştu: {str(e)}"}), 500

@app.route("/new_chat", methods=["POST"])
@login_required
def new_chat():
    yeni_sohbet = Sohbet(user_id=current_user.id, baslik="Yeni Sohbet")
    db.session.add(yeni_sohbet)
    db.session.commit()

    ilk_bot_mesaji = Mesaj(
        sohbet_id=yeni_sohbet.id,
        kim="bot",
        mesaj="Merhaba! Yeni bir sohbete başladık. Sana nasıl yardımcı olabilirim?",
        zaman=datetime.now().strftime("%H:%M")
    )
    db.session.add(ilk_bot_mesaji)
    db.session.commit()

    flash("Yeni sohbet oluşturuldu!", 'success')
    return redirect(url_for('index', chat_id=yeni_sohbet.id))

@app.route("/delete_chat/<int:chat_id>", methods=["POST"])
@login_required
def delete_chat(chat_id):
    sohbet = Sohbet.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if sohbet:
        db.session.delete(sohbet)
        db.session.commit()
        flash("Sohbet başarıyla silindi.", 'info')
    else:
        flash("Sohbet bulunamadı veya silme yetkiniz yok.", 'error')
    return redirect(url_for('index'))

@app.route("/rename_chat/<int:chat_id>", methods=["POST"])
@login_required
def rename_chat(chat_id):
    sohbet = Sohbet.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if sohbet:
        yeni_baslik = request.form.get("yeni_baslik", "").strip()
        if yeni_baslik:
            sohbet.baslik = yeni_baslik
            db.session.commit()
            flash("Sohbet başlığı güncellendi.", 'success')
        else:
            flash("Yeni başlık boş olamaz.", 'error')
    else:
        flash("Sohbet bulunamadı veya güncelleme yetkiniz yok.", 'error')
    return redirect(url_for('index', chat_id=chat_id))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
