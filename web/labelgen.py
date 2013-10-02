import cStringIO
import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib import units


def draw_label(c, fromaddr, imagename, imagesize, sender_data, address):
    # Draw the from address
    text = c.beginText()
    text.setTextOrigin(0, 59 * units.mm - 8)
    text.setFont("Helvetica-Bold", 8)
    text.setLeading(10)
    text.textLine("Return Address:")
    text.setFont("Helvetica", 8)
    text.textLines(fromaddr)
    c.drawText(text)

    # Draw the to address
    text = c.beginText()
    text.setTextOrigin(10 * units.mm, 36 * units.mm)
    text.setFont("Helvetica", 8)
    text.setLeading(12)
    text.textLine(sender_data)
    text.setFont("Helvetica", 12)
    text.setLeading(14)
    text.textLines(address)
    c.drawText(text)

    # Draw the PPI
    c.drawImage(
        imagename,
        (93 - imagesize[0]) * units.mm,
        (58 - imagesize[1]) * units.mm,
        width=imagesize[0] * units.mm,
        height=imagesize[1] * units.mm)

    c.showPage()


def draw_customs(c, customsname, weight, price):
    c.drawImage(
        customsname,
        0,
        0,
        width=55 * units.mm,
        height=54 * units.mm)

    text = c.beginText()
    text.setTextOrigin(58, 109)
    text.setFont("Helvetica", 10)
    text.textLine("X")
    c.drawText(text)

    text = c.beginText()
    text.setTextOrigin(5, 81)
    text.setFont("Helvetica", 8)
    text.textLine("Electronic Parts")

    text.setTextOrigin(97, 81)
    text.textLine(weight)

    text.setTextOrigin(128, 81)
    text.textLine(price)

    text.setTextOrigin(97, 33)
    text.textLine(weight)

    text.setTextOrigin(128, 33)
    text.textLine(price)

    c.drawText(text)

    text = c.beginText()
    text.setFont("Helvetica", 6)
    text.setTextOrigin(55, 5)
    text.textLine(datetime.datetime.now().strftime("%Y-%m-%d"))
    c.drawText(text)

    c.showPage()


def generate_label(fromaddr, imagename, imagesize, sender_data, address):
    data = cStringIO.StringIO()
    c = canvas.Canvas(data, pagesize=(94 * units.mm, 55 * units.mm))

    draw_label(c, fromaddr, imagename, imagesize, sender_data, address)
    c.save()

    return data.getvalue()


def generate_customs(customsname, weight, price):
    data = cStringIO.StringIO()
    c = canvas.Canvas(data, pagesize=(54 * units.mm, 55 * units.mm))

    draw_customs(c, customsname, weight, price)
    c.save()

    return data.getvalue()
