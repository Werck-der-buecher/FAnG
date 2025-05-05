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

CROP = OCR-D-SEG-CROP-tesserocr-crop

$(CROP): $(BIN)
$(CROP): TOOL = ocrd-tesserocr-crop

DEN = $(CROP)-DENOISE-ocropy

$(DEN): $(CROP)
$(DEN): TOOL = ocrd-cis-ocropy-denoise
$(DEN): PARAMS = "level-of-operation": "page", "noise_maxsize": 3.0

DESK = $(DEN)-DESKEW-tesseract

$(DESK): $(DEN)
$(DESK): TOOL = ocrd-tesserocr-deskew
$(DESK): PARAMS = "operation_level": "page"

SEG = OCR-D-SEG-tesseract

$(SEG): $(DESK)
$(SEG): TOOL = ocrd-tesserocr-segment
$(SEG): PARAMS = "shrink_polygons": true, "find_tables": false

RECOG = OCR-D-RECOG-tesseract

$(RECOG): $(SEG)
$(RECOG): TOOL = ocrd-tesserocr-recognize
$(RECOG): PARAMS = "textequiv_level": "glyph", "overwrite_segments": true, "model": "Latin", "padding": 10, "oem": "DEFAULT"

OUTPUT = OCR-D-EXTGLYPHS-tesseract

$(OUTPUT): $(RECOG)
$(OUTPUT): TOOL = ocrd-segment-extract-glyphs
$(OUTPUT): PARAMS = "feature_filter": "binarized,normalized,grayscale_normalized,despeckled", "to_binary": true, "in_memory": true, "transparency": true

.DEFAULT_GOAL = $(OUTPUT)

# Down here, custom configuration ends.
###

include Makefile
