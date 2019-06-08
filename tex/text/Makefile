VERSION = 1.0
TARBALL = ufbathesis-$(VERSION).tar.gz
UPLOAD_TO = app.dcc.ufba.br:~/public_html/ufbathesis/

all: qual msc 

qual: template-qual.bbl template-qual.dvi template-qual.pdf 

msc: template-msc.bbl template-msc.dvi template-msc.pdf

%.dvi: %.tex ufbathesis.cls
	latex $<

%.pdf: %.tex ufbathesis.cls
	pdflatex $<

%.bbl  : %.aux
	bibtex $<

%.aux : %.tex
	latex $<

dist: $(TARBALL)

$(TARBALL): ufbathesis.cls abntex2-alf.bst
	tar czf $(TARBALL) $^

index.html: README.md
	(pandoc -s -f markdown -t html $< | sed -e 's/##VERSION##/$(VERSION)/g' > $@) || ($(RM) $@; false)

upload: $(TARBALL) index.html template-qual.tex template-msc.tex .htaccess
	rsync -avp $^ $(UPLOAD_TO)

clean:
	$(RM) $(TARBALL)
	$(RM) *.bbl *.blg *.aux *.lof *.log *.lot *.toc *.out template*.pdf template*.dvi
	$(RM) index.html
