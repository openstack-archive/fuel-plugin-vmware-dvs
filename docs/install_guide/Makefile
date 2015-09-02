FILE=vmware_dvs_install_guide
EX=tex
REX=pdf
LATEX=pdflatex
SHOW=mupdf

all:	pdf show

pdf:
	$(LATEX) $(FILE).$(EX)

show:
	$(SHOW) $(FILE).$(REX)

clean:
	rm *.aux *~ *.log *.toc *\# *.out *.pdf
