include config/Makefile

#============================
### START DEVELOPING ########
#============================

init: ## start virtual environment and install dev. requirements
	rm -fr $(VIRTUAL_ENV)
	virtualenv -p python3 $(VIRTUAL_ENV)
	$(MAKE) install

install: ## install development libs
	pip install -r requirements.txt