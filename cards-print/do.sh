#!/usr/bin/env bash
#
# this script outputs PDF file of QR cards list.
#
# copyright (c) 2018 Sakutendev

trap 'rm src/qr/*.png src/*.html' 2
echo "Generating html..."
python mkhtml.py
echo "Done.\nGenerating PDF..."
html2pdf cards.html
echo "Done.\nAll processes are done properly.exit."
