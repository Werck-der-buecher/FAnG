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

DEN = $(CROP)-DENOISE-ocropy

$(DEN): $(CROP)
$(DEN): TOOL = ocrd-cis-ocropy-denoise
$(DEN): PARAMS = "level-of-operation": "page", "noise_maxsize": 3.0

DESK = $(DEN)-DESKEW-tesseract

$(DESK): $(DEN)
$(DESK): TOOL = ocrd-tesserocr-deskew
$(DESK): PARAMS = "operation_level": "page"

SEG = OCR-D-SEG-eynollah

$(SEG): $(DESK)
$(SEG): TOOL = ocrd-eynollah-segment
$(SEG): PARAMS = "models": "default"

OUTPUT = OCR-D-EXTREGIONS-eynollah

$(OUTPUT): $(SEG)
$(OUTPUT): TOOL = ocrd-segment-extract-regions
$(OUTPUT): PARAMS = "feature_filter": "binarized", "transparency": true

.DEFAULT_GOAL = $(OUTPUT)

# Down here, custom configuration ends.
###

include Makefile
