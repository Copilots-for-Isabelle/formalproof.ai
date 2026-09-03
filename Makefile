# The site is hand-written HTML and CSS. There is no build: index.html is the
# artifact, and it is what gets served. These targets are the chores around it.
#
#   make serve    preview on localhost
#   make check    the invariants that are easy to break by hand
#   make scene    re-run the one-shot illustration generators
#   make clean    drop generator output
#
# `make gen` is deliberately not wired into anything: the generators emit
# fragments to paste, not files the page includes. See README.

PORT   ?= 8000
PYTHON ?= python3

.DEFAULT_GOAL := help

.PHONY: help
help:
	@sed -n 's/^#   //p' $(MAKEFILE_LIST) | head -4
	@echo
	@echo "  PORT=$(PORT) overrides the serve port."

.PHONY: serve
serve:
	@echo "http://localhost:$(PORT)  (ctrl-c to stop)"
	@$(PYTHON) -m http.server -d . $(PORT)

.PHONY: check
check:
	@$(PYTHON) tools/check.py

# gen_scene.py writes .svgfrag and *_keyframes.css into the repo root for you
# to paste. It does not touch index.html, and its output has drifted behind the
# committed HTML -- read the diff before pasting anything. See README.
.PHONY: scene
scene:
	@$(PYTHON) tools/gen_scene.py
	@echo "fragments written to the repo root; diff before pasting."

# gen_mcp.py is NOT the same: it rewrites the band inside index.html in place.
# Commit or stash first, then check `git diff`.
.PHONY: mcp
mcp:
	@$(PYTHON) tools/gen_mcp.py >/dev/null
	@echo "index.html rewritten in place; check git diff."

.PHONY: gen
gen: scene mcp

.PHONY: clean
clean:
	@rm -f *.svgfrag scene_keyframes.css side_keyframes.css
	@echo "generator output removed"
