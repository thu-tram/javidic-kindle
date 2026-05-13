# The Kindle Publishing Guidelines recommend -c2 (huffdic compression),
# but it is excruciatingly slow. That's why -c1 is selected by default.
# Compression currently is not officially supported by Kindle Previewer according to the documentation
COMPRESSION ?= 1

# Sets the max sentences per entry
SENTENCES ?= 5

# This flag determines wheter only good and verified sentences are used in the
# dictionary. Set it to TRUE if you only want those sentences.
ONLY_CHECKED_SENTENCES ?= FALSE

# If true adds pronunciations to entries.
PRONUNCIATIONS ?= TRUE

# If true adds additional information to entries.
ADDITIONAL_INFO ?= TRUE

ISWSL ?= FALSE

ifeq ($(PRONUNCIATIONS), TRUE)
	FLAGS += -p
endif

ifeq ($(ADDITIONAL_INFO), TRUE)
	FLAGS += -i
endif

ifeq ($(OS), Windows_NT)
	PYTHON3 ?= python
	KINDLEGEN := kindlepreviewer.bat
else
ifeq ($(ISWSL), TRUE)
	PYTHON3 ?= python3
	KINDLEGEN := powershell.exe -command kindlepreviewer.bat
else
	PYTHON3 ?= python3
	KINDLEGEN := ./kindlegen
endif
endif

all: javidic.mobi

cache:
	mkdir $@
	
# Note that kindlegen was officially replaced by Kindle Previewer
cache/kindlegen_linux_2.6_i386_v2_9.tar.gz: cache
	wget -nv -O $@ https://www.dropbox.com/s/dl/vvg1n3mu04fdkoh

# See also https://wiki.mobileread.com/wiki/KindleGen
kindlegen: cache/kindlegen_linux_2.6_i386_v2_9.tar.gz
	tar -xzf $< $@
	touch $@

javidic.opf: javidic.py javidic_parser.py dictionary.py style.css javidic-frontmatter.html
	$(PYTHON3) javidic.py $(FLAGS)

jmdict.opf: style.css JMdict-frontmatter.html
	$(PYTHON3) jmdict.py -a -s $(SENTENCES) -d j $(FLAGS)

jmnedict.opf: style.css JMnedict-Frontmatter.html
	$(PYTHON3) jmdict.py -d n $(FLAGS)

%.mobi: %.opf kindlegen 
ifeq ($(OS), Windows_NT)
	mkdir -p out
	$(KINDLEGEN) $< -convert -output ./out -locale en
	cp ./out/mobi/$@ ./$@
else
ifeq ($(ISWSL), TRUE)
	mkdir -p out
	$(KINDLEGEN) $< -convert -output ./out -locale en
	cp ./out/mobi/$@ ./$@
else
	$(KINDLEGEN) $< -c$(COMPRESSION) -verbose -dont_append_source -o $@
endif
endif

test:
	PYTHONPATH=. $(PYTHON3) -m unittest discover tests

clean:
	rm -rf *.opf entry-*.html *cover.jpg *.tar.bz2 *.gz *.csv *cover.png *.tmp *.zip out cache
	rm -f javidic.opf entry-javidic-*.html javidic-cover.jpg

clean_all: clean
	rm -rf *.mobi

.PHONY: all clean
