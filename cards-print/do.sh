#!/usr/bin/env bash
#
# this script outputs PDF file of QR cards list.
#
# copyright (c) 2018 Sakutendev

echo 'Generating QR codes...'
python mkqr.py
echo "Done.\nGenerating html..."
python mkhtml.py
echo "Done.\nGenerating PDF..."
html2pdf cards.html
echo "Done.\nAll processes are done properly.exit."
