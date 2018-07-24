DIST_DIR:=./dist
QR_DIR:=${DIST_DIR}/qr
TEMPLATE_FILE:=./template/cards.html.j2
OUT_HTML_FILE:=${DIST_DIR}/cards.html
OUT_PDF_FILE:=${DIST_DIR}/cards.pdf

ID_LIST_FILE:=test.json

${OUT_PDF_FILE}: ${OUT_HTML_FILE}
	wkhtmltopdf --encoding 'utf-8' --lowquality ${OUT_HTML_FILE} ${OUT_PDF_FILE}

${OUT_HTML_FILE}: ${TEMPLATE_FILE} ${ID_LIST_FILE}
	mkdir -p ${DIST_DIR} ${QR_DIR}
	pipenv run python mkhtml.py

.PHONY: clean
clean:
	-rm -r ${DIST_DIR}
