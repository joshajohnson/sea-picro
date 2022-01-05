VERSION?=0.1
NAME?=
DESIGNER?=Josh Johnson

prod-files:
	make gerb
	make pnp
	make bom

new:
	git submodule update --init --recursive --progress
	cd josh-kicad-lib && git checkout master && git pull
	cd josh-kicad-lib && bash setup.sh "$(VERSION)" "$(NAME)" "$(DESIGNER)"

