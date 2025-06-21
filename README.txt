
# deFuture_bot

### Cara Deploy di Railway (atau Render):
1️⃣ Upload file ke GitHub repository (misal: deFuture-bot-repo)  
2️⃣ Buat project di Railway, hubungkan ke repo  
3️⃣ Tambahkan environment variable:  
   Name: BOT_TOKEN  
   Value: 8164194712:AAFpPh5-H490HbiCCW1k7hDikrcYBg9gkIs  
4️⃣ Railway otomatis build dan jalankan bot

### Local Run (optional)
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
BOT_TOKEN=8164194712:AAFpPh5-H490HbiCCW1k7hDikrcYBg9gkIs python bot.py
```
