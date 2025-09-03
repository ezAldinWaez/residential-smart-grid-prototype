# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Language-specific builds:"
	@echo "  make html-en     Build HTML documentation in English"
	@echo "  make html-ar     Build HTML documentation in Arabic"
	@echo "  make latex-en    Build LaTeX documentation in English"
	@echo "  make latex-ar    Build LaTeX documentation in Arabic"

.PHONY: help Makefile html-en html-ar latex-en latex-ar

# Language-specific builds
html-en:
	SPHINX_LANG=en $(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html/en/ $(SPHINXOPTS)

html-ar:
	SPHINX_LANG=ar $(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html/ar/ $(SPHINXOPTS)

latex-en:
	SPHINX_LANG=en $(SPHINXBUILD) -b latex $(SOURCEDIR) $(BUILDDIR)/latex/en/ $(SPHINXOPTS)
	$(MAKE) --directory=$(BUILDDIR)/latex/en/

latex-ar:
	SPHINX_LANG=ar $(SPHINXBUILD) -b latex $(SOURCEDIR) $(BUILDDIR)/latex/ar/ $(SPHINXOPTS)
	$(MAKE) --directory=$(BUILDDIR)/latex/ar/

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
