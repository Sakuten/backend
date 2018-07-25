DIST_DIR:=./dist
QR_DIR:=${DIST_DIR}/qr
TEMPLATE_FILE:=./template/cards.html.j2
OUT_HTML_FILE:=${DIST_DIR}/cards.html
OUT_PDF_FILE:=${DIST_DIR}/cards.pdf
QR_BASE_URL:=https://hoge

ID_LIST_FILE:=test.json

${OUT_PDF_FILE}: ${OUT_HTML_FILE}
	wkhtmltopdf --encoding 'utf-8' ${OUT_HTML_FILE} ${OUT_PDF_FILE}

${OUT_HTML_FILE}: ${TEMPLATE_FILE} ${ID_LIST_FILE}
	mkdir -p ${DIST_DIR} ${QR_DIR}
	pipenv run python mkhtml.py -i ${ID_LIST_FILE} -o ${OUT_HTML_FILE} -t ${TEMPLATE_FILE} -b ${QR_BASE_URL}

.PHONY: clean
clean:
	-rm -r ${DIST_DIR}
