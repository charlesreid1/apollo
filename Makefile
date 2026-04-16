# Makefile for Apollo mission data processing

# List of all Apollo mission directories
APOLLO_DIRS := apollo7 apollo8 apollo9 apollo10 apollo11 apollo12 apollo13 apollo14 apollo15 apollo16 apollo17

# Default target
.PHONY: all
all: $(APOLLO_DIRS)

# Rule for each Apollo mission
.PHONY: $(APOLLO_DIRS)
$(APOLLO_DIRS):
	@echo "Processing $@..."
	@if [ -f "$@/download_journals.py" ]; then \
		echo "  Running download script..."; \
		cd "$@" && python download_journals.py; \
	else \
		echo "  Warning: download_journals.py not found in $@"; \
	fi
	@if [ -f "$@/process_journal.py" ]; then \
		echo "  Running process script..."; \
		cd "$@" && python process_journal.py; \
	elif [ -f "$@/process_journals.py" ]; then \
		echo "  Running process script..."; \
		cd "$@" && python process_journals.py; \
	else \
		echo "  Warning: process script not found in $@"; \
	fi

# Force targets - re-download all HTML files even if they already exist
APOLLO_DIRS_FORCE := $(addsuffix -force,$(APOLLO_DIRS))

.PHONY: force
force: $(APOLLO_DIRS_FORCE)

.PHONY: $(APOLLO_DIRS_FORCE)
$(APOLLO_DIRS_FORCE):
	@dir=$$(echo $@ | sed 's/-force$$//'); \
	echo "Processing $$dir (force)..."; \
	if [ -f "$$dir/download_journals.py" ]; then \
		echo "  Running download script (--force)..."; \
		cd "$$dir" && python download_journals.py --force; \
	else \
		echo "  Warning: download_journals.py not found in $$dir"; \
	fi; \
	if [ -f "$$dir/process_journal.py" ]; then \
		echo "  Running process script..."; \
		cd "$$dir" && python process_journal.py; \
	elif [ -f "$$dir/process_journals.py" ]; then \
		echo "  Running process script..."; \
		cd "$$dir" && python process_journals.py; \
	else \
		echo "  Warning: process script not found in $$dir"; \
	fi

# Clean target - removes html/ and js/ directories in each Apollo subdirectory
.PHONY: clean
clean:
	@echo "Cleaning up generated directories..."
	@for dir in $(APOLLO_DIRS); do \
		if [ -d "$$dir/html" ]; then \
			echo "  Removing $$dir/html..."; \
			rm -rf "$$dir/html"; \
		fi; \
		if [ -d "$$dir/js" ]; then \
			echo "  Removing $$dir/js..."; \
			rm -rf "$$dir/js"; \
		fi; \
	done
	@echo "Cleanup complete."

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all           - Process all Apollo missions (default, skips existing HTML files)"
	@echo "  force         - Process all Apollo missions, re-downloading all HTML files"
	@echo "  apollo7       - Process Apollo 7 data"
	@echo "  apollo8       - Process Apollo 8 data"
	@echo "  apollo9       - Process Apollo 9 data"
	@echo "  apollo10      - Process Apollo 10 data"
	@echo "  apollo11      - Process Apollo 11 data"
	@echo "  apollo12      - Process Apollo 12 data"
	@echo "  apollo13      - Process Apollo 13 data"
	@echo "  apollo14      - Process Apollo 14 data"
	@echo "  apollo15      - Process Apollo 15 data"
	@echo "  apollo16      - Process Apollo 16 data"
	@echo "  apollo17      - Process Apollo 17 data"
	@echo "  clean         - Remove html/ and js/ directories from all Apollo subdirectories"
	@echo "  help          - Show this help message"