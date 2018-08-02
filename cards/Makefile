ID_NUM:=500

DIST_DIR:=./dist
QR_DIR:=${DIST_DIR}/qr
TEMPLATE_FILE:=./template/cards.html.j2
OUT_HTML_FILE:=${DIST_DIR}/cards.html
OUT_PDF_FILE:=${DIST_DIR}/cards.pdf
QR_BASE_URL:=https://sakuten.jp/lottery/login?sid=

ID_LIST_FILE:=ids.json

${OUT_PDF_FILE}: ${OUT_HTML_FILE}
	wkhtmltopdf --encoding 'utf-8' --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 ${OUT_HTML_FILE} ${OUT_PDF_FILE}

${OUT_HTML_FILE}: ${TEMPLATE_FILE} ${ID_LIST_FILE}
	mkdir -p ${DIST_DIR} ${QR_DIR}
	pipenv run python mkhtml.py -i ${ID_LIST_FILE} -o ${OUT_HTML_FILE} -t ${TEMPLATE_FILE} -b ${QR_BASE_URL}

${ID_LIST_FILE}:
	pipenv run python mkid.py -n ${ID_NUM} -o ${ID_LIST_FILE}

.PHONY: clean
clean:
	-rm -r ${DIST_DIR}
