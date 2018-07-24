cards.pdf: src/cards.html
	wkhtmltopdf --encoding 'utf-8' --lowquality src/cards.html cards.pdf

src/cards.html: template/cards.html.j2 test.json
	mkdir -p src/qr
	pipenv run python mkhtml.py

.PHONY: clean
clean:
	-rm -r src/ cards.pdf
