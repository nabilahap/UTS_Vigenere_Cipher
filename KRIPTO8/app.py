from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

# Fungsi Vigenere Cipher
def vigenereEncrypt(password, key):
    # Membuang spasi dan karakter non-alfabet
    password = ''.join(filter(str.isalpha, password))

    # Mengulangi kunci
    key = (key * ((len(password) // len(key)) + 1))[:len(password)]

    # Menerapkan Vigenère Cipher
    encrypted_password = ''
    for i in range(len(password)):
        char = password[i]
        key_char = key[i]
        shift = ord(key_char.upper()) - ord('A')
        
        if char.isupper():
            encrypted_password += chr((ord(char) + shift - ord('A')) % 26 + ord('A'))
        else:
            encrypted_password += chr((ord(char) + shift - ord('a')) % 26 + ord('a'))

    return encrypted_password.upper()

# Fungsi untuk membuat atau memeriksa tabel pengguna di database
def create_user_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            alamat TEXT NOT NULL,
            password TEXT NOT NULL,
            vigenere_key NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan pengguna baru ke database
def add_user(nama, alamat, password, key):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (nama, alamat, password, vigenere_key) VALUES (?, ?, ?, ?)', (nama, alamat, password, key))
    conn.commit()
    conn.close()


# Route untuk halaman pendaftaran
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        alamat = request.form['alamat']
        password = request.form['password']
        key = request.form['key']

        # Enkripsi password menggunakan Vigenere Cipher
        encrypted_password = vigenereEncrypt(password, key)

        # Tambahkan pengguna baru ke database dengan Vigenere key
        add_user(nama, alamat, encrypted_password, key)

        return redirect(url_for('login'))

    return render_template('register.html')

# Route untuk halaman menampilkan data
@app.route('/view_data')
def view_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    conn.close()

    return render_template('view_data.html', data=data)


# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nama = request.form['nama']
        password = request.form['password']

        # Mendapatkan data pengguna dari database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE nama = ?', (nama,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            stored_password = user_data[3]  # Indeks 3 adalah kolom password

            # Periksa kecocokan password tanpa dekripsi
            if stored_password == password:
                # Simpan informasi sesi
                session['user_id'] = user_data[0]  # Indeks 0 adalah kolom ID
                return render_template('success.html', user_name=user_data[1])  # Indeks 1 adalah kolom nama

    return render_template('login.html')

# Route for deleting a user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
   
# Delete the user with the specified user_id
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    
    # Update the IDs to be consecutive
    cursor.execute("UPDATE users SET id=ROWID")
    
    conn.commit()
    conn.close()

    return redirect(url_for('view_data'))



# Route untuk logout
@app.route('/logout')
def logout():
    # Hapus informasi sesi
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_user_table()
    app.run(debug=True)
