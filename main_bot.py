import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- الإعدادات الإدارية ---
TOKEN = os.getenv("BOT_TOKEN")
MAINTENANCE_GROUP_ID = -5016111677
ADMIN_GROUP_ID = -4932631153

pending_reports = {}

# القوائم
WORKERS = [["محمد زيتوني", "محمد كوسة"], ["ابوبكر", "هيثم بلعيفة", "شعبان غول"]]
LINES = [["Ligne 01", "Ligne 02", "Ligne 03"], ["Ligne 04", "Ligne 05", "Ligne 06"], ["خيط", "موندرا", "غرانيلي"]]
MACHINE_STATUS = [["STOPPED", "WORKING"]]
REPAIR_STATUS = [["REPAIRED", "FAILED"]]
TECHNICIANS = [["رمزي", "جمال", "امين"]]

def fix_arabic(text):
    if not text: return ""
    return get_display(reshape(str(text)))

# --- وظيفة بناء التقرير ---
async def create_structured_pdf(data):
    filename = f"Report_{datetime.now().strftime('%H%M%S')}.pdf"
    try:
        pdfmetrics.registerFont(TTFont('ArabicFont', 'ARIAL.TTF'))
    except: pass
        
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    if os.path.exists("logo.jpg"):
        try: c.drawImage("logo.jpg", 40, height - 70, width=60, height=60, mask='auto')
        except: pass

    # الهيدر
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.rect(110, height-70, width-150, 50, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont('ArabicFont', 20)
    c.drawCentredString(width/2 + 30, height-40, fix_arabic("تقرير صيانة مؤسسة الغلة"))

    # بيانات الإبلاغ
    y = height - 110
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.rect(40, y-20, width-80, 20, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont('ArabicFont', 11)
    c.drawRightString(width-50, y-15, fix_arabic(f"1. بيانات الإبلاغ - التاريخ: {data.get('report_time', '')}"))
    
    y -= 40
    c.setFillColorRGB(0, 0, 0)
    report_data = [
        ("المبلغ:", data.get('worker', '')), 
        ("الخط:", data.get('line', '')), 
        ("وصف العطل:", data.get('fault', ''))
    ]
    for label, val in report_data:
        c.drawRightString(width-50, y, fix_arabic(label))
        c.drawString(60, y, fix_arabic(val))
        c.line(40, y-5, width-40, y-5)
        y -= 25

    # بيانات التدخل
    y -= 15
    c.setFillColorRGB(0, 0.5, 0.2)
    c.rect(40, y-20, width-80, 20, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.drawRightString(width-50, y-15, fix_arabic(f"2. بيانات التدخل - التاريخ: {data.get('repair_time', '')}"))
    
    y -= 35
    c.setFillColorRGB(0, 0, 0)
    repair_data = [
        ("التقني:", data.get('tech', '')), 
        ("النتيجة:", data.get('r_status', '')), 
        ("حالة الالة بعد التدخل:", data.get('after_status', '')),
        ("ملاحظات التقني:", data.get('note', ''))
    ]
    for label, val in repair_data:
        c.drawRightString(width-50, y, fix_arabic(label))
        c.drawString(60, y, fix_arabic(val))
        c.line(40, y-5, width-40, y-5)
        y -= 25

    # الصور
    y -= 30
    c.setFont('ArabicFont', 12)
    if 'p_before' in data and os.path.exists(data['p_before']):
        c.drawRightString(width/2 - 50, y, fix_arabic("صورة للعطل"))
        c.drawImage(data['p_before'], 50, y-150, width=220, height=130)
    if 'p_after' in data and os.path.exists(data['p_after']):
        c.drawRightString(width - 50, y, fix_arabic("صورة بعد الاصلاح"))
        c.drawImage(data['p_after'], 310, y-150, width=220, height=130)
    
    c.setFont('Helvetica', 10)
    c.drawString(40, 40, "System Developer: Belguidoum Ramzi")
    c.save()
    return filename

# --- منطق البوت ---
async def handle_main_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    chat_id = update.effective_chat.id
    step = context.user_data.get('step')
    text = msg.text

    if step is None and text not in ["إبلاغ عن عطل (عامل)", "تسجيل تدخل (تقني)"]:
        kb = [["تسجيل تدخل (تقني)"]] if chat_id == MAINTENANCE_GROUP_ID else [["إبلاغ عن عطل (عامل)"]]
        await msg.reply_text("نظام الغلة جاهز:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return

    # مسار العامل
    if text == "إبلاغ عن عطل (عامل)":
        await msg.reply_text("اسمك؟", reply_markup=ReplyKeyboardMarkup(WORKERS, resize_keyboard=True)); context.user_data['step'] = 'W_NAME'
    elif step == 'W_NAME':
        context.user_data['worker'] = text; await msg.reply_text("الخط؟", reply_markup=ReplyKeyboardMarkup(LINES, resize_keyboard=True)); context.user_data['step'] = 'W_LINE'
    elif step == 'W_LINE':
        context.user_data['line'] = text; await msg.reply_text("وصف العطل:", reply_markup=ReplyKeyboardRemove()); context.user_data['step'] = 'W_FAULT'
    elif step == 'W_FAULT':
        context.user_data['fault'] = text; await msg.reply_text("أرسل صورة العطل:"); context.user_data['step'] = 'W_PHOTO'
    elif step == 'W_PHOTO' and msg.photo:
        context.user_data['report_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        p = f"bf_{msg.chat_id}.jpg"; f = await msg.photo[-1].get_file(); await f.download_to_drive(p); context.user_data['p_before'] = p
        rid = f"{datetime.now().strftime('%H%M%S')}-{context.user_data['line']}"
        pending_reports[rid] = context.user_data.copy()
        await context.bot.send_photo(chat_id=MAINTENANCE_GROUP_ID, photo=open(p, 'rb'), caption=f"🚨 بلاغ: {rid}\nالعامل: {context.user_data['worker']}")
        await msg.reply_text(f"✅ تم الإرسال برقم: {rid}"); context.user_data.clear()

    # مسار التقني
    elif text == "تسجيل تدخل (تقني)":
        if not pending_reports: await msg.reply_text("لا بلاغات."); return
        kb = [[r] for r in pending_reports.keys()]
        await msg.reply_text("اختر البلاغ:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)); context.user_data['step'] = 'T_SELECT'
    elif step == 'T_SELECT':
        if text in pending_reports:
            context.user_data.update(pending_reports[text]); context.user_data['selected_id'] = text
            await msg.reply_text("من التقني؟", reply_markup=ReplyKeyboardMarkup(TECHNICIANS, resize_keyboard=True)); context.user_data['step'] = 'T_NAME'
    elif step == 'T_NAME':
        context.user_data['tech'] = text; await msg.reply_text("النتيجة؟", reply_markup=ReplyKeyboardMarkup(REPAIR_STATUS, resize_keyboard=True)); context.user_data['step'] = 'T_STATUS'
    elif step == 'T_STATUS':
        context.user_data['r_status'] = text; await msg.reply_text("حالة الالة؟", reply_markup=ReplyKeyboardMarkup(MACHINE_STATUS, resize_keyboard=True)); context.user_data['step'] = 'T_AFTER'
    elif step == 'T_AFTER':
        context.user_data['after_status'] = text; await msg.reply_text("صورة بعد الإصلاح:"); context.user_data['step'] = 'T_PHOTO'
    elif step == 'T_PHOTO' and msg.photo:
        p = f"af_{msg.chat_id}.jpg"; f = await msg.photo[-1].get_file(); await f.download_to_drive(p); context.user_data['p_after'] = p
        await msg.reply_text("ملاحظاتك:", reply_markup=ReplyKeyboardRemove()); context.user_data['step'] = 'T_NOTE'
    elif step == 'T_NOTE':
        context.user_data['note'] = text; context.user_data['repair_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf = await create_structured_pdf(context.user_data)
        with open(pdf, 'rb') as doc: await context.bot.send_document(chat_id=ADMIN_GROUP_ID, document=doc)
        pending_reports.pop(context.user_data['selected_id'], None)
        await msg.reply_text("✅ تم إغلاق التقرير."); context.user_data.clear()

if _name_ == "_main_":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_main_logic))
    app.run_polling()