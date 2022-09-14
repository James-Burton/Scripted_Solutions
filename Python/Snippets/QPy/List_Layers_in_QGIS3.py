## for qgis 3, opens a new window with data source
layer = iface.activeLayer()
QMessageBox.information(None, "parDir: ", layer.source())