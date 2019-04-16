ADMIN_NUM:=1
CHECKER_NUM:=20
STUDENT_NUM:=1000
VISITOR_NUM:=0
MAX_QR_NUM:=492

DIST_DIR:=./dist
QR_DIR:=${DIST_DIR}/qr
TEMPLATE_FILE:=./template/cards.html.j2
OUT_HTML_DIR:=${DIST_DIR}
OUT_PDF_DIR:=${DIST_DIR}/pdf
QR_BASE_URL:=https://sakuten.jp/lottery/login?sid=

ID_LIST_FILE:=${DIST_DIR}/ids.json

.PHONY: pdf
pdf: html $(patsubst ${OUT_HTML_DIR}/%.html,${OUT_PDF_DIR}/%.pdf,$(wildcard ${OUT_HTML_DIR}/*.html))

.PHONY: html
html: ${OUT_HTML_DIR}

${OUT_PDF_DIR}/%.pdf: ${OUT_HTML_DIR}/%.html
	mkdir -p ${OUT_PDF_DIR}
	wkhtmltopdf --encoding 'utf-8' --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 $< $@

${OUT_HTML_DIR}: ${TEMPLATE_FILE} ${ID_LIST_FILE}
	mkdir -p ${DIST_DIR} ${QR_DIR} ${OUT_HTML_DIR}
	pipenv run python mkhtml.py --horizontal 2 -i ${ID_LIST_FILE} -o ${OUT_HTML_DIR} -t ${TEMPLATE_FILE} -b ${QR_BASE_URL} -m ${MAX_QR_NUM}

${ID_LIST_FILE}:
	mkdir -p ${DIST_DIR}
	pipenv run python mkid.py -a ${ADMIN_NUM} -c ${CHECKER_NUM} -s ${STUDENT_NUM} -v ${VISITOR_NUM} -o ${ID_LIST_FILE}

.PHONY: clean
clean:
	-rm -r ${DIST_DIR}
