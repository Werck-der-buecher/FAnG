# Install by copying (or symlinking) makefiles into a directory
# where all OCR-D workspaces (unpacked BagIts) reside. Then
# chdir to that location.

# Call via:
# `make -f WORKFLOW-CONFIG.mk WORKSPACE-DIRS` or
# `make -f WORKFLOW-CONFIG.mk all` or just
# `make -f WORKFLOW-CONFIG.mk`
# To rebuild partially, you must pass -W to recursive make:
# `make -f WORKFLOW-CONFIG.mk EXTRA_MAKEFLAGS="-W FILEGRP"`
# To get help on available goals:
# `make help`

###
# From here on, custom configuration begins.

info:
	@echo "Read image files and binarize+crop,"
	@echo "then binarize+denoise+deskew pages,"
	@echo "then segment into regions and lines,"
	@echo "then shrink regions into the hull polygon of its lines,"
	@echo "and finally extract page images and region coordinates"
	@echo "(including meta-data) into one directory,"
	@echo "with corresponding filename suffixes for segmentation training."

INPUT = OCR-D-IMG

$(INPUT):
	ocrd workspace find -G $@ --download
	ocrd workspace find -G OCR-D-IMG --download # just in case

BIN = $(INPUT)-BINPAGE-sauvola

$(BIN): $(INPUT)
$(BIN): TOOL = ocrd-olena-binarize
$(BIN): PARAMS = "impl": "sauvola-ms-split"

CROP = OCR-D-SEG-PAGE-anyocr

$(CROP): $(BIN)
$(CROP): TOOL = ocrd-anybaseocr-crop

BIN2 = $(CROP)-BINPAGE-sauvola

$(BIN2): $(CROP)
$(BIN2): TOOL = ocrd-olena-binarize
$(BIN2): PARAMS = "impl": "sauvola-ms-split"

DEN = $(BIN2)-DENOISE-ocropy

$(DEN): $(BIN2)
$(DEN): TOOL = ocrd-cis-ocropy-denoise
$(DEN): PARAMS = "level-of-operation": "page", "noise_maxsize": 3.0

FLIP = $(DEN)-DESKEW-tesseract

$(FLIP): $(DEN)
$(FLIP): TOOL = ocrd-tesserocr-deskew
$(FLIP): PARAMS = "operation_level": "page"

DESK = $(FLIP)-DESKEW-ocropy

$(DESK): $(FLIP)
$(DESK): TOOL = ocrd-cis-ocropy-deskew
$(DESK): PARAMS = "level-of-operation": "page", "maxskew": 5

BLOCK = OCR-D-SEG-BLOCK-tesseract

$(BLOCK): $(DESK)
$(BLOCK): TOOL = ocrd-tesserocr-segment-region
$(BLOCK): PARAMS = "padding": 5, "find_tables": false

PLAUSIBLE = $(BLOCK)-plausible

$(PLAUSIBLE): $(BLOCK)
$(PLAUSIBLE): TOOL = ocrd-segment-repair
$(PLAUSIBLE): PARAMS = "plausibilize": true, "plausibilize_merge_min_overlap": 0.7

CLIP = $(BLOCK)-CLIP

$(CLIP): $(PLAUSIBLE)
$(CLIP): TOOL = ocrd-cis-ocropy-clip

FLIPR = $(CLIP)-DESKEW-tesseract

$(FLIPR): $(CLIP)
$(FLIPR): TOOL = ocrd-tesserocr-deskew
$(FLIPR): PARAMS = "operation_level": "region"

LINE = OCR-D-SEG-LINE-tesseract-ocropy

$(LINE): $(FLIPR)
$(LINE): TOOL = ocrd-cis-ocropy-segment
$(LINE): PARAMS = "spread": 2.4

TIGHT = OCR-D-SEG-BLOCK-tesseract-ocropy

$(TIGHT): $(LINE)
$(TIGHT): TOOL = ocrd-segment-repair
$(TIGHT): PARAMS = "sanitize": true

OUTPUT = OCR-D-IMG-REGIONS

$(OUTPUT): $(TIGHT)
$(OUTPUT): TOOL = ocrd-segment-extract-regions
$(OUTPUT): PARAMS = "transparency": true

.DEFAULT_GOAL = $(OUTPUT)

# Down here, custom configuration ends.
###

include Makefile
