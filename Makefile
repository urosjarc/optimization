include config/Makefile

.PHONY: libs

#============================
### START DEVELOPING ########
#============================

init: ## start virtual environment and install dev. requirements
	rm -fr $(VIRTUAL_ENV)
	virtualenv -p python3 $(VIRTUAL_ENV)
	$(MAKE) install

libs:
	rm libs temp -rf
	mkdir libs temp
	git clone https://github.com/kbinani/colormap-shaders temp/colormap-shaders
	git clone https://github.com/philipmorrisintl/GOBench temp/GOBench
	mv temp/GOBench/gobench/go_benchmark_functions libs/go_benchmark_functions
	mkdir libs/colormap_shaders
	mv temp/colormap-shaders/shaders/glsl libs/colormap_shaders/glsl
	mv temp/colormap-shaders/sample libs/colormap_shaders/previews
	rm temp -rf

install: ## install development libs
	pip install -r requirements.txt
