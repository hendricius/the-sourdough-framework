.PHONY: website
website:
	cd ../book && make mrproper && make website
	bundle install
	ruby modify_build.rb
