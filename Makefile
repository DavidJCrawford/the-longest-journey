# Ingest and build. See Docs/HANDOFF.md for where this is up to.
#
# Unlike the two projects this is modelled on, the data here is not one source.
# New Zealand's environmental monitoring is published by regional councils, the
# Ministry for the Environment, NIWA and LAWA in different shapes. So there are
# two ingest steps rather than one: `fetch` asks data.govt.nz what exists, and
# `sources` downloads the ones that were chosen. Docs/SOURCES.md says which and
# on what licence.

CACHE ?= .cache
SITE  := site

.PHONY: help fetch sources emit verify data build links preview check clean

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  %-10s %s\n", $$1, $$2}'

fetch: ## Ask data.govt.nz what exists -> .cache/catalogue/
	python3 pipeline/fetch.py

sources: ## Download the chosen sources -> .cache/
	python3 pipeline/sources.py

emit: ## Source data -> canonical JSON in site/data/
	python3 pipeline/emit.py

verify: ## Check the emitted JSON against facts it did not produce
	python3 pipeline/verify.py

data: sources emit verify ## Full data refresh

build: verify ## Build the site and its search index, then check its links
	cd $(SITE) && npm run build
	python3 pipeline/check_site.py

links: ## Check the built site for links that go nowhere
	python3 pipeline/check_site.py

preview: ## Serve the built site
	cd $(SITE) && npm run preview

check: ## Type check
	cd $(SITE) && npm run check

clean:
	rm -rf $(SITE)/dist $(SITE)/node_modules/.astro
