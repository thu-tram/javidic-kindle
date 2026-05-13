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

# Check if kindlegen exists
kindlegen:
ifeq ($(OS), Windows_NT)
# On Windows, we assume kindlepreviewer.bat is in the PATH
else
ifeq ($(ISWSL), TRUE)
# On WSL, we assume kindlepreviewer.bat is accessible
else
	@if [ ! -f $(KINDLEGEN) ]; then \
		echo "Error: kindlegen binary not found at $(KINDLEGEN)."; \
		echo "Please download kindlegen manually and place it in the current directory."; \
		echo "You can find it at: https://www.amazon.com/gp/feature.html?docId=1000765211 (or search for Kindlegen legacy downloads)"; \
		exit 1; \
	fi
endif
endif

javidic.opf: javidic.py javidic_parser.py dictionary.py style.css javidic-frontmatter.html
	$(PYTHON3) javidic.py $(FLAGS)

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
