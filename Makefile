
install_deps:
	sudo -H pip3 install -r requirements.txt

install:
	install -m 755 -T terminaler.py /usr/bin/terminaler
	install -m 644 assets/terminaler.service /lib/systemd/system/
	@echo "now call systemctl daemon-reload"
	@echo ".. enable service via: systemctl enable terminaler.service"
	@echo ".. start service via:  systemctl start terminaler.service"
	@echo ".. status via:         systemctl status terminaler.service"
	@echo ".. log info via:       journalctl -u terminaler.service"

uninstall:
	rm -rf /usr/bin/terminaler
	rm -rf /lib/systemd/system/terminaler.service
