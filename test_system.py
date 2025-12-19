import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def arab(text):
    return get_display(reshape(text))

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d | %H:%M:%S")

def create_perfect_report():
    try:
        pdfmetrics.registerFont(TTFont('ArabicFont', 'ARIAL.TTF'))
        c = canvas.Canvas("Ghalla_Perfect_Report.pdf", pagesize=A4)
        width, height = A4

        # 1. الهيدر الاحترافي
        c.setFillColor(colors.blue)
        c.rect(0, height-100, width, 100, fill=1)
        if os.path.exists("logo.jpg"):
            c.drawImage("logo.jpg", 40, height - 85, width=65, height=50)
        c.setFillColor(colors.white)
        c.setFont('ArabicFont', 24)
        c.drawCentredString(width/2 + 30, height - 60, arab("نظام التوثيق الذكي - مؤسسة الغلة"))

        # 2. شريط التوقيت (واضح جداً ومنفصل)
        c.setFillColor(colors.black)
        c.setFont('ArabicFont', 11)
        c.drawString(50, height - 120, f"توقيت تسجيل العطل: {dt_string}")
        c.drawRightString(width - 50, height - 120, f"ID: #GH-{now.strftime('%H%M%S')}")
        c.setLineWidth(1)
        c.line(40, height - 125, width - 40, height - 125)

        # 3. قسم البلاغ (العامل) - مع مسافات آمنة
        y = height - 150
        c.setStrokeColor(colors.red)
        c.roundRect(40, y - 180, width - 80, 170, 10)
        c.setFillColor(colors.red)
        c.setFont('ArabicFont', 14)
        c.drawString(width - 200, y - 20, arab("🔴 بلاغ حالة العطل"))

        c.setFillColor(colors.black)
        c.setFont('ArabicFont', 12)
        # استخدام إحداثيات ثابتة لمنع التداخل
        c.drawString(width - 150, y - 50, arab("الجزء المتضرر:"))
        c.drawString(280, y - 50, arab("المحرك الرئيسي - وحدة الضغط"))
        c.drawString(width - 150, y - 75, arab("حالة الآلة:"))
        c.drawString(280, y - 75, arab("متوقفة تماماً (توقف الإنتاج)"))

        # إطار الصورة
        c.setStrokeColor(colors.grey)
        c.rect(55, y - 165, 180, 100)
        if os.path.exists("fault.jpg"):
            c.drawImage("fault.jpg", 60, y - 160, width=170, height=90)

        # 4. قسم التدخل (التقني) - مسافة كافية عن القسم العلوي
        y2 = y - 200
        c.setStrokeColor(colors.green)
        c.roundRect(40, y2 - 180, width - 80, 170, 10)
        c.setFillColor(colors.green)
        c.setFont('ArabicFont', 14)
        c.drawString(width - 200, y2 - 20, arab("🟢 تقرير التدخل الفني"))

        c.setFillColor(colors.black)
        c.setFont('ArabicFont', 12)
        c.drawString(width - 150, y2 - 50, arab("الإجراء المتخذ:"))
        c.drawString(50, y2 - 50, arab("استبدال الحساس التالف وتنظيف الفلاتر"))
        c.drawString(width - 150, y2 - 75, arab("الحالة النهائية:"))
        c.drawString(320, y2 - 75, arab("شغالة 100% (دخلت الإنتاج)"))

        # إطار الصورة الثاني
        c.setStrokeColor(colors.grey)
        c.rect(55, y2 - 165, 180, 100)
        if os.path.exists("repair.jpg"):
            c.drawImage("repair.jpg", 60, y2 - 160, width=170, height=90)

        # 5. التذييل (Footer)
        c.setFillColor(colors.lightgrey)
        c.rect(40, 40, width-80, 30, fill=1)
        c.setFillColor(colors.black)
        c.setFont('ArabicFont', 10)
        c.drawCentredString(width/2, 50, arab("💡 ملاحظة: هذا التقرير مستخرج آلياً ولا يمكن تعديل توقيته أو بياناته الأصلية."))

        c.save()
        print("🚀 تم توليد التقرير النهائي بنجاح تام وبدون تداخل!")

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

create_perfect_report()